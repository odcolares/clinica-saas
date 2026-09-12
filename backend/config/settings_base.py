"""Config Django da fundação multi-tenant (ETAPA 0) — parte 1: base/env/installed apps."""

from __future__ import annotations

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, True),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    DATABASE_URL=(str, "postgres://clinica:clinica_dev_only@127.0.0.1:5432/clinica"),
    REDIS_URL=(str, "redis://127.0.0.1:6379/0"),
    JWT_ACCESS_MINUTES=(int, 15),
    JWT_REFRESH_DAYS=(int, 7),
    SENTRY_DSN=(str, ""),
    SENTRY_ENVIRONMENT=(str, "development"),
    SENTRY_RELEASE=(str, "etapa-0"),
)

environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-etapa0-dev-only")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

if not DEBUG and SECRET_KEY.startswith("django-insecure-"):
    raise RuntimeError("DJANGO_SECRET_KEY real é obrigatório quando DEBUG=False.")

SHARED_APPS = [
    "django_tenants",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "apps.tenants",
]

TENANT_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "guardian",
    "simple_history",
    "apps.accounts",
    "apps.common",
]

INSTALLED_APPS = list(SHARED_APPS) + [
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "corsheaders",
    "guardian",
    "simple_history",
    "drf_spectacular",
    "apps.accounts",
    "apps.common",
]

TENANT_MODEL = "tenants.Tenant"
TENANT_DOMAIN_MODEL = "tenants.Domain"
AUTH_USER_MODEL = "accounts.User"

DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ENGINE"] = "django_tenants.postgresql_backend"
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}
