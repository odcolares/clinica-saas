"""Regras de domínio do Omnichannel (ETAPA 3).

Arquitetura (OMNICHANNEL.md): Canal externo → Adapter → Webhook → Normalização →
Conversation → CRM. Este módulo é o único ponto de verdade do ciclo de vida de
conversas/mensagens, do vínculo com Lead/Customer e da sessão em Redis.

Tudo opera no schema do tenant ativo (django-tenants). A sessão degrada de forma
graciosa se o Redis estiver indisponível: o atendimento não quebra por cache.
"""

from __future__ import annotations

from typing import Any

import structlog
from django.core.cache import cache
from django.db import connection
from rest_framework.exceptions import ValidationError

from apps.crm.models import Customer, Interaction, Lead, LeadSource, LeadStatus
from apps.crm.permissions import grant_member_perms
from apps.omnichannel.channels.base import (
    ChannelAdapter,
    NormalizedMessage,
    normalize_text,
)
from apps.omnichannel.channels.factory import get_adapter
from apps.omnichannel.models import Conversation, ConversationMessage

logger = structlog.get_logger(__name__)

SESSION_TTL_SECONDS = 3600
LEAD_SOURCE_NAME = "telegram"


def _tenant_schema() -> str:
    return getattr(connection, "schema_name", None) or "public"


def session_cache_key(tenant: str, channel: str, external_chat_id: str) -> str:
    """Chave da sessão omnichannel no Redis: tenant + canal + chat (TTL 3600s)."""
    return f"omnichannel:session:{tenant}:{channel}:{external_chat_id}"


def set_session(channel: str, external_chat_id: str, data: dict[str, Any]) -> None:
    """Grava a sessão da conversa. Redis fora do ar não derruba o atendimento."""
    key = session_cache_key(_tenant_schema(), channel, external_chat_id)
    try:
        cache.set(key, data, SESSION_TTL_SECONDS)
    except Exception as exc:  # noqa: BLE001 — cache é otimização, não fonte de verdade
        logger.warning("omnichannel_session_set_failed", error=type(exc).__name__)


def get_session(channel: str, external_chat_id: str) -> dict[str, Any] | None:
    """Lê a sessão da conversa (None se ausente ou cache indisponível)."""
    key = session_cache_key(_tenant_schema(), channel, external_chat_id)
    try:
        return cache.get(key)
    except Exception as exc:  # noqa: BLE001
        logger.warning("omnichannel_session_get_failed", error=type(exc).__name__)
        return None


def get_or_create_conversation(
    *,
    channel: str,
    external_chat_id: str,
    customer: Customer | None = None,
    lead: Lead | None = None,
) -> tuple[Conversation, bool]:
    """Localiza a conversa pelo par (canal, chat externo) ou cria uma nova."""
    conversation, created = Conversation.objects.get_or_create(
        channel=channel,
        external_chat_id=external_chat_id,
        defaults={"customer": customer, "lead": lead},
    )
    if created:
        logger.info(
            "omnichannel_conversation_created",
            channel=channel,
            conversation_id=conversation.pk,
        )
    return conversation, created


def ingest_inbound_message(
    *,
    channel: str,
    payload: dict[str, Any],
    adapter: ChannelAdapter | None = None,
) -> tuple[ConversationMessage, bool]:
    """Normaliza e persiste uma mensagem recebida de webhook.

    Idempotente por ``external_message_id`` (``telegram_message_id``): reentregas
    do provedor não duplicam a mensagem. Retorna (mensagem, criada).
    """
    adapter = adapter or get_adapter(channel)
    normalized = adapter.normalize(payload)

    conversation, _ = get_or_create_conversation(
        channel=normalized.channel,
        external_chat_id=normalized.external_chat_id,
    )
    _merge_metadata(conversation, normalized)

    if normalized.external_message_id:
        duplicate = ConversationMessage.objects.filter(
            conversation=conversation,
            telegram_message_id=normalized.external_message_id,
        ).first()
        if duplicate is not None:
            logger.info(
                "omnichannel_message_duplicate",
                conversation_id=conversation.pk,
                message_id=duplicate.pk,
            )
            return duplicate, False

    message = ConversationMessage.objects.create(
        conversation=conversation,
        direction=normalized.direction,
        sender_kind=normalized.sender_kind,
        body=normalized.body,
        normalized_body=normalized.normalized_body,
        telegram_message_id=normalized.external_message_id,
        payload=normalized.payload,
    )
    create_lead_from_message(conversation, normalized)
    set_session(
        conversation.channel,
        conversation.external_chat_id,
        {
            "conversation_id": conversation.pk,
            "last_message_id": message.pk,
            "last_message_at": message.created_at.isoformat(),
        },
    )
    logger.info(
        "omnichannel_message_ingested",
        channel=conversation.channel,
        conversation_id=conversation.pk,
        message_id=message.pk,
    )
    return message, True


