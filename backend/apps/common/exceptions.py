"""Handler de exceções: envelope de erro padronizado da fundação."""

from __future__ import annotations

from rest_framework.views import exception_handler


def tenant_aware_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    detail = response.data
    if isinstance(detail, dict) and set(detail.keys()) == {"detail"}:
        return response
    response.data = {"detail": detail}
    return response
