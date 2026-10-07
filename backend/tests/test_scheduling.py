"""Testes da ETAPA 2 (Agenda) — exigem Postgres real (django-tenants)."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.db import connection
from rest_framework.test import APIClient

from apps.scheduling.models import Appointment

pytestmark = pytest.mark.django_db

PASSWORD = "SenhaForte123"
TZ = ZoneInfo("America/Sao_Paulo")


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


def _auth(client: APIClient, access: str) -> None:
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


def _base(slug: str) -> tuple[APIClient, dict]:
    """Cria tenant + professional + service + customer; retorna (client, ids)."""
    client = APIClient()
    _auth(client, _signup(client, slug).data["access"])

    prof = client.post(
        "/api/v1/professionals/",
        {
            "name": "Dra. Ana",
            "email": "ana@example.com",
            "specialties": "Limpeza, Clareamento",
        },
        format="json",
    )
    assert prof.status_code == 201, prof.content

    svc = client.post(
        "/api/v1/services/",
        {"name": "Limpeza", "duration_minutes": 60, "price": "120.00"},
        format="json",
    )
    assert svc.status_code == 201, svc.content

    cust = client.post(
        "/api/v1/customers/",
        {"name": "Cliente", "email": "cli@example.com"},
        format="json",
    )
    assert cust.status_code == 201, cust.content

    return client, {
        "professional": prof.data["id"],
        "service": svc.data["id"],
        "customer": cust.data["id"],
    }


def _start(days_ahead: int = 7, hour: int = 10) -> datetime:
    base = datetime.now(TZ) + timedelta(days=days_ahead)
    return base.replace(hour=hour, minute=0, second=0, microsecond=0)


def _book(client: APIClient, ids: dict, start: datetime, **over):
    payload = {
        "professional": ids["professional"],
        "service": ids["service"],
        "customer": ids["customer"],
        "start": start.isoformat(),
    }
    payload.update(over)
    return client.post("/api/v1/appointments/", payload, format="json")


def test_crud_professional_service():
    client, ids = _base("sched-crud")
    assert client.get("/api/v1/professionals/").data["count"] == 1
    assert client.get("/api/v1/services/").data["count"] == 1
    assert (
        client.get(f"/api/v1/professionals/{ids['professional']}/").status_code == 200
    )


def test_criar_appointment_ok_e_token_no_detail():
    client, ids = _base("sched-create")
    resp = _book(client, ids, _start())
    assert resp.status_code == 201, resp.content
    assert resp.data["status"] == "SCHEDULED"
    assert resp.data["confirmation_token"]

    listing = client.get("/api/v1/appointments/")
    assert listing.data["count"] == 1
    assert "confirmation_token" not in listing.data["results"][0]


def test_overlap_mesmo_profissional_da_409():
    client, ids = _base("sched-conflict")
    assert _book(client, ids, _start(hour=10)).status_code == 201
    resp = _book(client, ids, _start(hour=10, days_ahead=7).replace(minute=30))
    assert resp.status_code == 409, resp.content


def test_adjacente_permitido():
    client, ids = _base("sched-adjacent")
    assert _book(client, ids, _start(hour=10)).status_code == 201
    resp = _book(client, ids, _start(hour=11))
    assert resp.status_code == 201, resp.content


def test_profissional_diferente_mesmo_horario_permitido():
    client, ids = _base("sched-diffprof")
    assert _book(client, ids, _start(hour=10)).status_code == 201

    other = client.post("/api/v1/professionals/", {"name": "Dr. Bia"}, format="json")
    assert other.status_code == 201, other.content
    resp = _book(client, {**ids, "professional": other.data["id"]}, _start(hour=10))
    assert resp.status_code == 201, resp.content


def test_cancelled_nao_bloqueia():
    client, ids = _base("sched-cancel")
    first = _book(client, ids, _start(hour=10))
    assert first.status_code == 201
    cancel = client.post(f"/api/v1/appointments/{first.data['id']}/cancel/")
    assert cancel.status_code == 200
    assert cancel.data["status"] == "CANCELLED"

    # Cancel idempotente
    again = client.post(f"/api/v1/appointments/{first.data['id']}/cancel/")
    assert again.status_code == 200

    resp = _book(client, ids, _start(hour=10))
    assert resp.status_code == 201, resp.content


def test_reschedule_para_horario_ocupado_da_409():
    client, ids = _base("sched-resched")
    a = _book(client, ids, _start(hour=10))
    b = _book(client, ids, _start(hour=12))
    assert a.status_code == 201 and b.status_code == 201

    resp = client.post(
        f"/api/v1/appointments/{b.data['id']}/reschedule/",
        {"start": _start(hour=10, days_ahead=7).replace(minute=30).isoformat()},
        format="json",
    )
    assert resp.status_code == 409, resp.content


def test_availability_exclui_horario_ocupado():
    client, ids = _base("sched-avail")
    start = _start(hour=10)
    assert _book(client, ids, start).status_code == 201

    resp = client.get(
        "/api/v1/availability/",
        {"professional": ids["professional"], "date": start.date().isoformat()},
    )
    assert resp.status_code == 200, resp.content
    slots = resp.data["slots"]
    assert len(slots) > 0
    # 10:00 e 10:30 (serviço de 60min) não podem estar livres
    starts = {s["start"] for s in slots}
    assert start.isoformat() not in starts


def test_webhook_confirm_e_token_invalido_404():
    client, ids = _base("sched-webhook")
    created = _book(client, ids, _start(hour=10))
    assert created.status_code == 201
    token = created.data["confirmation_token"]
    schema = _schema("sched-webhook")

    anon = APIClient()
    ok = anon.post(
        "/api/v1/appointments/confirm-webhook/",
        {"token": token, "action": "confirm"},
        format="json",
        HTTP_X_TENANT_ID=schema,
    )
    assert ok.status_code == 200, ok.content
    assert ok.data["status"] == "CONFIRMED"

    bad = anon.post(
        "/api/v1/appointments/confirm-webhook/",
        {"token": "00000000-0000-0000-0000-000000000000", "action": "confirm"},
        format="json",
        HTTP_X_TENANT_ID=schema,
    )
    assert bad.status_code == 404, bad.content


def test_isolamento_entre_tenants():
    client_a, ids_a = _base("sched-iso-a")
    created = _book(client_a, ids_a, _start(hour=10))
    assert created.status_code == 201

    client_b = APIClient()
    _auth(client_b, _signup(client_b, "sched-iso-b").data["access"])
    assert client_b.get("/api/v1/appointments/").data["results"] == []
    assert (
        client_b.get(f"/api/v1/appointments/{created.data['id']}/").status_code == 404
    )


def test_historico_appointment_registrado():
    client, ids = _base("sched-audit")
    created = _book(client, ids, _start(hour=10))
    assert created.status_code == 201
    from apps.tenants.models import Tenant

    connection.set_schema_to_public()
    tenant = Tenant.objects.using("default").get(schema_name=_schema("sched-audit"))
    connection.set_tenant(tenant)
    stored = Appointment.objects.get(pk=created.data["id"])
    assert stored.history.count() >= 1
