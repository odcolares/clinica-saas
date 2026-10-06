"""Regras de domínio da Agenda (ETAPA 2).

Mantidas fora das views para que o ciclo de vida do agendamento tenha um único
ponto de verdade. Conflitos de horário → Conflict (409); validações de
integridade → ValidationError (400).
"""

from __future__ import annotations

import structlog
from datetime import date as date_cls
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from apps.common.exceptions import Conflict
from apps.scheduling.calendar import CalendarAdapter, get_calendar_adapter
from apps.scheduling.models import Appointment, Professional, Service

logger = structlog.get_logger(__name__)

# Expediente fixo do profissional (America/Sao_Paulo).
BUSINESS_START = time(8, 0)  # 08:00
BUSINESS_END = time(18, 0)  # 18:00
TIMEZONE = ZoneInfo("America/Sao_Paulo")
DEFAULT_SLOT_MINUTES = 30
MIN_APPOINTMENT_MINUTES = 5


def validate_business_hours(start: datetime, end: datetime) -> None:
    """Valida que o agendamento cabe dentro do expediente (08:00-18:00,
    America/Sao_Paulo), no fuso correto, cruzando o limite se necessário.

    Levanta ValidationError (400) se start ou end caem fora do expediente.
    """
    local_start = start.astimezone(TIMEZONE)
    local_end = end.astimezone(TIMEZONE)

    day = local_start.date()
    if local_end.date() != day:
        raise ValidationError(
            {"end": "O agendamento não pode cruzar a virada do dia."}
        )

    open_at = datetime.combine(day, BUSINESS_START, tzinfo=TIMEZONE)
    close_at = datetime.combine(day, BUSINESS_END, tzinfo=TIMEZONE)

    if local_start < open_at or local_end > close_at:
        raise ValidationError(
            {
                "start": (
                    "Fora do expediente: agendamentos devem estar entre "
                    "08:00 e 18:00 (America/Sao_Paulo)."
                )
            }
        )


def validate_no_conflict(
    professional: Professional,
    start: datetime,
    end: datetime,
    exclude_pk: int | None = None,
) -> None:
    """Verifica sobreposição de horário para o profissional.

    Regra: overlap = mesmo professional + status em (SCHEDULED, CONFIRMED) +
    start < novo_end AND end > novo_start. Adjacente (end == start) é PERMITIDO.
    Status CANCELLED/COMPLETED/NO_SHOW não bloqueiam.

    Levanta ``Conflict`` (409) se houver sobreposição.
    """
    overlapping = Appointment.objects.filter(
        professional=professional,
        status__in=Appointment.BLOCKING_STATUSES,
        start__lt=end,
        end__gt=start,
    )
    if exclude_pk is not None:
        overlapping = overlapping.exclude(pk=exclude_pk)

    # Lock pessimista: travamos as linhas sobrepostas dentro da mesma
    # transação que vai inserir/atualizar, fechando a janela check-then-save
    # contra requisições simultâneas. A constraint de exclusão no banco
    # (models Appointment.Meta.constraints) é a barreira final.
    overlapping = overlapping.select_for_update()

    if overlapping.exists():
        conflict = overlapping.first()
        raise Conflict(
            f"Conflito de horário: o profissional já tem um agendamento "
            f"({conflict.status}) das {conflict.start:%H:%M} às "
            f"{conflict.end:%H:%M}."
        )


def sync_to_calendar(
    appointment: Appointment,
    adapter: CalendarAdapter | None = None,
) -> Appointment:
    """Sincroniza o agendamento com o calendário externo.

    Usa o adapter do tenant (Etapa 5) por padrão. Atualiza ``external_event_id``
    de forma idempotente.
    """
    if adapter is None:
        adapter = get_calendar_adapter()

    summary = f"{appointment.service.name} — {appointment.customer.name}"
    description = appointment.notes or ""

    if appointment.external_event_id:
        # Evento já existe: update idempotente
        external_id = adapter.update_event(
            external_id=appointment.external_event_id,
            professional_email=appointment.professional.email,
            summary=summary,
            start=appointment.start,
            end=appointment.end,
            description=description,
        )
    else:
        # Novo evento: create
        external_id = adapter.create_event(
            external_id=appointment.confirmation_token.hex,
            professional_email=appointment.professional.email,
            summary=summary,
            start=appointment.start,
            end=appointment.end,
            description=description,
        )

    if external_id:
        appointment.external_event_id = external_id
        appointment.save(update_fields=["external_event_id"])

    logger.info(
        "calendar_sync",
        appointment_id=appointment.pk,
        external_event_id=appointment.external_event_id,
    )
    return appointment


