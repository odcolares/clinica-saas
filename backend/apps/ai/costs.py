"""Tabela de preços OpenAI e cálculo de custo por chamada (ETAPA 4).

Valores em USD por 1.000.000 de tokens (fonte: página de preços da OpenAI).
Manter aqui — não espalhar constantes de preço pelo código. Modelos fora da
tabela retornam custo zero (não inventar preço).
"""

from __future__ import annotations

from decimal import Decimal

# USD por 1M tokens: {"prompt": ..., "completion": ...}
OPENAI_PRICING: dict[str, dict[str, Decimal]] = {
    "gpt-4o-mini": {"prompt": Decimal("0.15"), "completion": Decimal("0.60")},
    "gpt-4o": {"prompt": Decimal("2.50"), "completion": Decimal("10.00")},
}

_TOKENS_PER_MILLION = Decimal("1000000")
_CENT_PRECISION = Decimal("0.00000001")


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> Decimal:
    """Custo em USD da chamada, quantizado a 8 casas decimais.

    Retorna ``Decimal("0")`` para modelo desconhecido ou contagens negativas.
    """
    prompt = max(int(prompt_tokens or 0), 0)
    completion = max(int(completion_tokens or 0), 0)
    pricing = OPENAI_PRICING.get(model)
    if pricing is None:
        return Decimal("0")
    cost = (
        Decimal(prompt) * pricing["prompt"]
        + Decimal(completion) * pricing["completion"]
    ) / _TOKENS_PER_MILLION
    return cost.quantize(_CENT_PRECISION)
