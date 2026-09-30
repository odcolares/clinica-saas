"""Cache de respostas do LLM via Redis (django-redis) — ETAPA 4.

Só faz sentido cachear respostas determinísticas: ``temperature == 0``. Para
qualquer outra temperatura ``get``/``set`` são no-op. A chave é
``llm:sha256(model + messages + temperature)[:16]`` com TTL de 1h.

Redis indisponível não derruba o fluxo (mesmo contrato de
``apps/omnichannel/services.py``): a chamada apenas segue para o provedor.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import structlog
from django.conf import settings
from django.core.cache import cache

logger = structlog.get_logger(__name__)

LLM_CACHE_TTL_SECONDS = getattr(settings, "LLM_CACHE_TTL_SECONDS", 3600)
_CACHE_PREFIX = "llm:"
_KEY_DIGEST_LEN = 16


def _canonical_payload(
    model: str, messages: list[dict[str, Any]], temperature: float
) -> str:
    return json.dumps(
        {"model": model, "messages": messages, "temperature": temperature},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )


def cache_key(
    model: str, messages: list[dict[str, Any]], temperature: float = 0.0
) -> str:
    """Chave determinística ``llm:<sha256(...)[:16]>``."""
    digest = hashlib.sha256(
        _canonical_payload(model, messages, temperature).encode("utf-8")
    ).hexdigest()[:_KEY_DIGEST_LEN]
    return f"{_CACHE_PREFIX}{digest}"


def get_cached_response(
    model: str, messages: list[dict[str, Any]], temperature: float = 0.0
) -> str | None:
    """Resposta cacheada ou ``None`` (temperatura != 0, miss ou Redis fora)."""
    if temperature != 0:
        return None
    try:
        return cache.get(cache_key(model, messages, temperature))
    except Exception as exc:  # noqa: BLE001 — cache é otimização, não verdade
        logger.warning("llm_cache_get_failed", error=type(exc).__name__)
        return None


def set_cached_response(
    model: str,
    messages: list[dict[str, Any]],
    response: str,
    temperature: float = 0.0,
) -> None:
    """Grava a resposta no Redis (apenas ``temperature == 0``); falha é tolerada."""
    if temperature != 0:
        return
    try:
        cache.set(
            cache_key(model, messages, temperature),
            response,
            LLM_CACHE_TTL_SECONDS,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("llm_cache_set_failed", error=type(exc).__name__)


def invalidate(
    model: str, messages: list[dict[str, Any]], temperature: float = 0.0
) -> None:
    """Remove uma entrada do cache (tolerante a Redis indisponível)."""
    try:
        cache.delete(cache_key(model, messages, temperature))
    except Exception as exc:  # noqa: BLE001
        logger.warning("llm_cache_delete_failed", error=type(exc).__name__)
