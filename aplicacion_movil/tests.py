from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.models import Categoria, Producto, Proveedor

from .models import ChatMessage, ChatSession


class ChatbotAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vendedor', password='test1234')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        categoria = Categoria.objects.create(nombre='Bebidas', descripcion='')
        proveedor = Proveedor.objects.create(
            nombre='Proveedor Test',
            nit='900123456',
            telefono='3000000000',
            direccion='Calle 1',
        )
        Producto.objects.create(
            codigo_barras='7701234567890',
            nombre='Gaseosa Cola',
            descripcion='Refresco',
            categoria=categoria,
            proveedor=proveedor,
            precio_compra=2000,
            porcentaje_ganancia=25,
            stock_actual=10,
            stock_minimo=5,
        )

    def test_iniciar_chat_crea_sesion(self):
        url = reverse('mobile_api:chat-session-iniciar')
        response = self.client.post(url)
        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))
        self.assertTrue(ChatSession.objects.filter(usuario=self.user, activa=True).exists())

    def test_mensaje_buscar_producto(self):
        iniciar = reverse('mobile_api:chat-session-iniciar')
        session_resp = self.client.post(iniciar)
        session_id = session_resp.data['session']['id']

        url = reverse('mobile_api:chat-session-mensaje', args=[session_id])
        response = self.client.post(url, {'texto': 'buscar gaseosa'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['intent'], 'buscar_producto')
        self.assertIn('Gaseosa Cola', response.data['bot_message']['texto'])
        self.assertEqual(ChatMessage.objects.filter(session_id=session_id).count(), 3)

    def test_validar_imagen_requiere_archivo(self):
        url = reverse('mobile_api:chat-validar-imagen')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mensaje_ventas_hoy(self):
        iniciar = reverse('mobile_api:chat-session-iniciar')
        session_resp = self.client.post(iniciar)
        session_id = session_resp.data['session']['id']

        url = reverse('mobile_api:chat-session-mensaje', args=[session_id])
        response = self.client.post(url, {'texto': 'ventas de hoy'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['intent'], 'ventas_hoy')
        self.assertIn('Ventas de hoy', response.data['bot_message']['texto'])
        meta = response.data['bot_message']['metadata']
        self.assertIn('total_ventas', meta)
        self.assertIsInstance(meta['total_ventas'], (int, float))
