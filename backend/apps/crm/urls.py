"""Rotas do CRM (ETAPA 1), montadas sob /api/v1/."""

from rest_framework.routers import DefaultRouter

from apps.crm.views import (
    CustomerTagViewSet,
    CustomerViewSet,
    LeadSourceViewSet,
    LeadStatusViewSet,
    LeadViewSet,
)

router = DefaultRouter()
router.register("leads", LeadViewSet, basename="lead")
router.register("customers", CustomerViewSet, basename="customer")
router.register("tags", CustomerTagViewSet, basename="tag")
router.register("lead-sources", LeadSourceViewSet, basename="lead-source")
router.register("lead-statuses", LeadStatusViewSet, basename="lead-status")

urlpatterns = router.urls
