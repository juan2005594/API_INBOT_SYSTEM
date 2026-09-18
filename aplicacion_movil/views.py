from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatMessage, ChatSession
from .serializers import (
    ChatIncomingMessageSerializer,
    ChatMessageSerializer,
    ChatSessionSerializer,
)
from .services.chatbot import process_chat_turn
from .services.visual_validator import validate_product_image


def health(request):
    return JsonResponse({"status": "ok"})


class ChatSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """Sesiones de chat del usuario autenticado."""

    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            ChatSession.objects.filter(usuario=self.request.user)
            .prefetch_related('mensajes')
        )

    @action(detail=False, methods=['post'])
    def iniciar(self, request):
        """Obtiene la sesión activa o crea una nueva con mensaje de bienvenida."""
        session = (
            ChatSession.objects.filter(usuario=request.user, activa=True)
            .order_by('-actualizada_en')
            .first()
        )
        created = False
        if not session:
            session = ChatSession.objects.create(usuario=request.user)
            created = True
            ChatMessage.objects.create(
                session=session,
                rol=ChatMessage.ROLE_BOT,
                texto=(
                    '¡Bienvenido al chat de INBOTF! Escribe "ayuda" para ver '
                    'lo que puedo hacer por ti.'
                ),
                intent='saludo',
            )

        data = ChatSessionSerializer(session, context={'request': request}).data
        return Response(
            {'session': data, 'created': created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=['post'],
        parser_classes=[MultiPartParser, FormParser, JSONParser],
        url_path='mensaje',
    )
    def mensaje(self, request, pk=None):
        session = self.get_object()
        if not session.activa:
            return Response(
                {'detail': 'Esta sesión de chat está cerrada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        incoming = ChatIncomingMessageSerializer(data=request.data)
        incoming.is_valid(raise_exception=True)
        texto = incoming.validated_data.get('texto', '')
        imagen = incoming.validated_data.get('imagen')

        user_message = ChatMessage.objects.create(
            session=session,
            rol=ChatMessage.ROLE_USER,
            texto=texto,
            imagen=imagen,
        )

        intent, reply, metadata = process_chat_turn(session, texto=texto, imagen=imagen)

        bot_message = ChatMessage.objects.create(
            session=session,
            rol=ChatMessage.ROLE_BOT,
            texto=reply,
            intent=intent,
            metadata=metadata,
        )

        session.save(update_fields=['actualizada_en'])

        return Response(
            {
                'session_id': session.id,
                'intent': intent,
                'user_message': ChatMessageSerializer(
                    user_message, context={'request': request}
                ).data,
                'bot_message': ChatMessageSerializer(
                    bot_message, context={'request': request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        session = self.get_object()
        session.activa = False
        session.estado = ChatSession.STATE_IDLE
        session.save(update_fields=['activa', 'estado', 'actualizada_en'])
        ChatMessage.objects.create(
            session=session,
            rol=ChatMessage.ROLE_BOT,
            texto='Sesión cerrada. Cuando quieras, inicia una nueva conversación.',
            intent='cerrar',
        )
        return Response({'detail': 'Sesión cerrada.'})


class ValidarImagenView(APIView):
    """Validación rápida de producto por imagen (sin sesión de chat)."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        imagen = request.FILES.get('imagen')
        if not imagen:
            return Response(
                {'detail': 'Debes enviar el archivo "imagen".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = validate_product_image(imagen)
        return Response(result)
