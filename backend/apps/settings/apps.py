from django.apps import AppConfig


class SettingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.settings"
    label = "app_settings"
    verbose_name = "Configurações do tenant (Etapa 5)"
