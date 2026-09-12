"""Settings raiz: reexporta base + middleware (ponto de entrada DJANGO_SETTINGS_MODULE)."""

from .settings_base import *  # noqa: F401,F403
from .settings_middleware import *  # noqa: F401,F403
