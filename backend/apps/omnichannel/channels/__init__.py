"""Channel adapters (ETAPA 3) — integrações externas sempre por adapter.

Ver `Projeto_SaaS/domains/OMNICHANNEL.md` §Arquitetura e ETAPAS.md regra 5.
"""

from __future__ import annotations

from apps.omnichannel.channels.base import (
    ChannelAdapter,
    NormalizedMessage,
    normalize_text,
)
from apps.omnichannel.channels.factory import get_adapter

__all__ = [
    "ChannelAdapter",
    "NormalizedMessage",
    "get_adapter",
    "normalize_text",
]
