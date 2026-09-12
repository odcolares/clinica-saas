"""Configuração de testes para django-tenants + pytest-django.

django-tenants não funciona com sqlite — exige PostgreSQL real.
No CI, o serviço Postgres já fornece o banco. Localmente, rode:
  docker compose up db redis
e crie .env a partir de .env.example.
"""

import pytest
from django.core.cache import cache
from django.db import connection


@pytest.fixture(autouse=True)
def _reset_schema_e_cache():
    """Reseta schema para public e limpa cache após cada teste.

    Evita vazamento de search_path entre testes e de counters de rate-limit
    via throttle cache.
    """
    yield
    connection.set_schema_to_public()
    cache.clear()
