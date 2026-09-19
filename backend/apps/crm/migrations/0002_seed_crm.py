"""Seed idempotente do CRM (por schema de tenant).

DATABASE.md: seeds idempotentes e limitadas a dados iniciais necessários.
"""

from __future__ import annotations

from django.db import migrations

LEAD_STATUSES = (
    ("NEW", "Novo", 1, False),
    ("CONTACTED", "Contatado", 2, False),
    ("QUALIFIED", "Qualificado", 3, False),
    ("CONVERTED", "Convertido", 4, True),
    ("LOST", "Perdido", 5, True),
)

LEAD_SOURCES = (("manual", "Origem manual"),)


def seed_crm(apps, schema_editor):
    LeadStatus = apps.get_model("crm", "LeadStatus")
    for code, name, order, is_terminal in LEAD_STATUSES:
        LeadStatus.objects.update_or_create(
            code=code,
            defaults={"name": name, "order": order, "is_terminal": is_terminal},
        )

    LeadSource = apps.get_model("crm", "LeadSource")
    for name, description in LEAD_SOURCES:
        LeadSource.objects.get_or_create(
            name=name, defaults={"description": description}
        )


def unseed_crm(apps, schema_editor):
    LeadStatus = apps.get_model("crm", "LeadStatus")
    LeadStatus.objects.filter(code__in=[s[0] for s in LEAD_STATUSES]).delete()

    LeadSource = apps.get_model("crm", "LeadSource")
    LeadSource.objects.filter(name__in=[s[0] for s in LEAD_SOURCES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("crm", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_crm, unseed_crm),
    ]
