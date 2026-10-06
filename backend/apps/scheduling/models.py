"""Agenda (ETAPA 2) — profissionais, serviços e agendamentos.

Modelos conforme `Projeto_SaaS/architecture/API.md` §Scheduling e
`Projeto_SaaS/docs/PRODUCT-CONCEPT.md` §13. Todos operam dentro do schema do
tenant; o isolamento é garantido pelo django-tenants e o escopo de visibilidade
por objeto pelo django-guardian (ver apps.crm.permissions).
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeBoundary, RangeOperators
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Func, Q
from simple_history.models import HistoricalRecords

from apps.crm.models import TimeStampedModel


class TsTzRange(Func):
    """Mapeia (start, end) em tstzrange [start, end) para a constraint de exclusão."""

    function = "TSTZRANGE"
    output_field = DateTimeRangeField()


class Professional(TimeStampedModel):
    """Profissional que executa serviços na agenda."""

    class CommissionType(models.TextChoices):
        NONE = "none", "Sem comissão"
        PERCENT = "percent", "Percentual"
        FIXED = "fixed", "Valor fixo"

    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    specialties = models.TextField(
        blank=True,
        help_text="Lista de especialidades separadas por vírgula.",
    )
    active = models.BooleanField(default=True)
    commission_type = models.CharField(
        max_length=16,
        choices=CommissionType.choices,
        default=CommissionType.NONE,
    )
    commission_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    commission_fixed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="scheduling_professionals",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=["active"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def specialty_list(self) -> list[str]:
        """Retorna as especialidades como lista (split por vírgula)."""
        if not self.specialties:
            return []
        return [s.strip() for s in self.specialties.split(",") if s.strip()]


class Service(TimeStampedModel):
    """Serviço oferecido com duração e preço."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Duração mínima em minutos.",
        validators=[MinValueValidator(5)],
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=["active"]),
            models.Index(fields=["price"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="service_duration_min_5",
                condition=models.Q(duration_minutes__gte=5),
                violation_error_message="A duração mínima do serviço é de 5 minutos.",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Appointment(TimeStampedModel):
    """Agendamento de um serviço para um profissional e cliente."""

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Agendado"
        CONFIRMED = "CONFIRMED", "Confirmado"
        CANCELLED = "CANCELLED", "Cancelado"
        COMPLETED = "COMPLETED", "Concluído"
        NO_SHOW = "NO_SHOW", "Não compareceu"

    # Status que bloqueiam conflito de horário (agendado ou confirmado).
    BLOCKING_STATUSES = (Status.SCHEDULED, Status.CONFIRMED)

    professional = models.ForeignKey(
        Professional,
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    customer = models.ForeignKey(
        "crm.Customer",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    notes = models.TextField(blank=True)
    confirmation_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )
    external_event_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID do evento no calendário externo (para idempotência).",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ("-start",)
        indexes = [
            models.Index(fields=["professional", "start"]),
            models.Index(fields=["professional", "status"]),
            models.Index(fields=["start", "end"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            # Barreira atômica contra corrida: o check-then-save da camada de
            # serviço não é suficiente sob requisições simultâneas — duas
            # transações podem passar na validação e inserir sobreposição. A
            # constraint impede a segunda INSERT no nível do banco (409 via
            # IntegrityError tratado em services). Restrita aos status que
            # bloqueiam; CANCELLED/COMPLETED/NO_SHOW ficam fora.
            ExclusionConstraint(
                name="exclude_overlapping_appointments",
                expressions=[
                    ("professional", RangeOperators.EQUAL),
                    (TsTzRange("start", "end", RangeBoundary()), RangeOperators.OVERLAPS),
                ],
                condition=Q(status__in=("SCHEDULED", "CONFIRMED")),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.service} @ {self.professional} ({self.start:%Y-%m-%d %H:%M})"

    def clean(self) -> None:
        """Valida regras de domínio do agendamento."""
        from django.core.exceptions import ValidationError

        if self.end is not None:
            if self.end <= self.start:
                raise ValidationError(
                    {"end": "O horário de término deve ser posterior ao início."}
                )
            duration = (self.end - self.start).total_seconds() / 60
            if duration < 5:
                raise ValidationError(
                    {"end": "A duração mínima do agendamento é de 5 minutos."}
                )

    def save(self, *args, **kwargs) -> None:
        """Calcula `end` a partir de `service.duration_minutes` se não informado."""
        from datetime import timedelta

        if self.end is None and self.service_id and self.start:
            self.end = self.start + timedelta(
                minutes=self.service.duration_minutes
            )
        super().save(*args, **kwargs)