def get_daily_slots(
    professional: Professional,
    date: date_cls | datetime,
    service: Service | None = None,
) -> list[dict[str, str]]:
    """Calcula slots disponíveis para um profissional em uma data.

    Expediente fixo 08:00-18:00 (America/Sao_Paulo). Slots de
    ``service.duration_minutes`` (default 30). Subtrai sobreposições com
    appointments ativos (SCHEDULED/CONFIRMED) do profissional no dia.
    """
    duration = service.duration_minutes if service else DEFAULT_SLOT_MINUTES

    # Constrói o dia em America/Sao_Paulo
    day_start = datetime.combine(date, BUSINESS_START, tzinfo=TIMEZONE)
    day_end = datetime.combine(date, BUSINESS_END, tzinfo=TIMEZONE)

    # Busca appointments que bloqueiam no dia
    blocking = Appointment.objects.filter(
        professional=professional,
        status__in=Appointment.BLOCKING_STATUSES,
        start__date=date,
    ).values_list("start", "end")

    # Normaliza para comparação (todos em tz-aware)
    occupied: list[tuple[datetime, datetime]] = []
    for a_start, a_end in blocking:
        if a_start.tzinfo is None:
            a_start = a_start.replace(tzinfo=TIMEZONE)
        if a_end.tzinfo is None:
            a_end = a_end.replace(tzinfo=TIMEZONE)
        occupied.append((a_start, a_end))

    slots: list[dict[str, str]] = []
    cursor = day_start
    while cursor + timedelta(minutes=duration) <= day_end:
        slot_end = cursor + timedelta(minutes=duration)
        # Verifica se o slot não sobreponha nenhum appointment bloqueador
        is_free = True
        for occ_start, occ_end in occupied:
            if cursor < occ_end and slot_end > occ_start:
                is_free = False
                break
        if is_free:
            slots.append(
                {
                    "start": cursor.isoformat(),
                    "end": slot_end.isoformat(),
                }
            )
        cursor = slot_end

    return slots


def create_appointment(
    *,
    professional: Professional,
    service: Service,
    customer,
    start: datetime,
    end: datetime | None = None,
    notes: str = "",
) -> Appointment:
    """Cria um agendamento validando conflitos."""
    if not professional.active:
        raise ValidationError({"professional": "Profissional inativo."})
    if not service.active:
        raise ValidationError({"service": "Serviço inativo."})

    if end is None:
        end = start + timedelta(minutes=service.duration_minutes)

    # Valida duração mínima
    duration = (end - start).total_seconds() / 60
    if duration < MIN_APPOINTMENT_MINUTES:
        raise ValidationError(
            {"end": "A duração mínima do agendamento é de 5 minutos."}
        )

    validate_business_hours(start, end)

    try:
        with transaction.atomic():
            validate_no_conflict(professional, start, end)
            appointment = Appointment(
                professional=professional,
                service=service,
                customer=customer,
                start=start,
                end=end,
                notes=notes,
            )
            appointment.full_clean()
            appointment.save()
    except IntegrityError as exc:
        raise _conflict_from_integrity(exc) from exc

    sync_to_calendar(appointment)
    return appointment


def _conflict_from_integrity(exc: IntegrityError) -> Conflict:
    """Mapeia violação da exclusion constraint para 409 (barreira final do banco)."""
    message = str(exc)
    if "exclude_overlapping_appointments" in message or "overlap" in message.lower():
        return Conflict(
            "Conflito de horário detectado pelo banco: outro agendamento foi "
            "criado simultaneamente neste intervalo."
        )
    raise exc


