"""Middleware: x-tenant-id é hint; autoridade é o JWT (claim tenant)."""

from __future__ import annotations

from django.http import JsonResponse


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        header_tenant = request.headers.get("X-Tenant-Id") or request.headers.get(
            "X-Tenant-ID"
        )
        if not header_tenant:
            return self.get_response(request)
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return self.get_response(
                request
            )  # login usa header como roteamento; sem auth não valida
        token_tenant = None
        try:
            token = getattr(request, "auth", None)
            if token is not None:
                token_tenant = token.get("tenant")
        except Exception:
            token_tenant = None
        if token_tenant and header_tenant != token_tenant:
            return JsonResponse(
                {"detail": "Tenant divergente da identidade."}, status=403
            )
        return self.get_response(request)