def _merge_metadata(conversation: Conversation, normalized: NormalizedMessage) -> None:
    """Enriquece a conversa com dados do remetente (telefone, nome), sem sobrescrever."""
    metadata = dict(conversation.metadata or {})
    changed = False
    if normalized.phone and not metadata.get("phone"):
        metadata["phone"] = normalized.phone
        changed = True
    if normalized.sender_display_name and not metadata.get("display_name"):
        metadata["display_name"] = normalized.sender_display_name
        changed = True
    if changed:
        conversation.metadata = metadata
        conversation.save(update_fields=["metadata", "updated_at"])


def create_lead_from_message(
    conversation: Conversation, normalized: NormalizedMessage
) -> Lead | None:
    """Vincula ou cria Lead/Customer a partir da mensagem (OMNICHANNEL.md §Webhooks).

    Se a conversa já tem Customer/Lead, apenas registra a interação. Caso
    contrário, tenta casar por telefone; senão cria um Lead com origem
    ``telegram``. Sempre registra Interaction ``message`` no CRM.
    """
    if conversation.customer_id or conversation.lead_id:
        _record_interaction(conversation, normalized)
        return conversation.lead

    phone = (conversation.metadata or {}).get("phone", "")
    if phone:
        customer = Customer.objects.filter(phone=phone).first()
        if customer is not None:
            conversation.customer = customer
            conversation.save(update_fields=["customer", "updated_at"])
            _record_interaction(conversation, normalized)
            return None

        existing_lead = Lead.objects.filter(phone=phone).first()
        if existing_lead is not None:
            _link_lead(conversation, existing_lead, normalized)
            return existing_lead

    source, _ = LeadSource.objects.get_or_create(
        name=LEAD_SOURCE_NAME,
        defaults={"description": "Origem Telegram (omnichannel)"},
    )
    status = LeadStatus.objects.get(code=Lead.StatusCode.NEW)
    lead = Lead.objects.create(
        name=normalized.sender_display_name or conversation.external_chat_id,
        phone=phone,
        source=source,
        status=status,
        notes=f"Conversa {conversation.channel} #{conversation.external_chat_id}",
    )
    _link_lead(conversation, lead, normalized)
    logger.info(
        "omnichannel_lead_created",
        lead_id=lead.pk,
        conversation_id=conversation.pk,
        channel=conversation.channel,
    )
    return lead


def _link_lead(
    conversation: Conversation, lead: Lead, normalized: NormalizedMessage
) -> None:
    conversation.lead = lead
    conversation.save(update_fields=["lead", "updated_at"])
    _record_interaction(conversation, normalized, lead=lead)


def _record_interaction(
    conversation: Conversation,
    normalized: NormalizedMessage,
    *,
    lead: Lead | None = None,
) -> None:
    Interaction.objects.create(
        customer=conversation.customer,
        lead=lead or conversation.lead,
        kind=Interaction.KIND_MESSAGE,
        description=normalized.body or f"Mensagem {conversation.channel}",
    )


def assign_conversation(
    conversation: Conversation, *, user, author=None
) -> Conversation:
    """Atribui a conversa a um atendente e concede permissões de objeto (guardian)."""
    if user is None:
        raise ValidationError({"assigned_to": "Atendente é obrigatório."})

    conversation.assigned_to = user
    conversation.status = Conversation.Status.ASSIGNED
    conversation._change_reason = f"Atribuída a {user}"
    conversation._history_user = author or user
    conversation.save()
    grant_member_perms(user, conversation)
    if conversation.lead_id:
        grant_member_perms(user, conversation.lead)
    if conversation.customer_id:
        grant_member_perms(user, conversation.customer)
    logger.info(
        "omnichannel_conversation_assigned",
        conversation_id=conversation.pk,
        user_id=user.pk,
    )
    return conversation


def send_outbound_message(
    conversation: Conversation,
    *,
    text: str,
    author,
    adapter: ChannelAdapter | None = None,
) -> ConversationMessage:
    """Envia uma resposta do atendente pelo adapter do canal e persiste a mensagem."""
    body = (text or "").strip()
    if not body:
        raise ValidationError({"body": "Mensagem não pode ser vazia."})

    adapter = adapter or get_adapter(conversation.channel)
    result = adapter.send_message(
        external_chat_id=conversation.external_chat_id, text=body
    )
    external_id = None
    if isinstance(result, dict):
        provider_message = result.get("result")
        if isinstance(provider_message, dict) and provider_message.get("message_id"):
            external_id = str(provider_message["message_id"])

    message = ConversationMessage.objects.create(
        conversation=conversation,
        direction=ConversationMessage.Direction.OUTBOUND,
        sender_kind=ConversationMessage.SenderKind.AGENT,
        body=body,
        normalized_body=normalize_text(body),
        telegram_message_id=external_id,
        payload=result if isinstance(result, dict) else {},
    )
    logger.info(
        "omnichannel_message_sent",
        conversation_id=conversation.pk,
        message_id=message.pk,
        user_id=getattr(author, "pk", None),
    )
    return message
