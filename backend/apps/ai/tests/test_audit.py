"""Testes da auditoria de LLM e do isolamento por tenant (ETAPA 4)."""

from __future__ import annotations

import uuid

import pytest
from django.db import connection

from apps.ai.costs import calculate_cost
from apps.ai.models import LLMInteraction
from apps.ai.services import record_interaction
from apps.ai.tests._assertions import check, check_equal

pytestmark = pytest.mark.django_db


def test_record_interaction_grava_auditoria_completa(tenant):
    prompt = [{"role": "user", "content": "Oi, quero agendar."}]
    item = record_interaction(
        model="gpt-4o-mini",
        prompt=prompt,
        response="Claro! Qual horário?",
        prompt_tokens=100,
        completion_tokens=50,
        latency_ms=123,
    )

    check_equal(item.tenant_id, tenant.pk)
    check_equal(item.total_tokens, 150)
    check_equal(item.cost_usd, calculate_cost("gpt-4o-mini", 100, 50))
    check_equal(item.prompt, prompt)
    check_equal(item.response, "Claro! Qual horário?")
    check_equal(item.latency_ms, 123)
    check(isinstance(item.request_id, uuid.UUID))
    check(LLMInteraction.objects.filter(pk=item.pk).exists())


def test_record_interaction_preserva_request_id(tenant):
    rid = uuid.uuid4()
    item = record_interaction(model="gpt-4o-mini", request_id=rid)
    check_equal(item.request_id, rid)


def test_record_interaction_exige_tenant_ativo():
    connection.set_schema_to_public()
    with pytest.raises(ValueError):
        record_interaction(model="gpt-4o-mini")


def test_manager_nao_vaza_entre_tenants(tenant_factory):
    tenant_a = tenant_factory("ai_iso_a")
    connection.set_tenant(tenant_a)
    record_interaction(model="gpt-4o-mini", response="resposta A")
    check_equal(LLMInteraction.objects.count(), 1)

    tenant_b = tenant_factory("ai_iso_b")
    connection.set_tenant(tenant_b)
    check_equal(LLMInteraction.objects.count(), 0)
    record_interaction(model="gpt-4o", response="resposta B")
    check_equal(LLMInteraction.objects.get().response, "resposta B")

    connection.set_tenant(tenant_a)
    check_equal(LLMInteraction.objects.get().response, "resposta A")
    check_equal(LLMInteraction.objects.count(), 1)
