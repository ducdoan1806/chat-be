from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"conversations", ConversationViewSet)
router.register(r"messages", MessageViewSet)
router.register(r"participants", ConversationParticipantViewSet)
router.register(r"profile", CurrentUserViewSet, basename="profile")
urlpatterns = [
    path("", include(router.urls)),
]