def update_appointment(
    appointment: Appointment,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    service: Service | None = None,
    notes: str | None = None,
) -> Appointment:
    """Atualiza um agendamento revalidando conflitos."""
    if start is not None:
        appointment.start = start
    if end is not None:
        appointment.end = end
    if service is not None:
        appointment.service = service
    if notes is not None:
        appointment.notes = notes

    # Recalcula end se necessário
    if appointment.end is None and appointment.service_id:
        appointment.end = appointment.start + timedelta(
            minutes=appointment.service.duration_minutes
        )

    # Valida duração mínima
    if appointment.end is not None:
        duration = (appointment.end - appointment.start).total_seconds() / 60
        if duration < MIN_APPOINTMENT_MINUTES:
            raise ValidationError(
                {"end": "A duração mínima do agendamento é de 5 minutos."}
            )

    validate_business_hours(appointment.start, appointment.end)

    try:
        with transaction.atomic():
            validate_no_conflict(
                appointment.professional,
                appointment.start,
                appointment.end,
                exclude_pk=appointment.pk,
            )
            appointment.full_clean()
            appointment.save()
    except IntegrityError as exc:
        raise _conflict_from_integrity(exc) from exc

    sync_to_calendar(appointment)
    return appointment


def cancel_appointment(appointment: Appointment) -> Appointment:
    """Cancela um agendamento (idempotente: se já CANCELLED retorna 200)."""
    if appointment.status == Appointment.Status.CANCELLED:
        return appointment
    if appointment.status in (Appointment.Status.COMPLETED, Appointment.Status.NO_SHOW):
        return appointment
    appointment.status = Appointment.Status.CANCELLED
    appointment.save(update_fields=["status"])
    logger.info("appointment_cancelled", appointment_id=appointment.pk)
    return appointment


def complete_appointment(appointment: Appointment) -> Appointment:
    """Marca agendamento como COMPLETED (estado terminal)."""
    if appointment.status == Appointment.Status.COMPLETED:
        return appointment
    if appointment.status == Appointment.Status.CANCELLED:
        raise ValidationError({"status": "Agendamento cancelado não pode ser concluído."})
    if appointment.status == Appointment.Status.NO_SHOW:
        return appointment
    appointment.status = Appointment.Status.COMPLETED
    appointment.save(update_fields=["status"])
    logger.info("appointment_completed", appointment_id=appointment.pk)
    return appointment


def no_show_appointment(appointment: Appointment) -> Appointment:
    """Marca agendamento como NO_SHOW (estado terminal)."""
    if appointment.status == Appointment.Status.NO_SHOW:
        return appointment
    if appointment.status == Appointment.Status.CANCELLED:
        raise ValidationError({"status": "Agendamento cancelado não pode ser marcado como no-show."})
    if appointment.status == Appointment.Status.COMPLETED:
        return appointment
    appointment.status = Appointment.Status.NO_SHOW
    appointment.save(update_fields=["status"])
    logger.info("appointment_no_show", appointment_id=appointment.pk)
    return appointment


def reschedule_appointment(
    appointment: Appointment,
    *,
    start: datetime,
    end: datetime | None = None,
) -> Appointment:
    """Reagenda um agendamento revalidando conflitos."""
    if end is None:
        end = start + timedelta(
            minutes=appointment.service.duration_minutes
        )

    duration = (end - start).total_seconds() / 60
    if duration < MIN_APPOINTMENT_MINUTES:
        raise ValidationError(
            {"end": "A duração mínima do agendamento é de 5 minutos."}
        )

    validate_business_hours(start, end)

    try:
        with transaction.atomic():
            validate_no_conflict(
                appointment.professional,
                start,
                end,
                exclude_pk=appointment.pk,
            )
            appointment.start = start
            appointment.end = end
            appointment.full_clean()
            appointment.save(update_fields=["start", "end"])
    except IntegrityError as exc:
        raise _conflict_from_integrity(exc) from exc

    sync_to_calendar(appointment)
    return appointment


def confirm_appointment(appointment: Appointment) -> Appointment:
    """Confirma um agendamento (SCHEDULED → CONFIRMED)."""
    if appointment.status not in (Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED):
        return appointment
    appointment.status = Appointment.Status.CONFIRMED
    appointment.save(update_fields=["status"])
    logger.info("appointment_confirmed", appointment_id=appointment.pk)
    return appointment
