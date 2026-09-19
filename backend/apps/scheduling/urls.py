"""Rotas da Agenda (ETAPA 2), montadas sob /api/v1/."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.scheduling.views import (
    AppointmentViewSet,
    AvailabilityView,
    ConfirmWebhookView,
    ProfessionalViewSet,
    ServiceViewSet,
)

router = DefaultRouter()
router.register("professionals", ProfessionalViewSet, basename="professional")
router.register("services", ServiceViewSet, basename="service")
router.register("appointments", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("availability/", AvailabilityView.as_view(), name="availability"),
    path(
        "appointments/confirm-webhook/",
        ConfirmWebhookView.as_view(),
        name="appointment-confirm-webhook",
    ),
    *router.urls,
]
