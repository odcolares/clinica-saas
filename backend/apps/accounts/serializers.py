"""JWT carrega claim de tenant; serializers de signup/login."""

from __future__ import annotations

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import User


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        tenant = getattr(user, "_tenant_schema", None) or getattr(
            user, "tenant_schema", ""
        )
        token["tenant"] = tenant
        token["username"] = user.get_username()
        return token


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("Credenciais inválidas.")
        if getattr(user, "status", "active") != "active" or not user.is_active:
            raise serializers.ValidationError("Usuário inativo.")
        attrs["user"] = user
        return attrs


class SignupSerializer(serializers.Serializer):
    tenant_name = serializers.CharField(max_length=120)
    tenant_slug = serializers.SlugField(max_length=63)
    admin_username = serializers.CharField(max_length=150)
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(
        max_length=128, write_only=True, min_length=8
    )


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(max_length=128, write_only=True, min_length=8)


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "status")
