"""Testes da ETAPA 3 (Omnichannel) — exigem Postgres real (django-tenants).

Cobrem normalização, idempotência de webhook, criação de lead, atribuição,
isolamento por tenant, segredo inválido (403), adapter pattern, sessão em Redis
e rate limiting por canal. O webhook é simulado sem rede externa.
"""

from __future__ import annotations

import pytest
from django.core.cache import cache
from django.db import connection
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from apps.accounts.models import Role, User
from apps.crm.models import Customer, Interaction, Lead
from apps.omnichannel.channels.base import ChannelAdapter
from apps.omnichannel.channels.factory import get_adapter
from apps.omnichannel.channels.noop import NoopChannelAdapter
from apps.omnichannel.channels.telegram import TelegramChannelAdapter
from apps.omnichannel.models import Conversation, ConversationMessage
from apps.omnichannel.services import (
    get_session,
    ingest_inbound_message,
    session_cache_key,
)
from apps.tenants.models import Tenant

pytestmark = pytest.mark.django_db

PASSWORD = "SenhaForte123"
SECRET = "test-webhook-secret"
WEBHOOK_URL = "/api/v1/omnichannel/telegram/webhook/"
CHAT_ID = 555123


# --- Fixtures e helpers ----------------------------------------------------


@pytest.fixture(autouse=True)
def _webhook_settings(settings):
    settings.TELEGRAM_BOT_TOKEN = ""
    # O caminho seguro é o segredo POR TENANT. Nos testes genéricos habilitamos o
    # fallback global EXPLICITAMENTE; os testes de isolamento abaixo desligam-no.
    settings.TELEGRAM_WEBHOOK_SECRET = SECRET
    settings.TELEGRAM_WEBHOOK_SECRETS = {}
    settings.TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET = True


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield


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


def _schema(slug: str) -> str:
    return slug.replace("-", "_")


def _set_tenant(slug: str) -> Tenant:
    connection.set_schema_to_public()
    tenant = Tenant.objects.using("default").get(schema_name=_schema(slug))
    connection.set_tenant(tenant)
    return tenant


def _auth(client: APIClient, access: str) -> None:
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


def _access(client: APIClient, slug: str, username: str = "admin") -> str:
    resp = client.post(
        "/api/v1/auth/login/",
        {"username": username, "password": PASSWORD},
        HTTP_X_TENANT_ID=_schema(slug),
        format="json",
    )
    assert resp.status_code == 200, resp.content
    return resp.data["access"]


def _create_attendant(slug: str, username: str = "att") -> User:
    _set_tenant(slug)
    role, _ = Role.objects.get_or_create(name="attendant")
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password=PASSWORD,
        role=role,
        status="active",
    )


def _update(message_id: int = 1001, text: str = "Olá,   quero   agendar  ", **extra):
    message = {
        "message_id": message_id,
        "date": 1700000000,
        "chat": {"id": CHAT_ID, "type": "private"},
        "from": {
            "id": CHAT_ID,
            "first_name": "Maria",
            "last_name": "Souza",
            "username": "maria",
        },
        "text": text,
    }
    message.update(extra)
    return {"update_id": message_id, "message": message}


def _webhook(
    client: APIClient,
    slug: str,
    payload: dict,
    *,
    secret: str | None = SECRET,
    tenant: str | None = None,
):
    kwargs: dict = {"format": "json"}
    if tenant is not False:
        kwargs["HTTP_X_TENANT_ID"] = tenant or _schema(slug)
    if secret is not None:
        kwargs["HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN"] = secret
    return client.post(WEBHOOK_URL, payload, **kwargs)


# --- Normalização ----------------------------------------------------------


def test_normalize_strip_colapsa_espacos_e_minusculas():
    normalized = TelegramChannelAdapter().normalize(_update())
    assert normalized.channel == "telegram"
    assert normalized.external_chat_id == str(CHAT_ID)
    assert normalized.external_message_id == "1001"
    assert normalized.body == "Olá,   quero   agendar  "  # texto bruto preservado
    assert normalized.normalized_body == "olá, quero agendar"
    assert normalized.sender_display_name == "Maria Souza"


# --- Webhook: persistência e idempotência ----------------------------------


def test_webhook_cria_conversa_e_mensagem():
    client = APIClient()
    _signup(client, "omni-ingest")

    resp = _webhook(client, "omni-ingest", _update())
    assert resp.status_code == 200, resp.content
    assert resp.data["ok"] is True
    assert resp.data["duplicate"] is False

    _set_tenant("omni-ingest")
    conversation = Conversation.objects.get(
        channel="telegram", external_chat_id=str(CHAT_ID)
    )
    assert conversation.status == Conversation.Status.OPEN
    message = ConversationMessage.objects.get(conversation=conversation)
    assert message.direction == ConversationMessage.Direction.INBOUND
    assert message.sender_kind == ConversationMessage.SenderKind.CUSTOMER
    assert message.normalized_body == "olá, quero agendar"
    assert conversation.history.count() >= 1


