import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import speakeasy from 'speakeasy';
import db from '../database/db.js';
import { generateSecret, generateQRCode, verifyToken } from '../utils/twoFactor.js';

// Registro de usuario
export const register = async (req, res) => {
  try {
    const { email, password, nombre, apellido, documento, telefono, tipo_usuario = 'cliente' } = req.body;

    // Validaciones básicas
    if (!email || !password || !nombre || !apellido || !documento) {
      return res.status(400).json({ error: 'Todos los campos son requeridos' });
    }

    // Verificar si el email ya existe
    const existingUser = await db.getAsync(
      'SELECT id FROM usuarios WHERE email = ? OR documento = ?',
      [email, documento]
    );

    if (existingUser) {
      return res.status(400).json({ error: 'El email o documento ya está registrado' });
    }

    // Hash de la contraseña
    const passwordHash = await bcrypt.hash(password, 10);

    // Crear usuario
    const result = await db.runAsync(
      `INSERT INTO usuarios (email, password_hash, nombre, apellido, documento, telefono, tipo_usuario)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [email, passwordHash, nombre, apellido, documento, telefono || null, tipo_usuario]
    );

    const userId = result.lastID;

    // Si es cliente, crear registro en tabla clientes
    if (tipo_usuario === 'cliente') {
      await db.runAsync(
        'INSERT INTO clientes (usuario_id, estado) VALUES (?, ?)',
        [userId, 'activo']
      );
    }

    res.status(201).json({
      message: 'Usuario registrado exitosamente',
      userId: userId
    });
  } catch (error) {
    console.error('Error en registro:', error);
    res.status(500).json({ error: 'Error al registrar usuario' });
  }
};

// Login
export const login = async (req, res) => {
  try {
    const { email, password, twoFactorToken } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email y contraseña son requeridos' });
    }

    // Buscar usuario
    const user = await db.getAsync(
      'SELECT * FROM usuarios WHERE email = ?',
      [email]
    );

    if (!user) {
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    // Verificar contraseña
    const validPassword = await bcrypt.compare(password, user.password_hash);
    if (!validPassword) {
      return res.status(401).json({ error: 'Credenciales inválidas' });
    }

    // Si 2FA está habilitado, verificar token
    if (user.two_factor_enabled === 1) {
      if (!twoFactorToken) {
        return res.status(200).json({
          requiresTwoFactor: true,
          message: 'Se requiere código de autenticación de dos factores'
        });
      }

      const isValidToken = verifyToken(twoFactorToken, user.two_factor_secret);
      if (!isValidToken) {
        return res.status(401).json({ error: 'Código 2FA inválido' });
      }
    }

    // Generar JWT
    const token = jwt.sign(
      {
        id: user.id,
        email: user.email,
        tipo_usuario: user.tipo_usuario
      },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );

    // Obtener información del cliente si existe
    let cliente = null;
    if (user.tipo_usuario === 'cliente') {
      cliente = await db.getAsync(
        'SELECT * FROM clientes WHERE usuario_id = ?',
        [user.id]
      );
    }

    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        nombre: user.nombre,
        apellido: user.apellido,
        tipo_usuario: user.tipo_usuario,
        two_factor_enabled: user.two_factor_enabled === 1,
        cliente: cliente
      }
    });
  } catch (error) {
    console.error('Error en login:', error);
    res.status(500).json({ error: 'Error al iniciar sesión' });
  }
};

// Configurar 2FA
export const setup2FA = async (req, res) => {
  try {
    const userId = req.user.id;

    // Obtener usuario
    const user = await db.getAsync('SELECT * FROM usuarios WHERE id = ?', [userId]);

    if (!user) {
      return res.status(404).json({ error: 'Usuario no encontrado' });
    }

    // Si ya tiene 2FA habilitado, retornar el QR existente
    if (user.two_factor_enabled === 1 && user.two_factor_secret) {
      const qrCode = await generateQRCode({
        otpauth_url: speakeasy.otpauthURL({
          secret: user.two_factor_secret,
          label: `Banco App (${user.email})`,
          issuer: 'Banco App',
          encoding: 'base32'
        })
      });
      return res.json({
        qrCode,
        secret: user.two_factor_secret,
        enabled: true
      });
    }

    // Generar nuevo secreto
    const secret = generateSecret(user.email);
    const qrCode = await generateQRCode(secret);

    // Guardar secreto (aún no habilitado)
    await db.runAsync(
      'UPDATE usuarios SET two_factor_secret = ? WHERE id = ?',
      [secret.base32, userId]
    );

    res.json({
      qrCode,
      secret: secret.base32,
      enabled: false,
      message: 'Escanea el código QR con Google Authenticator y luego verifica con un token'
    });
  } catch (error) {
    console.error('Error al configurar 2FA:', error);
    res.status(500).json({ error: 'Error al configurar 2FA' });
  }
};

// Verificar y habilitar 2FA
export const verify2FA = async (req, res) => {
  try {
    const { token } = req.body;
    const userId = req.user.id;

    if (!token) {
      return res.status(400).json({ error: 'Token 2FA requerido' });
    }

    // Obtener usuario
    const user = await db.getAsync('SELECT * FROM usuarios WHERE id = ?', [userId]);

    if (!user || !user.two_factor_secret) {
      return res.status(400).json({ error: '2FA no configurado. Configure primero 2FA' });
    }

    // Verificar token
    const isValid = verifyToken(token, user.two_factor_secret);

    if (!isValid) {
      return res.status(401).json({ error: 'Token 2FA inválido' });
    }

    // Habilitar 2FA
    await db.runAsync(
      'UPDATE usuarios SET two_factor_enabled = 1 WHERE id = ?',
      [userId]
    );

    res.json({
      message: '2FA habilitado exitosamente',
      enabled: true
    });
  } catch (error) {
    console.error('Error al verificar 2FA:', error);
    res.status(500).json({ error: 'Error al verificar 2FA' });
  }
};

// Deshabilitar 2FA
export const disable2FA = async (req, res) => {
  try {
    const userId = req.user.id;

    await db.runAsync(
      'UPDATE usuarios SET two_factor_enabled = 0, two_factor_secret = NULL WHERE id = ?',
      [userId]
    );

    res.json({ message: '2FA deshabilitado exitosamente' });
  } catch (error) {
    console.error('Error al deshabilitar 2FA:', error);
    res.status(500).json({ error: 'Error al deshabilitar 2FA' });
  }
};

