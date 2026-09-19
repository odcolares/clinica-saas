"""Calendar adapter (ETAPA 2, regra 5 de ETAPAS.md).

Abstração para integração com calendários externos. O padrão é o
``NoopCalendarAdapter`` (apenas loga). O ``GoogleCalendarAdapter`` é um stub
que lê credenciais de variáveis de ambiente — nunca hardcode — e implementa
idempotência via ``external_event_id``.

Não adiciona dependências ao requirements.txt: usa apenas stdlib + Django +
structlog já instalados.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import structlog
from rest_framework.exceptions import ValidationError

logger = structlog.get_logger(__name__)


class CalendarAdapter(ABC):
    """Interface abstrata para integração com calendários externos."""

    @abstractmethod
    def create_event(
        self,
        *,
        external_id: str,
        professional_email: str,
        summary: str,
        start: datetime,
        end: datetime,
        description: str = "",
    ) -> str:
        """Cria um evento e retorna o ID externo atribuído."""

    @abstractmethod
    def update_event(
        self,
        *,
        external_id: str,
        summary: str,
        start: datetime,
        end: datetime,
        description: str = "",
    ) -> str:
        """Atualiza um evento existente e retorna o ID externo."""

    @abstractmethod
    def delete_event(self, external_id: str) -> None:
        """Remove um evento pelo ID externo."""

    @abstractmethod
    def list_busy(
        self,
        *,
        professional_email: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        """Lista blocos de horário ocupado no intervalo [start, end)."""


class NoopCalendarAdapter(CalendarAdapter):
    """Adapter padrão: apenas loga, não sincroniza com nada."""

    def create_event(self, **kwargs: Any) -> str:
        logger.info("calendar_noop_create", **kwargs)
        return kwargs.get("external_id", "")

    def update_event(self, **kwargs: Any) -> str:
        logger.info("calendar_noop_update", **kwargs)
        return kwargs.get("external_id", "")

    def delete_event(self, external_id: str) -> None:
        logger.info("calendar_noop_delete", external_id=external_id)

    def list_busy(self, **kwargs: Any) -> list[dict[str, Any]]:
        logger.info("calendar_noop_list_busy", **kwargs)
        return []


class GoogleCalendarAdapter(CalendarAdapter):
    """Stub de integração com Google Calendar.

    Credenciais são lidas de ``GOOGLE_CALENDAR_CREDENTIALS`` (JSON em env) e
    nunca hardcode. A idempotência é garantida por ``external_event_id``: se
    o evento já existe, faz update em vez de criar outro.
    """

    def __init__(self) -> None:
        creds_json = os.environ.get("GOOGLE_CALENDAR_CREDENTIALS", "")
        if not creds_json:
            logger.warning("google_calendar_credentials_missing")
        try:
            self._credentials = json.loads(creds_json) if creds_json else {}
        except json.JSONDecodeError:
            logger.error("google_calendar_credentials_invalid_json")
            self._credentials = {}

    def _ensure_credentials(self) -> None:
        if not self._credentials:
            raise ValidationError(
                "Credenciais do Google Calendar não configuradas.",
                code="google_calendar_unavailable",
            )

    def create_event(self, **kwargs: Any) -> str:
        self._ensure_credentials()
        external_id = kwargs.get("external_id", "")
        # Idempotência: se já temos external_event_id, faz update
        if external_id:
            return self.update_event(**kwargs)
        logger.info("google_calendar_create", **kwargs)
        # Stub: em produção, chamar a API do Google Calendar aqui
        return external_id

    def update_event(self, **kwargs: Any) -> str:
        self._ensure_credentials()
        external_id = kwargs.get("external_id", "")
        logger.info("google_calendar_update", external_id=external_id, **kwargs)
        # Stub: em produção, chamar a API do Google Calendar aqui
        return external_id

    def delete_event(self, external_id: str) -> None:
        self._ensure_credentials()
        logger.info("google_calendar_delete", external_id=external_id)
        # Stub: em produção, chamar a API do Google Calendar aqui

    def list_busy(self, **kwargs: Any) -> list[dict[str, Any]]:
        self._ensure_credentials()
        logger.info("google_calendar_list_busy", **kwargs)
        # Stub: em produção, chamar a API do Google Calendar aqui
        return []
