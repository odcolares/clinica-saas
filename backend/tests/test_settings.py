"""Testes da ETAPA 5 (fundação) — exigem Postgres real (django-tenants)."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

PASSWORD = "SenhaForte123"


def _signup(client: APIClient, slug: str):
    return client.post(
        "/api/v1/tenants/signup/",
        {
            "tenant_name": f"Clínica {slug}",
            "tenant_slug": slug,
            "admin_username": "admin",
            "admin_email": "admin@example.com",
            "admin_password": PASSWORD,
        },
        format="json",
    )


def _client(slug: str) -> APIClient:
    client = APIClient()
    resp = _signup(client, slug)
    assert resp.status_code == 201, resp.content
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    client.defaults["HTTP_X_TENANT_ID"] = slug.replace("-", "_")
    return client


def test_tenant_settings_singleton_e_patch():
    client = _client("et5-settings")
    got = client.get("/api/v1/settings/tenant/")
    assert got.status_code == 200, got.content
    assert got.data["timezone"] == "America/Sao_Paulo"

    patched = client.patch(
        "/api/v1/settings/tenant/",
        {"brand_name": "Sorriso", "primary_color": "#123456"},
        format="json",
    )
    assert patched.status_code == 200, patched.content
    assert patched.data["brand_name"] == "Sorriso"


def test_professional_commission_validation():
    client = _client("et5-commission")
    created = client.post("/api/v1/professionals/", {"name": "Dra. Bia"}, format="json")
    assert created.status_code == 201, created.content
    pid = created.data["id"]

    bad = client.patch(
        f"/api/v1/professionals/{pid}/",
        {"commission_type": "percent", "commission_percent": "150"},
        format="json",
    )
    assert bad.status_code == 400, bad.content

    ok = client.patch(
        f"/api/v1/professionals/{pid}/",
        {"commission_type": "percent", "commission_percent": "12.50"},
        format="json",
    )
    assert ok.status_code == 200, ok.content
    assert str(ok.data["commission_percent"]) == "12.50"


def test_webhook_crud_e_apikey_plain_unico():
    client = _client("et5-webhook-key")
    wh = client.post(
        "/api/v1/settings/webhooks/",
        {"name": "n8n", "url": "https://exemplo.test/hook", "events": ["appointment.created"]},
        format="json",
    )
    assert wh.status_code == 201, wh.content

    key = client.post("/api/v1/settings/api-keys/", {"name": "ci"}, format="json")
    assert key.status_code == 201, key.content
    assert key.data["plain_key"].startswith("sk_")

    listed = client.get("/api/v1/settings/api-keys/")
    assert listed.status_code == 200, listed.content
    assert "plain_key" not in str(listed.content)
    assert "key_hash" not in str(listed.content)


def test_integration_config_google_calendar_stub():
    client = _client("et5-integration")
    created = client.post(
        "/api/v1/settings/integrations/",
        {"provider": "google_calendar", "config": {"calendar_id": "primary"}},
        format="json",
    )
    assert created.status_code == 201, created.content
    assert "config" not in created.data