def test_webhook_idempotente_nao_duplica_mensagem():
    client = APIClient()
    _signup(client, "omni-idem")

    first = _webhook(client, "omni-idem", _update(message_id=2001))
    second = _webhook(client, "omni-idem", _update(message_id=2001))
    assert first.data["duplicate"] is False
    assert second.data["duplicate"] is True
    assert first.data["message"] == second.data["message"]

    _set_tenant("omni-idem")
    assert ConversationMessage.objects.count() == 1


def test_webhook_payload_invalido_400():
    client = APIClient()
    _signup(client, "omni-badpayload")
    resp = _webhook(client, "omni-badpayload", {"update_id": 1})
    assert resp.status_code == 400, resp.content


# --- Integração com CRM ----------------------------------------------------


def test_webhook_cria_lead_e_interacao():
    client = APIClient()
    _signup(client, "omni-lead")
    assert _webhook(client, "omni-lead", _update()).status_code == 200

    _set_tenant("omni-lead")
    conversation = Conversation.objects.get(external_chat_id=str(CHAT_ID))
    assert conversation.lead_id is not None
    lead = conversation.lead
    assert lead.name == "Maria Souza"
    assert lead.source.name == "telegram"
    assert lead.status.code == "NEW"
    assert Interaction.objects.filter(lead=lead, kind=Interaction.KIND_MESSAGE).exists()


def test_webhook_vincula_customer_existente_por_telefone():
    client = APIClient()
    _signup(client, "omni-link")

    _set_tenant("omni-link")
    customer = Customer.objects.create(name="Cliente Existente", phone="11999998888")

    payload = _update(
        message_id=3001,
        text="meu telefone",
        contact={"phone_number": "11999998888"},
    )
    assert _webhook(client, "omni-link", payload).status_code == 200

    _set_tenant("omni-link")
    conversation = Conversation.objects.get(external_chat_id=str(CHAT_ID))
    assert conversation.customer_id == customer.pk
    assert conversation.lead_id is None
    assert not Lead.objects.filter(phone="11999998888").exists()


# --- Atribuição / RBAC -----------------------------------------------------


def test_atribuicao_concede_permissao_e_muda_status():
    client = APIClient()
    access = _signup(client, "omni-assign").data["access"]
    attendant = _create_attendant("omni-assign")

    assert _webhook(client, "omni-assign", _update()).status_code == 200

    _auth(client, access)
    conversation_id = client.get("/api/v1/conversations/").data["results"][0]["id"]
    resp = client.post(
        f"/api/v1/conversations/{conversation_id}/assign/",
        {"assigned_to": attendant.pk},
        format="json",
    )
    assert resp.status_code == 200, resp.content
    assert resp.data["status"] == Conversation.Status.ASSIGNED
    assert resp.data["assigned_to"] == "att"

    _set_tenant("omni-assign")
    stored = Conversation.objects.get(pk=conversation_id)
    attendant.refresh_from_db()
    assert attendant.has_perm("view_conversation", stored)

    # Atendente passa a enxergar a conversa atribuída
    att_client = APIClient()
    _auth(att_client, _access(client, "omni-assign", username="att"))
    listing = att_client.get("/api/v1/conversations/")
    assert [c["id"] for c in listing.data["results"]] == [conversation_id]


def test_mensagens_da_conversa_listadas_para_gestor():
    client = APIClient()
    access = _signup(client, "omni-msgs").data["access"]
    assert _webhook(client, "omni-msgs", _update()).status_code == 200

    _auth(client, access)
    conversation_id = client.get("/api/v1/conversations/").data["results"][0]["id"]
    resp = client.get(f"/api/v1/conversations/{conversation_id}/messages/")
    assert resp.status_code == 200, resp.content
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["direction"] == "inbound"

    assert client.get("/api/v1/messages/").data["count"] == 1


