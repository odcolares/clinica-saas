"""Admin do app ``ai`` (por tenant).

``LLMInteraction`` é somente-leitura (trilha de auditoria); ``PromptTemplate``
pode ser editado pelo admin do tenant.
"""

from __future__ import annotations

from django.contrib import admin

from apps.ai.models import LLMInteraction, PromptTemplate


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "model_hint", "is_active", "updated_at")
    list_filter = ("is_active", "model_hint")
    search_fields = ("name", "content")
    readonly_fields = ("created_at", "updated_at")


@admin.register(LLMInteraction)
class LLMInteractionAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "provider",
        "model",
        "total_tokens",
        "cost_usd",
        "latency_ms",
        "request_id",
    )
    list_filter = ("provider", "model")
    search_fields = ("request_id", "response")
    date_hierarchy = "created_at"
    readonly_fields = tuple(f.name for f in LLMInteraction._meta.fields)

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False
