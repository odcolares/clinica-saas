"""User/Role/Permission por tenant (TENANT_APPS)."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords


class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name


class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.codename


class RolePermission(models.Model):
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="role_permissions"
    )
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="role_permissions"
    )

    class Meta:
        unique_together = ("role", "permission")


class User(AbstractUser):
    role = models.ForeignKey(
        Role, null=True, blank=True, on_delete=models.SET_NULL, related_name="users"
    )
    status = models.CharField(max_length=16, default="active")
    history = HistoricalRecords()

    class Meta:
        indexes = [models.Index(fields=["status"]), models.Index(fields=["email"])]
