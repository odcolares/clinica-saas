"""Testes da fundação ETAPA 0 — exigem Postgres real (django-tenants não funciona em sqlite)."""

import jwt
import pytest
from django.db import connection
from django.test import Client, override_settings
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
        format="json",
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


def test_login_emite_jwt_com_claim_tenant():
    """Login com x-tenant-id roteia ao schema correto e o JWT carrega claim tenant."""
    client = APIClient()
    resp = _signup(client, "clinica-login")
    assert resp.status_code == 201

    login_resp = client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "SenhaForte123"},
        HTTP_X_TENANT_ID="clinica_login",
        format="json",
    )
    assert login_resp.status_code == 200, login_resp.content
    assert login_resp.data["tenant"] == "clinica_login"
    assert "access" in login_resp.data
    assert "refresh" in login_resp.data

    # Verifica o claim "tenant" dentro do JWT (sem validar assinatura)
    payload = jwt.decode(
        login_resp.data["access"],
        options={"verify_signature": False, "verify_exp": False},
    )
    assert payload["tenant"] == "clinica_login"


def test_isolamento_dados_entre_dois_tenants():
    """Dados do tenant A não são acessíveis do tenant B (isolamento de schema)."""
    client = APIClient()
    resp_a = _signup(client, "tenant-iso-a")
    resp_b = _signup(client, "tenant-iso-b")

    # Com JWT de A → /me retorna tenant A
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp_a.data['access']}")
    me_a = client.get("/api/v1/auth/me/", HTTP_X_TENANT_ID="tenant_iso_a")
    assert me_a.status_code == 200
    assert me_a.data["tenant"] == "tenant_iso_a"

    # Com JWT de B → /me retorna tenant B, não enxerga dados de A
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp_b.data['access']}")
    me_b = client.get("/api/v1/auth/me/", HTTP_X_TENANT_ID="tenant_iso_b")
    assert me_b.status_code == 200
    assert me_b.data["tenant"] == "tenant_iso_b"
    assert me_b.data["tenant"] != me_a.data["tenant"]


def test_rate_limit_login_429():
    """Login throttle: 11ª tentativa dentro de 1 minuto retorna 429."""
    client = APIClient()
    _signup(client, "tenant-rl")

    for _ in range(10):
        r = client.post(
            "/api/v1/auth/login/",
            {"username": "admin", "password": "SenhaForte123"},
            HTTP_X_TENANT_ID="tenant_rl",
            format="json",
        )
        assert r.status_code == 200, r.content

    blocked = client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "SenhaForte123"},
        HTTP_X_TENANT_ID="tenant_rl",
        format="json",
    )
    assert blocked.status_code == 429


def test_password_reset_request_generic_200_for_unknown_email():
    """Reset request sempre retorna 200 genérico, mesmo e-mail inexistente."""
    client = APIClient()
    _signup(client, "tenant-reset-unknown")
    resp = client.post(
        "/api/v1/auth/password-reset/",
        {"email": "naoexiste@example.com"},
        HTTP_X_TENANT_ID="tenant_reset_unknown",
        format="json",
    )
    assert resp.status_code == 200
    assert "detail" in resp.data


@override_settings(DEBUG=True)
def test_password_reset_flow_resets_password():
    """Fluxo completo: reset request → confirm → senha antiga inválida, nova funciona."""
    client = APIClient()
    resp = _signup(client, "tenant-reset-flow")
    assert resp.status_code == 201

    reset_resp = client.post(
        "/api/v1/auth/password-reset/",
        {"email": "admin@example.com"},
        HTTP_X_TENANT_ID="tenant_reset_flow",
        format="json",
    )
    assert reset_resp.status_code == 200
    assert "detail" in reset_resp.data

    uid = reset_resp.data["uid"]
    token = reset_resp.data["token"]

    confirm_resp = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "NovaSenha456"},
        HTTP_X_TENANT_ID="tenant_reset_flow",
        format="json",
    )
    assert confirm_resp.status_code == 200

    # Senha antiga não funciona mais
    old_login = client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "SenhaForte123"},
        HTTP_X_TENANT_ID="tenant_reset_flow",
        format="json",
    )
    assert old_login.status_code == 400

    # Nova senha funciona
    new_login = client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "NovaSenha456"},
        HTTP_X_TENANT_ID="tenant_reset_flow",
        format="json",
    )
    assert new_login.status_code == 200


@override_settings(DEBUG=True)
def test_password_reset_reused_token_rejected():
    """Token de reset é de uso único: reutilização não altera a senha."""
    client = APIClient()
    resp = _signup(client, "tenant-reset-reuse")
    assert resp.status_code == 201

    reset_resp = client.post(
        "/api/v1/auth/password-reset/",
        {"email": "admin@example.com"},
        HTTP_X_TENANT_ID="tenant_reset_reuse",
        format="json",
    )
    uid = reset_resp.data["uid"]
    token = reset_resp.data["token"]

    # Primeiro uso: sucesso
    confirm_resp = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "NovaSenha789"},
        HTTP_X_TENANT_ID="tenant_reset_reuse",
        format="json",
    )
    assert confirm_resp.status_code == 200

    # Reutilização: 200 genérico (sem enumeração), mas senha não muda
    reuse_resp = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {"uid": uid, "token": token, "new_password": "OutraSenha000"},
        HTTP_X_TENANT_ID="tenant_reset_reuse",
        format="json",
    )
    assert reuse_resp.status_code == 200

    # Nova senha do primeiro reset ainda funciona
    login_resp = client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "NovaSenha789"},
        HTTP_X_TENANT_ID="tenant_reset_reuse",
        format="json",
    )
    assert login_resp.status_code == 200

    # Segunda senha NÃO foi aplicada
    login_resp2 = client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "OutraSenha000"},
        HTTP_X_TENANT_ID="tenant_reset_reuse",
        format="json",
    )
    assert login_resp2.status_code == 400


def test_scrub_processor_removes_secrets():
    """O processor structlog remove chaves sensíveis (case-insensitive)."""
    from config.settings_middleware import _scrub_secrets

    event = {
        "event": "password_reset_requested",
        "tenant": "clinica_a",
        "password": "SenhaForte123",
        "token": "abc123token",
        "Authorization": "Bearer xyz",
        "Cookie": "session=abc",
        "safe_key": "safe_value",
    }
    result = _scrub_secrets(None, "info", event)
    assert "password" not in result
    assert "token" not in result
    assert "Authorization" not in result
    assert "Cookie" not in result
    assert result["event"] == "password_reset_requested"
    assert result["tenant"] == "clinica_a"
    assert result["safe_key"] == "safe_value"


def test_failed_login_no_echoed_password():
    """Resposta de login falhou não contém a senha enviada."""
    client = APIClient()
    _signup(client, "tenant-noleak")
    resp = client.post(
        "/api/v1/auth/login/",
        {"username": "admin", "password": "SenhaErrada999"},
        HTTP_X_TENANT_ID="tenant_noleak",
        format="json",
    )
    assert resp.status_code == 400
    assert "SenhaErrada999" not in resp.content.decode()
