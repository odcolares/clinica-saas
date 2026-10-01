"""Testes do cache de respostas LLM (ETAPA 4) — chave e regras de temperatura."""

from __future__ import annotations

import re

import pytest

from apps.ai.cache import cache_key, get_cached_response, set_cached_response
from apps.ai.tests._assertions import check, check_equal

pytestmark = pytest.mark.django_db

MESSAGES = [{"role": "user", "content": "Olá, quero agendar."}]


def test_cache_key_formato_e_determinismo():
    key = cache_key("gpt-4o-mini", MESSAGES, 0.0)
    check(re.fullmatch(r"llm:[0-9a-f]{16}", key))
    check_equal(key, cache_key("gpt-4o-mini", MESSAGES, 0.0))


def test_cache_key_muda_com_modelo_mensagem_ou_temperatura():
    base = cache_key("gpt-4o-mini", MESSAGES, 0.0)
    check(cache_key("gpt-4o", MESSAGES, 0.0) != base)
    check(cache_key("gpt-4o-mini", [{"role": "user", "content": "x"}], 0.0) != base)
    check(cache_key("gpt-4o-mini", MESSAGES, 0.7) != base)


def test_cache_roundtrip_apenas_temperature_zero():
    set_cached_response("gpt-4o-mini", MESSAGES, "resposta-cacheada", 0.0)
    check_equal(get_cached_response("gpt-4o-mini", MESSAGES, 0.0), "resposta-cacheada")


def test_cache_ignora_temperature_diferente_de_zero():
    set_cached_response("gpt-4o-mini", MESSAGES, "nao-deve-cachear", 0.5)
    check(get_cached_response("gpt-4o-mini", MESSAGES, 0.5) is None)
    # Nem vaza para a variante determinística.
    check(get_cached_response("gpt-4o-mini", MESSAGES, 0.0) is None)
