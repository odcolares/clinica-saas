"""Handler de exceções: envelope de erro padronizado da fundação."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class Conflict(APIException):
    """409 — recurso em estado conflitante com a operação (ex.: já convertido)."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflito de estado do recurso."
    default_code = "conflict"


def tenant_aware_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    detail = response.data
    if isinstance(detail, dict) and set(detail.keys()) == {"detail"}:
        return response
    response.data = {"detail": detail}
    return response
