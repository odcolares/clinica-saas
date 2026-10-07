"""Configurações do tenant (ETAPA 5, fundação).

Todos vivem no schema do tenant (TENANT_APPS). Isolamento via
django-tenants; visibilidade por objeto via guardian (ver
apps.crm.permissions). Segredos (ApiKey plain, webhook secret,
IntegrationConfig.config) nunca são logados.
"""

from __future__ import annotations

import hashlib
import secrets

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from apps.crm.models import TimeStampedModel


class TenantSettings(TimeStampedModel):
    """Singleton por schema: horários + branding do tenant."""

    business_start = models.TimeField(default="08:00")
    business_end = models.TimeField(default="18:00")
    timezone = models.CharField(max_length=64, default="America/Sao_Paulo")
    logo_url = models.URLField(blank=True, default="")
    primary_color = models.CharField(max_length=7, default="#0F766E")
    brand_name = models.CharField(max_length=120, blank=True, default="")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "configuração do tenant"
        verbose_name_plural = "configurações do tenant"

    def __str__(self) -> str:
        return f"TenantSettings({self.timezone} {self.business_start}-{self.business_end})"

    def clean(self) -> None:
        if self.business_start and self.business_end and self.business_end <= self.business_start:
            raise ValidationError({"business_end": "Encerramento deve ser após a abertura."})

    @classmethod
    def current(cls) -> TenantSettings:
        """Retorna o singleton, criando o default se ausente."""
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj


class IntegrationConfig(TimeStampedModel):
    """Integração externa por tenant (ex. google_calendar)."""

    class Provider(models.TextChoices):
        NOOP = "noop", "Nenhuma"
        GOOGLE_CALENDAR = "google_calendar", "Google Calendar"

    provider = models.CharField(max_length=32, choices=Provider.choices, default=Provider.NOOP)
    active = models.BooleanField(default=True)
    professional_email = models.EmailField(blank=True, default="")
    config = models.JSONField(default=dict, blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ("provider",)

    def __str__(self) -> str:
        return f"{self.provider} ({'on' if self.active else 'off'})"


class WebhookEndpoint(TimeStampedModel):
    """Webhook configurável do tenant (disparo entra em etapa posterior)."""

    name = models.CharField(max_length=120)
    url = models.URLField(max_length=500)
    events = models.JSONField(default=list, blank=True)
    secret = models.CharField(max_length=128, blank=True, default="")
    active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.events and not isinstance(self.events, list):
            raise ValidationError({"events": "events deve ser uma lista."})


class ApiKey(TimeStampedModel):
    """Chave de API por tenant. Só o hash é persistido."""

    name = models.CharField(max_length=120)
    prefix = models.CharField(max_length=16, unique=True)
    key_hash = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} ({self.prefix}…)"

    @classmethod
    def issue(cls, *, name: str) -> tuple[ApiKey, str]:
        """Gera par (obj, plain_key). plain_key exibido uma única vez."""
        prefix = secrets.token_hex(4)
        raw = secrets.token_urlsafe(32)
        plain = f"sk_{prefix}_{raw}"
        digest = hashlib.sha256(plain.encode()).hexdigest()
        obj = cls.objects.create(name=name, prefix=prefix, key_hash=digest)
        return obj, plain

    def mark_used(self) -> None:
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])
