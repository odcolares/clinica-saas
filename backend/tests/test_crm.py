"""Testes da ETAPA 1 (CRM) — exigem Postgres real (django-tenants)."""

import pytest
from django.db import connection
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.crm.models import Customer, Lead
from apps.tenants.models import Tenant

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


def _schema(slug: str) -> str:
    return slug.replace("-", "_")


def _set_tenant(slug: str) -> Tenant:
    connection.set_schema_to_public()
    tenant = Tenant.objects.using("default").get(schema_name=_schema(slug))
    connection.set_tenant(tenant)
    return tenant


def _access(client: APIClient, slug: str, username: str = "admin") -> str:
    resp = client.post(
        "/api/v1/auth/login/",
        {"username": username, "password": PASSWORD},
        HTTP_X_TENANT_ID=_schema(slug),
        format="json",
    )
    assert resp.status_code == 200, resp.content
    return resp.data["access"]


def _auth(client: APIClient, access: str) -> None:
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


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


def _new_lead(client: APIClient, **overrides) -> dict:
    payload = {
        "name": "Lead Teste",
        "email": "lead@example.com",
        "phone": "11999990000",
    }
    payload.update(overrides)
    resp = client.post("/api/v1/leads/", payload, format="json")
    assert resp.status_code == 201, resp.content
    return resp.data


def _advance(client: APIClient, lead_id: int, code: str, reason: str = ""):
    return client.patch(
        f"/api/v1/leads/{lead_id}/status/",
        {"status": code, "reason": reason},
        format="json",
    )


# --- Leads -----------------------------------------------------------------


def test_lead_crud_listagem_e_busca():
    client = APIClient()
    _auth(client, _signup(client, "crm-lead-flow").data["access"])

    lead = _new_lead(client, name="João Silva", email="joao@example.com")
    assert lead["status"] == "NEW"
    assert lead["converted_customer"] is None

    listing = client.get("/api/v1/leads/")
    assert listing.status_code == 200
    assert listing.data["count"] == 1

    found = client.get("/api/v1/leads/", {"search": "joao"})
    assert found.data["count"] == 1
    assert client.get("/api/v1/leads/", {"search": "maria"}).data["results"] == []

    patches = client.patch(
        f"/api/v1/leads/{lead['id']}/", {"phone": "11888887777"}, format="json"
    )
    assert patches.status_code == 200, patches.content
    assert patches.data["phone"] == "11888887777"


def test_lead_transicao_invalida_rejeitada():
    client = APIClient()
    _auth(client, _signup(client, "crm-lead-trans").data["access"])
    lead = _new_lead(client)

    resp = _advance(client, lead["id"], "QUALIFIED")
    assert resp.status_code == 400, resp.content


def test_lead_lost_exige_motivo():
    client = APIClient()
    _auth(client, _signup(client, "crm-lead-lost").data["access"])
    lead = _new_lead(client)

    sem_motivo = _advance(client, lead["id"], "LOST")
    assert sem_motivo.status_code == 400, sem_motivo.content

    com_motivo = _advance(client, lead["id"], "LOST", reason="Sem interesse")
    assert com_motivo.status_code == 200, com_motivo.content
    assert com_motivo.data["status"] == "LOST"
    assert com_motivo.data["lost_reason"] == "Sem interesse"


def test_conversao_lead_cria_customer_e_preserva_lead():
    client = APIClient()
    _auth(client, _signup(client, "crm-conv-new").data["access"])
    lead = _new_lead(client, name="Carlos", email="carlos@example.com")
    assert _advance(client, lead["id"], "CONTACTED").status_code == 200
    assert _advance(client, lead["id"], "QUALIFIED").status_code == 200

    conv = client.post(f"/api/v1/leads/{lead['id']}/convert/")
    assert conv.status_code == 201, conv.content
    assert conv.data["created"] is True
    customer_id = conv.data["customer"]["id"]

    _set_tenant("crm-conv-new")
    stored = Lead.objects.get(pk=lead["id"])
    assert stored.status.code == "CONVERTED"
    assert stored.converted_customer_id == customer_id
    assert stored.converted_at is not None
    assert Customer.objects.filter(pk=customer_id).exists()

    repeat = client.post(f"/api/v1/leads/{lead['id']}/convert/")
    assert repeat.status_code == 409, repeat.content


def test_conversao_vincula_customer_existente():
    client = APIClient()
    _auth(client, _signup(client, "crm-conv-link").data["access"])

    existing = client.post(
        "/api/v1/customers/",
        {"name": "Maria", "email": "maria@example.com"},
        format="json",
    )
    assert existing.status_code == 201, existing.content

    lead = _new_lead(client, name="Maria Lead", email="maria@example.com")
    _advance(client, lead["id"], "CONTACTED")
    _advance(client, lead["id"], "QUALIFIED")

    conv = client.post(f"/api/v1/leads/{lead['id']}/convert/")
    assert conv.status_code == 200, conv.content
    assert conv.data["created"] is False
    assert conv.data["customer"]["id"] == existing.data["id"]


