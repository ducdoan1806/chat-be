from django.db import models
from django.contrib.auth.models import User  # dùng User mặc định của Django


class Conversation(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    participants = models.ManyToManyField(
        User, through="ConversationParticipant", related_name="conversations"
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="conversation_participants"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversation_participants"
    )
    last_checked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("conversation", "user")

    def __str__(self):
        return f"{self.user.username} in {self.conversation.name}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    body = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.username} in {self.conversation.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.conversation.updated_at = self.created_at
        self.conversation.save()
