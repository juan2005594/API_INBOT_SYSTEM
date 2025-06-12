from decimal import Decimal

def calcular_precio_venta(precio_compra: Decimal, porcentaje_ganancia: Decimal) -> Decimal:
    """
    Calcula el precio de venta basado en el precio de compra y el porcentaje de ganancia.
    
    Args:
        precio_compra (Decimal): Precio de compra del producto
        porcentaje_ganancia (Decimal): Porcentaje de ganancia deseado
        
    Returns:
        Decimal: Precio de venta calculado
    """
    return precio_compra * (1 + porcentaje_ganancia / 100)

def calcular_ganancia(precio_venta: Decimal, precio_compra: Decimal) -> Decimal:
    """
    Calcula la ganancia en base al precio de venta y compra.
    
    Args:
        precio_venta (Decimal): Precio de venta del producto
        precio_compra (Decimal): Precio de compra del producto
        
    Returns:
        Decimal: Ganancia calculada
    """
    return precio_venta - precio_compra

def calcular_porcentaje_ganancia(precio_venta: Decimal, precio_compra: Decimal) -> Decimal:
    """
    Calcula el porcentaje de ganancia en base al precio de venta y compra.
    
    Args:
        precio_venta (Decimal): Precio de venta del producto
        precio_compra (Decimal): Precio de compra del producto
        
    Returns:
        Decimal: Porcentaje de ganancia calculado
    """
    if precio_compra == 0:
        return Decimal('0')
    return ((precio_venta - precio_compra) / precio_compra) * 100 