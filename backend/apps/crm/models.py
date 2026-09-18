"""CRM (TENANT_APPS) — proprietário de Lead e Customer.

Modelos conforme `Projeto_SaaS/domains/CRM.md` e `DATABASE.md`. Todos operam
dentro do schema do tenant; o isolamento é garantido pelo django-tenants e o
escopo de visibilidade por objeto pelo django-guardian (ver permissions.py).
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LeadSource(TimeStampedModel):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class LeadStatus(TimeStampedModel):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=64)
    order = models.PositiveIntegerField(default=0)
    is_terminal = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        ordering = ("order", "code")
        verbose_name_plural = "lead statuses"

    def __str__(self) -> str:
        return self.code


class CustomerTag(TimeStampedModel):
    name = models.CharField(max_length=64, unique=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Customer(TimeStampedModel):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Ativo"),
        (STATUS_INACTIVE, "Inativo"),
    )

    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    document = models.CharField(max_length=32, blank=True)
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    source = models.ForeignKey(
        LeadSource,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="customers",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="crm_customers",
    )
    tags = models.ManyToManyField(CustomerTag, blank=True, related_name="customers")
    history = HistoricalRecords()

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["email"]),
            models.Index(fields=["document"]),
        ]

    def __str__(self) -> str:
        return self.name


class CustomerContact(TimeStampedModel):
    KIND_EMAIL = "email"
    KIND_PHONE = "phone"
    KIND_WHATSAPP = "whatsapp"
    KIND_OTHER = "other"
    KIND_CHOICES = (
        (KIND_EMAIL, "E-mail"),
        (KIND_PHONE, "Telefone"),
        (KIND_WHATSAPP, "WhatsApp"),
        (KIND_OTHER, "Outro"),
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="contacts"
    )
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default=KIND_OTHER)
    value = models.CharField(max_length=255)
    label = models.CharField(max_length=64, blank=True)
    is_primary = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["kind"])]

    def __str__(self) -> str:
        return f"{self.get_kind_display()}: {self.value}"


class CustomerAddress(TimeStampedModel):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="addresses"
    )
    label = models.CharField(max_length=64, blank=True)
    street = models.CharField(max_length=150)
    number = models.CharField(max_length=20, blank=True)
    complement = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, blank=True)
    zipcode = models.CharField(max_length=12, blank=True)
    country = models.CharField(max_length=64, default="Brasil")
    is_primary = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.street}, {self.number} - {self.city}"


class CustomerNote(TimeStampedModel):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="notes"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="crm_notes",
    )
    body = models.TextField()
    history = HistoricalRecords()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.body[:60]


class Lead(TimeStampedModel):
    class StatusCode(models.TextChoices):
        NEW = "NEW", "Novo"
        CONTACTED = "CONTACTED", "Contatado"
        QUALIFIED = "QUALIFIED", "Qualificado"
        CONVERTED = "CONVERTED", "Convertido"
        LOST = "LOST", "Perdido"

    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    document = models.CharField(max_length=32, blank=True)
    source = models.ForeignKey(
        LeadSource,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="leads",
    )
    status = models.ForeignKey(
        LeadStatus, on_delete=models.PROTECT, related_name="leads"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="crm_leads",
    )
    notes = models.TextField(blank=True)
    lost_reason = models.CharField(max_length=255, blank=True)
    converted_customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="converted_from_leads",
    )
    converted_at = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self) -> str:
        return self.name


class Interaction(TimeStampedModel):
    """Interação relevante com Lead/Customer — base da timeline do CRM.

    Não duplica dados proprietários de Quotes/Agenda/Finance: apenas registra
    fatos do próprio CRM (notas, contatos, transições, conversão).
    """

    KIND_NOTE = "note"
    KIND_CALL = "call"
    KIND_EMAIL = "email"
    KIND_MEETING = "meeting"
    KIND_MESSAGE = "message"
    KIND_SYSTEM = "system"
    KIND_OTHER = "other"
    KIND_CHOICES = (
        (KIND_NOTE, "Nota"),
        (KIND_CALL, "Ligação"),
        (KIND_EMAIL, "E-mail"),
        (KIND_MEETING, "Reunião"),
        (KIND_MESSAGE, "Mensagem"),
        (KIND_SYSTEM, "Sistema"),
        (KIND_OTHER, "Outro"),
    )

    customer = models.ForeignKey(
        Customer,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="interactions",
    )
    lead = models.ForeignKey(
        Lead,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="interactions",
    )
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default=KIND_OTHER)
    description = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="crm_interactions",
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.description[:60]


# Estados e transições permitidas do Lead (CRM.md: NEW → CONTACTED → QUALIFIED
# → CONVERTED, com caminhos controlados para LOST e reativação).
LEAD_TRANSITIONS: dict[str, set[str]] = {
    Lead.StatusCode.NEW: {Lead.StatusCode.CONTACTED, Lead.StatusCode.LOST},
    Lead.StatusCode.CONTACTED: {Lead.StatusCode.QUALIFIED, Lead.StatusCode.LOST},
    Lead.StatusCode.QUALIFIED: {Lead.StatusCode.CONVERTED, Lead.StatusCode.LOST},
    Lead.StatusCode.LOST: {Lead.StatusCode.CONTACTED},
    Lead.StatusCode.CONVERTED: set(),
}
