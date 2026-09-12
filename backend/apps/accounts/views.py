"""Views de auth multi-tenant (ETAPA 0)."""

from __future__ import annotations

import structlog
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import connection
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.text import slugify
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from apps.accounts.models import Role
from apps.accounts.serializers import (
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    SignupSerializer,
    UserSerializer,
)
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
        # Signup sempre opera no schema public. Como um request anterior pode
        # ter deixado a conexão no schema de um tenant (ex.: set_tenant no final
        # de signups/login anteriores, num worker/thread único), resetamos para
        # public de forma idempotente antes de provisionar.
        connection.set_schema_to_public()
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
        except Exception as exc:
            logger.warning("tenant_signup_schema_failed", tenant=schema, error=str(exc))
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
            # Emitir tokens ainda dentro do schema do tenant: o blacklist do
            # simplejwt (BLACKLIST_AFTER_ROTATION) grava em
            # token_blacklist_outstandingtoken, que só existe no schema do
            # tenant (TENANT_APPS).
            tokens = _issue_tokens(admin, schema)
        except Exception as exc:
            logger.warning("tenant_signup_admin_failed", tenant=schema, error=str(exc))
            # Compensação documentada: schema órfão fica auditável via lista de
            # tenants; a falha é 409 para permitir retry idempotente do signup.
            return Response(
                {"detail": "Não foi possível provisionar o admin do tenant."},
                status=status.HTTP_409_CONFLICT,
            )
        finally:
            # Não vazar o schema do tenant para requests seguintes na mesma
            # conexão (worker/thread único). Operations de signup pertencem ao
            # public; o próximo request voltará a selecionar seu schema via JWT
            # ou header.
            connection.set_schema_to_public()
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


_password_reset_token_generator = PasswordResetTokenGenerator()


class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        tenant = getattr(connection, "tenant", None)
        schema = tenant.schema_name if tenant else "public"

        user = User.objects.filter(email=email).first()

        logger.info("password_reset_requested", tenant=schema)
        response = {
            "detail": "Se o e-mail estiver cadastrado, você receberá instruções para redefinir sua senha."
        }
        if settings.DEBUG and user is not None:
            response["uid"] = urlsafe_base64_encode(force_bytes(user.pk))
            response["token"] = _password_reset_token_generator.make_token(user)
        return Response(response, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        tenant = getattr(connection, "tenant", None)
        schema = tenant.schema_name if tenant else "public"

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            if _password_reset_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                logger.info("password_reset_confirmed", tenant=schema)
            else:
                logger.info("password_reset_invalid_token", tenant=schema)
        except (User.DoesNotExist, ValueError, TypeError):
            logger.info("password_reset_invalid_token", tenant=schema)

        return Response(
            {"detail": "Senha redefinida com sucesso."},
            status=status.HTTP_200_OK,
        )


__all__ = [
    "LoginView",
    "LogoutView",
    "MeView",
    "PasswordResetConfirmView",
    "PasswordResetView",
    "SignupView",
    "TenantTokenRefreshView",
]


class TenantTokenRefreshView(TokenRefreshView):
    throttle_scope = "login"
