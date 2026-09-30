"""Resumo de conversa (Etapa 4).

Função principal: ``summarize_conversation(messages) -> str`` — resumo
em PT-BR do histórico atendimento, para o painel do atendente.

Segue o padrão de ``apps/omnichannel/services.py``: tenant ativo,
``structlog``, ``LLMInteraction`` a cada chamada e tráfego só via
``apps.ai.client`` (breaker+cache, temperature 0 → cacheável).

Import path: ``apps.ai.summarizer`` (flat, cf. decisão do coordenador).
"""

from __future__ import annotations

from typing import Any, Iterable

import structlog

from apps.ai._base import DEFAULT_MODEL, llm_call

logger = structlog.get_logger(__name__)

#: Limite de mensagens no prompt (evita estourar contexto em threads longas).
MAX_MESSAGES = 40

_UNAVAILABLE = "Resumo indisponível no momento."

SYSTEM_PROMPT = (
    "Você resume conversas de atendimento de uma clínica em português do "
    "Brasil. Em no máximo 3 frases, destaque o que o cliente quer e o "
    "próximo passo. Não invente informação que não esteja na conversa."
)


def _author_label(message: Any) -> str:
    """Rótulo do autor: cliente, atendente ou sistema."""
    sender = getattr(message, "sender_kind", "") or ""
    if sender == "customer":
        return "Cliente"
    if sender == "agent":
        return "Atendente"
    return "Sistema"


def _body_of(message: Any) -> str:
    """Texto da mensagem, aceitando objeto ou dict."""
    if isinstance(message, dict):
        return str(message.get("body") or message.get("content") or "")
    return str(getattr(message, "body", "") or "")


def format_conversation(messages: Iterable[Any]) -> str:
    """Serializa o histórico em linhas ``Autor: texto`` (determinístico)."""
    rows = list(messages)[-MAX_MESSAGES:]
    return "\n".join(
        f"{_author_label(item)}: {_body_of(item).strip()}"
        for item in rows
        if _body_of(item).strip()
    )


def summarize_conversation(messages: Iterable[Any]) -> str:
    """Resume a conversa em PT-BR.

    Recebe objetos ``ConversationMessage`` ou dicts com ``body``.
    Conversa vazia → string vazia (nada a resumir). Provedor
    indisponível → mensagem neutra (nunca inventa resumo).
    """
    conversation = format_conversation(messages)
    if not conversation:
        return ""

    prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Conversa:\n---\n{conversation}\n---"},
    ]

    def _call(client: Any) -> Any:
        return client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=prompt,
            temperature=0.0,
        )

    def _extract(response: Any) -> str:
        return (response.choices[0].message.content or "").strip()

    def _usage(response: Any) -> tuple[int, int]:
        return response.usage.prompt_tokens, response.usage.completion_tokens

    try:
        summary, _, _ = llm_call(
            feature="summarize_conversation",
            messages=prompt,
            call=_call,
            extract_text=_extract,
            extract_usage=_usage,
        )
    except Exception as exc:  # noqa: BLE001 — indisponível → texto neutro
        logger.warning("summarizer_unavailable", error=type(exc).__name__)
        return _UNAVAILABLE

    return summary or _UNAVAILABLE
