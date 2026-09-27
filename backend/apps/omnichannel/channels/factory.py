"""Factory de adapters por canal (ETAPA 3).

Canais sem adapter dedicado (ex.: WhatsApp futuro) recebem o ``NoopChannelAdapter``
— o webhook/ingestão continua funcionando sem rede até a integração real existir.
"""

from __future__ import annotations

from apps.omnichannel.channels.base import ChannelAdapter
from apps.omnichannel.channels.noop import NoopChannelAdapter
from apps.omnichannel.channels.telegram import TelegramChannelAdapter

_ADAPTERS: dict[str, type[ChannelAdapter]] = {
    "telegram": TelegramChannelAdapter,
}


def get_adapter(channel: str) -> ChannelAdapter:
    """Retorna o adapter do canal (Noop para canais ainda não integrados)."""
    adapter_cls = _ADAPTERS.get(channel)
    if adapter_cls is None:
        return NoopChannelAdapter(channel=channel)
    return adapter_cls()
