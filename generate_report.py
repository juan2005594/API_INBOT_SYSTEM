from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_heading_style(paragraph, level):
    paragraph.style = f'Heading {level}'
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in paragraph.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.bold = True

def append_evidence_section(doc):
    doc.add_page_break()
    heading = doc.add_paragraph('Evidencia de Pruebas Unitarias')
    set_heading_style(heading, 1)
    evidencias = [
        ('test_crear_usuario()', 'Verifica que se pueda registrar un usuario con datos válidos.'),
        ('test_autenticacion_usuario()', 'Valida que un usuario pueda iniciar sesión con credenciales válidas.'),
        ('test_crear_vehiculo()', 'Comprueba que se pueda registrar un vehículo con datos correctos.'),
        ('test_crear_conductor()', 'Valida que se registre un conductor y se relacione con un vehículo correctamente.'),
        ('test_crear_ruta()', 'Comprueba que se cree una ruta con horarios válidos y asociación con vehículo.'),
        ('test_calificar_servicio()', 'Verifica que un usuario pueda calificar un servicio finalizado.'),
        ('test_crear_producto()', 'Verifica que se pueda registrar un producto con datos válidos.'),
        ('test_crear_venta()', 'Comprueba que se pueda registrar una venta correctamente.'),
        ('test_actualizar_inventario()', 'Valida que el inventario se actualice correctamente tras una venta.'),
        ('test_gestion_clientes()', 'Verifica que se pueda registrar y listar clientes.'),
        ('test_gestion_proveedores()', 'Verifica que se pueda registrar y listar proveedores.'),
        ('test_gestion_categorias()', 'Verifica que se pueda registrar y listar categorías de productos.'),
        ('test_gestion_metodos_pago()', 'Verifica que se puedan registrar y listar métodos de pago.'),
        ('test_generar_reporte_ventas()', 'Comprueba que se generen reportes de ventas correctamente.'),
    ]
    for idx, (nombre, desc) in enumerate(evidencias, 1):
        doc.add_paragraph()
        p = doc.add_paragraph(f'{idx}. {nombre}')
        p.runs[0].font.bold = True
        doc.add_paragraph(f'Descripción: {desc}')
        doc.add_paragraph('Inserta aquí la imagen del código de la prueba')
        doc.add_paragraph(f'Figura {idx}. Código de la prueba {nombre}')

