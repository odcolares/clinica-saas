"""Extração de dados do cliente (Etapa 4).

Função principal: ``extract_client_data(text) -> {nome, telefone, servico}``
via function calling strict do ``chat.completions.create`` (gpt-4o-mini).

Campos ausentes na mensagem voltam ``None`` — nunca inventar dado.
Segue o padrão de ``apps/omnichannel/services.py``: tenant ativo,
``structlog``, ``LLMInteraction`` a cada chamada e tráfego só via
``apps.ai.client`` (breaker+cache). Import path: ``apps.ai.extraction``
(flat, cf. decisão do coordenador em ``apps.ai.intent``).
"""

from __future__ import annotations

import json
from typing import Any

import structlog

from apps.ai._base import DEFAULT_MODEL, llm_call

logger = structlog.get_logger(__name__)

#: Campos do contrato público (ordem estável na resposta).
CLIENT_FIELDS: tuple[str, ...] = ("nome", "telefone", "servico")

SYSTEM_PROMPT = (
    "Você extrai dados de contato de mensagens de clientes de uma clínica. "
    "Chame a função extract_client_data com os campos encontrados. "
    "Campos ausentes devem ser null — nunca invente valores."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "extract_client_data",
            "description": "Dados do cliente extraídos da mensagem.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {
                        "type": ["string", "null"],
                        "description": "Nome do cliente.",
                    },
                    "telefone": {
                        "type": ["string", "null"],
                        "description": "Telefone/WhatsApp no formato original.",
                    },
                    "servico": {
                        "type": ["string", "null"],
                        "description": "Serviço/procedimento desejado.",
                    },
                },
                "required": ["nome", "telefone", "servico"],
                "additionalProperties": False,
            },
        },
    }
]


def build_messages(text: str) -> list[dict[str, Any]]:
    """Mensagens enviadas ao modelo (determinísticas — cacheáveis)."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (text or "").strip() or "(mensagem vazia)"},
    ]


def extract_client_data(text: str) -> dict[str, Any]:
    """Extrai ``{nome, telefone, servico}`` da mensagem do cliente.

    Campos não encontrados voltam ``None``. Provedor indisponível →
    todos ``None`` (nunca inventar dado de contato).
    """
    messages = build_messages(text)

    def _call(client: Any) -> Any:
        return client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=0.0,
            tools=TOOLS,
            tool_choice={"type": "function", "function": {"name": "extract_client_data"}},
        )

    def _extract(response: Any) -> str:
        calls = response.choices[0].message.tool_calls or []
        if not calls:
            return json.dumps(dict.fromkeys(CLIENT_FIELDS))
        return calls[0].function.arguments or "{}"

    def _usage(response: Any) -> tuple[int, int]:
        return response.usage.prompt_tokens, response.usage.completion_tokens

    try:
        raw, _, _ = llm_call(
            feature="extract_client_data",
            messages=messages,
            call=_call,
            extract_text=_extract,
            extract_usage=_usage,
        )
    except Exception as exc:  # noqa: BLE001 — indisponível → tudo None
        logger.warning("extraction_unavailable", error=type(exc).__name__)
        return dict.fromkeys(CLIENT_FIELDS)

    return _coerce(raw)


def _coerce(raw: str) -> dict[str, Any]:
    """Normaliza a resposta para exatamente ``{nome, telefone, servico}``."""
    result: dict[str, Any] = dict.fromkeys(CLIENT_FIELDS)
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        logger.warning("extraction_payload_invalido")
        return result
    if not isinstance(payload, dict):
        return result
    for field in CLIENT_FIELDS:
        value = payload.get(field)
        result[field] = value if isinstance(value, str) and value.strip() else None
    return result
