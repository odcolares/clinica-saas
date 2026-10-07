from django.contrib import admin

from .models import Appointment, Professional, Service


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "active", "commission_type", "user")
    search_fields = ("name", "email", "specialties")
    list_filter = ("active", "commission_type")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_minutes", "price", "active")
    search_fields = ("name", "description")
    list_filter = ("active",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("customer", "professional", "service", "start", "status")
    search_fields = ("notes",)
    list_filter = ("status", "professional", "service")
