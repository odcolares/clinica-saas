from django.contrib import admin

from .models import (
    Customer,
    CustomerAddress,
    CustomerContact,
    CustomerNote,
    CustomerTag,
    Interaction,
    Lead,
    LeadSource,
    LeadStatus,
)


@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(LeadStatus)
class LeadStatusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "order", "is_terminal")
    ordering = ("order",)


@admin.register(CustomerTag)
class CustomerTagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class CustomerContactInline(admin.TabularInline):
    model = CustomerContact
    extra = 0


class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "status", "assigned_to")
    search_fields = ("name", "email", "phone", "document")
    list_filter = ("status", "tags")
    inlines = (CustomerContactInline, CustomerAddressInline)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "status", "assigned_to", "converted_at")
    search_fields = ("name", "email", "phone", "document")
    list_filter = ("status", "source")


@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ("customer", "author", "created_at")
    search_fields = ("body",)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("kind", "customer", "lead", "author", "created_at")
    list_filter = ("kind",)
