"""Testes de ``PromptTemplate.render`` e do seed de prompts (ETAPA 4)."""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from apps.ai.models import PromptTemplate
from apps.ai.tests._assertions import check, check_equal

pytestmark = pytest.mark.django_db


def test_render_aplica_parameters_e_overrides():
    template = PromptTemplate(
        name="saudacao",
        content="Olá {nome}, serviço {servico}.",
        parameters={"nome": "Cliente", "servico": "limpeza"},
    )
    check_equal(template.render(), "Olá Cliente, serviço limpeza.")
    check_equal(
        template.render(servico="clareamento"), "Olá Cliente, serviço clareamento."
    )


def test_render_parametro_ausente_levanta_validationerror():
    template = PromptTemplate(name="sem-default", content="Olá {nome}.")
    with pytest.raises(ValidationError):
        template.render()


def test_render_template_invalido_levanta_validationerror():
    template = PromptTemplate(name="quebrado", content="Olá {nome.")
    with pytest.raises(ValidationError):
        template.render(nome="A")


def test_seed_cria_prompts_iniciais(tenant):
    names = set(PromptTemplate.objects.values_list("name", flat=True))
    check({"intent_classifier", "data_extractor", "summarizer"} <= names)
    check(PromptTemplate.objects.filter(is_active=True).count() >= 3)
