"""Config Django da fundação multi-tenant (ETAPA 0) — parte 1: base/env/installed apps."""

from __future__ import annotations

import os
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
    TELEGRAM_BOT_TOKEN=(str, ""),
    TELEGRAM_WEBHOOK_SECRET=(str, ""),
    TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET=(bool, False),
    OPENAI_API_KEY=(str, ""),
    OPENAI_TIMEOUT_SECONDS=(float, 30.0),
    OPENAI_MAX_CONNECTIONS=(int, 20),
    OPENAI_MAX_KEEPALIVE_CONNECTIONS=(int, 10),
    OPENAI_BREAKER_FAIL_MAX=(int, 5),
    OPENAI_BREAKER_RESET_TIMEOUT=(int, 30),
    LLM_CACHE_TTL_SECONDS=(int, 3600),
)

environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-etapa0-dev-only")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# Credenciais de integração (nunca no código; vazio por padrão em dev).
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
# Segredo global: NÃO autoriza um tenant por si só. Só é aceito como fallback se
# TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET=True (desligado por padrão → fail-closed).
TELEGRAM_WEBHOOK_SECRET = env("TELEGRAM_WEBHOOK_SECRET")
TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET = env("TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET")


def _tenant_webhook_secrets() -> dict[str, str]:
    """Segredos de webhook por tenant: ``TELEGRAM_WEBHOOK_SECRET_<SCHEMA>``.

    Vincula o segredo ao schema do tenant (ex.: ``TELEGRAM_WEBHOOK_SECRET_CLINICA_A``
    → ``clinica_a``), impedindo que um segredo compartilhado escreva em outro
    tenant via header ``x-tenant-id``.
    """
    prefix = "TELEGRAM_WEBHOOK_SECRET_"
    return {
        key[len(prefix) :].lower(): value
        for key, value in os.environ.items()
        if key.startswith(prefix) and len(key) > len(prefix) and value
    }


TELEGRAM_WEBHOOK_SECRETS = _tenant_webhook_secrets()

# OpenAI / LLM (ETAPA 4) — segredos só via ambiente; vazio desativa chamadas.
OPENAI_API_KEY = env("OPENAI_API_KEY")
OPENAI_TIMEOUT_SECONDS = env("OPENAI_TIMEOUT_SECONDS")
OPENAI_MAX_CONNECTIONS = env("OPENAI_MAX_CONNECTIONS")
OPENAI_MAX_KEEPALIVE_CONNECTIONS = env("OPENAI_MAX_KEEPALIVE_CONNECTIONS")
OPENAI_BREAKER_FAIL_MAX = env("OPENAI_BREAKER_FAIL_MAX")
OPENAI_BREAKER_RESET_TIMEOUT = env("OPENAI_BREAKER_RESET_TIMEOUT")
LLM_CACHE_TTL_SECONDS = env("LLM_CACHE_TTL_SECONDS")

if not DEBUG and SECRET_KEY.startswith("django-insecure-"):
    raise RuntimeError("DJANGO_SECRET_KEY real é obrigatório quando DEBUG=False.")

SHARED_APPS = [
    "django_tenants",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.tenants",
]

# admin e token_blacklist ficam em TENANT_APPS (não em SHARED): ambos criam FK
# para o AUTH_USER_MODEL (accounts.User), que é tenant-specific. Se ficassem em
# SHARED_APPS, o migrate_schemas tentaria criar essas FKs no schema public onde
# a tabela accounts_user não existe — quebrando a migração do zero. O admin do
# Django passa a ser por-tenant (cada tenant vê só os seus dados), e a token
# blacklist referencia usuários do próprio schema.
TENANT_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework",
    "django_filters",
    "corsheaders",
    "guardian",
    "simple_history",
    "drf_spectacular",
    "apps.accounts",
    "apps.common",
    "apps.crm",
    "apps.scheduling",
    "apps.omnichannel",
    "apps.ai",
    "apps.settings",
]

# contenttypes aparece em SHARED_APPS e TENANT_APPS (padrão exigido pelo
# django-tenants). Deduplicar preservando a ordem para evitar o erro do Django
# "Application labels aren't unique, duplicates: contenttypes".
INSTALLED_APPS = list(dict.fromkeys(SHARED_APPS + TENANT_APPS))

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
