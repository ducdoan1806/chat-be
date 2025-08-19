from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, ConversationParticipantViewSet

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet)
router.register(r"messages", MessageViewSet)
router.register(r"participants", ConversationParticipantViewSet)

urlpatterns = [
    path("/", include(router.urls)),
]
