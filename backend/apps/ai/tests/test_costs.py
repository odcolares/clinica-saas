"""Testes da tabela de preços e do cálculo de custo (ETAPA 4)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.ai.costs import OPENAI_PRICING, calculate_cost
from apps.ai.tests._assertions import check, check_equal

pytestmark = pytest.mark.django_db


def test_pricing_cobre_modelos_esperados():
    check(set(OPENAI_PRICING) >= {"gpt-4o-mini", "gpt-4o"})


def test_calculate_cost_gpt_4o_mini():
    # (1000*0.15 + 500*0.60) / 1e6 = 0.00045
    check_equal(calculate_cost("gpt-4o-mini", 1000, 500), Decimal("0.00045000"))


def test_calculate_cost_gpt_4o():
    # (1000*2.50 + 1000*10.00) / 1e6 = 0.0125
    check_equal(calculate_cost("gpt-4o", 1000, 1000), Decimal("0.01250000"))


def test_calculate_cost_modelo_desconhecido_zera():
    check_equal(calculate_cost("modelo-inexistente", 9999, 9999), Decimal("0"))


def test_calculate_cost_ignora_tokens_invalidos():
    check_equal(calculate_cost("gpt-4o-mini", -10, 0), Decimal("0"))
