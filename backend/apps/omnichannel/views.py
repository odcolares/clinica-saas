"""Views do Omnichannel (ETAPA 3) — conversas, mensagens e webhook do Telegram.

Contrato: `Projeto_SaaS/architecture/API.md` §Omnichannel. As viewsets derivam
tenant/identidade do contexto autenticado (JWT) e restringem o escopo por objeto
via guardian (reutiliza apps.crm.permissions). O webhook é público, valida o
segredo do Telegram e é idempotente.
"""

from __future__ import annotations

from django.db import connection
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.crm.permissions import visible_queryset
from apps.crm.views import CrmBaseViewSet
from apps.omnichannel.channels.factory import get_adapter
from apps.omnichannel.models import Conversation, ConversationMessage
from apps.omnichannel.serializers import (
    AssignConversationSerializer,
    ConversationListSerializer,
    ConversationMessageSerializer,
    ConversationSerializer,
    OutboundMessageSerializer,
)
from apps.omnichannel.services import (
    assign_conversation,
    ingest_inbound_message,
    send_outbound_message,
)


class ConversationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    CrmBaseViewSet,
):
    filterset_fields = ("channel", "status", "assigned_to", "customer", "lead")
    search_fields = ("external_chat_id",)
    ordering_fields = ("created_at", "updated_at", "status")

    def get_queryset(self):
        base = Conversation.objects.select_related("assigned_to", "customer", "lead")
        return visible_queryset(self.request.user, Conversation, base)

    def get_serializer_class(self):
        if self.action == "list":
            return ConversationListSerializer
        return ConversationSerializer

    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        conversation = self.get_object()
        serializer = AssignConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = assign_conversation(
            conversation,
            user=serializer.validated_data["assigned_to"],
            author=request.user,
        )
        return Response(ConversationSerializer(conversation).data)

    @action(detail=True, methods=["post"], url_path="reply")
    def reply(self, request, pk=None):
        conversation = self.get_object()
        serializer = OutboundMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = send_outbound_message(
            conversation,
            text=serializer.validated_data["body"],
            author=request.user,
        )
        return Response(
            ConversationMessageSerializer(message).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="messages")
    def messages(self, request, pk=None):
        conversation = self.get_object()
        queryset = conversation.messages.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                ConversationMessageSerializer(page, many=True).data
            )
        return Response(ConversationMessageSerializer(queryset, many=True).data)


class MessageViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    CrmBaseViewSet,
):
    filterset_fields = ("conversation", "direction", "sender_kind")
    search_fields = ("body",)
    ordering_fields = ("created_at",)

    def get_queryset(self):
        conversation_ids = visible_queryset(
            self.request.user, Conversation, Conversation.objects.all()
        ).values_list("pk", flat=True)
        return ConversationMessage.objects.select_related("conversation").filter(
            conversation_id__in=conversation_ids
        )

    def get_serializer_class(self):
        return ConversationMessageSerializer


class TelegramWebhookView(APIView):
    """Webhook público do Telegram (sem JWT).

    Tenant vem do header x-tenant-id (hint de roteamento, ver middleware). A
    autenticidade é validada pelo segredo do webhook **do tenant** (fallback
    global só se habilitado explicitamente); a entrega é idempotente por
    ``telegram_message_id``. Responde rápido com 200.
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "telegram"

    def post(self, request):
        if connection.schema_name in (None, "public"):
            return Response(
                {"detail": "Tenant não identificado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        adapter = get_adapter("telegram")
        if not adapter.verify_webhook(request):
            return Response(
                {"detail": "Webhook não autorizado."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            message, created = ingest_inbound_message(
                channel="telegram", payload=request.data, adapter=adapter
            )
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "ok": True,
                "conversation": message.conversation_id,
                "message": message.pk,
                "duplicate": not created,
            },
            status=status.HTTP_200_OK,
        )
