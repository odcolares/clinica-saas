from django.contrib import admin

from .models import ApiKey, IntegrationConfig, TenantSettings, WebhookEndpoint


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    list_display = ("timezone", "business_start", "business_end", "brand_name")


@admin.register(IntegrationConfig)
class IntegrationConfigAdmin(admin.ModelAdmin):
    list_display = ("provider", "active", "professional_email")
    list_filter = ("provider", "active")


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "active")
    list_filter = ("active",)


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "prefix", "active", "last_used_at")
    list_filter = ("active",)
    readonly_fields = ("prefix", "key_hash")
