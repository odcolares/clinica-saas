"""URLs raiz — ETAPA 0 (fundação)."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.common.urls")),
]
