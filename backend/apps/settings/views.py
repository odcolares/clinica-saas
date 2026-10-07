"""Views da Etapa 5 — seguem CrmBaseViewSet + guardian (padrão ETAPA 1/2)."""

from __future__ import annotations

import structlog
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.crm.permissions import grant_member_perms, visible_queryset
from apps.crm.views import CrmBaseViewSet
from rest_framework.throttling import ScopedRateThrottle
from apps.settings.models import (
    ApiKey,
    IntegrationConfig,
    TenantSettings,
    WebhookEndpoint,
)
from apps.settings.serializers import (
    ApiKeySerializer,
    IntegrationConfigSerializer,
    TenantSettingsSerializer,
    WebhookCreateSerializer,
    WebhookEndpointSerializer,
)
from apps.settings.throttling import PlanRateThrottle

logger = structlog.get_logger(__name__)


class TenantSettingsView(APIView):
    """Singleton: GET cria default se ausente; PATCH atualiza."""

    def get(self, request):
        obj = TenantSettings.current()
        return Response(TenantSettingsSerializer(obj).data)

    def patch(self, request):
        obj = TenantSettings.current()
        serializer = TenantSettingsSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class IntegrationConfigViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    CrmBaseViewSet,
):
    throttle_classes = [ScopedRateThrottle, PlanRateThrottle]
    filterset_fields = ("provider", "active")
    search_fields = ("provider", "professional_email")
    ordering_fields = ("provider", "created_at")

    def get_queryset(self):
        return visible_queryset(
            self.request.user, IntegrationConfig, IntegrationConfig.objects.all()
        )

    def get_serializer_class(self):
        return IntegrationConfigSerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        grant_member_perms(self.request.user, obj)


class WebhookEndpointViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    CrmBaseViewSet,
):
    throttle_classes = [ScopedRateThrottle, PlanRateThrottle]
    filterset_fields = ("active",)
    search_fields = ("name", "url")
    ordering_fields = ("name", "created_at")

    def get_queryset(self):
        return visible_queryset(
            self.request.user, WebhookEndpoint, WebhookEndpoint.objects.all()
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return WebhookCreateSerializer
        return WebhookEndpointSerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        grant_member_perms(self.request.user, obj)


class ApiKeyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    CrmBaseViewSet,
):
    throttle_classes = [ScopedRateThrottle, PlanRateThrottle]
    filterset_fields = ("active",)
    search_fields = ("name", "prefix")
    ordering_fields = ("name", "created_at")

    def get_queryset(self):
        return visible_queryset(self.request.user, ApiKey, ApiKey.objects.all())

    def get_serializer_class(self):
        return ApiKeySerializer

    def create(self, request, *args, **kwargs):
        name = (request.data.get("name") or "").strip()
        if not name:
            return Response(
                {"detail": {"name": "Obrigatório."}}, status=status.HTTP_400_BAD_REQUEST
            )
        obj, plain = ApiKey.issue(name=name)
        grant_member_perms(request.user, obj)
        logger.info("api_key_issued", key_id=obj.pk, prefix=obj.prefix)
        data = ApiKeySerializer(obj).data
        data["plain_key"] = plain
        return Response(data, status=status.HTTP_201_CREATED)
