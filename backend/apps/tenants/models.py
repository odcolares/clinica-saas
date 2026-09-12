"""Tenant + Domain no schema public (django-tenants)."""

from __future__ import annotations

from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Tenant(TenantMixin):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=63, unique=True)
    plan = models.CharField(max_length=32, default="starter")
    status = models.CharField(max_length=16, default="active")
    auto_create_schema = True

    def __str__(self) -> str:
        return f"{self.name} ({self.schema_name})"


class Domain(DomainMixin):
    pass
