"""Omnichannel (ETAPA 3) — proprietário de Conversation e ConversationMessage.

Modelos conforme `Projeto_SaaS/domains/OMNICHANNEL.md` e `DATABASE.md`. Todos
operam dentro do schema do tenant; o isolamento é garantido pelo django-tenants
e o escopo de visibilidade por objeto pelo django-guardian (ver
apps.crm.permissions). O vínculo com Lead/Customer usa FK nullable — o canal
registra a comunicação; o CRM apresenta a relação (OMNICHANNEL.md §CRM).
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from apps.crm.models import TimeStampedModel


class Conversation(TimeStampedModel):
    """Conversa contínua com um contato externo em um canal."""

    class Channel(models.TextChoices):
        TELEGRAM = "telegram", "Telegram"
        WHATSAPP = "whatsapp", "WhatsApp"

    class Status(models.TextChoices):
        OPEN = "open", "Aberta"
        ASSIGNED = "assigned", "Atribuída"
        CLOSED = "closed", "Fechada"

    channel = models.CharField(
        max_length=16, choices=Channel.choices, default=Channel.TELEGRAM
    )
    external_chat_id = models.CharField(
        max_length=128,
        help_text="Identificador da conversa no provedor (ex.: chat.id do Telegram).",
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.OPEN
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="omnichannel_conversations",
    )
    customer = models.ForeignKey(
        "crm.Customer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="conversations",
    )
    lead = models.ForeignKey(
        "crm.Lead",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="conversations",
    )
    metadata = models.JSONField(default=dict, blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ("-updated_at",)
        indexes = [
            models.Index(fields=["channel", "status"]),
            models.Index(fields=["external_chat_id"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["channel", "external_chat_id"],
                name="uniq_conversation_channel_chat",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.channel}:{self.external_chat_id}"


class ConversationMessage(TimeStampedModel):
    """Mensagem individual de uma Conversation (inbound/outbound)."""

    class Direction(models.TextChoices):
        INBOUND = "inbound", "Entrada"
        OUTBOUND = "outbound", "Saída"

    class SenderKind(models.TextChoices):
        CUSTOMER = "customer", "Cliente"
        AGENT = "agent", "Atendente"
        SYSTEM = "system", "Sistema"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    direction = models.CharField(
        max_length=16, choices=Direction.choices, default=Direction.INBOUND
    )
    sender_kind = models.CharField(
        max_length=16, choices=SenderKind.choices, default=SenderKind.CUSTOMER
    )
    body = models.TextField()
    normalized_body = models.TextField(blank=True)
    telegram_message_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="message_id do Telegram — base da idempotência de webhook.",
    )
    payload = models.JSONField(default=dict, blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["direction"]),
            models.Index(fields=["telegram_message_id"]),
        ]
        constraints = [
            # Idempotência no nível do banco: uma mensagem do provedor não pode
            # ser persistida duas vezes na mesma conversa.
            models.UniqueConstraint(
                fields=["conversation", "telegram_message_id"],
                condition=models.Q(telegram_message_id__isnull=False),
                name="uniq_message_telegram_id",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.direction}:{self.pk}"
