"""Interface base dos adapters de canal (ETAPA 3).

Cada canal externo (Telegram, WhatsApp, ...) implementa três responsabilidades:
normalizar a mensagem recebida, enviar mensagens e verificar a autenticidade do
webhook. Nenhum segredo é logado (OMNICHANNEL.md §Segurança).
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

_MULTI_SPACE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Normaliza texto: strip nas bordas, colapsa espaços múltiplos e minúsculas."""
    return _MULTI_SPACE.sub(" ", (value or "").strip()).lower()


@dataclass(frozen=True)
class NormalizedMessage:
    """Mensagem normalizada, independente do canal de origem."""

    channel: str
    external_chat_id: str
    body: str
    normalized_body: str
    direction: str = "inbound"
    sender_kind: str = "customer"
    external_message_id: str | None = None
    sender_display_name: str = ""
    phone: str = ""
    payload: dict[str, Any] = field(default_factory=dict)


class ChannelAdapter(ABC):
    """Contrato de integração com um canal externo."""

    channel: str = ""

    @abstractmethod
    def normalize(self, payload: dict[str, Any]) -> NormalizedMessage:
        """Converte o payload bruto do provedor em ``NormalizedMessage``."""

    @abstractmethod
    def send_message(
        self,
        *,
        external_chat_id: str,
        text: str,
        reply_to: str | None = None,
    ) -> dict[str, Any]:
        """Envia uma mensagem ao canal e retorna os dados do provedor."""

    @abstractmethod
    def verify_webhook(self, request) -> bool:
        """Valida autenticidade/assinatura do webhook do provedor."""
