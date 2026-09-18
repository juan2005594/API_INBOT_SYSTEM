import db from '../database/db.js';

// Generar número de producto único
const generarNumeroProducto = (tipo) => {
  const prefix = tipo === 'cuenta_ahorros' ? 'AH' : 
                 tipo === 'cuenta_corriente' ? 'CC' :
                 tipo === 'cdt' ? 'CDT' : 'CR';
  const random = Math.floor(Math.random() * 1000000000).toString().padStart(10, '0');
  return `${prefix}${random}`;
};

// Crear producto bancario
export const crearProducto = async (req, res) => {
  try {
    const { cliente_id, tipo_producto, saldo_inicial = 0 } = req.body;
    const userId = req.user.id;
    const tipoUsuario = req.user.tipo_usuario;

    if (!cliente_id || !tipo_producto) {
      return res.status(400).json({ error: 'cliente_id y tipo_producto son requeridos' });
    }

    const tiposValidos = ['cuenta_ahorros', 'cuenta_corriente', 'cdt', 'credito'];
    if (!tiposValidos.includes(tipo_producto)) {
      return res.status(400).json({ error: 'Tipo de producto inválido' });
    }

    // Verificar que el cliente existe
    const cliente = await db.getAsync('SELECT * FROM clientes WHERE id = ?', [cliente_id]);
    if (!cliente) {
      return res.status(404).json({ error: 'Cliente no encontrado' });
    }

    // Si es cliente, solo puede crear productos para sí mismo
    if (tipoUsuario === 'cliente') {
      const miCliente = await db.getAsync('SELECT * FROM clientes WHERE usuario_id = ?', [userId]);
      if (!miCliente || miCliente.id !== parseInt(cliente_id)) {
        return res.status(403).json({ error: 'Solo puedes crear productos para tu propia cuenta' });
      }
    }

    // Generar número de producto único
    let numeroProducto;
    let existe = true;
    while (existe) {
      numeroProducto = generarNumeroProducto(tipo_producto);
      const productoExistente = await db.getAsync(
        'SELECT id FROM productos WHERE numero_producto = ?',
        [numeroProducto]
      );
      existe = !!productoExistente;
    }

    // Crear producto
    const result = await db.runAsync(
      `INSERT INTO productos (cliente_id, tipo_producto, numero_producto, saldo, estado)
       VALUES (?, ?, ?, ?, ?)`,
      [cliente_id, tipo_producto, numeroProducto, saldo_inicial, 'activo']
    );

    // Si hay saldo inicial, crear transacción
    if (saldo_inicial > 0) {
      await db.runAsync(
        `INSERT INTO transacciones (producto_id, tipo_transaccion, monto, saldo_anterior, saldo_nuevo, descripcion)
         VALUES (?, ?, ?, ?, ?, ?)`,
        [result.lastID, 'consignacion', saldo_inicial, 0, saldo_inicial, 'Saldo inicial']
      );
    }

    const producto = await db.getAsync('SELECT * FROM productos WHERE id = ?', [result.lastID]);

    res.status(201).json({
      message: 'Producto creado exitosamente',
      producto
    });
  } catch (error) {
    console.error('Error al crear producto:', error);
    res.status(500).json({ error: 'Error al crear producto' });
  }
};

// Obtener productos de un cliente
export const obtenerProductos = async (req, res) => {
  try {
    const { cliente_id } = req.query;
    const userId = req.user.id;
    const tipoUsuario = req.user.tipo_usuario;

    let productos;

    if (tipoUsuario === 'cliente') {
      // Cliente solo ve sus propios productos
      const miCliente = await db.getAsync('SELECT * FROM clientes WHERE usuario_id = ?', [userId]);
      if (!miCliente) {
        return res.status(404).json({ error: 'Cliente no encontrado' });
      }

      productos = await db.allAsync(
        'SELECT * FROM productos WHERE cliente_id = ? ORDER BY fecha_apertura DESC',
        [miCliente.id]
      );
    } else {
      // Admin puede ver productos de cualquier cliente o todos
      if (cliente_id) {
        productos = await db.allAsync(
          'SELECT * FROM productos WHERE cliente_id = ? ORDER BY fecha_apertura DESC',
          [cliente_id]
        );
      } else {
        productos = await db.allAsync(
          'SELECT * FROM productos ORDER BY fecha_apertura DESC'
        );
      }
    }

    res.json(productos);
  } catch (error) {
    console.error('Error al obtener productos:', error);
    res.status(500).json({ error: 'Error al obtener productos' });
  }
};

// Obtener producto por ID
export const obtenerProducto = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;
    const tipoUsuario = req.user.tipo_usuario;

    const producto = await db.getAsync('SELECT * FROM productos WHERE id = ?', [id]);

    if (!producto) {
      return res.status(404).json({ error: 'Producto no encontrado' });
    }

    // Si es cliente, verificar que el producto le pertenece
    if (tipoUsuario === 'cliente') {
      const miCliente = await db.getAsync('SELECT * FROM clientes WHERE usuario_id = ?', [userId]);
      if (!miCliente || miCliente.id !== producto.cliente_id) {
        return res.status(403).json({ error: 'No tienes acceso a este producto' });
      }
    }

    res.json(producto);
  } catch (error) {
    console.error('Error al obtener producto:', error);
    res.status(500).json({ error: 'Error al obtener producto' });
  }
};

// Verificar saldo de un producto
export const verificarSaldo = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;
    const tipoUsuario = req.user.tipo_usuario;

    const producto = await db.getAsync('SELECT * FROM productos WHERE id = ?', [id]);

    if (!producto) {
      return res.status(404).json({ error: 'Producto no encontrado' });
    }

    // Si es cliente, verificar que el producto le pertenece
    if (tipoUsuario === 'cliente') {
      const miCliente = await db.getAsync('SELECT * FROM clientes WHERE usuario_id = ?', [userId]);
      if (!miCliente || miCliente.id !== producto.cliente_id) {
        return res.status(403).json({ error: 'No tienes acceso a este producto' });
      }
    }

    res.json({
      producto_id: producto.id,
      numero_producto: producto.numero_producto,
      tipo_producto: producto.tipo_producto,
      saldo: producto.saldo,
      estado: producto.estado
    });
  } catch (error) {
    console.error('Error al verificar saldo:', error);
    res.status(500).json({ error: 'Error al verificar saldo' });
  }
};


