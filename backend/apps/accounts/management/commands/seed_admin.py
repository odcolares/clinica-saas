"""Provisiona o usuário admin padrão de um tenant (e o tenant, se preciso)."""

from __future__ import annotations

import os
import secrets

import structlog
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from apps.accounts.models import Role, User
from apps.tenants.models import Domain, Tenant

logger = structlog.get_logger(__name__)

DEFAULT_ROLES = ("admin", "manager", "attendant")
MIN_PASSWORD_LENGTH = 8


class Command(BaseCommand):
    help = "Cria/atualiza o admin padrão de um tenant; opcionalmente cria o tenant."

    def add_arguments(self, parser):
        parser.add_argument("--tenant", required=True, help="schema_name do tenant")
        parser.add_argument("--tenant-name", default=None, help="nome do tenant")
        parser.add_argument(
            "--create-tenant",
            action="store_true",
            help="Cria o tenant (schema + domínio) se ele não existir.",
        )
        parser.add_argument("--domain", default=None, help="domínio primário do tenant")
        parser.add_argument("--username", default="admin")
        parser.add_argument("--email", default="admin@clinica.com")
        parser.add_argument(
            "--password",
            default=None,
            help="Senha do admin. Evite: vaza no histórico do shell. Prefira "
            "SEED_ADMIN_PASSWORD ou --generate-password.",
        )
        parser.add_argument(
            "--generate-password",
            action="store_true",
            help="Gera uma senha forte e a imprime ao final.",
        )
        parser.add_argument(
            "--force-password",
            action="store_true",
            help="Se o usuário já existir, redefine a senha.",
        )

    def handle(self, *args, **options):
        password, generated = self._resolve_password(options)
        tenant = self._get_or_create_tenant(options)

        try:
            connection.set_tenant(tenant)
            admin_role = self._ensure_roles()["admin"]
            _, created = self._upsert_admin(options, admin_role, password)
        finally:
            connection.set_schema_to_public()

        state = "criado" if created else "existente"
        logger.info(
            "seed_admin_ok",
            tenant=tenant.schema_name,
            username=options["username"],
            created=created,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Admin '{options['username']}' pronto no tenant "
                f"'{tenant.schema_name}' ({state})."
            )
        )
        if generated:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Senha gerada (guarde agora):"))
            self.stdout.write(f"  usuário: {options['username']}")
            self.stdout.write(f"  senha:   {password}")

    def _resolve_password(self, options) -> tuple[str, bool]:
        if options["generate_password"]:
            return secrets.token_urlsafe(18), True
        password = options["password"] or os.environ.get("SEED_ADMIN_PASSWORD")
        if not password:
            raise CommandError(
                "Senha obrigatória: use --generate-password, --password ou "
                "SEED_ADMIN_PASSWORD."
            )
        if len(password) < MIN_PASSWORD_LENGTH:
            raise CommandError(
                f"Senha deve ter ao menos {MIN_PASSWORD_LENGTH} caracteres."
            )
        return password, False

    def _get_or_create_tenant(self, options) -> Tenant:
        schema_name = options["tenant"]
        tenant = Tenant.objects.using("default").filter(schema_name=schema_name).first()
        if tenant is not None:
            return tenant
        if not options["create_tenant"]:
            raise CommandError(
                f"Tenant '{schema_name}' não existe. Use --create-tenant para criá-lo."
            )

        name = options["tenant_name"] or schema_name.replace("_", " ").title()
        tenant = Tenant(schema_name=schema_name, name=name)
        tenant.slug = schema_name.replace("_", "-")
        tenant.save()
        Domain.objects.get_or_create(
            domain=options["domain"] or f"{tenant.slug}.localhost",
            tenant=tenant,
            defaults={"is_primary": True},
        )
        logger.info("tenant_created", tenant=schema_name)
        self.stdout.write(f"Tenant '{schema_name}' criado.")
        return tenant

    def _ensure_roles(self) -> dict[str, Role]:
        roles = {}
        for name in DEFAULT_ROLES:
            role, _ = Role.objects.get_or_create(
                name=name, defaults={"description": f"Papel {name}"}
            )
            roles[name] = role
        return roles

    def _upsert_admin(self, options, admin_role, password) -> tuple[User, bool]:
        username = options["username"]
        defaults = {
            "email": options["email"],
            "role": admin_role,
            "status": "active",
            "is_active": True,
            "is_staff": True,
        }

        existing = User.objects.filter(username=username).first()
        if existing is None:
            user = User.objects.create_user(
                username=username, password=password, **defaults
            )
            return user, True

        for field, value in defaults.items():
            setattr(existing, field, value)
        update_fields = list(defaults)
        if options["force_password"]:
            existing.set_password(password)
            update_fields.append("password")
        existing.save(update_fields=update_fields)
        return existing, False
