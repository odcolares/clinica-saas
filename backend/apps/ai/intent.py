"""Classificação de intenção do cliente (Etapa 4).

Função principal: ``classify_intent(text) -> {intent, confidence}`` via
``chat.completions.parse`` (gpt-4o-mini, Structured Outputs Pydantic).

- ``intent``: booking|cancellation|query|feedback|handoff
- ``confidence``: float 0.0-1.0

Segue o padrão de ``apps/omnichannel/services.py``: opera no schema do
tenant ativo, loga com ``structlog`` e grava ``LLMInteraction`` a cada
chamada (tokens/custo/latência). Nunca chama OpenAI direto — todo tráfego
passa por ``apps.ai.client``, sob ``apps.ai.breaker`` e ``apps.ai.cache``.

Import path: ``apps.ai.intent`` (arquivo flat). O brief previa
``apps.ai.services.intent``, mas Python não permite ``services.py`` e
``services/`` lado a lado — e ``services.py`` pertence à infra da PI.
"""

from __future__ import annotations

import json
from typing import Any

import structlog
from pydantic import BaseModel, Field

from apps.ai._base import DEFAULT_MODEL, llm_call

logger = structlog.get_logger(__name__)

#: Intenções suportadas pela triagem da clínica.
INTENT_NAMES: tuple[str, ...] = (
    "booking",
    "cancellation",
    "query",
    "feedback",
    "handoff",
)

FALLBACK_INTENT = "handoff"
_PATTERN = "^(booking|cancellation|query|feedback|handoff)$"

SYSTEM_PROMPT = (
    "Você classifica a intenção de mensagens de clientes de uma clínica. "
    "Categorias: booking (agendar/remarcar), cancellation (cancelar), "
    "query (dúvida/informação), feedback (elogio/reclamação), "
    "handoff (assunto sensível ou fora do escopo — escalar para humano). "
    "Devolva a intenção e uma confiança entre 0 e 1."
)


class IntentOutput(BaseModel):
    """Saída estruturada do classificador (Structured Outputs)."""

    intent: str = Field(..., pattern=_PATTERN, description="Intenção detectada.")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confiança na classificação."
    )


def build_messages(text: str) -> list[dict[str, Any]]:
    """Mensagens enviadas ao modelo (determinísticas — cacheáveis)."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (text or "").strip() or "(mensagem vazia)"},
    ]


def classify_intent(text: str) -> dict[str, Any]:
    """Classifica a intenção do cliente.

    Retorna ``{"intent": <enum>, "confidence": <float>}``. Quando o
    provedor está indisponível (breaker aberto e sem cache), devolve
    ``{"intent": "handoff", "confidence": 0.0}`` — a IA indisponível
    nunca decide sozinha; a conversa vai para um humano.
    """
    messages = build_messages(text)

    def _call(client: Any) -> Any:
        return client.chat.completions.parse(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=0.0,
            response_format=IntentOutput,
        )

    def _extract(response: Any) -> str:
        parsed = response.choices[0].message.parsed
        if parsed is None:
            return json.dumps({"intent": FALLBACK_INTENT, "confidence": 0.0})
        return parsed.model_dump_json()

    def _usage(response: Any) -> tuple[int, int]:
        return response.usage.prompt_tokens, response.usage.completion_tokens

    try:
        raw, _, _ = llm_call(
            feature="classify_intent",
            messages=messages,
            call=_call,
            extract_text=_extract,
            extract_usage=_usage,
        )
    except Exception as exc:  # noqa: BLE001 — indisponível → fail-safe humano
        logger.warning("intent_unavailable", error=type(exc).__name__)
        return {"intent": FALLBACK_INTENT, "confidence": 0.0}

    return _coerce(raw)


def _coerce(raw: str) -> dict[str, Any]:
    """Valida/normaliza a resposta do modelo para o contrato público."""
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        logger.warning("intent_payload_invalido")
        return {"intent": FALLBACK_INTENT, "confidence": 0.0}

    intent = str(payload.get("intent", "")).strip().lower()
    if intent not in INTENT_NAMES:
        intent = FALLBACK_INTENT

    try:
        confidence = float(payload.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = min(max(confidence, 0.0), 1.0)

    return {"intent": intent, "confidence": confidence}
