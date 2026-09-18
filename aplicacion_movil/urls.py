from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChatSessionViewSet, ValidarImagenView, health


app_name = 'mobile_api'

router = DefaultRouter()
router.register('chat/sessions', ChatSessionViewSet, basename='chat-session')

urlpatterns = [
    path('health/', health, name='health'),
    path('chat/validar-imagen/', ValidarImagenView.as_view(), name='chat-validar-imagen'),
    path('', include(router.urls)),
]
