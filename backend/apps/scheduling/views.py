"""Views da Agenda (ETAPA 2) — Professionals, Services, Appointments.

Contrato: `Projeto_SaaS/architecture/API.md` §Scheduling. Tenant e identidade
derivam do contexto autenticado (JWT); o schema isola os dados e o guardian
restringe o escopo por objeto dentro do tenant (reutilizado de apps.crm).
"""

from __future__ import annotations

from datetime import datetime

import structlog
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.crm.permissions import (
    grant_member_perms,
    visible_queryset,
)
from apps.crm.views import CrmBaseViewSet
from apps.scheduling.models import Appointment, Professional, Service
from apps.scheduling.serializers import (
    AppointmentListSerializer,
    AppointmentReadSerializer,
    AppointmentWriteSerializer,
    ConfirmWebhookSerializer,
    ProfessionalSerializer,
    RescheduleSerializer,
    ServiceSerializer,
)
from apps.scheduling.services import (
    cancel_appointment,
    complete_appointment,
    confirm_appointment,
    get_daily_slots,
    no_show_appointment,
    reschedule_appointment,
)

logger = structlog.get_logger(__name__)


class ProfessionalViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    CrmBaseViewSet,
):
    filterset_fields = ("active",)
    search_fields = ("name", "email", "specialties")
    ordering_fields = ("name", "created_at")

    def get_queryset(self):
        return visible_queryset(
            self.request.user, Professional, Professional.objects.all()
        )

    def get_serializer_class(self):
        return ProfessionalSerializer

    def perform_create(self, serializer):
        professional = serializer.save()
        grant_member_perms(self.request.user, professional)
        if professional.user:
            grant_member_perms(professional.user, professional)

    def perform_update(self, serializer):
        professional = serializer.save()
        if professional.user:
            grant_member_perms(professional.user, professional)


class ServiceViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    CrmBaseViewSet,
):
    filterset_fields = ("active",)
    search_fields = ("name", "description")
    ordering_fields = ("name", "price", "created_at")

    def get_queryset(self):
        return visible_queryset(self.request.user, Service, Service.objects.all())

    def get_serializer_class(self):
        return ServiceSerializer

    def perform_create(self, serializer):
        service = serializer.save()
        grant_member_perms(self.request.user, service)

    def perform_update(self, serializer):
        serializer.save()


class AppointmentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    CrmBaseViewSet,
):
    filterset_fields = ("status", "professional", "service", "customer")
    search_fields = ("notes",)
    ordering_fields = ("start", "created_at")

    def get_queryset(self):
        base = Appointment.objects.select_related("professional", "service", "customer")
        return visible_queryset(self.request.user, Appointment, base)

    def get_serializer_class(self):
        if self.action == "list":
            return AppointmentListSerializer
        if self.action in ("create", "update", "partial_update"):
            return AppointmentWriteSerializer
        return AppointmentReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = AppointmentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            AppointmentReadSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = AppointmentWriteSerializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(AppointmentReadSerializer(serializer.instance).data)

    def perform_create(self, serializer):
        appointment = serializer.save()
        grant_member_perms(self.request.user, appointment)
        if appointment.professional.user:
            grant_member_perms(appointment.professional.user, appointment)

    def perform_update(self, serializer):
        appointment = serializer.save()
        if appointment.professional.user:
            grant_member_perms(appointment.professional.user, appointment)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        appointment = cancel_appointment(appointment)
        return Response(AppointmentReadSerializer(appointment).data)

    @action(detail=True, methods=["post"], url_path="reschedule")
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        serializer = RescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = reschedule_appointment(
            appointment,
            start=serializer.validated_data["start"],
            end=serializer.validated_data.get("end"),
        )
        return Response(AppointmentReadSerializer(appointment).data)

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        appointment = confirm_appointment(appointment)
        return Response(AppointmentReadSerializer(appointment).data)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        appointment = self.get_object()
        appointment = complete_appointment(appointment)
        return Response(AppointmentReadSerializer(appointment).data)

    @action(detail=True, methods=["post"], url_path="no-show")
    def no_show(self, request, pk=None):
        appointment = self.get_object()
        appointment = no_show_appointment(appointment)
        return Response(AppointmentReadSerializer(appointment).data)


class AvailabilityView(APIView):
    """Slots livres por profissional/dia. Consulta derivada: só IsAuthenticated."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        professional_id = request.query_params.get("professional")
        date_str = request.query_params.get("date")
        service_id = request.query_params.get("service")

        if not professional_id or not date_str:
            return Response(
                {
                    "detail": {
                        "professional": "Obrigatório.",
                        "date": "Obrigatório (YYYY-MM-DD).",
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": {"date": "Formato inválido. Use YYYY-MM-DD."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        professional = visible_queryset(
            request.user,
            Professional,
            Professional.objects.filter(pk=professional_id, active=True),
        ).first()
        if not professional:
            return Response(
                {"detail": "Profissional não encontrado ou sem permissão."},
                status=status.HTTP_404_NOT_FOUND,
            )
        service = None
        if service_id:
            service = visible_queryset(
                request.user,
                Service,
                Service.objects.filter(pk=service_id, active=True),
            ).first()
            if not service:
                return Response(
                    {"detail": "Serviço não encontrado ou sem permissão."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        slots = get_daily_slots(professional, target_date, service)
        return Response(
            {"professional": professional.pk, "date": date_str, "slots": slots}
        )


class ConfirmWebhookView(APIView):
    """Webhook público de confirmação (link do cliente, sem JWT).

    O tenant vem do header x-tenant-id (hint de roteamento, ver middleware).
    O segredo é o confirmation_token (UUID). Nada de token é logado.
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []

    def post(self, request):
        serializer = ConfirmWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        act = serializer.validated_data["action"]

        appointment = (
            Appointment.objects.select_related("professional", "service", "customer")
            .filter(confirmation_token=token)
            .first()
        )
        if appointment is None:
            return Response(
                {"detail": "Agendamento não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if act == "confirm":
            appointment = confirm_appointment(appointment)
            logger.info("webhook_confirmed", appointment_id=appointment.pk)
        else:
            appointment = cancel_appointment(appointment)
            logger.info("webhook_cancelled", appointment_id=appointment.pk)
        return Response(AppointmentReadSerializer(appointment).data)
