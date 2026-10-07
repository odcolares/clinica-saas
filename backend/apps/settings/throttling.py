"""Throttle por plano do tenant (Etapa 5).

Lê ``connection.tenant.plan`` (django-tenants). Sem tenant (public/health)
cai no default starter. Env override: ``THROTTLE_PLAN_STARTER`` etc.
"""

from __future__ import annotations

import os

from django.db import connection
from rest_framework.throttling import SimpleRateThrottle


PLAN_RATES = {
    "starter": os.getenv("THROTTLE_PLAN_STARTER", "60/min"),
    "pro": os.getenv("THROTTLE_PLAN_PRO", "300/min"),
    "enterprise": os.getenv("THROTTLE_PLAN_ENTERPRISE", "1000/min"),
}


class PlanRateThrottle(SimpleRateThrottle):
    scope = "plan"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}

    def get_rate(self):
        plan = "starter"
        tenant = getattr(connection, "tenant", None)
        candidate = getattr(tenant, "plan", None)
        if isinstance(candidate, str) and candidate in PLAN_RATES:
            plan = candidate
        return PLAN_RATES[plan]
