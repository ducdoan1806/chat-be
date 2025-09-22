import socketio
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import *
import logging

# Kết nối tới Socket.IO server Node.js
sio = socketio.Client()

try:
    sio.connect("http://localhost:5000")
    print("✅ Django connected to Socket.IO server")
except Exception as e:
    print("⚠️ Could not connect to Socket.IO server:", e)

logger = logging.getLogger(__name__)


def get_user_ids_by_conversation(conversation_id):
    return list(
        ConversationParticipant.objects.filter(
            conversation_id=conversation_id
        ).values_list("user_id", flat=True)
    )


def emit_message_event(message):
    """Emit event khi có message mới."""
    user_ids = get_user_ids_by_conversation(message.conversation_id)

    sio.emit(
        "message",
        {
            "sender": message.sender_id,
            "conversation": message.conversation_id,
            "body": message.body,
            "created_at": message.created_at.isoformat(),
            "recipients": user_ids,
        },
    )


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    if created:
        logger.info("📩 New message: %s", instance.body)
        transaction.on_commit(lambda: emit_message_event(instance))
