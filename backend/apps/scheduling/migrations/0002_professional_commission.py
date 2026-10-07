# Etapa 5 — comissões no Professional.
from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scheduling", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalprofessional",
            name="commission_fixed",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="historicalprofessional",
            name="commission_percent",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name="historicalprofessional",
            name="commission_type",
            field=models.CharField(
                choices=[("none", "Sem comissão"), ("percent", "Percentual"), ("fixed", "Valor fixo")],
                default="none",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="professional",
            name="commission_fixed",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name="professional",
            name="commission_percent",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name="professional",
            name="commission_type",
            field=models.CharField(
                choices=[("none", "Sem comissão"), ("percent", "Percentual"), ("fixed", "Valor fixo")],
                default="none",
                max_length=16,
            ),
        ),
    ]
