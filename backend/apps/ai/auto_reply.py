"""Resposta automática RAG (Etapa 4).

Monta o contexto FAQ (``rag.search_faq``) e gera resposta com
temperature 0. A resposta volta ``{answer, source}``:

- ``source == "faq"`` → resposta baseada no FAQ.
- ``source == "fallback"`` → sem FAQ → sugere atendente humano
  (nunca inventa nada; fail-safe).

Segue o padrão de ``apps/omnichannel/services.py``: tenant ativo,
``structlog``, ``LLMInteraction`` a cada chamada e tráfego só via
``apps.ai.client`` (breaker+cache). Import path:
``apps.ai.auto_reply`` (flat, cf. decisão do coordenador).
"""

from __future__ import annotations

from typing import Any

import structlog

from apps.ai._base import DEFAULT_MODEL, llm_call
from apps.ai.rag import build_context, search_faq

logger = structlog.get_logger(__name__)

FALLBACK_ANSWER = (
    "Não encontramos resposta automática para isso — "
    "um atendente vai te ajudar em breve."
)

SYSTEM_PROMPT = (
    "Responda ao cliente em português do Brasil, com base no "
    "contexto fornecido. Se não houver contexto, diga que "
    "não encontrou e encaminhe para um atendente humano."
)


def build_messages(text: str) -> list[dict[str, Any]]:
    """Mensagens determinísticas (cacheáveis, temperature 0)."""
    context = build_context(text)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Pergunta do cliente: {text}\n"
                f"Contexto (FAQ/respostas anteriores): {context or 'Nenhum FAQ encontrado.'}"
            ),
        },
    ]


def auto_reply(text: str) -> dict[str, Any]:
    """Gera resposta automática RAG (FAQ + LLM, temperature 0).

    Retorna ``{"answer": ..., "source": "faq"|"fallback"}``.
    Provedor indisponível → fallback humano (nunca expõe erro).
    """
    messages = build_messages(text)

    def _call(client: Any) -> Any:
        return client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=0.0,
        )

    def _extract(response: Any) -> str:
        return (response.choices[0].message.content or "").strip()

    def _usage(response: Any) -> tuple[int, int]:
        return response.usage.prompt_tokens, response.usage.completion_tokens

    try:
        answer, _, _ = llm_call(
            feature="auto_reply",
            messages=messages,
            call=_call,
            extract_text=_extract,
            extract_usage=_usage,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("auto_reply_unavailable", error=type(exc).__name__)
        return {"answer": FALLBACK_ANSWER, "source": "fallback"}

    source = "faq" if search_faq(text) else "fallback"
    return {"answer": answer or FALLBACK_ANSWER, "source": source}
