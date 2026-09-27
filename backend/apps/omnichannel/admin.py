from django.contrib import admin

from .models import Conversation, ConversationMessage


class ConversationMessageInline(admin.TabularInline):
    model = ConversationMessage
    extra = 0
    fields = ("direction", "sender_kind", "body", "telegram_message_id", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "channel",
        "external_chat_id",
        "status",
        "assigned_to",
        "customer",
        "lead",
        "created_at",
    )
    list_filter = ("channel", "status")
    search_fields = ("external_chat_id",)
    inlines = (ConversationMessageInline,)


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "direction", "sender_kind", "created_at")
    list_filter = ("direction", "sender_kind")
    search_fields = ("body", "normalized_body")
