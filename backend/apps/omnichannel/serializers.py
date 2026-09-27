"""Serializers do Omnichannel (ETAPA 3)."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.omnichannel.models import Conversation, ConversationMessage

User = get_user_model()


class ConversationSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SlugRelatedField(slug_field="username", read_only=True)
    customer = serializers.SlugRelatedField(slug_field="name", read_only=True)
    lead = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Conversation
        fields = (
            "id",
            "channel",
            "external_chat_id",
            "status",
            "assigned_to",
            "customer",
            "lead",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ConversationListSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SlugRelatedField(slug_field="username", read_only=True)
    customer = serializers.SlugRelatedField(slug_field="name", read_only=True)
    lead = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Conversation
        fields = (
            "id",
            "channel",
            "external_chat_id",
            "status",
            "assigned_to",
            "customer",
            "lead",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ConversationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = (
            "id",
            "conversation",
            "direction",
            "sender_kind",
            "body",
            "normalized_body",
            "telegram_message_id",
            "payload",
            "created_at",
        )
        read_only_fields = fields


class AssignConversationSerializer(serializers.Serializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class OutboundMessageSerializer(serializers.Serializer):
    body = serializers.CharField(allow_blank=False)