def test_reply_usa_adapter_do_canal(monkeypatch):
    client = APIClient()
    access = _signup(client, "omni-reply").data["access"]
    assert _webhook(client, "omni-reply", _update()).status_code == 200

    _auth(client, access)
    conversation_id = client.get("/api/v1/conversations/").data["results"][0]["id"]

    monkeypatch.setattr(
        "apps.omnichannel.services.get_adapter",
        lambda channel: NoopChannelAdapter(channel=channel),
    )
    resp = client.post(
        f"/api/v1/conversations/{conversation_id}/reply/",
        {"body": "  Olá!  "},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert resp.data["direction"] == "outbound"
    assert resp.data["sender_kind"] == "agent"
    assert resp.data["body"] == "Olá!"


# --- Segurança do webhook --------------------------------------------------


def test_webhook_secret_invalido_403():
    client = APIClient()
    _signup(client, "omni-secret")
    resp = _webhook(client, "omni-secret", _update(), secret="segredo-errado")
    assert resp.status_code == 403, resp.content

    _set_tenant("omni-secret")
    assert Conversation.objects.count() == 0


def test_webhook_sem_tenant_400():
    client = APIClient()
    _signup(client, "omni-notenant")
    resp = _webhook(client, "omni-notenant", _update(), tenant=False)
    assert resp.status_code == 400, resp.content


def test_webhook_segredo_por_tenant_isola_cross_tenant(settings):
    """Segredo de um tenant não autoriza escrita em outro (X-Tenant-Id forjado)."""
    client = APIClient()
    _signup(client, "omni-tsec-a")
    _signup(client, "omni-tsec-b")

    settings.TELEGRAM_WEBHOOK_SECRETS = {
        _schema("omni-tsec-a"): "secret-a",
        _schema("omni-tsec-b"): "secret-b",
    }
    settings.TELEGRAM_WEBHOOK_SECRET = ""
    settings.TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET = False

    forged = _webhook(
        client, "omni-tsec-a", _update(message_id=5001), secret="secret-b"
    )
    assert forged.status_code == 403, forged.content
    _set_tenant("omni-tsec-a")
    assert Conversation.objects.count() == 0

    ok = _webhook(client, "omni-tsec-a", _update(message_id=5002), secret="secret-a")
    assert ok.status_code == 200, ok.content


def test_webhook_global_nao_autoriza_tenant_sem_segredo(settings):
    """Sem segredo do tenant e com fallback desligado, o segredo global é rejeitado."""
    client = APIClient()
    _signup(client, "omni-gsec")

    settings.TELEGRAM_WEBHOOK_SECRETS = {}
    settings.TELEGRAM_WEBHOOK_SECRET = SECRET
    settings.TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET = False

    resp = _webhook(client, "omni-gsec", _update(message_id=6001), secret=SECRET)
    assert resp.status_code == 403, resp.content
    _set_tenant("omni-gsec")
    assert Conversation.objects.count() == 0


def test_webhook_fallback_global_explicito_autoriza(settings):
    """O segredo global só autoriza quando o fallback é habilitado explicitamente."""
    client = APIClient()
    _signup(client, "omni-fallback")

    settings.TELEGRAM_WEBHOOK_SECRETS = {}
    settings.TELEGRAM_WEBHOOK_SECRET = SECRET
    settings.TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET = True

    resp = _webhook(client, "omni-fallback", _update(message_id=7001), secret=SECRET)
    assert resp.status_code == 200, resp.content


# --- Isolamento por tenant -------------------------------------------------


def test_isolamento_de_conversas_entre_tenants():
    client = APIClient()
    _signup(client, "omni-iso-a")
    access_b = _signup(client, "omni-iso-b").data["access"]

    assert _webhook(client, "omni-iso-a", _update()).status_code == 200

    _auth(client, access_b)
    listing = client.get("/api/v1/conversations/")
    assert listing.data["results"] == []
    assert client.get("/api/v1/messages/").data["results"] == []

    _set_tenant("omni-iso-b")
    assert Conversation.objects.count() == 0


# --- Adapter pattern / canais futuros --------------------------------------


def test_factory_extensivel_para_canal_futuro():
    telegram = get_adapter("telegram")
    assert isinstance(telegram, TelegramChannelAdapter)
    assert isinstance(telegram, ChannelAdapter)

    whatsapp = get_adapter("whatsapp")  # ainda não implementado → Noop
    assert isinstance(whatsapp, NoopChannelAdapter)
    assert whatsapp.channel == "whatsapp"

    result = whatsapp.send_message(external_chat_id="x", text="oi")
    assert result["ok"] is True


# --- Sessão em Redis -------------------------------------------------------


def test_sessao_gravada_no_cache_com_ttl():
    client = APIClient()
    _signup(client, "omni-cache")
    assert _webhook(client, "omni-cache", _update()).status_code == 200

    session = get_session("telegram", str(CHAT_ID))
    assert session is not None
    assert session["conversation_id"]

    key = session_cache_key(connection.schema_name, "telegram", str(CHAT_ID))
    assert cache.get(key) == session
    ttl = cache.ttl(key)
    assert 0 < ttl <= 3600


def test_ingestao_nao_quebra_com_cache_indisponivel(monkeypatch):
    client = APIClient()
    _signup(client, "omni-badcache")
    _set_tenant("omni-badcache")

    class _BrokenCache:
        def get(self, *args, **kwargs):
            raise RuntimeError("redis indisponível")

        def set(self, *args, **kwargs):
            raise RuntimeError("redis indisponível")

    monkeypatch.setattr("apps.omnichannel.services.cache", _BrokenCache())

    message, created = ingest_inbound_message(
        channel="telegram", payload=_update(), adapter=TelegramChannelAdapter()
    )
    assert created is True
    assert ConversationMessage.objects.filter(pk=message.pk).exists()


# --- Rate limiting por canal -----------------------------------------------


def test_rate_limit_telegram_429(monkeypatch):
    client = APIClient()
    _signup(client, "omni-throttle")

    # DRF vincula THROTTLE_RATES no import da classe; ajustamos o rate do escopo
    # diretamente para validar o 429 (restaurado pelo monkeypatch).
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "telegram", "2/min")
    cache.clear()

    first = _webhook(client, "omni-throttle", _update(message_id=4001))
    second = _webhook(client, "omni-throttle", _update(message_id=4002))
    third = _webhook(client, "omni-throttle", _update(message_id=4003))
    assert first.status_code == 200, first.content
    assert second.status_code == 200, second.content
    assert third.status_code == 429, third.content
