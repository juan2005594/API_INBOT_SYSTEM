import db from '../database/db.js';

// Crear cliente bancario (solo admin)
export const crearCliente = async (req, res) => {
  try {
    const { email, password, nombre, apellido, documento, telefono, fecha_nacimiento, direccion, ciudad } = req.body;

    if (!email || !password || !nombre || !apellido || !documento) {
      return res.status(400).json({ error: 'Email, contraseña, nombre, apellido y documento son requeridos' });
    }

    // Verificar si ya existe
    const existing = await db.getAsync(
      'SELECT id FROM usuarios WHERE email = ? OR documento = ?',
      [email, documento]
    );

    if (existing) {
      return res.status(400).json({ error: 'El email o documento ya está registrado' });
    }

    // Usar el controlador de auth para crear el usuario
    const bcrypt = (await import('bcryptjs')).default;
    const passwordHash = await bcrypt.hash(password, 10);

    // Crear usuario tipo cliente
    const userResult = await db.runAsync(
      `INSERT INTO usuarios (email, password_hash, nombre, apellido, documento, telefono, tipo_usuario)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [email, passwordHash, nombre, apellido, documento, telefono || null, 'cliente']
    );

    // Crear cliente
    const clienteResult = await db.runAsync(
      `INSERT INTO clientes (usuario_id, fecha_nacimiento, direccion, ciudad, estado)
       VALUES (?, ?, ?, ?, ?)`,
      [userResult.lastID, fecha_nacimiento || null, direccion || null, ciudad || null, 'activo']
    );

    const cliente = await db.getAsync(
      `SELECT c.*, u.email, u.nombre, u.apellido, u.documento, u.telefono
       FROM clientes c
       JOIN usuarios u ON c.usuario_id = u.id
       WHERE c.id = ?`,
      [clienteResult.lastID]
    );

    res.status(201).json({
      message: 'Cliente creado exitosamente',
      cliente
    });
  } catch (error) {
    console.error('Error al crear cliente:', error);
    res.status(500).json({ error: 'Error al crear cliente' });
  }
};

// Obtener todos los clientes (solo admin)
export const obtenerClientes = async (req, res) => {
  try {
    const clientes = await db.allAsync(
      `SELECT c.*, u.email, u.nombre, u.apellido, u.documento, u.telefono
       FROM clientes c
       JOIN usuarios u ON c.usuario_id = u.id
       ORDER BY c.id DESC`
    );

    res.json(clientes);
  } catch (error) {
    console.error('Error al obtener clientes:', error);
    res.status(500).json({ error: 'Error al obtener clientes' });
  }
};

// Obtener cliente por ID
export const obtenerCliente = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id;
    const tipoUsuario = req.user.tipo_usuario;

    // Si es cliente, solo puede ver su propia información
    if (tipoUsuario === 'cliente') {
      const cliente = await db.getAsync(
        `SELECT c.*, u.email, u.nombre, u.apellido, u.documento, u.telefono
         FROM clientes c
         JOIN usuarios u ON c.usuario_id = u.id
         WHERE u.id = ?`,
        [userId]
      );

      if (!cliente) {
        return res.status(404).json({ error: 'Cliente no encontrado' });
      }

      return res.json(cliente);
    }

    // Si es admin, puede ver cualquier cliente
    const cliente = await db.getAsync(
      `SELECT c.*, u.email, u.nombre, u.apellido, u.documento, u.telefono
       FROM clientes c
       JOIN usuarios u ON c.usuario_id = u.id
       WHERE c.id = ?`,
      [id]
    );

    if (!cliente) {
      return res.status(404).json({ error: 'Cliente no encontrado' });
    }

    res.json(cliente);
  } catch (error) {
    console.error('Error al obtener cliente:', error);
    res.status(500).json({ error: 'Error al obtener cliente' });
  }
};

// Obtener mi información como cliente
export const obtenerMiInformacion = async (req, res) => {
  try {
    const userId = req.user.id;

    const cliente = await db.getAsync(
      `SELECT c.*, u.email, u.nombre, u.apellido, u.documento, u.telefono
       FROM clientes c
       JOIN usuarios u ON c.usuario_id = u.id
       WHERE u.id = ?`,
      [userId]
    );

    if (!cliente) {
      return res.status(404).json({ error: 'Cliente no encontrado' });
    }

    res.json(cliente);
  } catch (error) {
    console.error('Error al obtener información:', error);
    res.status(500).json({ error: 'Error al obtener información' });
  }
};


