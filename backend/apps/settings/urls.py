"""Rotas da Etapa 5, montadas sob /api/v1/settings/."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.settings.views import (
    ApiKeyViewSet,
    IntegrationConfigViewSet,
    TenantSettingsView,
    WebhookEndpointViewSet,
)

router = DefaultRouter()
router.register("integrations", IntegrationConfigViewSet, basename="integration")
router.register("webhooks", WebhookEndpointViewSet, basename="webhook")
router.register("api-keys", ApiKeyViewSet, basename="apikey")

urlpatterns = [
    path("tenant/", TenantSettingsView.as_view(), name="tenant-settings"),
    *router.urls,
]
