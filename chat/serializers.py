from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message, ConversationParticipant


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class LastMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "body", "created_at", "sender", "read"]


class ConversationParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = ConversationParticipant
        fields = ["conversation", "user", "user_id"]


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    new_message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
            "participants",
            "last_message",
            "new_message_count",
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by("-created_at").first()
        if last_msg:
            return LastMessageSerializer(last_msg).data
        return None

    def get_new_message_count(self, obj):
        user = self.context.get("request").user
        check = ConversationParticipant.objects.get(
            conversation=obj, user=user
        ).last_checked_at
        if not user.is_authenticated or not check:
            return 0
        return (
            Message.objects.filter(conversation=obj, created_at__gt=check)
            .exclude(sender=user)
            .count()
        )


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="sender", write_only=True
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_id",
            "body",
            "read",
            "created_at",
        ]
