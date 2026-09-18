import db from '../database/db.js';

// Realizar consignación
export const realizarConsignacion = async (req, res) => {
  try {
    const { producto_id, monto, descripcion } = req.body;
    const userId = req.user.id;
    const tipoUsuario = req.user.tipo_usuario;

    if (!producto_id || !monto || monto <= 0) {
      return res.status(400).json({ error: 'producto_id y monto válido son requeridos' });
    }

    // Obtener producto
    const producto = await db.getAsync('SELECT * FROM productos WHERE id = ?', [producto_id]);

    if (!producto) {
      return res.status(404).json({ error: 'Producto no encontrado' });
    }

    if (producto.estado !== 'activo') {
      return res.status(400).json({ error: 'El producto no está activo' });
    }

    // Si es cliente, verificar que el producto le pertenece
    if (tipoUsuario === 'cliente') {
      const miCliente = await db.getAsync('SELECT * FROM clientes WHERE usuario_id = ?', [userId]);
      if (!miCliente || miCliente.id !== producto.cliente_id) {
        return res.status(403).json({ error: 'No tienes acceso a este producto' });
      }
    }

    const saldoAnterior = parseFloat(producto.saldo);
    const saldoNuevo = saldoAnterior + parseFloat(monto);

    // Iniciar transacción
    await db.runAsync('BEGIN TRANSACTION');

    try {
      // Actualizar saldo del producto
      await db.runAsync(
        'UPDATE productos SET saldo = ? WHERE id = ?',
        [saldoNuevo, producto_id]
      );

      // Registrar transacción
      await db.runAsync(
        `INSERT INTO transacciones (producto_id, tipo_transaccion, monto, saldo_anterior, saldo_nuevo, descripcion)
         VALUES (?, ?, ?, ?, ?, ?)`,
        [producto_id, 'consignacion', monto, saldoAnterior, saldoNuevo, descripcion || 'Consignación']
      );

      await db.runAsync('COMMIT');

      // Obtener producto actualizado
      const productoActualizado = await db.getAsync('SELECT * FROM productos WHERE id = ?', [producto_id]);

      res.json({
        message: 'Consignación realizada exitosamente',
        transaccion: {
          tipo: 'consignacion',
          monto: parseFloat(monto),
          saldo_anterior: saldoAnterior,
          saldo_nuevo: saldoNuevo
        },
        producto: productoActualizado
      });
    } catch (error) {
      await db.runAsync('ROLLBACK');
      throw error;
    }
  } catch (error) {
    console.error('Error al realizar consignación:', error);
    res.status(500).json({ error: 'Error al realizar consignación' });
  }
};

// Realizar retiro
export const realizarRetiro = async (req, res) => {
  try {
    const { producto_id, monto, descripcion } = req.body;
    const userId = req.user.id;
    const tipoUsuario = req.user.tipo_usuario;

    if (!producto_id || !monto || monto <= 0) {
      return res.status(400).json({ error: 'producto_id y monto válido son requeridos' });
    }

    // Obtener producto
    const producto = await db.getAsync('SELECT * FROM productos WHERE id = ?', [producto_id]);

    if (!producto) {
      return res.status(404).json({ error: 'Producto no encontrado' });
    }

    if (producto.estado !== 'activo') {
      return res.status(400).json({ error: 'El producto no está activo' });
    }

    // Si es cliente, verificar que el producto le pertenece
    if (tipoUsuario === 'cliente') {
      const miCliente = await db.getAsync('SELECT * FROM clientes WHERE usuario_id = ?', [userId]);
      if (!miCliente || miCliente.id !== producto.cliente_id) {
        return res.status(403).json({ error: 'No tienes acceso a este producto' });
      }
    }

    const saldoAnterior = parseFloat(producto.saldo);
    const montoRetiro = parseFloat(monto);

    // Verificar saldo suficiente
    if (saldoAnterior < montoRetiro) {
      return res.status(400).json({ 
        error: 'Saldo insuficiente',
        saldo_disponible: saldoAnterior,
        monto_solicitado: montoRetiro
      });
    }

    const saldoNuevo = saldoAnterior - montoRetiro;

    // Iniciar transacción
    await db.runAsync('BEGIN TRANSACTION');

    try {
      // Actualizar saldo del producto
      await db.runAsync(
        'UPDATE productos SET saldo = ? WHERE id = ?',
        [saldoNuevo, producto_id]
      );

      // Registrar transacción
      await db.runAsync(
        `INSERT INTO transacciones (producto_id, tipo_transaccion, monto, saldo_anterior, saldo_nuevo, descripcion)
         VALUES (?, ?, ?, ?, ?, ?)`,
        [producto_id, 'retiro', montoRetiro, saldoAnterior, saldoNuevo, descripcion || 'Retiro']
      );

      await db.runAsync('COMMIT');

      // Obtener producto actualizado
      const productoActualizado = await db.getAsync('SELECT * FROM productos WHERE id = ?', [producto_id]);

      res.json({
        message: 'Retiro realizado exitosamente',
        transaccion: {
          tipo: 'retiro',
          monto: montoRetiro,
          saldo_anterior: saldoAnterior,
          saldo_nuevo: saldoNuevo
        },
        producto: productoActualizado
      });
    } catch (error) {
      await db.runAsync('ROLLBACK');
      throw error;
    }
  } catch (error) {
    console.error('Error al realizar retiro:', error);
    res.status(500).json({ error: 'Error al realizar retiro' });
  }
};

// Obtener historial de transacciones
export const obtenerTransacciones = async (req, res) => {
  try {
    const { producto_id } = req.query;
    const userId = req.user.id;
    const tipoUsuario = req.user.tipo_usuario;

    let transacciones;

    if (producto_id) {
      // Verificar acceso al producto
      const producto = await db.getAsync('SELECT * FROM productos WHERE id = ?', [producto_id]);

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

      transacciones = await db.allAsync(
        `SELECT * FROM transacciones 
         WHERE producto_id = ? 
         ORDER BY fecha_transaccion DESC 
         LIMIT 100`,
        [producto_id]
      );
    } else {
      // Si es cliente, solo sus transacciones
      if (tipoUsuario === 'cliente') {
        const miCliente = await db.getAsync('SELECT * FROM clientes WHERE usuario_id = ?', [userId]);
        if (!miCliente) {
          return res.status(404).json({ error: 'Cliente no encontrado' });
        }

        const productos = await db.allAsync(
          'SELECT id FROM productos WHERE cliente_id = ?',
          [miCliente.id]
        );

        const productoIds = productos.map(p => p.id);

        if (productoIds.length === 0) {
          return res.json([]);
        }

        const placeholders = productoIds.map(() => '?').join(',');
        transacciones = await db.allAsync(
          `SELECT * FROM transacciones 
           WHERE producto_id IN (${placeholders})
           ORDER BY fecha_transaccion DESC 
           LIMIT 100`,
          productoIds
        );
      } else {
        // Admin puede ver todas las transacciones
        transacciones = await db.allAsync(
          `SELECT * FROM transacciones 
           ORDER BY fecha_transaccion DESC 
           LIMIT 100`
        );
      }
    }

    res.json(transacciones);
  } catch (error) {
    console.error('Error al obtener transacciones:', error);
    res.status(500).json({ error: 'Error al obtener transacciones' });
  }
};


