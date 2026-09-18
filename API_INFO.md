# API de Sistema de Inventario - Documentación

## ✅ Estado del Proyecto
La API ha sido restaurada y está funcionando correctamente.

## 🚀 Inicio Rápido

### Iniciar el Servidor
```bash
.\venv\Scripts\python.exe manage.py runserver
```

El servidor estará disponible en: http://127.0.0.1:8000

### Crear un Superusuario
```bash
.\venv\Scripts\python.exe manage.py createsuperuser
```

### Crear Grupos de Usuarios
Para usar la API correctamente, necesitas crear los siguientes grupos:
- **Vendedor**: Para usuarios vendedores
- **Bodeguero**: Para usuarios de bodega

Crea los grupos desde el panel de administración de Django: http://127.0.0.1:8000/admin/

## 📡 Endpoints de la API

### Autenticación
- **POST** `/core-api/login/` - Iniciar sesión
- **POST** `/core-api/logout/` - Cerrar sesión

### Endpoints Principales
- **Categorías**: `/core-api/categorias/`
- **Proveedores**: `/core-api/proveedores/`
- **Productos**: `/core-api/productos/`
- **Facturas de Compra**: `/core-api/facturas-compra/`
- **Ventas**: `/core-api/ventas/`

### Endpoints de Acciones Especiales

#### Productos
- **GET** `/core-api/productos/stock_bajo/` - Productos con stock bajo
- **GET** `/core-api/productos/buscar_codigo/?codigo=XXX` - Buscar por código de barras

#### Ventas
- **GET** `/core-api/ventas/reporte_ventas/?fecha=YYYY-MM-DD` - Reporte diario de ventas
- **GET** `/core-api/ventas/reporte_inventario/` - Reporte completo de inventario
- **GET** `/core-api/ventas/reporte_compras/?mes=6&año=2024` - Reporte de compras
- **GET** `/core-api/ventas/ventas_dia/` - Ventas del día actual

## 🔐 Permisos

La API utiliza un sistema de permisos basado en grupos:

- **IsAdminOrWarehouse**: Administradores y usuarios de bodega pueden crear/editar
- **IsSeller**: Vendedores pueden crear ventas
- Todos pueden leer (list y retrieve)

## 💾 Base de Datos

La base de datos ha sido configurada para usar **SQLite** para desarrollo. 
Para volver a usar SQL Server, actualiza la configuración en `api_project/settings.py`.

## 📝 Modelos Principales

1. **Categoria** - Categorías de productos
2. **Proveedor** - Proveedores
3. **Producto** - Productos con:
   - Código de barras
   - Precio de compra y venta (calculado automáticamente)
   - Stock actual y mínimo
4. **FacturaCompra** - Facturas de compra
5. **DetalleFacturaCompra** - Detalles de facturas de compra
6. **Venta** - Ventas
7. **DetalleVenta** - Detalles de ventas

## 🎯 Características

- ✅ Cálculo automático de precios de venta basado en porcentaje de ganancia
- ✅ Control de stock (validación de stock disponible antes de ventas)
- ✅ Actualización automática de inventario al realizar compras o ventas
- ✅ Reportes de ventas, inventario y compras
- ✅ Autenticación por token
- ✅ Paginación (10 elementos por página)
- ✅ Filtrado y búsqueda

## 🔧 Tecnologías

- Django 5.0.14
- Django REST Framework 3.16.0
- Django Filter 25.1.0
- SQLite (desarrollo) / SQL Server (producción)
- Pillow (imágenes)
- python-docx (reportes)

## 📄 Interfaces Web

La API incluye interfaces web en:
- `/` - Página de login
- `/dashboard/` - Dashboard principal
- `/catalogo/` - Catálogo de productos
- `/categorias-lista/` - Lista de categorías
- `/proveedores-lista/` - Lista de proveedores
- `/facturas-compra-lista/` - Lista de facturas de compra
- `/ventas-lista/` - Lista de ventas

## 🐛 Debug

Los logs de la aplicación se encuentran en: `logs/debug.log`

