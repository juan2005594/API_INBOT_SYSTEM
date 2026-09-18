import bcrypt from 'bcryptjs';
import db from '../database/db.js';
import { initDatabase } from '../database/db.js';

const createAdmin = async () => {
  try {
    // Inicializar base de datos
    await initDatabase();

    const email = process.argv[2] || 'admin@banco.com';
    const password = process.argv[3] || 'admin123';
    const nombre = process.argv[4] || 'Admin';
    const apellido = process.argv[5] || 'Sistema';
    const documento = process.argv[6] || '123456789';

    // Verificar si ya existe
    const existing = await db.getAsync(
      'SELECT id FROM usuarios WHERE email = ?',
      [email]
    );

    if (existing) {
      console.log('El usuario admin ya existe');
      process.exit(0);
    }

    // Hash de la contraseña
    const passwordHash = await bcrypt.hash(password, 10);

    // Crear usuario admin
    await new Promise((resolve, reject) => {
      db.run(
        `INSERT INTO usuarios (email, password_hash, nombre, apellido, documento, tipo_usuario)
         VALUES (?, ?, ?, ?, ?, ?)`,
        [email, passwordHash, nombre, apellido, documento, 'admin'],
        function(err) {
          if (err) reject(err);
          else resolve(this.lastID);
        }
      );
    });

    console.log('✅ Usuario administrador creado exitosamente');
    console.log(`Email: ${email}`);
    console.log(`Password: ${password}`);

    process.exit(0);
  } catch (error) {
    console.error('Error al crear admin:', error);
    process.exit(1);
  }
};

createAdmin();


