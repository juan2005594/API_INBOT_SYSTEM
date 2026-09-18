from django.contrib import admin

from .models import ChatMessage, ChatSession


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('rol', 'texto', 'intent', 'creado_en')


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'estado', 'activa', 'actualizada_en')
    list_filter = ('activa', 'estado')
    search_fields = ('usuario__username',)
    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'rol', 'intent', 'creado_en')
    list_filter = ('rol', 'intent')
    search_fields = ('texto',)
