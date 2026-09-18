from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaViewSet, ProveedorViewSet, ProductoViewSet,
    FacturaCompraViewSet, VentaViewSet,
    LoginView, LogoutView
)

app_name = 'core_api'

# Configurar el router para las vistas basadas en ViewSet
router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'facturas-compra', FacturaCompraViewSet, basename='facturacompra')
router.register(r'ventas', VentaViewSet, basename='venta')

# URLs de autenticación y API
urlpatterns = [
    # URLs de autenticación
    path('login/', LoginView.as_view(), name='api_login'),
    path('logout/', LogoutView.as_view(), name='api_logout'),
    
    # URLs de la API
    path('', include(router.urls)),
] 