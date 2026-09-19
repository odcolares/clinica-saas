"""Regras de domínio do CRM: transições de status e conversão Lead → Customer.

Mantidas fora das views para que o ciclo de vida do Lead tenha um único ponto
de verdade (CRM.md: transições controladas; conversão preserva o Lead).
"""

from __future__ import annotations

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.common.exceptions import Conflict
from apps.crm.models import (
    LEAD_TRANSITIONS,
    Customer,
    Interaction,
    Lead,
    LeadStatus,
)

MATCH_FIELDS = ("email", "document", "phone")


def change_lead_status(lead: Lead, code: str, *, author, reason: str = "") -> Lead:
    """Aplica uma transição de status do Lead, registrando autor/data/motivo."""
    current = lead.status.code
    if code == current:
        raise ValidationError({"status": f"Lead já está em {current}."})
    if code not in LEAD_TRANSITIONS.get(current, set()):
        raise ValidationError(
            {"status": f"Transição {current} → {code} não permitida."}
        )
    if code == Lead.StatusCode.LOST and not reason:
        raise ValidationError({"reason": "Motivo é obrigatório ao marcar LOST."})

    try:
        new_status = LeadStatus.objects.get(code=code)
    except LeadStatus.DoesNotExist as exc:
        raise ValidationError({"status": f"Status {code} inexistente."}) from exc

    lead.status = new_status
    if code == Lead.StatusCode.LOST:
        lead.lost_reason = reason
    lead._change_reason = reason or f"Status {current} → {code}"
    lead._history_user = author
    lead.save()

    Interaction.objects.create(
        customer=lead.converted_customer,
        lead=lead,
        kind=Interaction.KIND_SYSTEM,
        description=f"Status {current} → {code}",
        author=author,
    )
    return lead


def _find_matching_customer(lead: Lead) -> Customer | None:
    """Localiza Customer existente pelo primeiro critério com valor.

    Critérios configurados: e-mail, documento, telefone (CRM.md §Conversão).
    """
    for field in MATCH_FIELDS:
        value = getattr(lead, field, "")
        if not value:
            continue
        match = Customer.objects.filter(**{field: value}).first()
        if match is not None:
            return match
    return None


def convert_lead(lead: Lead, *, author) -> tuple[Customer, bool]:
    """Converte o Lead em Customer preservando o Lead original.

    Retorna (customer, created). O Lead permanece com status CONVERTED e
    converted_customer apontando para o Customer vinculado/criado.
    """
    if lead.status.code == Lead.StatusCode.CONVERTED:
        raise Conflict("Lead já convertido.")
    if lead.status.code != Lead.StatusCode.QUALIFIED:
        raise ValidationError(
            {
                "status": "Lead precisa estar QUALIFIED para conversão "
                f"(atual: {lead.status.code})."
            }
        )

    customer = _find_matching_customer(lead)
    created = customer is None
    if created:
        customer = Customer(
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            document=lead.document,
            source=lead.source,
            assigned_to=lead.assigned_to or author,
        )
        customer._history_user = author
        customer.save()

    lead.status = LeadStatus.objects.get(code=Lead.StatusCode.CONVERTED)
    lead.converted_customer = customer
    lead.converted_at = timezone.now()
    lead._change_reason = "Conversão de lead"
    lead._history_user = author
    lead.save()

    Interaction.objects.create(
        customer=customer,
        lead=lead,
        kind=Interaction.KIND_SYSTEM,
        description=(
            f"Lead #{lead.pk} convertido; Customer existente vinculado."
            if not created
            else f"Lead #{lead.pk} convertido; Customer criado."
        ),
        author=author,
    )
    return customer, created
