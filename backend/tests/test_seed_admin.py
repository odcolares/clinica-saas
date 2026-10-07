"""Testes do management command seed_admin — exigem Postgres real."""

from __future__ import annotations

from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection
from rest_framework.test import APIClient

from apps.accounts.models import Role, User

pytestmark = pytest.mark.django_db

PASSWORD = "SenhaForte123"


def _set_public():
    connection.set_schema_to_public()


def test_seed_admin_cria_admin_em_tenant_via_signup():
    client = APIClient()
    resp = client.post(
        "/api/v1/tenants/signup/",
        {
            "tenant_name": "Clínica Seed",
            "tenant_slug": "seed-admin-a",
            "admin_username": "original",
            "admin_email": "original@example.com",
            "admin_password": PASSWORD,
        },
        format="json",
    )
    assert resp.status_code == 201, resp.content
    _set_public()
    call_command(
        "seed_admin",
        tenant="seed_admin_a",
        password=PASSWORD,
        stdout=StringIO(),
        stderr=StringIO(),
    )
    _set_public()
    connection.set_schema("seed_admin_a")
    admin = User.objects.get(username="admin")
    assert admin.email == "admin@clinica.com"
    assert admin.role.name == "admin"
    assert admin.status == "active"
    assert admin.check_password(PASSWORD)


def test_seed_admin_requis_password_e_tenant_invalido():
    with pytest.raises(Exception):
        call_command(
            "seed_admin", tenant="inexistente_xyz", stdout=StringIO(), stderr=StringIO()
        )
    with pytest.raises(Exception):
        call_command(
            "seed_admin",
            tenant="public",
            password="curta",
            stdout=StringIO(),
            stderr=StringIO(),
        )


def test_seed_admin_garante_papeis_default():
    client = APIClient()
    resp = client.post(
        "/api/v1/tenants/signup/",
        {
            "tenant_name": "Clínica Seed Roles",
            "tenant_slug": "seed-admin-b",
            "admin_username": "root",
            "admin_email": "root@example.com",
            "admin_password": PASSWORD,
        },
        format="json",
    )
    assert resp.status_code == 201, resp.content
    _set_public()
    call_command(
        "seed_admin",
        tenant="seed_admin_b",
        username="root2",
        email="root2@example.com",
        password=PASSWORD,
        stdout=StringIO(),
        stderr=StringIO(),
    )
    _set_public()
    connection.set_schema("seed_admin_b")
    assert {r.name for r in Role.objects.all()} >= {"admin", "manager", "attendant"}
    _set_public()
