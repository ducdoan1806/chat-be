# chat/signals.py
import socketio
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message

# Kết nối tới Socket.IO server Node.js
sio = socketio.Client()

try:
    sio.connect("http://localhost:5000")
    print("✅ Django connected to Socket.IO server")
except Exception as e:
    print("⚠️ Could not connect to Socket.IO server:", e)


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    if created:
        print(f"📩 New message: {instance.content}")
        # Gửi event tới server Node.js
        sio.emit(
            "new_message",
            {
                "user": instance.user,
                "content": instance.content,
                "created_at": instance.created_at.isoformat(),
            },
        )
