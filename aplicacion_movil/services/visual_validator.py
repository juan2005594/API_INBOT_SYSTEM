from io import BytesIO

from PIL import Image

from api.models import Producto

HASH_SIZE = 8
VISUAL_MATCH_THRESHOLD = 0.72
VISUAL_CANDIDATE_THRESHOLD = 0.60


def _average_hash(image: Image.Image, hash_size: int = HASH_SIZE) -> str:
    img = image.convert('L').resize((hash_size, hash_size), Image.Resampling.LANCZOS)
    pixels = list(img.getdata())
    avg = sum(pixels) / len(pixels)
    return ''.join('1' if pixel > avg else '0' for pixel in pixels)


def _hamming_similarity(hash_a: str, hash_b: str) -> float:
    if len(hash_a) != len(hash_b) or not hash_a:
        return 0.0
    distance = sum(a != b for a, b in zip(hash_a, hash_b))
    return 1.0 - (distance / len(hash_a))


def _decode_barcode(image: Image.Image) -> str | None:
    try:
        from pyzbar.pyzbar import decode

        for result in decode(image):
            value = result.data.decode('utf-8', errors='ignore').strip()
            if value:
                return value
    except Exception:
        return None
    return None


def _product_payload(producto: Producto, confidence: float, method: str) -> dict:
    imagen_url = producto.imagen.url if producto.imagen else None
    return {
        'id': producto.id,
        'nombre': producto.nombre,
        'codigo_barras': producto.codigo_barras,
        'precio_venta': float(producto.precio_venta),
        'stock_actual': producto.stock_actual,
        'stock_minimo': producto.stock_minimo,
        'categoria': producto.categoria.nombre,
        'imagen': imagen_url,
        'confidence': round(confidence, 3),
        'method': method,
    }


def _find_by_barcode(barcode: str) -> dict | None:
    producto = Producto.objects.filter(codigo_barras=barcode).first()
    if not producto:
        producto = Producto.objects.filter(codigo_barras__icontains=barcode).first()
    if not producto:
        return None
    return _product_payload(producto, 1.0, 'barcode')


def _find_by_visual_similarity(image: Image.Image) -> dict:
    uploaded_hash = _average_hash(image)
    candidates: list[tuple[float, Producto]] = []

    for producto in Producto.objects.exclude(imagen='').exclude(imagen__isnull=True):
        try:
            with producto.imagen.open('rb') as catalog_file:
                catalog_image = Image.open(catalog_file)
                catalog_hash = _average_hash(catalog_image)
                similarity = _hamming_similarity(uploaded_hash, catalog_hash)
                if similarity >= VISUAL_CANDIDATE_THRESHOLD:
                    candidates.append((similarity, producto))
        except Exception:
            continue

    candidates.sort(key=lambda item: item[0], reverse=True)

    if not candidates:
        return {
            'matched': False,
            'method': 'visual_similarity',
            'confidence': 0.0,
            'product': None,
            'alternatives': [],
            'message': 'No encontré coincidencias visuales en el catálogo.',
        }

    best_score, best_product = candidates[0]
    alternatives = [
        _product_payload(producto, score, 'visual_similarity')
        for score, producto in candidates[1:4]
    ]

    if best_score >= VISUAL_MATCH_THRESHOLD:
        return {
            'matched': True,
            'method': 'visual_similarity',
            'confidence': best_score,
            'product': _product_payload(best_product, best_score, 'visual_similarity'),
            'alternatives': alternatives,
            'message': 'Producto identificado por validación visual.',
        }

    return {
        'matched': False,
        'method': 'visual_similarity',
        'confidence': best_score,
        'product': None,
        'alternatives': [
            _product_payload(producto, score, 'visual_similarity')
            for score, producto in candidates[:3]
        ],
        'message': 'La foto se parece a algunos productos, pero no hay suficiente confianza.',
    }


def validate_product_image(uploaded_file) -> dict:
    uploaded_file.seek(0)
    image_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    try:
        image = Image.open(BytesIO(image_bytes))
        image.load()
    except Exception:
        return {
            'matched': False,
            'method': 'none',
            'confidence': 0.0,
            'product': None,
            'alternatives': [],
            'message': 'No pude leer la imagen. Intenta con otra foto más clara.',
        }

    barcode = _decode_barcode(image)
    if barcode:
        product = _find_by_barcode(barcode)
        if product:
            return {
                'matched': True,
                'method': 'barcode',
                'confidence': 1.0,
                'product': product,
                'alternatives': [],
                'message': 'Producto identificado por código de barras en la foto.',
            }

    return _find_by_visual_similarity(image)
