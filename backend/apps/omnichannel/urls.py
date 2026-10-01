"""Rotas do Omnichannel (ETAPA 3 + endpoints AI da ETAPA 4).

Montadas sob /api/v1/. Os endpoints AI usam Conversation/ConversationMessage
do omnichannel e gravam LLMInteraction a cada chamada.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.omnichannel.views import (
    ConversationViewSet,
    MessageViewSet,
    TelegramWebhookView,
)
from apps.omnichannel.views_ai import (
    AutoReplyView,
    ClassifyView,
    ExtractView,
    SummarizeView,
)

router = DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversation")
router.register("messages", MessageViewSet, basename="message")

urlpatterns = [
    path(
        "omnichannel/telegram/webhook/",
        TelegramWebhookView.as_view(),
        name="telegram-webhook",
    ),
    # ETAPA 4 — AI Assistant (tenant-scoped, JWT)
    path("ai/classify/", ClassifyView.as_view(), name="ai-classify"),
    path("ai/extract/", ExtractView.as_view(), name="ai-extract"),
    path("ai/summarize/", SummarizeView.as_view(), name="ai-summarize"),
    path("ai/auto-reply/", AutoReplyView.as_view(), name="ai-auto-reply"),
    *router.urls,
]
