"""Serializers da Etapa 5 (fundação). Segredos nunca voltam na leitura."""

from __future__ import annotations

from rest_framework import serializers

from apps.settings.models import (
    ApiKey,
    IntegrationConfig,
    TenantSettings,
    WebhookEndpoint,
)


class TenantSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantSettings
        fields = (
            "id",
            "business_start",
            "business_end",
            "timezone",
            "logo_url",
            "primary_color",
            "brand_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class IntegrationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationConfig
        fields = (
            "id",
            "provider",
            "active",
            "professional_email",
            "config",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {"config": {"write_only": True}}


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ("id", "name", "url", "events", "active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class WebhookCreateSerializer(WebhookEndpointSerializer):
    secret = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta(WebhookEndpointSerializer.Meta):
        fields = (*WebhookEndpointSerializer.Meta.fields, "secret")


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = (
            "id",
            "name",
            "prefix",
            "active",
            "last_used_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
