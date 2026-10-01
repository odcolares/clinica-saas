"""Config do app ``ai`` (ETAPA 4).

Registrado em ``TENANT_APPS``: prompts e auditoria vivem no schema do tenant.
"""

from __future__ import annotations

from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai"
    verbose_name = "IA / LLM"
