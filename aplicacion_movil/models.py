from django.conf import settings
from django.db import models


class ChatSession(models.Model):
    STATE_IDLE = 'idle'
    STATE_AWAITING_PHOTO = 'awaiting_photo'
    STATE_CHOICES = [
        (STATE_IDLE, 'Normal'),
        (STATE_AWAITING_PHOTO, 'Esperando foto'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
    )
    estado = models.CharField(max_length=30, choices=STATE_CHOICES, default=STATE_IDLE)
    contexto = models.JSONField(default=dict, blank=True)
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-actualizada_en']

    def __str__(self):
        return f'Chat {self.id} - {self.usuario.username}'


class ChatMessage(models.Model):
    ROLE_USER = 'user'
    ROLE_BOT = 'bot'
    ROLE_CHOICES = [
        (ROLE_USER, 'Usuario'),
        (ROLE_BOT, 'Bot'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='mensajes',
    )
    rol = models.CharField(max_length=10, choices=ROLE_CHOICES)
    texto = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='chat/', blank=True, null=True)
    intent = models.CharField(max_length=50, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['creado_en']

    def __str__(self):
        preview = self.texto[:40] if self.texto else '[imagen]'
        return f'{self.rol}: {preview}'
