"""Serializers do CRM."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.crm.models import (
    Customer,
    CustomerAddress,
    CustomerContact,
    CustomerNote,
    CustomerTag,
    Interaction,
    Lead,
    LeadSource,
    LeadStatus,
)

User = get_user_model()


class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadSource
        fields = ("id", "name", "description")


class LeadStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStatus
        fields = ("id", "code", "name", "order", "is_terminal")


class CustomerTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTag
        fields = ("id", "name")


class CustomerContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerContact
        fields = ("id", "kind", "value", "label", "is_primary", "created_at")
        read_only_fields = ("id", "created_at")


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = (
            "id",
            "label",
            "street",
            "number",
            "complement",
            "district",
            "city",
            "state",
            "zipcode",
            "country",
            "is_primary",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class CustomerNoteSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = CustomerNote
        fields = ("id", "body", "author", "created_at")
        read_only_fields = ("id", "author", "created_at")


class InteractionSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Interaction
        fields = ("id", "kind", "description", "author", "created_at")
        read_only_fields = ("id", "author", "created_at")


class CustomerListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    assigned_to = serializers.SlugRelatedField(slug_field="username", read_only=True)
    tags = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)

    class Meta:
        model = Customer
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "document",
            "status",
            "source",
            "assigned_to",
            "tags",
            "created_at",
            "updated_at",
        )


class CustomerSerializer(serializers.ModelSerializer):
    source = serializers.PrimaryKeyRelatedField(
        queryset=LeadSource.objects.all(), required=False, allow_null=True
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    tags = serializers.SlugRelatedField(
        slug_field="name",
        many=True,
        required=False,
        queryset=CustomerTag.objects.all(),
    )
    contacts = CustomerContactSerializer(many=True, read_only=True)
    addresses = CustomerAddressSerializer(many=True, read_only=True)
    notes = CustomerNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "document",
            "status",
            "source",
            "assigned_to",
            "tags",
            "contacts",
            "addresses",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class LeadSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    status = serializers.SlugRelatedField(slug_field="code", read_only=True)
    assigned_to = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Lead
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "document",
            "source",
            "status",
            "assigned_to",
            "notes",
            "lost_reason",
            "converted_customer",
            "converted_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class LeadWriteSerializer(serializers.ModelSerializer):
    source = serializers.PrimaryKeyRelatedField(
        queryset=LeadSource.objects.all(), required=False, allow_null=True
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Lead
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "document",
            "source",
            "assigned_to",
            "notes",
        )
        read_only_fields = ("id",)


class LeadStatusUpdateSerializer(serializers.Serializer):
    status = serializers.SlugRelatedField(
        slug_field="code", queryset=LeadStatus.objects.all()
    )
    reason = serializers.CharField(required=False, allow_blank=True, default="")
