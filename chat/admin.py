from django.contrib import admin
from .models import Conversation, ConversationParticipant, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "user")
    list_filter = ("conversation", "user")
    search_fields = ("conversation__name", "user__username")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "body", "read", "created_at")
    list_filter = ("conversation", "sender", "read")
    search_fields = ("body", "conversation__name", "sender__username")
    readonly_fields = ("created_at",)
