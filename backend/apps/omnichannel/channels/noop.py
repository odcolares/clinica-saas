"""Adapter Noop (ETAPA 3) — testes e canais futuros ainda não implementados.

Não faz rede: normaliza de forma genérica e apenas registra o envio. Serve de
fallback para canais como WhatsApp até que um adapter real exista (prova a
extensibilidade do factory).
"""

from __future__ import annotations

from typing import Any

import structlog

from apps.omnichannel.channels.base import (
    ChannelAdapter,
    NormalizedMessage,
    normalize_text,
)

logger = structlog.get_logger(__name__)


class NoopChannelAdapter(ChannelAdapter):
    """Adapter inerte, sem integração externa."""

    def __init__(self, channel: str = "noop") -> None:
        self.channel = channel

    def normalize(self, payload: dict[str, Any]) -> NormalizedMessage:
        body = str(payload.get("text") or payload.get("body") or "")
        return NormalizedMessage(
            channel=self.channel,
            external_chat_id=str(
                payload.get("external_chat_id") or payload.get("chat_id") or ""
            ),
            body=body,
            normalized_body=normalize_text(body),
            direction=payload.get("direction", "inbound"),
            sender_kind=payload.get("sender_kind", "customer"),
            external_message_id=payload.get("external_message_id"),
            sender_display_name=str(payload.get("sender_display_name", "")),
            phone=str(payload.get("phone", "")),
            payload=payload,
        )

    def send_message(
        self,
        *,
        external_chat_id: str,
        text: str,
        reply_to: str | None = None,
    ) -> dict[str, Any]:
        logger.info("noop_send_message", channel=self.channel, chat=external_chat_id)
        return {"ok": True, "channel": self.channel, "chat_id": external_chat_id}

    def verify_webhook(self, request) -> bool:
        return True
