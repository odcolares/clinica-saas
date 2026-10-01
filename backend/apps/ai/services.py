"""Regras de domínio do app ``ai`` (ETAPA 4).

Ponto único de escrita da auditoria de LLM (``record_interaction``) e de
renderização de prompts. Segue o padrão de ``apps/omnichannel/services.py``:
opera no schema do tenant ativo, loga com ``structlog`` e degrada com segurança
quando dependências externas (Redis/OpenAI) falham.

Nenhum segredo é logado. Toda linha de auditoria é ancorada ao tenant ativo.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from django.db import connection, transaction

from apps.ai.costs import calculate_cost
from apps.ai.models import LLMInteraction, PromptTemplate

logger = structlog.get_logger(__name__)


def _active_tenant_id() -> int | None:
    return getattr(getattr(connection, "tenant", None), "pk", None)


def render_prompt(name: str, **values: Any) -> str:
    """Busca o prompt ativo ``name`` no schema do tenant e renderiza."""
    template = PromptTemplate.objects.filter(name=name, is_active=True).first()
    if template is None:
        raise PromptTemplate.DoesNotExist(f"Prompt ativo não encontrado: {name}")
    return template.render(**values)


@transaction.atomic
def record_interaction(
    *,
    model: str,
    prompt: list[dict[str, Any]] | None = None,
    response: str = "",
    provider: str = "openai",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    latency_ms: int = 0,
    request_id: uuid.UUID | None = None,
    tenant_id: int | None = None,
) -> LLMInteraction:
    """Grava uma interação de LLM na auditoria do tenant ativo.

    ``total_tokens`` e ``cost_usd`` são derivados quando não informados. Exige
    tenant ativo (ou ``tenant_id`` explícito): sem escopo, nunca grava — evita
    registro órfão que poderia ser lido por outro schema.
    """
    tenant_id = tenant_id or _active_tenant_id()
    if tenant_id is None:
        raise ValueError("Nenhum tenant ativo: auditoria de LLM exige tenant.")

    total_tokens = int(prompt_tokens or 0) + int(completion_tokens or 0)
    interaction = LLMInteraction.objects.create(
        tenant_id=tenant_id,
        request_id=request_id or uuid.uuid4(),
        model=model,
        provider=provider,
        prompt_tokens=int(prompt_tokens or 0),
        completion_tokens=int(completion_tokens or 0),
        total_tokens=total_tokens,
        cost_usd=calculate_cost(model, prompt_tokens, completion_tokens),
        latency_ms=int(latency_ms or 0),
        prompt=prompt or [],
        response=response or "",
    )
    logger.info(
        "llm_interaction_recorded",
        request_id=str(interaction.request_id),
        model=model,
        provider=provider,
        total_tokens=total_tokens,
        cost_usd=str(interaction.cost_usd),
        latency_ms=interaction.latency_ms,
        tenant_id=tenant_id,
    )
    return interaction
