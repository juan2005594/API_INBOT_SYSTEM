from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Categoria, Proveedor, Producto, FacturaCompra, Venta, DetalleFacturaCompra, DetalleVenta
from django.contrib.auth.models import User
from decimal import Decimal

# Create your tests here.

class APITest(APITestCase):

    def setUp(self):
        # Create an admin user for authentication
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        self.client.login(username='admin', password='adminpassword')

        # Create dummy data for relationships
        self.categoria = Categoria.objects.create(
            nombre='Electrónica', descripcion='Productos electrónicos'
        )
        self.proveedor = Proveedor.objects.create(
            nombre='Tech Supplies', nit='123456789', telefono='1234567890',
            direccion='Calle Falsa 123', email='info@tech.com'
        )
        self.producto = Producto.objects.create(
            codigo_barras='PROD001', nombre='Laptop', descripcion='Portátil de alto rendimiento',
            categoria=self.categoria, proveedor=self.proveedor,
            precio_compra=Decimal('1000.00'), porcentaje_ganancia=Decimal('20.00'),
            stock_actual=50, stock_minimo=10
        )

        self.producto2 = Producto.objects.create(
            codigo_barras='PROD002', nombre='Mouse', descripcion='Mouse inalámbrico',
            categoria=self.categoria, proveedor=self.proveedor,
            precio_compra=Decimal('10.00'), porcentaje_ganancia=Decimal('50.00'),
            stock_actual=100, stock_minimo=20
        )

    def test_create_categoria(self):
        url = reverse('categoria-list')
        data = {'nombre': 'Ropa', 'descripcion': 'Artículos de vestir'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Categoria.objects.count(), 2) # Initial + new one
        self.assertEqual(Categoria.objects.get(nombre='Ropa').descripcion, 'Artículos de vestir')

    def test_create_proveedor(self):
        url = reverse('proveedor-list')
        data = {
            'nombre': 'Office Supplies Inc.',
            'nit': '987654321',
            'telefono': '0987654321',
            'direccion': 'Avenida Siempre Viva 456',
            'email': 'contact@office.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Proveedor.objects.count(), 2) # Initial + new one
        self.assertEqual(Proveedor.objects.get(nombre='Office Supplies Inc.').nit, '987654321')

    def test_create_producto(self):
        url = reverse('producto-list')
        data = {
            'codigo_barras': 'PROD003',
            'nombre': 'Monitor',
            'descripcion': 'Monitor de 27 pulgadas',
            'categoria': self.categoria.id,
            'proveedor': self.proveedor.id,
            'precio_compra': '250.00',
            'porcentaje_ganancia': '30.00',
            'stock_actual': 30,
            'stock_minimo': 5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 3) # Two initial + new one
        new_product = Producto.objects.get(codigo_barras='PROD003')
        self.assertEqual(new_product.nombre, 'Monitor')
        self.assertEqual(new_product.precio_venta, Decimal('325.00')) # 250 * (1 + 30/100)

    def test_create_factura_compra(self):
        url = reverse('facturacompra-list')
        initial_stock = self.producto.stock_actual
        data = {
            'numero_factura': 'FC001',
            'proveedor': self.proveedor.id,
            'fecha_compra': '2025-06-12',
            'detalles': [
                {
                    'producto': self.producto.id,
                    'cantidad': 10,
                    'precio_unitario': '950.00'
                },
                {
                    'producto': self.producto2.id,
                    'cantidad': 5,
                    'precio_unitario': '8.00'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FacturaCompra.objects.count(), 1)
        factura = FacturaCompra.objects.first()
        self.assertEqual(factura.detalles.count(), 2)
        self.assertEqual(factura.total, Decimal('9540.00')) # (10 * 950) + (5 * 8) = 9500 + 40 = 9540
        self.producto.refresh_from_db()
        self.producto2.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, initial_stock + 10)
        self.assertEqual(self.producto2.stock_actual, self.producto2.stock_actual + 5) # This should be the original stock + 5

    def test_create_venta(self):
        url = reverse('venta-list')
        initial_stock_prod1 = self.producto.stock_actual
        initial_stock_prod2 = self.producto2.stock_actual
        data = {
            'fecha_venta': '2025-06-12',
            'metodo_pago': 'Tarjeta',
            'vendedor': 'Juan Perez',
            'detalles': [
                {
                    'producto': self.producto.id,
                    'cantidad': 5,
                    'precio_unitario': str(self.producto.precio_venta)
                },
                {
                    'producto': self.producto2.id,
                    'cantidad': 2,
                    'precio_unitario': str(self.producto2.precio_venta)
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Venta.objects.count(), 1)
        venta = Venta.objects.first()
        self.assertEqual(venta.detalles.count(), 2)
        expected_total = (self.producto.precio_venta * 5) + (self.producto2.precio_venta * 2)
        self.assertEqual(venta.total, expected_total)
        self.producto.refresh_from_db()
        self.producto2.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, initial_stock_prod1 - 5)
        self.assertEqual(self.producto2.stock_actual, initial_stock_prod2 - 2)
