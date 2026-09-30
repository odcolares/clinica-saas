"""Helpers de verificação para os testes do app ``ai``.

Evitam ``assert`` (bandit B101) porque os testes vivem sob ``backend/apps/``,
diretório varrido pelo bandit no CI (``bandit -r backend/apps``).
"""

from __future__ import annotations

from typing import Any


def check(condition: Any, message: str = "") -> None:
    if not condition:
        raise AssertionError(message or "verificação falhou")


def check_equal(actual: Any, expected: Any) -> None:
    check(actual == expected, f"esperado {expected!r}, obtido {actual!r}")
