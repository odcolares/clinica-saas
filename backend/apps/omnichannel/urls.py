"""Rotas do Omnichannel (ETAPA 3), montadas sob /api/v1/."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.omnichannel.views import (
    ConversationViewSet,
    MessageViewSet,
    TelegramWebhookView,
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
    *router.urls,
]
