"""Views de auth multi-tenant (ETAPA 0)."""

from __future__ import annotations

import structlog
from django.contrib.auth import get_user_model
from django.db import connection
from django.utils.text import slugify
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from apps.accounts.models import Role
from apps.accounts.serializers import LoginSerializer, SignupSerializer, UserSerializer
from apps.tenants.models import Tenant

logger = structlog.get_logger(__name__)
User = get_user_model()


def _issue_tokens(user, tenant_schema: str) -> dict:
    user._tenant_schema = tenant_schema
    refresh = RefreshToken.for_user(user)
    refresh["tenant"] = tenant_schema
    access = refresh.access_token
    access["tenant"] = tenant_schema
    return {"refresh": str(refresh), "access": str(access)}


def _ensure_default_roles():
    for name in ("admin", "manager", "attendant"):
        Role.objects.get_or_create(name=name, defaults={"description": f"Papel {name}"})


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "signup"

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        schema = slugify(data["tenant_slug"]).replace("-", "_")

        if Tenant.objects.filter(schema_name=schema).exists():
            return Response(
                {"detail": "Tenant já existe."}, status=status.HTTP_409_CONFLICT
            )

        tenant = Tenant(schema_name=schema, name=data["tenant_name"])
        tenant.slug = data["tenant_slug"]
        try:
            # save() cria o schema do tenant (auto_create_schema=True)
            tenant.save()
        except Exception:
            logger.warning("tenant_signup_schema_failed", tenant=schema)
            return Response(
                {"detail": "Não foi possível provisionar o tenant."},
                status=status.HTTP_409_CONFLICT,
            )

        # Troca para o schema novo e cria o admin dentro dele
        try:
            connection.set_tenant(tenant)
            _ensure_default_roles()
            admin_role = Role.objects.get(name="admin")
            admin = User.objects.create_user(
                username=data["admin_username"],
                email=data["admin_email"],
                password=data["admin_password"],
                role=admin_role,
                status="active",
            )
        except Exception:
            logger.warning("tenant_signup_admin_failed", tenant=schema)
            # Compensação documentada: schema órfão fica auditável via lista de
            # tenants; a falha é 409 para permitir retry idempotente do signup.
            return Response(
                {"detail": "Não foi possível provisionar o admin do tenant."},
                status=status.HTTP_409_CONFLICT,
            )
        tokens = _issue_tokens(admin, schema)
        logger.info("tenant_signup", tenant=schema)
        payload = {"tenant": schema, "user": UserSerializer(admin).data, **tokens}
        return Response(payload, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tenant = getattr(connection, "tenant", None)
        schema = tenant.schema_name if tenant else "public"
        tokens = _issue_tokens(user, schema)
        logger.info("login_ok", tenant=schema)
        return Response({"tenant": schema, "user": UserSerializer(user).data, **tokens})


class LogoutView(TokenBlacklistView):
    throttle_scope = "login"


class MeView(APIView):
    def get(self, request):
        tenant = getattr(connection, "tenant", None)
        schema = tenant.schema_name if tenant else "public"
        return Response({"tenant": schema, "user": UserSerializer(request.user).data})


__all__ = ["LoginView", "LogoutView", "MeView", "SignupView", "TenantTokenRefreshView"]


class TenantTokenRefreshView(TokenRefreshView):
    throttle_scope = "login"
