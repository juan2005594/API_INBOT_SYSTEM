import re
import unicodedata
from decimal import Decimal

from django.db.models import F, Q
from django.utils import timezone

from api.models import Producto
from api.utils.reports import generar_reporte_ventas_diario

from .visual_validator import validate_product_image

INTENT_SALUDO = 'saludo'
INTENT_AYUDA = 'ayuda'
INTENT_BUSCAR_PRODUCTO = 'buscar_producto'
INTENT_STOCK_BAJO = 'stock_bajo'
INTENT_VENTAS_HOY = 'ventas_hoy'
INTENT_IDENTIFICAR_FOTO = 'identificar_foto'
INTENT_DESCONOCIDO = 'desconocido'


def _normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize('NFD', text)
    return ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')


def detect_intent(text: str) -> tuple[str, dict]:
    normalized = _normalize(text)
    if not normalized:
        return INTENT_DESCONOCIDO, {}

    if re.search(r'\b(hola|buenas|buenos dias|buenas tardes|buenas noches|hey|saludos)\b', normalized):
        return INTENT_SALUDO, {}

    if re.search(r'\b(ayuda|comandos|que puedes|que puedo|menu|opciones)\b', normalized):
        return INTENT_AYUDA, {}

    if re.search(
        r'\b(stock bajo|inventario bajo|productos bajos|poco stock|faltantes)\b',
        normalized,
    ):
        return INTENT_STOCK_BAJO, {}

    if re.search(
        r'\b(ventas de hoy|ventas hoy|venta del dia|total vendido hoy|cuanto vendi)\b',
        normalized,
    ):
        return INTENT_VENTAS_HOY, {}

    if re.search(
        r'\b(foto|imagen|camara|escanear|codigo de barras|identificar producto|reconocer)\b',
        normalized,
    ):
        return INTENT_IDENTIFICAR_FOTO, {}

    query = _extract_product_query(normalized)
    if query:
        return INTENT_BUSCAR_PRODUCTO, {'query': query}

    if re.fullmatch(r'[\d\-]+', normalized.replace(' ', '')):
        return INTENT_BUSCAR_PRODUCTO, {'query': text.strip()}

    return INTENT_DESCONOCIDO, {}


def _extract_product_query(normalized: str) -> str | None:
    patterns = [
        r'(?:buscar|busca|encuentra|precio de|precio del|stock de|stock del|producto)\s+(.+)',
        r'(?:cuanto cuesta|cuanto vale|donde esta)\s+(.+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            query = match.group(1).strip(' ?!.')
            if len(query) >= 2:
                return query
    return None


def _json_safe_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _json_safe_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe_value(v) for v in value]
    return value


def _help_text() -> str:
    return (
        'Soy el asistente de INBOTF. Puedes escribirme:\n'
        '• "buscar [nombre o código]" — consultar producto\n'
        '• "stock bajo" — productos con inventario bajo\n'
        '• "ventas de hoy" — resumen del día\n'
        '• "identificar producto" — luego envía una foto del producto\n'
        '• Envía una imagen directamente para validación visual o código de barras'
    )


def _format_product(producto: Producto) -> str:
    estado = 'BAJO' if producto.stock_actual <= producto.stock_minimo else 'OK'
    return (
        f'{producto.nombre}\n'
        f'  Código: {producto.codigo_barras}\n'
        f'  Precio venta: ${producto.precio_venta:,.2f}\n'
        f'  Stock: {producto.stock_actual} (mín. {producto.stock_minimo}) — {estado}\n'
        f'  Categoría: {producto.categoria.nombre}'
    )


def _search_products(query: str, limit: int = 5) -> list[Producto]:
    return list(
        Producto.objects.filter(
            Q(nombre__icontains=query)
            | Q(codigo_barras__icontains=query)
            | Q(descripcion__icontains=query)
        )
        .select_related('categoria')
        .order_by('nombre')[:limit]
    )


def _handle_stock_bajo() -> tuple[str, dict]:
    productos = list(
        Producto.objects.filter(stock_actual__lte=F('stock_minimo'))
        .select_related('categoria')
        .order_by('stock_actual')[:10]
    )
    if not productos:
        return 'No hay productos con stock bajo en este momento.', {'count': 0}

    lines = [f'Hay {len(productos)} producto(s) con stock bajo:']
    for p in productos:
        lines.append(f'• {p.nombre}: {p.stock_actual}/{p.stock_minimo}')
    return '\n'.join(lines), {'count': len(productos), 'productos': [p.id for p in productos]}


