# Etapa 5 (fundação) — TenantSettings, IntegrationConfig, WebhookEndpoint, ApiKey.
import django.db.models.deletion
import simple_history.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("crm", "0002_seed_crm"),
    ]

    operations = [
        migrations.CreateModel(
            name="TenantSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("business_start", models.TimeField(default="08:00")),
                ("business_end", models.TimeField(default="18:00")),
                ("timezone", models.CharField(default="America/Sao_Paulo", max_length=64)),
                ("logo_url", models.URLField(blank=True, default="")),
                ("primary_color", models.CharField(default="#0F766E", max_length=7)),
                ("brand_name", models.CharField(blank=True, default="", max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalTenantSettings",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("business_start", models.TimeField(default="08:00")),
                ("business_end", models.TimeField(default="18:00")),
                ("timezone", models.CharField(default="America/Sao_Paulo", max_length=64)),
                ("logo_url", models.URLField(blank=True, default="")),
                ("primary_color", models.CharField(default="#0F766E", max_length=7)),
                ("brand_name", models.CharField(blank=True, default="", max_length=120)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                ("history_user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="accounts.user")),
            ],
            options={
                "verbose_name": "historical configuração do tenant",
                "verbose_name_plural": "historical configurações do tenant",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="IntegrationConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("provider", models.CharField(choices=[("noop", "Nenhuma"), ("google_calendar", "Google Calendar")], default="noop", max_length=32)),
                ("active", models.BooleanField(default=True)),
                ("professional_email", models.EmailField(blank=True, default="", max_length=254)),
                ("config", models.JSONField(blank=True, default=dict)),
            ],
            options={"ordering": ("provider",)},
        ),
        migrations.CreateModel(
            name="HistoricalIntegrationConfig",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("provider", models.CharField(choices=[("noop", "Nenhuma"), ("google_calendar", "Google Calendar")], default="noop", max_length=32)),
                ("active", models.BooleanField(default=True)),
                ("professional_email", models.EmailField(blank=True, default="", max_length=254)),
                ("config", models.JSONField(blank=True, default=dict)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                ("history_user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="accounts.user")),
            ],
            options={
                "verbose_name": "historical integration config",
                "verbose_name_plural": "historical integration configs",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="WebhookEndpoint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("url", models.URLField(max_length=500)),
                ("events", models.JSONField(blank=True, default=list)),
                ("secret", models.CharField(blank=True, default="", max_length=128)),
                ("active", models.BooleanField(default=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="HistoricalWebhookEndpoint",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("name", models.CharField(max_length=120)),
                ("url", models.URLField(max_length=500)),
                ("events", models.JSONField(blank=True, default=list)),
                ("secret", models.CharField(blank=True, default="", max_length=128)),
                ("active", models.BooleanField(default=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                ("history_user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="accounts.user")),
            ],
            options={
                "verbose_name": "historical webhook endpoint",
                "verbose_name_plural": "historical webhook endpoints",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="ApiKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("prefix", models.CharField(max_length=16, unique=True)),
                ("key_hash", models.CharField(max_length=64)),
                ("active", models.BooleanField(default=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="HistoricalApiKey",
            fields=[
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("name", models.CharField(max_length=120)),
                ("prefix", models.CharField(db_index=True, max_length=16)),
                ("key_hash", models.CharField(max_length=64)),
                ("active", models.BooleanField(default=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                ("history_user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="accounts.user")),
            ],
            options={
                "verbose_name": "historical api key",
                "verbose_name_plural": "historical api keys",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
