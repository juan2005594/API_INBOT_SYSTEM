from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Union
from django.db.models import Sum, Count, F, Q
from django.utils import timezone

from ..models import Producto, Venta, DetalleVenta, FacturaCompra


def _coerce_report_date(fecha: Union[None, str, date, datetime]) -> date:
    if fecha is None:
        return timezone.localdate()
    if isinstance(fecha, datetime):
        return timezone.localdate(fecha) if timezone.is_aware(fecha) else fecha.date()
    if isinstance(fecha, date):
        return fecha
    if isinstance(fecha, str):
        return datetime.strptime(fecha.strip(), '%Y-%m-%d').date()
    raise ValueError('Formato de fecha inválido. Use YYYY-MM-DD.')


def generar_reporte_ventas_diario(fecha: Union[None, str, date, datetime] = None) -> Dict:
    """
    Genera un reporte de ventas del día especificado.
    
    Args:
        fecha (datetime, optional): Fecha del reporte. Defaults to today.
        
    Returns:
        Dict: Datos del reporte
    """
    fecha = _coerce_report_date(fecha)

    ventas = Venta.objects.filter(fecha_venta__date=fecha)
    total_ventas = ventas.aggregate(total=Sum('total'))['total'] or Decimal('0')
    cantidad_ventas = ventas.count()
    
    # Productos más vendidos
    productos_mas_vendidos = DetalleVenta.objects.filter(
        venta__fecha_venta__date=fecha
    ).values(
        'producto__nombre'
    ).annotate(
        cantidad=Sum('cantidad'),
        total=Sum('subtotal')
    ).order_by('-cantidad')[:5]
    
    return {
        'fecha': fecha,
        'total_ventas': total_ventas,
        'cantidad_ventas': cantidad_ventas,
        'productos_mas_vendidos': list(productos_mas_vendidos)
    }

def generar_reporte_inventario() -> Dict:
    """
    Genera un reporte completo del estado actual del inventario, incluyendo:
    - Todos los productos con su información relevante.
    - Productos con stock bajo.
    - Productos más vendidos.
    - Productos con mayor stock.
    """
    # 1. Todos los productos con información relevante
    all_products = Producto.objects.select_related('categoria', 'proveedor').annotate(
        total_vendido=Sum('detalleventa__cantidad', default=0) # Sumar la cantidad vendida de este producto
    ).order_by('nombre')

    productos_data = []
    for p in all_products:
        productos_data.append({
            'id': p.id,
            'nombre': p.nombre,
            'codigo_barras': p.codigo_barras,
            'descripcion': p.descripcion,
            'precio_compra': float(p.precio_compra),
            'precio_venta': float(p.precio_venta),
            'stock_actual': p.stock_actual,
            'stock_minimo': p.stock_minimo,
            'categoria': p.categoria.nombre,
            'proveedor': p.proveedor.nombre,
            'total_vendido': p.total_vendido,
            'estado_stock': 'Bajo' if p.stock_actual <= p.stock_minimo else 'Normal'
        })

    # 2. Productos con stock bajo (ya existente, pero actualizado con la nueva query)
    productos_bajo_stock = [p for p in productos_data if p['estado_stock'] == 'Bajo']

    # 3. Productos más vendidos (basado en total_vendido)
    productos_mas_vendidos = sorted(productos_data, key=lambda x: x['total_vendido'], reverse=True)[:10] # Top 10

    # 4. Productos con mayor stock
    productos_mayor_stock = sorted(productos_data, key=lambda x: x['stock_actual'], reverse=True)[:10] # Top 10

    total_productos = all_products.count()
    valor_total_inventario = all_products.aggregate(
        total=Sum(F('stock_actual') * F('precio_compra'))
    )['total'] or Decimal('0')

    return {
        'total_productos': total_productos,
        'valor_total_inventario': float(valor_total_inventario),
        'productos_list': productos_data,
        'productos_bajo_stock': productos_bajo_stock,
        'productos_mas_vendidos': productos_mas_vendidos,
        'productos_mayor_stock': productos_mayor_stock
    }

def generar_reporte_compras(mes: int = None, año: int = None) -> Dict:
    """
    Genera un reporte de compras del mes especificado.
    
    Args:
        mes (int, optional): Mes del reporte. Defaults to current month.
        año (int, optional): Año del reporte. Defaults to current year.
        
    Returns:
        Dict: Datos del reporte
    """
    if mes is None:
        mes = timezone.now().month
    if año is None:
        año = timezone.now().year
    
    compras = FacturaCompra.objects.filter(
        fecha_compra__month=mes,
        fecha_compra__year=año
    )
    
    total_compras = compras.aggregate(total=Sum('total'))['total'] or Decimal('0')
    cantidad_compras = compras.count()
    
    # Proveedores más frecuentes
    proveedores_frecuentes = compras.values(
        'proveedor__nombre'
    ).annotate(
        total_compras=Count('id'),
        monto_total=Sum('total')
    ).order_by('-monto_total')[:5]
    
    return {
        'mes': mes,
        'año': año,
        'total_compras': total_compras,
        'cantidad_compras': cantidad_compras,
        'proveedores_frecuentes': list(proveedores_frecuentes)
    } 