def _handle_ventas_hoy() -> tuple[str, dict]:
    reporte = generar_reporte_ventas_diario(timezone.now().date())
    total = reporte['total_ventas']
    cantidad = reporte['cantidad_ventas']
    texto = (
        f'Ventas de hoy ({reporte["fecha"]}):\n'
        f'  Transacciones: {cantidad}\n'
        f'  Total: ${Decimal(total):,.2f}'
    )
    top = reporte.get('productos_mas_vendidos') or []
    if top:
        texto += '\n  Más vendidos:'
        for item in top[:3]:
            nombre = item.get('producto__nombre', 'Producto')
            qty = item.get('cantidad', 0)
            texto += f'\n  • {nombre}: {qty} uds.'
    metadata = {
        'fecha': str(reporte['fecha']),
        'total_ventas': float(reporte['total_ventas'] or 0),
        'cantidad_ventas': reporte['cantidad_ventas'],
    }
    return texto, _json_safe_value(metadata)


def _handle_buscar(query: str) -> tuple[str, dict]:
    productos = _search_products(query)
    if not productos:
        return f'No encontré productos que coincidan con "{query}".', {'query': query, 'found': 0}
    if len(productos) == 1:
        return _format_product(productos[0]), {'query': query, 'found': 1, 'product_id': productos[0].id}
    lines = [f'Encontré {len(productos)} coincidencias para "{query}":']
    for p in productos:
        lines.append(f'• {p.nombre} — ${p.precio_venta:,.2f}, stock {p.stock_actual}')
    return '\n'.join(lines), {'query': query, 'found': len(productos)}


def _handle_image(uploaded_file) -> tuple[str, dict]:
    result = validate_product_image(uploaded_file)
    metadata = {
        'validation': {
            'matched': result.get('matched'),
            'method': result.get('method'),
            'confidence': result.get('confidence'),
            'alternatives': result.get('alternatives', []),
        }
    }
    product = result.get('product')
    if product:
        metadata['validation']['product'] = product
        texto = (
            f'{result.get("message", "Producto identificado.")}\n\n'
            f'{product["nombre"]}\n'
            f'  Código: {product["codigo_barras"]}\n'
            f'  Precio: ${product["precio_venta"]:,.2f}\n'
            f'  Stock: {product["stock_actual"]}\n'
            f'  Confianza: {product.get("confidence", 0) * 100:.0f}%'
        )
        return texto, metadata

    alts = result.get('alternatives') or []
    texto = result.get('message', 'No pude identificar el producto.')
    if alts:
        texto += '\n\nPosibles coincidencias:'
        for alt in alts[:3]:
            texto += f'\n• {alt["nombre"]} ({alt.get("confidence", 0) * 100:.0f}%)'
    return texto, metadata


def process_chat_turn(session, texto: str = '', imagen=None) -> tuple[str, str, dict]:
    """
    Procesa un turno de conversación. Retorna (intent, respuesta_texto, metadata).
    """
    from aplicacion_movil.models import ChatSession

    texto = (texto or '').strip()

    if imagen is not None:
        reply, metadata = _handle_image(imagen)
        session.estado = ChatSession.STATE_IDLE
        session.contexto = {}
        session.save(update_fields=['estado', 'contexto', 'actualizada_en'])
        return 'validar_imagen', reply, metadata

    if session.estado == ChatSession.STATE_AWAITING_PHOTO:
        reply = 'Estoy esperando la foto del producto. Adjunta una imagen en tu mensaje.'
        return INTENT_IDENTIFICAR_FOTO, reply, {}

    intent, params = detect_intent(texto)

    if intent == INTENT_SALUDO:
        reply = (
            '¡Hola! Soy el asistente virtual de INBOTF.\n'
            'Puedo ayudarte con productos, stock e ventas del día.\n\n'
            + _help_text()
        )
    elif intent == INTENT_AYUDA:
        reply = _help_text()
    elif intent == INTENT_STOCK_BAJO:
        reply, extra = _handle_stock_bajo()
        params.update(extra)
    elif intent == INTENT_VENTAS_HOY:
        reply, extra = _handle_ventas_hoy()
        params.update(extra)
    elif intent == INTENT_BUSCAR_PRODUCTO:
        reply, extra = _handle_buscar(params.get('query', texto))
        params.update(extra)
    elif intent == INTENT_IDENTIFICAR_FOTO:
        session.estado = ChatSession.STATE_AWAITING_PHOTO
        session.save(update_fields=['estado', 'actualizada_en'])
        reply = 'Perfecto. Envíame una foto clara del producto o del código de barras.'
    else:
        reply = (
            'No entendí tu mensaje. Prueba con "ayuda" o "buscar [producto]".\n\n'
            + _help_text()
        )

    return intent, reply, params
