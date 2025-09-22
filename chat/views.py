from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message, ConversationParticipant
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CurrentUserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


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

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user).order_by("-created_at")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        part, _ = ConversationParticipant.objects.get_or_create(
            conversation=instance, user=user
        )
        if part:
            part.last_checked_at = datetime.now()
            part.save()
        return Response(
            ConversationSerializer(instance, context={"request": request}).data
        )


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

    @action(detail=False, methods=["post"], url_path="mark-as-read")
    def mark_as_read(self, request):
        """
        Cập nhật trạng thái 'read' cho list message IDs gửi lên
        """
        ids = request.data.get("ids", [])
        if not isinstance(ids, list) or not ids:
            return Response(
                {"error": "ids must be a non-empty array"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update messages thuộc về user (an toàn hơn)
        updated_messages = Message.objects.filter(id__in=ids)

        count = updated_messages.update(read=True)

        serializer = MessageSerializer(updated_messages, many=True)
        return Response(
            {"updated_count": count, "messages": serializer.data},
            status=status.HTTP_200_OK,
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
