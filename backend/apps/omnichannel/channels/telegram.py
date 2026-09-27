"""Adapter do Telegram (ETAPA 3).

Usa apenas stdlib + Django + structlog (sem dependência nova). O token do bot e
o segredo do webhook vêm do ambiente (``TELEGRAM_BOT_TOKEN`` e
``TELEGRAM_WEBHOOK_SECRET``) e nunca entram em logs.
"""

from __future__ import annotations

import hmac
import json
import urllib.error
import urllib.request
from typing import Any

import structlog
from django.conf import settings
from django.db import connection
from rest_framework.exceptions import ValidationError

from apps.omnichannel.channels.base import (
    ChannelAdapter,
    NormalizedMessage,
    normalize_text,
)

logger = structlog.get_logger(__name__)

# B105: nome do header, não um segredo (o valor vem de TELEGRAM_WEBHOOK_SECRET).
WEBHOOK_SECRET_HEADER = "X-Telegram-Bot-Api-Secret-Token"  # nosec B105
API_BASE = "https://api.telegram.org"
SEND_TIMEOUT_SECONDS = 5


class TelegramChannelAdapter(ChannelAdapter):
    """Integração com o Telegram Bot API."""

    channel = "telegram"

    def __init__(self) -> None:
        self._token = getattr(settings, "TELEGRAM_BOT_TOKEN", "") or ""

    def normalize(self, payload: dict[str, Any]) -> NormalizedMessage:
        """Extrai e normaliza uma mensagem de um Update do Telegram."""
        message = payload.get("message") or payload.get("edited_message") or {}
        chat = message.get("chat") or {}
        sender = message.get("from") or {}

        chat_id = chat.get("id")
        if chat_id is None:
            raise ValidationError({"detail": "Payload do Telegram sem chat.id."})

        body = message.get("text") or message.get("caption") or ""
        message_id = message.get("message_id")
        display_name = " ".join(
            part for part in (sender.get("first_name"), sender.get("last_name")) if part
        ).strip() or (sender.get("username") or "")
        phone = (message.get("contact") or {}).get("phone_number") or ""

        return NormalizedMessage(
            channel=self.channel,
            external_chat_id=str(chat_id),
            body=body,
            normalized_body=normalize_text(body),
            direction="inbound",
            sender_kind="customer",
            external_message_id=str(message_id) if message_id is not None else None,
            sender_display_name=display_name,
            phone=phone,
            payload=payload,
        )

    def send_message(
        self,
        *,
        external_chat_id: str,
        text: str,
        reply_to: str | None = None,
    ) -> dict[str, Any]:
        """Envia mensagem via Bot API. Levanta ValidationError se não configurado."""
        if not self._token:
            raise ValidationError({"detail": "TELEGRAM_BOT_TOKEN não configurado."})

        body: dict[str, Any] = {"chat_id": external_chat_id, "text": text}
        if reply_to:
            body["reply_to_message_id"] = reply_to
        request = urllib.request.Request(
            f"{API_BASE}/bot{self._token}/sendMessage",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            # B310: URL é uma constante HTTPS fixa (api.telegram.org) com token do ambiente.
            with urllib.request.urlopen(  # nosec B310
                request, timeout=SEND_TIMEOUT_SECONDS
            ) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            logger.warning("telegram_send_failed", error=type(exc).__name__)
            raise ValidationError(
                {"detail": "Falha ao enviar mensagem no Telegram."}
            ) from exc

    def verify_webhook(self, request) -> bool:
        """Valida o segredo do webhook vinculado ao tenant do request.

        O segredo é POR TENANT (``TELEGRAM_WEBHOOK_SECRET_<SCHEMA>``), resolvido a
        partir do schema já ativo no request. O segredo global só é aceito como
        fallback explícito quando ``TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET=True``.
        Sem segredo para o tenant → 403 (fail-closed). Comparação em tempo
        constante; nenhum segredo é logado.
        """
        provided = request.headers.get(WEBHOOK_SECRET_HEADER, "")
        expected = self._expected_secret()
        if not provided or not expected:
            return False
        return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))

    def _expected_secret(self) -> str:
        schema = getattr(connection, "schema_name", "") or ""
        secrets = getattr(settings, "TELEGRAM_WEBHOOK_SECRETS", {}) or {}
        tenant_secret = secrets.get(schema)
        if tenant_secret:
            return tenant_secret
        if getattr(settings, "TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET", False):
            return getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "") or ""
        logger.warning("telegram_webhook_secret_missing", tenant=schema)
        return ""
