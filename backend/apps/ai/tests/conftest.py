"""Fixtures dos testes do app ``ai``.

django-tenants exige Postgres real. O conftest global (``backend/tests``) não é
ancestral deste diretório, então replicamos o reset de schema/cache e criamos
fixtures que provisionam o schema do tenant (com as migrations do app).

Seguimos a convenção dos demais testes do projeto: os schemas criados NÃO são
removidos no teardown (DDL dentro da transação de teste falha com "pending
trigger events"); o banco de teste é destruído ao fim da sessão.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from django.core.cache import cache
from django.db import connection

from apps.tenants.models import Tenant


@pytest.fixture(autouse=True)
def _reset_schema_e_cache():
    """Reseta schema para public e limpa cache após cada teste (isolamento)."""
    yield
    connection.set_schema_to_public()
    cache.clear()


@pytest.fixture
def tenant(db) -> Tenant:
    """Cria um tenant com schema migrado e ativa-o na conexão."""
    connection.set_schema_to_public()
    item = Tenant(schema_name="ai_test", name="Clínica AI Test")
    item.slug = "ai-test"
    item.save()
    connection.set_tenant(item)
    return item


@pytest.fixture
def tenant_factory(db) -> Callable[[str], Tenant]:
    """Fábrica de tenants isolados (para testes de não vazamento)."""

    def _make(schema_name: str) -> Tenant:
        connection.set_schema_to_public()
        item = Tenant(schema_name=schema_name, name=f"Clínica {schema_name}")
        item.slug = schema_name.replace("_", "-")
        item.save()
        return item

    return _make
