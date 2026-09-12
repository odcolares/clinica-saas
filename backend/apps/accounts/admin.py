from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Permission, Role, RolePermission, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("codename", "description")
    search_fields = ("codename",)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission")
    list_filter = ("role",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "status", "is_active")
    list_filter = ("status", "role", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (("Tenant", {"fields": ("role", "status")}),)
