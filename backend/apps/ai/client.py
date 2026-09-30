"""Cliente OpenAI assíncrono com pooling de conexões (ETAPA 4).

Um único ``AsyncOpenAI`` reaproveita um ``httpx.AsyncClient`` com pool
(max 20 conexões, 10 keep-alive, timeout 30s). A chave vem exclusivamente do
ambiente (``OPENAI_API_KEY``, exposta em ``settings``) — nunca do banco/código.

O cliente é criado sob demanda e pode ser fechado no shutdown do processo.
"""

from __future__ import annotations

from typing import Any

import httpx
from django.conf import settings
from openai import AsyncOpenAI

OPENAI_TIMEOUT_SECONDS = getattr(settings, "OPENAI_TIMEOUT_SECONDS", 30.0)
OPENAI_MAX_CONNECTIONS = getattr(settings, "OPENAI_MAX_CONNECTIONS", 20)
OPENAI_MAX_KEEPALIVE = getattr(settings, "OPENAI_MAX_KEEPALIVE_CONNECTIONS", 10)

_client: AsyncOpenAI | None = None
_http_client: httpx.AsyncClient | None = None


def build_limits() -> httpx.Limits:
    """Limites de pool do provedor (max 20 conexões, 10 keep-alive)."""
    return httpx.Limits(
        max_connections=OPENAI_MAX_CONNECTIONS,
        max_keepalive_connections=OPENAI_MAX_KEEPALIVE,
    )


def build_http_client() -> httpx.AsyncClient:
    """Cria o ``httpx.AsyncClient`` com os limites de pool do projeto."""
    return httpx.AsyncClient(
        limits=build_limits(),
        timeout=httpx.Timeout(OPENAI_TIMEOUT_SECONDS),
    )


def get_client() -> AsyncOpenAI:
    """Retorna o cliente singleton, criando-o na primeira chamada.

    Levanta ``RuntimeError`` se ``OPENAI_API_KEY`` não estiver configurada —
    falha explícita em vez de tentar rede sem credencial.
    """
    global _client, _http_client
    if _client is None:
        api_key = (getattr(settings, "OPENAI_API_KEY", "") or "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada (defina no .env).")
        _http_client = build_http_client()
        _client = AsyncOpenAI(api_key=api_key, http_client=_http_client)
    return _client


async def close_client() -> None:
    """Fecha o pool e descarta o singleton (shutdown / testes)."""
    global _client, _http_client
    if _http_client is not None:
        await _http_client.aclose()
    _client = None
    _http_client = None


async def complete(
    *,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float = 0.0,
    **kwargs: Any,
):
    """Atalho para ``chat.completions.create`` usando o cliente com pooling."""
    client = get_client()
    return await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        **kwargs,
    )
