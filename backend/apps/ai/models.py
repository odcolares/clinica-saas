"""Modelos do app ``ai`` (ETAPA 4).

- ``PromptTemplate``: prompt versionado e parametrizável (render seguro).
- ``LLMInteraction``: trilha de auditoria de cada chamada ao LLM.

Multi-tenancy (DATABASE.md / django-tenants): o app vive em ``TENANT_APPS`` —
cada schema de tenant tem suas próprias tabelas. Como defesa extra, toda leitura
de ``LLMInteraction`` passa por ``LLMInteractionManager``, que injeta o tenant
ativo (``connection.tenant``) e nunca devolve linhas de outro schema. Segredos
(``OPENAI_API_KEY``) só vêm do ambiente — nunca são persistidos aqui.
"""

from __future__ import annotations

import uuid
from typing import Any

from django.core.exceptions import ValidationError
from django.db import connection, models

from apps.crm.models import TimeStampedModel


class PromptTemplate(TimeStampedModel):
    """Prompt versionado, parametrizável e por tenant.

    ``content`` usa placeholders ``{chave}``; ``parameters`` guarda os valores
    padrão/esperados. ``render`` combina os dois e falha de forma explícita
    quando falta um parâmetro obrigatório.
    """

    DEFAULT_MODEL = "gpt-4o-mini"

    name = models.CharField(max_length=120, unique=True)
    content = models.TextField(
        help_text="Template com placeholders no formato {chave}."
    )
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    model_hint = models.CharField(max_length=64, default=DEFAULT_MODEL)
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Valores padrão dos placeholders (JSON objeto).",
    )

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(
                fields=["name", "is_active"], name="ai_prompt_name_active_idx"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"

    def render(self, **values: Any) -> str:
        """Renderiza o template aplicando ``parameters`` + ``values``.

        ``parameters`` funciona como valores padrão; ``values`` sobrescreve.
        Levanta ``ValidationError`` (400 na API) quando falta um placeholder.
        """
        context = {**(self.parameters or {}), **values}
        try:
            return self.content.format(**context)
        except KeyError as exc:
            missing = exc.args[0]
            raise ValidationError(
                {"parameters": f"Parâmetro obrigatório ausente: {missing}."}
            ) from exc
        except (IndexError, ValueError) as exc:
            raise ValidationError({"content": f"Template inválido: {exc}."}) from exc


def _current_tenant_id() -> int | None:
    """PK do tenant ativo (``None`` no schema public / sem tenant)."""
    return getattr(getattr(connection, "tenant", None), "pk", None)


class LLMInteractionQuerySet(models.QuerySet):
    """QuerySet sempre escopado ao tenant ativo."""

    def for_current_tenant(self) -> "LLMInteractionQuerySet":
        tenant_id = _current_tenant_id()
        if tenant_id is None:
            return self.none()
        return self.filter(tenant_id=tenant_id)


class LLMInteractionManager(models.Manager.from_queryset(LLMInteractionQuerySet)):
    """Manager que filtra por tenant ativo — nenhuma query cruza schemas.

    Sem tenant ativo (``public``) a leitura retorna vazio em vez de vazar todas
    as linhas. As migrations usam um manager histórico simples (não serializado).
    """

    use_in_migrations = False

    def get_queryset(self) -> LLMInteractionQuerySet:
        return super().get_queryset().for_current_tenant()


class LLMInteraction(models.Model):
    """Auditoria de uma chamada ao provedor de LLM (uso interno, imutável).

    ``tenant`` ancora a linha ao tenant; ``request_id`` correlaciona com o log
    estruturado. Tokens/custo são calculados por ``apps.ai.costs``.
    """

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.DO_NOTHING,
        related_name="llm_interactions",
        db_constraint=False,
        help_text=(
            "Tenant dono da interação. Sem cascade no ORM: o schema do tenant "
            "é removido com ele; db_constraint=False evita FK cross-schema."
        ),
    )
    request_id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
    model = models.CharField(max_length=64)
    provider = models.CharField(max_length=32, default="openai")
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=12, decimal_places=8, default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    prompt = models.JSONField(
        default=list, blank=True, help_text="Mensagens enviadas ao modelo."
    )
    response = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = LLMInteractionManager()

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=["tenant", "created_at"], name="ai_llm_tenant_created_idx"
            ),
            models.Index(fields=["model"], name="ai_llm_model_idx"),
            models.Index(fields=["provider"], name="ai_llm_provider_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.model} {self.request_id}"
