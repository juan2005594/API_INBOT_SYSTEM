-- Base de datos para aplicación bancaria

-- Tabla de usuarios (clientes y administradores)
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    documento TEXT UNIQUE NOT NULL,
    telefono TEXT,
    tipo_usuario TEXT NOT NULL DEFAULT 'cliente', -- 'cliente' o 'admin'
    two_factor_secret TEXT, -- Secret para 2FA
    two_factor_enabled INTEGER DEFAULT 0, -- 0 = deshabilitado, 1 = habilitado
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de clientes bancarios
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    fecha_nacimiento DATE,
    direccion TEXT,
    ciudad TEXT,
    estado TEXT DEFAULT 'activo', -- 'activo', 'inactivo', 'bloqueado'
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE(usuario_id)
);

-- Tabla de productos bancarios
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    tipo_producto TEXT NOT NULL, -- 'cuenta_ahorros', 'cuenta_corriente', 'cdt', 'credito'
    numero_producto TEXT UNIQUE NOT NULL,
    saldo DECIMAL(15, 2) DEFAULT 0.00,
    estado TEXT DEFAULT 'activo', -- 'activo', 'inactivo', 'bloqueado'
    fecha_apertura DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- Tabla de transacciones
CREATE TABLE IF NOT EXISTS transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    tipo_transaccion TEXT NOT NULL, -- 'consignacion', 'retiro'
    monto DECIMAL(15, 2) NOT NULL,
    saldo_anterior DECIMAL(15, 2) NOT NULL,
    saldo_nuevo DECIMAL(15, 2) NOT NULL,
    descripcion TEXT,
    fecha_transaccion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_documento ON usuarios(documento);
CREATE INDEX IF NOT EXISTS idx_clientes_usuario_id ON clientes(usuario_id);
CREATE INDEX IF NOT EXISTS idx_productos_cliente_id ON productos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_productos_numero ON productos(numero_producto);
CREATE INDEX IF NOT EXISTS idx_transacciones_producto_id ON transacciones(producto_id);
CREATE INDEX IF NOT EXISTS idx_transacciones_fecha ON transacciones(fecha_transaccion);


