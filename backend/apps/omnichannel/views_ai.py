"""Endpoints AI (Etapa 4) — classify, extract, summarize, auto-reply.

Contrato: ``docs/ETAPA-4-AI.md``. Tenant deriva do contexto autenticado
(JWT claim → schema ativo via ``TenantContextMiddleware``); conversas
são restringidas por guardian (``visible_queryset``) — um ``conversation_id``
de outro tenant responde 404, nunca expõe dado cross-tenant.

Toda chamada que chega ao provedor grava ``LLMInteraction``
(tokens/custo/latência) via ``apps.ai._base.llm_call`` — auditoria
obrigatória. Segue o padrão de ``apps/omnichannel/views.py``.
"""

from __future__ import annotations

from django.db import connection
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.auto_reply import auto_reply
from apps.ai.extraction import extract_client_data
from apps.ai.intent import classify_intent
from apps.ai.summarizer import summarize_conversation
from apps.crm.permissions import visible_queryset
from apps.omnichannel.models import Conversation


class AIInputSerializer(serializers.Serializer):
    """Entrada comum: texto livre OU conversa existente."""

    text = serializers.CharField(required=False, allow_blank=True, default="")
    conversation_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if not (attrs.get("text", "").strip() or attrs.get("conversation_id")):
            raise ValidationError("Informe 'text' ou 'conversation_id'.")
        return attrs


class SummarizeInputSerializer(serializers.Serializer):
    """Resumo exige uma conversa do tenant."""

    conversation_id = serializers.IntegerField(required=True)


class AIBaseView(APIView):
    """Base: auth JWT, escopo de conversa por tenant+guardian."""

    permission_classes = [IsAuthenticated]

    def _conversation(self, request, pk: int) -> Conversation:
        """Conversa visível ao usuário no tenant ativo (404 se não)."""
        queryset = visible_queryset(
            request.user, Conversation, Conversation.objects.all()
        )
        try:
            return queryset.get(pk=pk)
        except Conversation.DoesNotExist:
            raise NotFound({"detail": "Conversa não encontrada."}) from None

    def _resolve_text(self, request, validated: dict) -> str:
        """Texto direto ou última mensagem de entrada da conversa."""
        text = (validated.get("text") or "").strip()
        if text:
            return text
        conversation = self._conversation(request, validated["conversation_id"])
        last_inbound = (
            conversation.messages.order_by("-created_at")
            .filter(direction="inbound")
            .first()
        )
        if last_inbound is None:
            raise ValidationError(
                {"conversation_id": "Conversa sem mensagens de entrada."}
            )
        return last_inbound.body

    @staticmethod
    def _guard_tenant() -> None:
        """Sem tenant ativo não há como auditar nem isolar — recusa."""
        if connection.schema_name in (None, "public"):
            raise ValidationError({"detail": "Tenant não identificado."})


class ClassifyView(AIBaseView):
    """POST /api/v1/ai/classify/ → ``{intent, confidence}``."""

    def post(self, request):
        serializer = AIInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._guard_tenant()
        text = self._resolve_text(request, serializer.validated_data)
        return Response(classify_intent(text))


class ExtractView(AIBaseView):
    """POST /api/v1/ai/extract/ → ``{nome, telefone, servico}``."""

    def post(self, request):
        serializer = AIInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._guard_tenant()
        text = self._resolve_text(request, serializer.validated_data)
        return Response(extract_client_data(text))


class SummarizeView(AIBaseView):
    """POST /api/v1/ai/summarize/ → ``{summary}`` (PT-BR)."""

    def post(self, request):
        serializer = SummarizeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._guard_tenant()
        conversation = self._conversation(
            request, serializer.validated_data["conversation_id"]
        )
        messages = list(conversation.messages.all())
        if not messages:
            raise ValidationError({"conversation_id": "Conversa sem mensagens."})
        return Response({"summary": summarize_conversation(messages)})


class AutoReplyView(AIBaseView):
    """POST /api/v1/ai/auto-reply/ → ``{answer, source}`` (RAG, temp 0)."""

    def post(self, request):
        serializer = AIInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._guard_tenant()
        text = self._resolve_text(request, serializer.validated_data)
        return Response(auto_reply(text))


__all__ = [
    "AIInputSerializer",
    "SummarizeInputSerializer",
    "AIBaseView",
    "ClassifyView",
    "ExtractView",
    "SummarizeView",
    "AutoReplyView",
    "status",
]
