"""FAQ retrieval RAG (Etapa 4) — primeira versão.

Busca ILIKE sobre as mensagens de ``ConversationMessage`` do omnichannel
(respostas já dadas no tenant) + stub de embedding para a migração
futura. Sem match → lista vazia (o ``auto_reply`` escala para humano).

**Migração futura (pgvector)**: hoje a relevância é por ``ILIKE``/substring
sobre ``normalized_body``. Quando houver pgvector, este módulo deve
gerar embeddings (``embedding_stub`` → ``text-embedding-3-small``) e
trocar o filtro por busca por similaridade de cosseno com índice IVFFlat
— a assinatura pública (``search_faq``) não muda.

Import path: ``apps.ai.rag`` (flat, cf. decisão do coordenador).
"""

from __future__ import annotations

from typing import Any

import structlog
from django.db.models import Q

from apps.omnichannel.models import ConversationMessage

logger = structlog.get_logger(__name__)

#: Limite de trechos retornados para montar o contexto.
MAX_SNIPPETS = 5

#: Tamanho do stub de embedding (migração pgvector manterá o formato).
EMBEDDING_DIM = 8


def embedding_stub(text: str) -> list[float]:
    """Embedding determinístico e barato (stub da migração pgvector).

    Vetor de ``EMBEDDING_DIM`` derivado do hash do texto — suficiente
    para dedupe/identidade em testes, NÃO para similaridade semântica.
    A versão real trocará por ``text-embedding-3-small`` sem mudar a
    assinatura.
    """
    digest = 0
    for char in (text or "").strip().lower():
        digest = (digest * 131 + ord(char)) % (2**32)
    return [
        ((digest >> (idx * 4)) & 0xF) / 15.0
        for idx in range(EMBEDDING_DIM)
    ]


def search_faq(question: str, *, limit: int = MAX_SNIPPETS) -> list[dict[str, Any]]:
    """Busca ILIKE nas mensagens do omnichannel do tenant ativo.

    Filtra ``normalized_body`` (minúsculas) por cada termo relevante da
    pergunta, restringindo a respostas de atendente/sistema (fonte de
    verdade do FAQ operacional). Tenant isolation: o schema ativo do
    django-tenants já restringe as linhas — nenhum dado cross-tenant.
    """
    terms = [
        term
        for term in (question or "").lower().split()
        if len(term) >= 3
    ]
    if not terms:
        return []

    query = ConversationMessage.objects.filter(
        direction=ConversationMessage.Direction.OUTBOUND,
        sender_kind__in=[
            ConversationMessage.SenderKind.AGENT,
            ConversationMessage.SenderKind.SYSTEM,
        ],
    )
    condition = Q()
    for term in terms:
        condition |= Q(normalized_body__icontains=term) | Q(body__icontains=term)
    rows = (
        query.filter(condition)
        .order_by("-created_at")
        .values_list("id", "conversation_id", "body", "normalized_body")[:limit]
    )
    results = [
        {
            "message_id": row[0],
            "conversation_id": row[1],
            "snippet": (row[2] or "").strip()[:300],
        }
        for row in rows
    ]
    logger.info("rag_search", terms=len(results), question_terms=len(terms))
    return results


def build_context(question: str) -> str:
    """Monta o bloco de contexto em PT-BR para o prompt do auto_reply."""
    snippets = search_faq(question)
    if not snippets:
        return ""
    lines = [f"- {item['snippet']}" for item in snippets]
    return "Respostas anteriores da equipe:\n" + "\n".join(lines)