# --- Customers -------------------------------------------------------------


def test_customer_agregados_e_timeline():
    client = APIClient()
    _auth(client, _signup(client, "crm-cust-agg").data["access"])

    customer = client.post(
        "/api/v1/customers/",
        {"name": "Ana", "email": "ana@example.com", "phone": "11911112222"},
        format="json",
    )
    assert customer.status_code == 201, customer.content
    cid = customer.data["id"]

    contact = client.post(
        f"/api/v1/customers/{cid}/contacts/",
        {"kind": "whatsapp", "value": "11911112222", "is_primary": True},
        format="json",
    )
    assert contact.status_code == 201, contact.content

    address = client.post(
        f"/api/v1/customers/{cid}/addresses/",
        {"street": "Rua A", "number": "10", "city": "São Paulo", "state": "SP"},
        format="json",
    )
    assert address.status_code == 201, address.content

    note = client.post(
        f"/api/v1/customers/{cid}/notes/",
        {"body": "Primeiro contato por telefone."},
        format="json",
    )
    assert note.status_code == 201, note.content
    assert note.data["author"] == "admin"

    detail = client.get(f"/api/v1/customers/{cid}/")
    assert detail.status_code == 200
    assert len(detail.data["contacts"]) == 1
    assert len(detail.data["addresses"]) == 1
    assert len(detail.data["notes"]) == 1

    timeline = client.get(f"/api/v1/customers/{cid}/timeline/")
    assert timeline.status_code == 200
    events = timeline.data["events"]
    assert any(e["type"] == "note" for e in events)
    assert events[0]["description"] == "Primeiro contato por telefone."


def test_tags_endpoint_e_vinculo_com_customer():
    client = APIClient()
    _auth(client, _signup(client, "crm-tags").data["access"])

    tag = client.post("/api/v1/tags/", {"name": "VIP"}, format="json")
    assert tag.status_code == 201, tag.content

    customer = client.post(
        "/api/v1/customers/",
        {"name": "Cliente VIP", "email": "vip@example.com", "tags": ["VIP"]},
        format="json",
    )
    assert customer.status_code == 201, customer.content
    assert customer.data["tags"] == ["VIP"]

    filtrado = client.get("/api/v1/customers/", {"tags": tag.data["id"]})
    assert filtrado.data["count"] == 1


# --- Isolamento / RBAC / auditoria -----------------------------------------


def test_isolamento_crm_entre_dois_tenants():
    client = APIClient()
    access_a = _signup(client, "crm-iso-a").data["access"]
    access_b = _signup(client, "crm-iso-b").data["access"]

    _auth(client, access_a)
    customer = client.post("/api/v1/customers/", {"name": "Só do A"}, format="json")
    assert customer.status_code == 201
    cid = customer.data["id"]

    _auth(client, access_b)
    assert client.get("/api/v1/customers/").data["results"] == []
    assert client.get(f"/api/v1/customers/{cid}/").status_code == 404
    assert (
        client.patch(
            f"/api/v1/customers/{cid}/", {"name": "hack"}, format="json"
        ).status_code
        == 404
    )


def test_guardian_escopo_por_objeto_dentro_do_tenant():
    client = APIClient()
    admin_access = _signup(client, "crm-guard").data["access"]
    _create_attendant("crm-guard")
    att_access = _access(client, "crm-guard", username="att")

    _auth(client, admin_access)
    do_admin = client.post("/api/v1/customers/", {"name": "Do admin"}, format="json")
    assert do_admin.status_code == 201

    _auth(client, att_access)
    do_att = client.post("/api/v1/customers/", {"name": "Do atendente"}, format="json")
    assert do_att.status_code == 201, do_att.content

    lista = client.get("/api/v1/customers/")
    assert [c["name"] for c in lista.data["results"]] == ["Do atendente"]
    assert client.get(f"/api/v1/customers/{do_admin.data['id']}/").status_code == 404
    assert client.delete(f"/api/v1/customers/{do_att.data['id']}/").status_code == 403


def test_auditoria_lead_registra_autor_data_e_motivo():
    client = APIClient()
    _auth(client, _signup(client, "crm-audit").data["access"])
    lead = _new_lead(client)
    _advance(client, lead["id"], "CONTACTED", reason="Primeiro contato")

    _set_tenant("crm-audit")
    stored = Lead.objects.get(pk=lead["id"])
    assert stored.history.count() >= 2
    latest = stored.history.first()
    assert latest.history_user is not None
    assert latest.history_user.username == "admin"
    assert latest.history_change_reason == "Primeiro contato"
