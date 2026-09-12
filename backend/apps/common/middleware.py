"""Middleware: x-tenant-id é hint; autoridade é o JWT (claim tenant).

- Para requests autenticadas (Authorization: Bearer <JWT>): o tenant é
  derivado do claim ``tenant`` do token. Header ``X-Tenant-Id`` divergente
  → 403.
- Para requests não autenticadas (login/signup/refresh): ``x-tenant-id``
  funciona como hint de roteamento para o schema do tenant. Não há
  validação de divergência porque não há identidade a validar.
- Sem JWT e sem header: permanece no schema public (health, signup sem
  tenant pré-existente).
"""

from __future__ import annotations

import jwt
from django.db import connection
from django.http import JsonResponse

from apps.tenants.models import Tenant


def _extract_tenant_from_jwt(auth_header: str) -> str | None:
    """Extrai o claim ``tenant`` de um JWT Bearer sem verificar assinatura.

    A verificação propriamente dita (e rejeição de tokens inválidos) é
    feita pelo ``JWTAuthentication`` do DRF no view. Aqui só precisamos
    saber **qual** schema ativar para que a autenticação rode contra o
    tenant correto.
    """
    if not auth_header.startswith("Bearer "):
        return None
    token_str = auth_header[7:]
    return _tenant_claim_of(token_str)


def _tenant_claim_of(token_str: str) -> str | None:
    """Decodifica um JWT e devolve o claim ``tenant`` (sem verificar assinatura)."""
    if not token_str:
        return None
    try:
        payload = jwt.decode(
            token_str,
            options={"verify_signature": False, "verify_exp": False},
        )
        return payload.get("tenant") or None
    except Exception:
        return None


def _extract_tenant_from_refresh_body(request) -> str | None:
    """Tenta obter o tenant a partir do refresh token no corpo JSON.

    Endpoints não autenticados como ``auth/refresh`` e ``auth/logout`` enviam
    o refresh token no corpo (não no header ``Authorization``). Como o refresh
    carrega o claim ``tenant`` (ver _issue_tokens), conseguimos ativar o schema
    correto sem depender do cliente mandar ``X-Tenant-Id``. Retorna ``None`` se
    o corpo não for JSON com ``refresh`` reconhecível.
    """
    if request.method not in ("POST", "PUT", "PATCH"):
        return None
    content_type = request.headers.get("Content-Type", "")
    if "json" not in content_type.lower():
        return None
    try:
        import json as _json

        payload = _json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return None
    refresh = payload.get("refresh")
    if not isinstance(refresh, str):
        return None
    return _tenant_claim_of(refresh)


def _resolve_and_set(schema_name: str | None) -> Tenant | None:
    """Resolve schema_name → Tenant (via schema public) e ativa no connection."""
    if not schema_name:
        return None
    try:
        tenant = Tenant.objects.using("default").get(schema_name=schema_name)
    except Tenant.DoesNotExist:
        return None
    connection.set_tenant(tenant)
    return tenant


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        header_tenant = request.headers.get("X-Tenant-Id") or request.headers.get(
            "X-Tenant-ID"
        )

        # 1. Tenta extrair tenant do JWT (claim "tenant")
        token_tenant = _extract_tenant_from_jwt(
            request.headers.get("Authorization", "")
        )

        if token_tenant:
            # --- Request autenticado: JWT é autoridade ---
            tenant = _resolve_and_set(token_tenant)
            if tenant is None:
                return JsonResponse(
                    {"detail": "Tenant não encontrado na identidade."}, status=403
                )
            # Valida header divergence (hint vs identidade)
            if header_tenant and header_tenant != token_tenant:
                return JsonResponse(
                    {"detail": "Tenant divergente da identidade."}, status=403
                )
        elif header_tenant:
            # --- Request não autenticado: x-tenant-id como hint de roteamento ---
            # Usado por login/signup/refresh para selecionar o schema do tenant.
            # Se o tenant indicado não existir, responder 404 em vez de continuar
            # no schema public: requests como login tentariam consultar as tabelas
            # do tenant (ex.: accounts_user) no schema public, onde não existem,
            # resultando em 500. (Signup não envia header — provisiona em public.)
            if _resolve_and_set(header_tenant) is None:
                return JsonResponse({"detail": "Tenant não encontrado."}, status=404)
        else:
            # --- Request não autenticado sem header: tenta inferir pelo refresh
            # token do corpo (ex.: auth/refresh, auth/logout). O claim "tenant"
            # foi gravado no token em _issue_tokens. ---
            refresh_tenant = _extract_tenant_from_refresh_body(request)
            _resolve_and_set(refresh_tenant)

        return self.get_response(request)
