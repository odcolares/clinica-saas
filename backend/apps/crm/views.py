"""Views do CRM (ETAPA 1) — Leads, Customers e agregados.

Contrato: `Projeto_SaaS/architecture/API.md` §CRM. Tenant e identidade derivam
do contexto autenticado (JWT); o schema isola os dados e o guardian restringe
o escopo por objeto dentro do tenant.
"""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.crm.models import (
    Customer,
    CustomerTag,
    Lead,
    LeadSource,
    LeadStatus,
)
from apps.crm.permissions import (
    CrmObjectPermission,
    grant_member_perms,
    visible_queryset,
)
from apps.crm.serializers import (
    CustomerAddressSerializer,
    CustomerContactSerializer,
    CustomerListSerializer,
    CustomerNoteSerializer,
    CustomerSerializer,
    CustomerTagSerializer,
    LeadSerializer,
    LeadSourceSerializer,
    LeadStatusSerializer,
    LeadStatusUpdateSerializer,
    LeadWriteSerializer,
)
from apps.crm.services import change_lead_status, convert_lead


class CrmBaseViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, CrmObjectPermission]
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    ordering = ("-created_at",)


class LeadViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    CrmBaseViewSet,
):
    filterset_fields = ("status__code", "source", "assigned_to")
    search_fields = ("name", "email", "phone", "document")
    ordering_fields = ("created_at", "updated_at", "name")

    def get_queryset(self):
        base = Lead.objects.select_related("status", "source", "assigned_to")
        return visible_queryset(self.request.user, Lead, base)

    def get_serializer_class(self):
        return LeadSerializer

    def create(self, request, *args, **kwargs):
        serializer = LeadWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            LeadSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = LeadWriteSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(LeadSerializer(serializer.instance).data)

    def perform_create(self, serializer):
        new_status = LeadStatus.objects.get(code=Lead.StatusCode.NEW)
        lead = serializer.save(status=new_status)
        grant_member_perms(self.request.user, lead)
        if lead.assigned_to:
            grant_member_perms(lead.assigned_to, lead)

    def perform_update(self, serializer):
        lead = serializer.save()
        if lead.assigned_to:
            grant_member_perms(lead.assigned_to, lead)

    @action(detail=True, methods=["patch"], url_path="status")
    def status_change(self, request, pk=None):  # noqa: D401 - nome exposto via url_path
        lead = self.get_object()
        serializer = LeadStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = change_lead_status(
            lead,
            serializer.validated_data["status"].code,
            author=request.user,
            reason=serializer.validated_data["reason"],
        )
        return Response(LeadSerializer(lead).data)

    @action(detail=True, methods=["post"], url_path="convert")
    def convert(self, request, pk=None):
        lead = self.get_object()
        customer, created = convert_lead(lead, author=request.user)
        grant_member_perms(request.user, customer)
        return Response(
            {
                "customer": CustomerListSerializer(customer).data,
                "created": created,
                "lead_id": lead.pk,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class CustomerViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    CrmBaseViewSet,
):
    filterset_fields = ("status", "source", "assigned_to", "tags")
    search_fields = ("name", "email", "phone", "document")
    ordering_fields = ("created_at", "updated_at", "name")

    def get_queryset(self):
        base = Customer.objects.prefetch_related(
            "contacts", "addresses", "notes", "tags"
        ).select_related("source", "assigned_to")
        return visible_queryset(self.request.user, Customer, base)

    def get_serializer_class(self):
        if self.action == "list":
            return CustomerListSerializer
        return CustomerSerializer

    def perform_create(self, serializer):
        customer = serializer.save()
        grant_member_perms(self.request.user, customer)
        if customer.assigned_to:
            grant_member_perms(customer.assigned_to, customer)

    def perform_update(self, serializer):
        customer = serializer.save()
        if customer.assigned_to:
            grant_member_perms(customer.assigned_to, customer)

    @action(detail=True, methods=["post"], url_path="contacts")
    def contacts(self, request, pk=None):
        customer = self.get_object()
        serializer = CustomerContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="addresses")
    def addresses(self, request, pk=None):
        customer = self.get_object()
        serializer = CustomerAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="notes")
    def notes(self, request, pk=None):
        customer = self.get_object()
        serializer = CustomerNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=customer, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="timeline")
    def timeline(self, request, pk=None):
        customer = self.get_object()
        events = []

        for note in customer.notes.all():
            events.append(
                {
                    "type": "note",
                    "id": note.pk,
                    "kind": "note",
                    "description": note.body,
                    "author": getattr(note.author, "username", None),
                    "created_at": note.created_at.isoformat(),
                }
            )
        for interaction in customer.interactions.all():
            events.append(
                {
                    "type": "interaction",
                    "id": interaction.pk,
                    "kind": interaction.kind,
                    "description": interaction.description,
                    "author": getattr(interaction.author, "username", None),
                    "created_at": interaction.created_at.isoformat(),
                }
            )
        for lead in customer.converted_from_leads.all():
            events.append(
                {
                    "type": "conversion",
                    "id": lead.pk,
                    "kind": "conversion",
                    "description": f"Lead #{lead.pk} convertido",
                    "author": None,
                    "created_at": (lead.converted_at or lead.created_at).isoformat(),
                }
            )

        events.sort(key=lambda event: event["created_at"], reverse=True)
        return Response({"customer": customer.pk, "events": events})


class CustomerTagViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    CrmBaseViewSet,
):
    queryset = CustomerTag.objects.all()
    serializer_class = CustomerTagSerializer
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")


class LeadSourceViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    CrmBaseViewSet,
):
    queryset = LeadSource.objects.all()
    serializer_class = LeadSourceSerializer
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")


class LeadStatusViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, CrmBaseViewSet
):
    queryset = LeadStatus.objects.all()
    serializer_class = LeadStatusSerializer
    ordering_fields = ("order", "code")
