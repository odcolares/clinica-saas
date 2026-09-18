"""RBAC do CRM: escopo por objeto via django-guardian dentro do tenant.

O isolamento entre tenants é garantido pelo django-tenants (schema). Aqui
tratamos o escopo *dentro* do tenant: papéis administrativos (admin/manager)
enxergam todo o tenant; os demais só enxergam objetos sobre os quais receberam
permissão (criador ou responsável atribuído).

Regra (ETAPAS.md §Regras): backend é a autoridade; RBAC rigoroso, por objeto.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from guardian.shortcuts import assign_perm, get_objects_for_user
from rest_framework.permissions import BasePermission

User = get_user_model()

OBJECT_PERMS = ("view", "change", "delete")
MEMBER_PERMS = ("view", "change")
MANAGER_ROLES = frozenset({"admin", "manager"})


def is_manager(user) -> bool:
    """Papel administrativo do tenant (ou superuser) enxerga tudo no schema."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = getattr(user, "role", None)
    return bool(role and role.name in MANAGER_ROLES)


def grant_object_perms(user, obj, actions: tuple[str, ...] = OBJECT_PERMS) -> None:
    """Concede permissões de objeto ao usuário (criador/responsável)."""
    if not user or not user.is_authenticated:
        return
    model_name = obj._meta.model_name
    for action in actions:
        assign_perm(f"{action}_{model_name}", user, obj)


def grant_member_perms(user, obj) -> None:
    """Concede apenas leitura/edição (sem exclusão) — usado no responsável."""
    grant_object_perms(user, obj, MEMBER_PERMS)


def visible_queryset(user, model, base):
    """Restringe o queryset ao que o usuário pode ver dentro do tenant.

    Managers veem tudo; demais veem objetos com permissão de view/change.
    """
    if is_manager(user):
        return base
    ids = get_objects_for_user(
        user,
        [f"{action}_{model._meta.model_name}" for action in MEMBER_PERMS],
        klass=model,
        any_perm=True,
        accept_global_perms=False,
    ).values_list("pk", flat=True)
    return base.filter(pk__in=ids)


class CrmObjectPermission(BasePermission):
    """Autoriza ações por objeto; managers têm passe livre no tenant."""

    ACTION_PERM = {
        "GET": "view",
        "HEAD": "view",
        "OPTIONS": "view",
        "PUT": "change",
        "PATCH": "change",
        "POST": "change",
        "DELETE": "delete",
    }

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if is_manager(user):
            return True
        action = self.ACTION_PERM.get(request.method, "view")
        codename = f"{action}_{obj._meta.model_name}"
        return user.has_perm(codename, obj)
