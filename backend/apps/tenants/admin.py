from django.contrib import admin

from .models import Domain, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "schema_name", "plan", "status")
    search_fields = ("name", "slug", "schema_name")
    list_filter = ("plan", "status")


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")
    search_fields = ("domain",)
