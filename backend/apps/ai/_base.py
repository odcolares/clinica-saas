"""Ponte sync entre os serviços AI e o cliente LLM (Etapa 4).

Centraliza o que é comum aos 5 serviços (``intent``, ``extraction``,
``rag``, ``summarizer``, ``auto_reply``) para não duplicar:

- execução de coroutine em contexto sync (views DRF são sync) sobre um
  **loop persistente em thread própria** — o ``AsyncOpenAI`` singleton
  mantém o pool httpx vivo entre chamadas (recriar o loop a cada chamada
  quebraria conexões keep-alive);
- cache determinístico (``temperature == 0``) antes do provedor, via
  ``apps.ai.cache``;
- chamada sob circuit breaker via ``apps.ai.breaker.call_with_fallback``,
  com fallback para resposta cacheada (stale) quando disponível;
- gravação da auditoria em ``LLMInteraction`` via
  ``apps.ai.services.record_interaction`` (tokens/custo/latência),
  inclusive em falha — toda chamada gera linha;
- log estruturado com ``structlog`` (nenhum segredo).

Nunca chama OpenAI direto: todo tráfego sai por ``apps.ai.client``.
Tudo opera no schema do tenant ativo.
"""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any, Awaitable, Callable

import structlog
from django.db import connection

from apps.ai import breaker as ai_breaker
from apps.ai import cache as ai_cache
from apps.ai import client as ai_client
from apps.ai.services import record_interaction

logger = structlog.get_logger(__name__)

DEFAULT_MODEL = "gpt-4o-mini"
UNAVAILABLE_TEXT = "[indisponível]"

_LOOP: asyncio.AbstractEventLoop | None = None
_LOOP_LOCK = threading.Lock()


def _tenant_schema() -> str:
    """Schema do tenant ativo (apenas para diagnóstico em logs)."""
    return getattr(connection, "schema_name", None) or "public"


def _ensure_loop() -> asyncio.AbstractEventLoop:
    """Loop persistente em thread daemon para as chamadas async.

    O cliente ``AsyncOpenAI`` é um singleton com pool httpx próprio; o
    mesmo loop entre chamadas mantém as conexões keep-alive utilizáveis.
    """
    global _LOOP
    with _LOOP_LOCK:
        if _LOOP is None or _LOOP.is_closed():
            _LOOP = asyncio.new_event_loop()
            threading.Thread(
                target=_LOOP.run_forever,
                name="ai-llm-loop",
                daemon=True,
            ).start()
        return _LOOP


def run_coro(coro: Awaitable[Any]) -> Any:
    """Agenda uma coroutine no loop persistente e aguarda o resultado."""
    loop = _ensure_loop()
    return asyncio.run_coroutine_threadsafe(coro, loop).result()


def _sync(fn: Callable[[], Awaitable[Any]]) -> Callable[[], Any]:
    """Adapta ``() -> coroutine`` para callable sync (o breaker é sync)."""

    def _run() -> Any:
        return run_coro(fn())

    return _run


def _record(
    *,
    feature: str,
    model: str,
    messages: list[dict[str, Any]],
    response: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    latency_ms: int = 0,
) -> None:
    """Grava a auditoria; falha de gravação não derruba a resposta."""
    try:
        record_interaction(
            model=model,
            prompt=messages,
            response=response,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
        )
    except Exception as exc:  # noqa: BLE001 — auditoria nunca quebra a API
        logger.error(
            "ai_audit_failed",
            feature=feature,
            tenant=_tenant_schema(),
            error=type(exc).__name__,
        )


def llm_call(
    *,
    feature: str,
    messages: list[dict[str, Any]],
    call: Callable[[Any], Awaitable[Any]],
    extract_text: Callable[[Any], str],
    extract_usage: Callable[[Any], tuple[int, int]] | None = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
) -> tuple[str, int, int]:
    """Executa uma chamada LLM com cache → breaker → auditoria.

    ``call`` recebe o cliente e devolve uma coroutine; ``extract_text``
    converte a resposta do provedor em texto (o que vai ao cache e à
    auditoria). Retorna ``(texto, prompt_tokens, completion_tokens)``.

    Em falha do provedor sem fallback cacheado levanta
    ``LLMUnavailableError`` — e mesmo assim grava a linha de auditoria.
    """
    cached = ai_cache.get_cached_response(model, messages, temperature)
    if cached is not None:
        logger.info("ai_cache_hit", feature=feature, tenant=_tenant_schema())
        _record(
            feature=feature,
            model=model,
            messages=messages,
            response=cached,
        )
        return cached, 0, 0

    started = time.monotonic()

    async def _invoke() -> Any:
        # get_client DENTRO do breaker: ausência de chave conta como falha.
        return await call(ai_client.get_client())

    def _fallback() -> str | None:
        stale = ai_cache.get_cached_response(model, messages, temperature)
        if stale is not None:
            logger.info("ai_fallback_cache", feature=feature, tenant=_tenant_schema())
        return stale

    try:
        response = ai_breaker.call_with_fallback(_sync(_invoke), fallback=_fallback)
    except ai_breaker.LLMUnavailableError:
        latency_ms = int((time.monotonic() - started) * 1000)
        _record(
            feature=feature,
            model=model,
            messages=messages,
            response=UNAVAILABLE_TEXT,
            latency_ms=latency_ms,
        )
        raise

    latency_ms = int((time.monotonic() - started) * 1000)
    if response is None:
        _record(
            feature=feature,
            model=model,
            messages=messages,
            response=UNAVAILABLE_TEXT,
            latency_ms=latency_ms,
        )
        raise ai_breaker.LLMUnavailableError(
            "Serviço de IA indisponível. Tente novamente."
        )

    # Fallback do breaker devolve texto cru (stale); sucesso devolve o
    # objeto do provedor — extrai tokens apenas do objeto.
    if isinstance(response, str):
        text, prompt_tokens, completion_tokens = response, 0, 0
    else:
        text = extract_text(response)
        prompt_tokens = completion_tokens = 0
        if extract_usage is not None:
            try:
                prompt_tokens, completion_tokens = extract_usage(response)
            except Exception:  # noqa: BLE001 — usage ausente não bloqueia
                prompt_tokens = completion_tokens = 0

    ai_cache.set_cached_response(model, messages, text, temperature)
    _record(
        feature=feature,
        model=model,
        messages=messages,
        response=text,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
    )
    logger.info(
        "ai_llm_call",
        feature=feature,
        model=model,
        tenant=_tenant_schema(),
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )
    return text, prompt_tokens, completion_tokens
