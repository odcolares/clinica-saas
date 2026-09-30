"""Circuit breaker para chamadas ao provedor de LLM (ETAPA 4).

Usa ``pybreaker`` (fail-max 5, recovery 30s). Quando o circuito abre — ou o
provedor falha — o fallback pode devolver uma resposta cacheada; sem fallback,
o erro é convertido em ``LLMUnavailableError`` (erro tratado, sem propagar
detalhes internos do provedor).

Configurável por settings ``OPENAI_BREAKER_FAIL_MAX`` e
``OPENAI_BREAKER_RESET_TIMEOUT``.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

import pybreaker
import structlog
from django.conf import settings

logger = structlog.get_logger(__name__)

FAILURE_THRESHOLD = getattr(settings, "OPENAI_BREAKER_FAIL_MAX", 5)
RECOVERY_TIMEOUT = getattr(settings, "OPENAI_BREAKER_RESET_TIMEOUT", 30)

T = TypeVar("T")


class LLMUnavailableError(RuntimeError):
    """Provedor de LLM indisponível (circuito aberto ou falha tratada)."""


def create_breaker(
    *,
    name: str = "openai",
    fail_max: int = FAILURE_THRESHOLD,
    reset_timeout: int = RECOVERY_TIMEOUT,
) -> pybreaker.CircuitBreaker:
    """Cria um breaker isolado (útil em testes e em múltiplos provedores)."""
    return pybreaker.CircuitBreaker(
        fail_max=fail_max,
        reset_timeout=reset_timeout,
        name=name,
    )


llm_breaker = create_breaker()


def _fallback_or_raise(
    exc: Exception, fallback: Callable[[], T] | None, reason: str
) -> T:
    logger.warning("llm_call_fallback", reason=reason, error=type(exc).__name__)
    if fallback is not None:
        return fallback()
    raise LLMUnavailableError("Serviço de IA indisponível. Tente novamente.") from exc


def call_with_fallback(
    fn: Callable[..., T],
    *args: Any,
    fallback: Callable[[], T] | None = None,
    breaker: pybreaker.CircuitBreaker | None = None,
    **kwargs: Any,
) -> T:
    """Executa ``fn`` sob o breaker; em falha usa ``fallback`` ou erro tratado.

    ``fallback`` tipicamente é ``lambda: get_cached_response(...)``. Qualquer
    exceção do provedor conta como falha para o breaker (pybreaker).
    """
    active_breaker = breaker or llm_breaker
    try:
        return active_breaker.call(fn, *args, **kwargs)
    except pybreaker.CircuitBreakerError as exc:
        return _fallback_or_raise(exc, fallback, "circuit_open")
    except Exception as exc:  # noqa: BLE001 — provedor externo: normalizar erro
        return _fallback_or_raise(exc, fallback, "provider_error")
