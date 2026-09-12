"""Rotas da fundação (ETAPA 0): health + auth multi-tenant."""

from django.http import JsonResponse
from django.urls import path

from apps.accounts.views import (
    LoginView,
    LogoutView,
    MeView,
    SignupView,
    TenantTokenRefreshView,
)


def health(request):
    return JsonResponse({"status": "ok", "etapa": 0})


urlpatterns = [
    path("health/", health, name="health"),
    path("tenants/signup/", SignupView.as_view(), name="tenant-signup"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TenantTokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
]
