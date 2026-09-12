"""Testes da fundação ETAPA 0 — exigem Postgres real (django-tenants não funciona em sqlite)."""

import pytest
from django.db import connection
from django.test import Client
from rest_framework.test import APIClient

from apps.tenants.models import Tenant

pytestmark = pytest.mark.django_db


def _signup(client: Client, slug: str):
    return client.post(
        "/api/v1/tenants/signup/",
        {
            "tenant_name": f"Clínica {slug}",
            "tenant_slug": slug,
            "admin_username": "admin",
            "admin_email": "admin@example.com",
            "admin_password": "SenhaForte123",
        },
        content_type="application/json",
    )


def test_signup_cria_schema_e_admin():
    client = APIClient()
    resp = _signup(client, "clinica-a")
    assert resp.status_code == 201, resp.content
    assert resp.data["tenant"] == "clinica_a"
    assert resp.data["user"]["username"] == "admin"
    assert Tenant.objects.filter(schema_name="clinica_a").exists()


def test_isolamento_entre_dois_tenants():
    client = APIClient()
    _signup(client, "clinica-b")
    _signup(client, "clinica-c")
    tenants = set(Tenant.objects.values_list("schema_name", flat=True))
    assert {"clinica_b", "clinica_c"} <= tenants
    connection.set_schema_to_public()
    assert Tenant.objects.filter(schema_name="clinica_b").exists()
    assert Tenant.objects.filter(schema_name="clinica_c").exists()


def test_header_divergente_do_token_rejeitado():
    client = APIClient()
    resp = _signup(client, "clinica-d")
    access = resp.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    probe = client.get("/api/v1/auth/me/", HTTP_X_TENANT_ID="outro_tenant")
    assert probe.status_code == 403


def test_logout_invalida_refresh():
    client = APIClient()
    resp = _signup(client, "clinica-e")
    refresh = resp.data["refresh"]
    out = client.post("/api/v1/auth/logout/", {"refresh": refresh}, format="json")
    assert out.status_code == 200, out.content
    reuse = client.post("/api/v1/auth/refresh/", {"refresh": refresh}, format="json")
    assert reuse.status_code == 401
