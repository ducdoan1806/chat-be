from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message, ConversationParticipant
from rest_framework.pagination import PageNumberPagination
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    ConversationParticipantSerializer,
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by("-created_at")
    serializer_class = ConversationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["id", "name", "participants"]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by("-created_at")
    serializer_class = MessageSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["conversation", "sender", "read"]
    search_fields = ["body"]
    ordering_fields = ["created_at"]

    def perform_create(self, serializer):
        message = serializer.save()

        # broadcast qua channel layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{message.conversation.id}",
            {
                "type": "chat_message",
                "id": message.id,
                "message": message.body,
                "sender": message.sender.id,
                "created_at": str(message.created_at),
            },
        )


class ConversationParticipantViewSet(viewsets.ModelViewSet):
    queryset = ConversationParticipant.objects.all()
    serializer_class = ConversationParticipantSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["conversation", "user"]
    search_fields = ["user__username"]
    ordering_fields = ["conversation"]