def create_apa_document():
    doc = Document()
    
    # Configurar márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # PORTADA APA
    doc.add_paragraph()
    portada = doc.add_paragraph()
    portada.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = portada.add_run('UNIVERSIDAD DE CUNDINAMARCA')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(16)
    run.bold = True
    doc.add_paragraph()
    titulo = doc.add_paragraph()
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = titulo.add_run('Reporte de Pruebas Unitarias\nSistema de Ventas (API)')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.bold = True
    doc.add_paragraph()
    estudiante = doc.add_paragraph()
    estudiante.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = estudiante.add_run('Presentado por: Pablo')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    doc.add_paragraph()
    profesor = doc.add_paragraph()
    profesor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = profesor.add_run('Profesor: [Nombre del Profesor]')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    doc.add_paragraph()
    curso = doc.add_paragraph()
    curso.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = curso.add_run('Facultad de Ingeniería - Programa de Ingeniería de Sistemas')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    doc.add_paragraph()
    fecha = doc.add_paragraph()
    fecha.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fecha.add_run('Junio, 2024')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    # Salto de página
    doc.add_page_break()

    # Título
    title = doc.add_paragraph()
    title_run = title.add_run('Reporte de Pruebas Unitarias - API Sistema de Ventas')
    title_run.font.name = 'Times New Roman'
    title_run.font.size = Pt(14)
    title_run.font.bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Resumen Ejecutivo
    doc.add_paragraph()
    heading = doc.add_paragraph('Resumen Ejecutivo')
    set_heading_style(heading, 1)
    doc.add_paragraph('Este documento presenta los resultados de las pruebas unitarias realizadas al sistema de API para el manejo de ventas. Todas las pruebas ejecutadas sobre los diferentes módulos y servicios han sido exitosas, demostrando la robustez y confiabilidad del sistema.')

    # Metodología
    doc.add_paragraph()
    heading = doc.add_paragraph('Metodología')
    set_heading_style(heading, 1)
    doc.add_paragraph('Se implementaron pruebas unitarias utilizando el framework de pruebas de Django y Django REST Framework. Las pruebas se organizaron en las siguientes categorías principales:')
    
    categories = doc.add_paragraph()
    categories.style = 'List Bullet'
    categories.add_run('1. Pruebas de Modelos\n')
    categories.add_run('2. Pruebas de API\n')
    categories.add_run('3. Pruebas de Validación de Negocio')

    # Resultados de las Pruebas
    doc.add_paragraph()
    heading = doc.add_paragraph('Resultados de las Pruebas')
    set_heading_style(heading, 1)

    # TABLA DE RESULTADOS DE PRUEBAS (ESTILO DEL USUARIO)
    table = doc.add_table(rows=1, cols=5)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Nº'
    hdr_cells[1].text = 'Funcionalidad'
    hdr_cells[2].text = 'Descripción del Caso de Prueba'
    hdr_cells[3].text = 'Prueba Unitaria Realizada'
    hdr_cells[4].text = 'Resultado'

    pruebas = [
        (1, 'Registro de usuario', 'Verificar que se pueda registrar un usuario con datos válidos', 'test_crear_usuario()', 'Aprobada'),
        (2, 'Autenticación de usuario', 'Validar que un usuario pueda iniciar sesión con credenciales válidas', 'test_autenticacion_usuario()', 'Aprobada'),
        (3, 'Creación de vehículo', 'Comprobar que se pueda registrar un vehículo con datos correctos', 'test_crear_vehiculo()', 'Aprobada'),
        (4, 'Creación de conductor', 'Validar que se registre un conductor y se relacione con un vehículo correctamente', 'test_crear_conductor()', 'Aprobada'),
        (5, 'Creación de ruta', 'Comprobar que se cree una ruta con horarios válidos y asociación con vehículo', 'test_crear_ruta()', 'Aprobada'),
        (6, 'Calificación de servicio', 'Verificar que un usuario pueda calificar un servicio finalizado', 'test_calificar_servicio()', 'Aprobada'),
        (7, 'Registro de producto', 'Verificar que se pueda registrar un producto con datos válidos', 'test_crear_producto()', 'Aprobada'),
        (8, 'Registro de venta', 'Comprobar que se pueda registrar una venta correctamente', 'test_crear_venta()', 'Aprobada'),
        (9, 'Gestión de inventario', 'Validar que el inventario se actualice correctamente tras una venta', 'test_actualizar_inventario()', 'Aprobada'),
        (10, 'Gestión de clientes', 'Verificar que se pueda registrar y listar clientes', 'test_gestion_clientes()', 'Aprobada'),
        (11, 'Gestión de proveedores', 'Verificar que se pueda registrar y listar proveedores', 'test_gestion_proveedores()', 'Aprobada'),
        (12, 'Gestión de categorías', 'Verificar que se pueda registrar y listar categorías de productos', 'test_gestion_categorias()', 'Aprobada'),
        (13, 'Gestión de métodos de pago', 'Verificar que se puedan registrar y listar métodos de pago', 'test_gestion_metodos_pago()', 'Aprobada'),
        (14, 'Generación de reportes', 'Comprobar que se generen reportes de ventas correctamente', 'test_generar_reporte_ventas()', 'Aprobada'),
    ]
    for n, func, desc, prueba, res in pruebas:
        row = table.add_row().cells
        row[0].text = str(n)
        row[1].text = func
        row[2].text = desc
        row[3].text = prueba
        row[4].text = res

    # Análisis de Resultados
    doc.add_paragraph()
    heading = doc.add_paragraph('Análisis de Resultados')
    set_heading_style(heading, 1)
    doc.add_paragraph('Los resultados de las pruebas unitarias demuestran que todos los módulos y servicios del sistema funcionan correctamente. No se detectaron errores ni fallos en la validación de datos ni en la lógica de negocio. El sistema cumple con los requisitos establecidos y responde adecuadamente ante los diferentes escenarios evaluados.')

    # Recomendaciones
    doc.add_paragraph('Recomendaciones')
    doc.add_paragraph('Se recomienda mantener la cobertura de pruebas y continuar con la integración continua para asegurar la calidad del sistema ante futuras actualizaciones.')

    # Conclusiones
    doc.add_paragraph()
    heading = doc.add_paragraph('Conclusiones')
    set_heading_style(heading, 1)
    doc.add_paragraph('Las pruebas unitarias han confirmado la robustez y confiabilidad del sistema de API para el manejo de ventas. Todos los módulos y servicios funcionan correctamente, lo que garantiza la integridad y calidad del sistema.')

    # Referencias
    doc.add_paragraph()
    heading = doc.add_paragraph('Referencias')
    set_heading_style(heading, 1)
    doc.add_paragraph('Django Documentation. (2024). Testing in Django. https://docs.djangoproject.com/en/stable/topics/testing/')
    doc.add_paragraph('Django REST Framework. (2024). Testing. https://www.django-rest-framework.org/api-guide/testing/')

    # Anexos
    doc.add_paragraph()
    heading = doc.add_paragraph('Anexos')
    set_heading_style(heading, 1)

    # Anexo A
    doc.add_paragraph('Anexo A: Código de Pruebas')
    codigo = doc.add_paragraph()
    codigo.add_run('''# Ejemplo de prueba de creación de producto\ndef test_crear_producto(self):\n    url = reverse('producto-list')\n    data = {\n        'nombre': 'Nuevo Producto',\n        'descripcion': 'Nueva Descripción',\n        'precio_venta': '150.00',\n        'stock_actual': 15,\n        'stock_minimo': 5,\n        'categoria': self.categoria.id,\n        'proveedor': self.proveedor.id\n    }\n    response = self.client.post(url, data, format='json')\n    self.assertEqual(response.status_code, status.HTTP_201_CREATED)''')

    # Anexo B
    doc.add_paragraph('Anexo B: Resultados Detallados de Pruebas')
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    
    # Encabezados
    header_cells = table.rows[0].cells
    header_cells[0].text = 'Test'
    header_cells[1].text = 'Estado'
    header_cells[2].text = 'Descripción'

    # Datos
    data = [
        ('test_producto_creation', 'Éxito', 'El producto se crea correctamente'),
        ('test_venta_creation', 'Éxito', 'La venta se crea correctamente'),
        ('test_cliente_creation', 'Éxito', 'El cliente se crea correctamente'),
        ('test_proveedor_creation', 'Éxito', 'El proveedor se crea correctamente'),
        ('test_categoria_creation', 'Éxito', 'La categoría se crea correctamente'),
        ('test_usuario_creation', 'Éxito', 'El usuario se crea correctamente'),
        ('test_inventario_update', 'Éxito', 'El inventario se actualiza correctamente'),
        ('test_metodo_pago_creation', 'Éxito', 'El método de pago se registra correctamente'),
        ('test_listar_productos', 'Éxito', 'Lista los productos correctamente'),
        ('test_crear_producto', 'Éxito', 'Crea productos correctamente'),
        ('test_crear_venta', 'Éxito', 'Funciona correctamente'),
        ('test_validar_stock', 'Éxito', 'Valida el stock correctamente'),
        ('test_listar_clientes', 'Éxito', 'Lista los clientes correctamente'),
        ('test_crear_cliente', 'Éxito', 'Crea clientes correctamente'),
        ('test_listar_proveedores', 'Éxito', 'Lista los proveedores correctamente'),
        ('test_crear_proveedor', 'Éxito', 'Crea proveedores correctamente'),
        ('test_listar_categorias', 'Éxito', 'Lista las categorías correctamente'),
        ('test_crear_categoria', 'Éxito', 'Crea categorías correctamente'),
        ('test_registro_usuario', 'Éxito', 'Registra usuarios correctamente'),
        ('test_login_usuario', 'Éxito', 'Autentica usuarios correctamente'),
        ('test_actualizar_inventario', 'Éxito', 'Actualiza inventario correctamente'),
        ('test_listar_metodos_pago', 'Éxito', 'Lista los métodos de pago correctamente'),
        ('test_registrar_metodo_pago', 'Éxito', 'Registra métodos de pago correctamente'),
        ('test_generar_reporte_ventas', 'Éxito', 'Genera reportes de ventas correctamente')
    ]

    for test, estado, descripcion in data:
        row_cells = table.add_row().cells
        row_cells[0].text = test
        row_cells[1].text = estado
        row_cells[2].text = descripcion

    # Guardar el documento principal
    doc.save('Reporte_Pruebas_API.docx')
    # Reabrir y agregar el apartado de evidencia
    doc = Document('Reporte_Pruebas_API.docx')
    append_evidence_section(doc)
    doc.save('Reporte_Pruebas_API.docx')

if __name__ == '__main__':
    create_apa_document() 