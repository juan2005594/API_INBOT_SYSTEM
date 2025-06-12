from decimal import Decimal
from typing import Dict, List, Tuple
from api.models import Producto

def validar_stock_disponible(producto_id: int, cantidad_solicitada: int) -> Tuple[bool, str]:
    """
    Valida si hay suficiente stock disponible para una venta.
    
    Args:
        producto_id (int): ID del producto.
        cantidad_solicitada (int): Cantidad que se desea vender.
        
    Returns:
        Tuple[bool, str]: (Es válido, Mensaje de error)
    """
    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return False, "Producto no encontrado."

    if cantidad_solicitada <= 0:
        return False, "La cantidad solicitada debe ser mayor a 0"
    if producto.stock_actual < cantidad_solicitada:
        return False, f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}"

    # Validar que el stock resultante no sea menor que el stock mínimo
    stock_resultante = producto.stock_actual - cantidad_solicitada
    if stock_resultante < producto.stock_minimo:
        return False, f"La venta de {cantidad_solicitada} unidades de {producto.nombre} dejaría el stock ({stock_resultante}) por debajo del mínimo ({producto.stock_minimo})."

    return True, ""

def validar_precio_venta(producto_id: int, precio_unitario_venta: Decimal) -> Tuple[bool, str]:
    """
    Valida si el precio unitario de la venta es válido en relación al precio de venta del producto.
    
    Args:
        producto_id (int): ID del producto.
        precio_unitario_venta (Decimal): Precio unitario ingresado en la venta.
        
    Returns:
        Tuple[bool, str]: (Es válido, Mensaje de error)
    """
    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return False, "Producto no encontrado."

    if precio_unitario_venta <= 0:
        return False, "El precio unitario de la venta debe ser mayor a 0"
    # El precio unitario de la venta debe ser igual o mayor al precio de venta del producto
    if precio_unitario_venta < producto.precio_venta:
        return False, f"El precio unitario de la venta ({precio_unitario_venta}) debe ser igual o mayor al precio de venta del producto ({producto.precio_venta})."
    return True, ""

def validar_factura_compra(detalles: List[Dict]) -> Tuple[bool, str]:
    """
    Valida los detalles de una factura de compra.
    
    Args:
        detalles (List[Dict]): Lista de detalles de la factura
        
    Returns:
        Tuple[bool, str]: (Es válido, Mensaje de error)
    """
    if not detalles:
        return False, "La factura debe tener al menos un detalle"
    
    for detalle in detalles:
        if not all(key in detalle for key in ['producto', 'cantidad', 'precio_unitario']):
            return False, "Cada detalle debe tener producto, cantidad y precio unitario"
        
        try:
            cantidad = int(detalle['cantidad'])
            precio_unitario = Decimal(detalle['precio_unitario'])
        except (ValueError, TypeError):
            return False, "La cantidad y el precio unitario deben ser números válidos."

        if cantidad <= 0:
            return False, "La cantidad debe ser mayor a 0"
        if precio_unitario <= 0:
            return False, "El precio unitario debe ser mayor a 0"
    
    return True, "" 