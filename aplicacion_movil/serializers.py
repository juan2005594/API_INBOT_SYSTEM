from rest_framework import serializers

from .models import ChatMessage, ChatSession


class ChatMessageSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'rol',
            'texto',
            'intent',
            'metadata',
            'imagen_url',
            'creado_en',
        ]
        read_only_fields = fields

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get('request')
        url = obj.imagen.url
        if request:
            return request.build_absolute_uri(url)
        return url


class ChatSessionSerializer(serializers.ModelSerializer):
    mensajes = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            'id',
            'estado',
            'contexto',
            'activa',
            'creada_en',
            'actualizada_en',
            'mensajes',
        ]
        read_only_fields = [
            'id',
            'estado',
            'contexto',
            'creada_en',
            'actualizada_en',
            'mensajes',
        ]


class ChatIncomingMessageSerializer(serializers.Serializer):
    texto = serializers.CharField(required=False, allow_blank=True, max_length=4000)
    imagen = serializers.ImageField(required=False, allow_null=True)

    def validate(self, attrs):
        texto = (attrs.get('texto') or '').strip()
        imagen = attrs.get('imagen')
        if not texto and not imagen:
            raise serializers.ValidationError(
                'Envía un texto o una imagen para continuar la conversación.'
            )
        attrs['texto'] = texto
        return attrs
