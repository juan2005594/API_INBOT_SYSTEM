from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from .models import (
    Categoria, Proveedor, Producto,
    FacturaCompra, DetalleFacturaCompra,
    Venta, DetalleVenta
)
from .serializers import (
    CategoriaSerializer, ProveedorSerializer, ProductoSerializer,
    FacturaCompraSerializer, DetalleFacturaCompraSerializer,
    VentaSerializer, DetalleVentaSerializer, LoginSerializer
)
from .utils.price_calculator import calcular_precio_venta
from .utils.inventory_validator import (
    validar_stock_disponible,
    validar_precio_venta,
    validar_factura_compra
)
from .utils.reports import (
    generar_reporte_ventas_diario,
    generar_reporte_inventario,
    generar_reporte_compras
)
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .permissions import IsAdminOrWarehouse, IsSeller
from django.db.utils import IntegrityError, DatabaseError

# Create your views here.

class CategoriaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrWarehouse]
    # ViewSet para la gestión de categorías.
    # Proporciona operaciones CRUD (Crear, Recuperar, Actualizar, Borrar) para el modelo Categoria.
    #
    # Endpoints:
    # - GET /api/categorias/
    #   Descripción: Recupera una lista de todas las categorías.
    #   Ejemplo de uso: Navega a http://127.0.0.1:8000/api/categorias/ en tu navegador.
    #
    # - POST /api/categorias/
    #   Descripción: Crea una nueva categoría.
    #   Cuerpo de la Petición (JSON): {"nombre": "Nombre de Categoria", "descripcion": "Descripción de la categoría"}
    #   Ejemplo de uso: Usa la interfaz de POST de DRF en http://127.0.0.1:8000/api/categorias/ con el JSON.
    #
    # - GET /api/categorias/{id}/
    #   Descripción: Recupera los detalles de una categoría específica.
    #   Ejemplo de uso: Navega a http://127.0.0.1:8000/api/categorias/1/ (reemplaza 1 con un ID existente).
    #
    # - PUT /api/categorias/{id}/
    #   Descripción: Actualiza todos los campos de una categoría específica.
    #   Cuerpo de la Petición (JSON): {"nombre": "Nuevo Nombre", "descripcion": "Nueva descripción"}
    #   Ejemplo de uso: Usa la interfaz de PUT de DRF en http://127.0.0.1:8000/api/categorias/{id}/.
    #
    # - PATCH /api/categorias/{id}/
    #   Descripción: Actualiza parcialmente los campos de una categoría específica.
    #   Cuerpo de la Petición (JSON): {"descripcion": "Solo actualiza la descripción"}
    #   Ejemplo de uso: Usa la interfaz de PATCH de DRF en http://127.0.0.1:8000/api/categorias/{id}/.
    #
    # - DELETE /api/categorias/{id}/
    #   Descripción: Elimina una categoría específica.
    #   Ejemplo de uso: Usa el botón DELETE en la interfaz de DRF en http://127.0.0.1:8000/api/categorias/{id}/.
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProveedorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrWarehouse]
    # ViewSet para la gestión de proveedores.
    # Proporciona operaciones CRUD (Crear, Recuperar, Actualizar, Borrar) para el modelo Proveedor.
    #
    # Endpoints:
    # - GET /api/proveedores/
    #   Descripción: Recupera una lista de todos los proveedores.
    #   Ejemplo de uso: http://127.0.0.1:8000/api/proveedores/
    #
    # - POST /api/proveedores/
    #   Descripción: Crea un nuevo proveedor.
    #   Cuerpo de la Petición (JSON): {"nombre": "Proveedor XYZ", "nit": "123456789", "telefono": "1234567890", "direccion": "Calle Falsa 123", "email": "contacto@xyz.com"}
    #
    # - GET /api/proveedores/{id}/
    #   Descripción: Recupera los detalles de un proveedor específico.
    #
    # - PUT /api/proveedores/{id}/
    #   Descripción: Actualiza todos los campos de un proveedor.
    #
    # - PATCH /api/proveedores/{id}/
    #   Descripción: Actualiza parcialmente los campos de un proveedor.
    #
    # - DELETE /api/proveedores/{id}/
    #   Descripción: Elimina un proveedor específico.
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'stock_bajo', 'buscar_codigo']:
            self.permission_classes = [IsAdminOrWarehouse | IsSeller]
        else:
            self.permission_classes = [IsAdminOrWarehouse]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        # Calcular precio de venta automáticamente
        instance = serializer.save()
        initial_precio_venta = calcular_precio_venta(
            instance.precio_compra,
            instance.porcentaje_ganancia
        )

        # Aplicar lógica de redondeo a la unidad de mil más cercana si supera los 500
        initial_precio_venta = Decimal(str(initial_precio_venta)) # Asegurar que es un Decimal
        
        remainder = initial_precio_venta % 1000
        if remainder > Decimal('500'):
            instance.precio_venta = (initial_precio_venta - remainder) + Decimal('1000')
        else:
            instance.precio_venta = initial_precio_venta
        
        # Redondear a 2 decimales para consistencia, aunque con esta lógica de miles debería ser entero
        instance.precio_venta = instance.precio_venta.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        instance.save()

    @action(detail=False, methods=['get'])
    def stock_bajo(self, request):
        productos = Producto.objects.filter(stock_actual__lte=F('stock_minimo'))
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def buscar_codigo(self, request):
        codigo = request.query_params.get('codigo', None)
        if codigo:
            productos = Producto.objects.filter(codigo_barras__icontains=codigo)
            serializer = self.get_serializer(productos, many=True)
            return Response(serializer.data)
        return Response({'error': 'Código no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)

class FacturaCompraViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrWarehouse]
    # ViewSet para la gestión de facturas de compra.
    # Permite crear y recuperar facturas de compra, incluyendo sus detalles.
    #
    # Endpoints CRUD básicos:
    # - GET /api/facturas-compra/
    # - POST /api/facturas-compra/
    #   Cuerpo de la Petición (JSON) para POST:
    #   {
    #       "proveedor": 1,  # ID del proveedor
    #       "numero_factura": "FC001",
    #       "fecha_compra": "2024-06-09",
    #       "detalles": [
    #           {"producto": 1, "cantidad": 10, "precio_unitario": 50.00},
    #           {"producto": 2, "cantidad": 5, "precio_unitario": 20.00}
    #       ]
    #   }
    #   Nota: Los 'detalles' son una lista anidada y se procesan en el método `create` personalizado.
    # - GET /api/facturas-compra/{id}/
    # - PUT /api/facturas-compra/{id}/ (Requiere enviar todos los campos)
    # - PATCH /api/facturas-compra/{id}/ (Actualización parcial)
    # - DELETE /api/facturas-compra/{id}/
    queryset = FacturaCompra.objects.all()
    serializer_class = FacturaCompraSerializer

    def create(self, request, *args, **kwargs):
        # Lógica personalizada para crear una factura de compra y sus detalles.
        # Valida los detalles y actualiza el stock del producto al crear un detalle de factura.
        data = request.data.copy() # Crear una copia mutable de request.data
        detalles_data = data.pop('detalles', [])
        
        # Validar detalles de la factura
        es_valido, mensaje = validar_factura_compra(detalles_data)
        if not es_valido:
            return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)

        # Re-agregar los detalles a `data` para que el serializer los procese
        data['detalles'] = detalles_data

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # El método create del serializador ya maneja la creación de detalles y el cálculo del total
        factura = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class VentaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSeller | IsAdminOrWarehouse]
    # ViewSet para la gestión de ventas.
    # Permite crear y recuperar ventas, incluyendo sus detalles, y generar reportes.
    #
    # Endpoints CRUD básicos:
    # - GET /api/ventas/
    # - POST /api/ventas/
    #   Cuerpo de la Petición (JSON) para POST:
    #   {
    #       "metodo_pago": "Tarjeta",
    #       "vendedor": "Juan Pérez",
    #       "detalles": [
    #           {"producto": 1, "cantidad": 2, "precio_unitario": 120.00},
    #           {"producto": 3, "cantidad": 1, "precio_unitario": 75.00}
    #       ]
    #   }
    #   Nota: Los 'detalles' son una lista anidada y se procesan en el método `create` personalizado.
    #         También valida el stock antes de crear la venta.
    # - GET /api/ventas/{id}/
    # - PUT /api/ventas/{id}/ (Requiere enviar todos los campos)
    # - PATCH /api/ventas/{id}/ (Actualización parcial)
    # - DELETE /api/ventas/{id}/
    #
    # Acciones Personalizadas:
    # - GET /api/ventas/reporte_ventas/?fecha=YYYY-MM-DD
    #   Descripción: Genera un reporte de ventas para una fecha específica.
    #   Ejemplo de uso: http://127.0.0.1:8000/api/ventas/reporte_ventas/?fecha=2024-06-09
    #
    # - GET /api/ventas/reporte_inventario/
    #   Descripción: Genera un reporte completo del inventario actual.
    #   Ejemplo de uso: http://127.0.0.1:8000/api/ventas/reporte_inventario/
    #
    # - GET /api/ventas/reporte_compras/?mes={mes}&año={año}
    #   Descripción: Genera un reporte de compras por mes y año.
    #   Ejemplo de uso: http://127.0.0.1:8000/api/ventas/reporte_compras/?mes=6&año=2024
    #
    # - GET /api/ventas/ventas_dia/
    #   Descripción: Obtiene el total de ventas y la cantidad de ventas para el día actual.
    #   Ejemplo de uso: http://127.0.0.1:8000/api/ventas/ventas_dia/
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

    def create(self, request, *args, **kwargs):
        print(f"DEBUG: VentaViewSet.create - Datos recibidos: {request.data}")
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            print(f"DEBUG: VentaViewSet.create - Venta creada exitosamente: {serializer.instance.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            print(f"DEBUG: VentaViewSet.create - Error de validación: {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            print(f"DEBUG: VentaViewSet.create - Error de integridad de la base de datos: {e}")
            return Response({'error': f'Error de integridad de la base de datos: {str(e)}'}, status=status.HTTP_409_CONFLICT)
        except DatabaseError as e:
            print(f"DEBUG: VentaViewSet.create - Error de base de datos: {e}")
            return Response({'error': f'Error de base de datos: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f"DEBUG: VentaViewSet.create - Error inesperado: {e}")
            return Response({'error': f'Error inesperado del servidor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def reporte_ventas(self, request):
        fecha_str = request.query_params.get('fecha')
        # Descomentado la generación de reporte
        if not fecha_str:
            return Response({'error': 'Se requiere el parámetro fecha (YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            reporte = generar_reporte_ventas_diario(fecha_str)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(reporte)

    @action(detail=False, methods=['get'])
    def reporte_inventario(self, request):
        # Descomentado la generación de reporte
        reporte = generar_reporte_inventario()
        return Response(reporte)

    @action(detail=False, methods=['get'])
    def reporte_compras(self, request):
        mes = request.query_params.get('mes')
        año = request.query_params.get('año')
        # Descomentado la generación de reporte
        if not mes or not año:
            return Response({'error': 'Se requieren los parámetros mes y año'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            reporte = generar_reporte_compras(int(mes), int(año))
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(reporte)

    @action(detail=False, methods=['get'])
    def ventas_dia(self, request):
        hoy = timezone.localdate()
        ventas_hoy = Venta.objects.filter(fecha_venta__date=hoy)
        
        total_ventas_dia = ventas_hoy.aggregate(Sum('total'))['total__sum'] or 0
        cantidad_ventas_dia = ventas_hoy.count()

        return Response({
            'fecha': hoy.strftime('%Y-%m-%d'),
            'total_ventas_dia': float(total_ventas_dia),
            'cantidad_ventas_dia': cantidad_ventas_dia
        })

class LoginView(APIView):
    permission_classes = []  # No requiere permisos para el login
    authentication_classes = []  # No requiere autenticación para el login
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                token, created = Token.objects.get_or_create(user=user)
                user_groups = list(user.groups.values_list('name', flat=True))
                return Response({
                    'token': token.key,
                    'user_id': user.pk,
                    'username': user.username,
                    'groups': user_groups,
                    'is_staff': user.is_staff
                })
            else:
                return Response({'error': 'Usuario inactivo'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
