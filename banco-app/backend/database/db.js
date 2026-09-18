import sqlite3 from 'sqlite3';
import { promisify } from 'util';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const DB_PATH = process.env.DB_PATH || join(__dirname, 'banco.db');

// Crear conexión a la base de datos
const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('Error al conectar a la base de datos:', err.message);
  } else {
    console.log('Conectado a la base de datos SQLite');
    // Habilitar foreign keys
    db.run('PRAGMA foreign_keys = ON');
  }
});

// Promisificar métodos
db.runAsync = promisify(db.run.bind(db));
db.getAsync = promisify(db.get.bind(db));
db.allAsync = promisify(db.all.bind(db));

// Inicializar base de datos
export const initDatabase = async () => {
  const schemaPath = join(__dirname, 'schema.sql');
  
  if (!existsSync(schemaPath)) {
    console.error('No se encontró el archivo schema.sql');
    return;
  }

  const schema = readFileSync(schemaPath, 'utf8');
  
  return new Promise((resolve, reject) => {
    db.exec(schema, (err) => {
      if (err) {
        console.error('Error al inicializar la base de datos:', err.message);
        reject(err);
      } else {
        console.log('Base de datos inicializada correctamente');
        resolve();
      }
    });
  });
};

export default db;


