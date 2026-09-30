"""Testes da configuração do cliente OpenAI (pool/timeout/segredo)."""

from __future__ import annotations

import pytest

from apps.ai import client
from apps.ai.tests._assertions import check_equal

pytestmark = pytest.mark.django_db


def test_parametros_de_pool_e_timeout():
    check_equal(client.OPENAI_MAX_CONNECTIONS, 20)
    check_equal(client.OPENAI_MAX_KEEPALIVE, 10)
    check_equal(client.OPENAI_TIMEOUT_SECONDS, 30.0)

    limits = client.build_limits()
    check_equal(limits.max_connections, 20)
    check_equal(limits.max_keepalive_connections, 10)
    check_equal(client.build_http_client().timeout.connect, 30.0)


def test_get_client_exige_api_key(settings):
    settings.OPENAI_API_KEY = ""
    client._client = None
    with pytest.raises(RuntimeError):
        client.get_client()
