"""Serializers da Agenda (ETAPA 2)."""

from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.crm.models import Customer
from apps.scheduling.models import Appointment, Professional, Service
from apps.scheduling.services import MIN_APPOINTMENT_MINUTES

User = get_user_model()


class ProfessionalSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    specialty_list = serializers.SerializerMethodField()

    class Meta:
        model = Professional
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "specialties",
            "specialty_list",
            "active",
            "commission_type",
            "commission_percent",
            "commission_fixed",
            "user",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_specialty_list(self, obj) -> list[str]:
        return obj.specialty_list

    def validate(self, attrs):
        ctype = attrs.get("commission_type", getattr(self.instance, "commission_type", "none"))
        percent = attrs.get("commission_percent", getattr(self.instance, "commission_percent", 0))
        fixed = attrs.get("commission_fixed", getattr(self.instance, "commission_fixed", 0))
        if ctype == "percent" and (percent is None or float(percent) < 0 or float(percent) > 100):
            raise serializers.ValidationError(
                {"commission_percent": "Percentual deve estar entre 0 e 100."}
            )
        if ctype == "fixed" and (fixed is None or float(fixed) < 0):
            raise serializers.ValidationError(
                {"commission_fixed": "Valor fixo não pode ser negativo."}
            )
        return attrs


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "description",
            "duration_minutes",
            "price",
            "active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class AppointmentReadSerializer(serializers.ModelSerializer):
    """Serializer de leitura — expõe nested slugs e confirmation_token no detail."""

    professional_name = serializers.SlugRelatedField(
        source="professional", slug_field="name", read_only=True
    )
    service_name = serializers.SlugRelatedField(
        source="service", slug_field="name", read_only=True
    )
    customer_name = serializers.SlugRelatedField(
        source="customer", slug_field="name", read_only=True
    )

    class Meta:
        model = Appointment
        fields = (
            "id",
            "professional",
            "professional_name",
            "service",
            "service_name",
            "customer",
            "customer_name",
            "start",
            "end",
            "status",
            "notes",
            "confirmation_token",
            "external_event_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AppointmentListSerializer(serializers.ModelSerializer):
    """Lista — sem confirmation_token/external_event_id (só no detail)."""

    professional_name = serializers.SlugRelatedField(
        source="professional", slug_field="name", read_only=True
    )
    service_name = serializers.SlugRelatedField(
        source="service", slug_field="name", read_only=True
    )
    customer_name = serializers.SlugRelatedField(
        source="customer", slug_field="name", read_only=True
    )

    class Meta:
        model = Appointment
        fields = (
            "id",
            "professional",
            "professional_name",
            "service",
            "service_name",
            "customer",
            "customer_name",
            "start",
            "end",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RescheduleSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField(required=False, allow_null=True, default=None)

    def validate(self, attrs):
        if attrs.get("end") and attrs["end"] <= attrs["start"]:
            raise serializers.ValidationError(
                {"end": "O horário de término deve ser posterior ao início."}
            )
        return attrs


class ConfirmWebhookSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    action = serializers.ChoiceField(choices=("confirm", "cancel"))


class AppointmentWriteSerializer(serializers.ModelSerializer):
    """Serializer de escrita — valida end>start, profissional/service ativos,
    customer existente. confirmation_token é gerado automaticamente."""

    professional = serializers.PrimaryKeyRelatedField(
        queryset=Professional.objects.filter(active=True)
    )
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.filter(active=True)
    )
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all()
    )
    start = serializers.DateTimeField()
    end = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "professional",
            "service",
            "customer",
            "start",
            "end",
            "notes",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        start = attrs.get("start")
        end = attrs.get("end")
        service = attrs.get("service") or self.instance.service if self.instance else None

        if start and end:
            if end <= start:
                raise serializers.ValidationError(
                    {"end": "O horário de término deve ser posterior ao início."}
                )
            duration = (end - start).total_seconds() / 60
            if duration < MIN_APPOINTMENT_MINUTES:
                raise serializers.ValidationError(
                    {"end": "A duração mínima do agendamento é de 5 minutos."}
                )

        # Se end não informado, calcula a partir da duração do serviço
        if start and not end and service:
            attrs["end"] = start + timedelta(minutes=service.duration_minutes)

        return attrs

    def create(self, validated_data):
        from apps.scheduling.services import create_appointment

        return create_appointment(**validated_data)

    def update(self, instance, validated_data):
        from apps.scheduling.services import update_appointment

        start = validated_data.pop("start", None)
        end = validated_data.pop("end", None)
        service = validated_data.pop("service", None)
        notes = validated_data.pop("notes", None)

        return update_appointment(
            instance,
            start=start,
            end=end,
            service=service,
            notes=notes,
        )
