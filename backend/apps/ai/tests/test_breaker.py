"""Testes do circuit breaker e do fallback (ETAPA 4)."""

from __future__ import annotations

import pytest

from apps.ai.breaker import (
    FAILURE_THRESHOLD,
    LLMUnavailableError,
    RECOVERY_TIMEOUT,
    call_with_fallback,
    create_breaker,
)
from apps.ai.tests._assertions import check_equal

pytestmark = pytest.mark.django_db


def _boom():
    raise RuntimeError("provedor fora do ar")


def test_configuracao_do_breaker_usa_limites_do_projeto():
    check_equal(FAILURE_THRESHOLD, 5)
    check_equal(RECOVERY_TIMEOUT, 30)


def test_breaker_abre_apos_limite_e_usa_fallback():
    breaker = create_breaker(fail_max=5, reset_timeout=30)
    for _ in range(5):
        with pytest.raises(LLMUnavailableError):
            call_with_fallback(_boom, breaker=breaker)

    check_equal(breaker.current_state, "open")

    # Circuito aberto → devolve cached em vez de tocar o provedor.
    result = call_with_fallback(
        _boom, breaker=breaker, fallback=lambda: "resposta-cacheada"
    )
    check_equal(result, "resposta-cacheada")


def test_falha_do_provedor_usa_fallback_imediatamente():
    breaker = create_breaker(fail_max=5, reset_timeout=30)
    result = call_with_fallback(
        _boom, breaker=breaker, fallback=lambda: {"cached": True}
    )
    check_equal(result, {"cached": True})


def test_sem_fallback_erro_e_tratado_como_llmunavailable():
    breaker = create_breaker(fail_max=5, reset_timeout=30)
    with pytest.raises(LLMUnavailableError):
        call_with_fallback(_boom, breaker=breaker)


def test_sucesso_nao_abre_circuito():
    breaker = create_breaker(fail_max=5, reset_timeout=30)
    result = call_with_fallback(lambda: "ok", breaker=breaker)
    check_equal(result, "ok")
    check_equal(breaker.current_state, "closed")
