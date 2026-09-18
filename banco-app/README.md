# 🏦 Banco App - Sistema Bancario con 2FA

Aplicación web full stack para el manejo de banco con autenticación de dos factores (2FA), desarrollada como proyecto final.

## 🚀 Características

- ✅ Crear clientes bancarios
- ✅ Crear productos bancarios a clientes
- ✅ Ingresar a cuenta del cliente
- ✅ Hacer consignaciones simuladas a productos del cliente
- ✅ Hacer retiros simulados a productos del cliente
- ✅ Verificar saldos de productos bancarios del cliente
- ✅ Autenticación de dos factores (2FA) con TOTP
- ✅ Interfaz moderna y responsive

## 📋 Requisitos Previos

- Node.js 18+ 
- npm o yarn
- Git

## 🛠️ Instalación

### Backend

```bash
cd banco-app/backend
npm install
cp .env.example .env
# Edita .env y configura JWT_SECRET
npm start
```

El backend estará corriendo en `http://localhost:3001`

### Frontend

```bash
cd banco-app/frontend
npm install
npm run dev
```

El frontend estará corriendo en `http://localhost:3000`

## 📁 Estructura del Proyecto

```
banco-app/
├── backend/
│   ├── controllers/      # Controladores de la API
│   ├── database/         # Base de datos SQLite
│   ├── middleware/       # Middleware de autenticación
│   ├── routes/           # Rutas de la API
│   ├── utils/            # Utilidades (2FA, etc.)
│   └── server.js         # Servidor principal
├── frontend/
│   ├── src/
│   │   ├── components/   # Componentes React
│   │   ├── context/      # Context API (Auth)
│   │   ├── pages/        # Páginas de la aplicación
│   │   └── services/     # Servicios API
│   └── package.json
└── netlify.toml          # Configuración Netlify
```

## 🗄️ Base de Datos

La aplicación usa SQLite para desarrollo. La base de datos se crea automáticamente al iniciar el servidor.

### Esquema de Base de Datos

- **usuarios**: Usuarios del sistema (clientes y administradores)
- **clientes**: Información adicional de clientes bancarios
- **productos**: Productos bancarios (cuentas, CDT, créditos)
- **transacciones**: Historial de consignaciones y retiros

## 🔐 Autenticación 2FA

La aplicación soporta autenticación de dos factores usando TOTP (Time-based One-Time Password).

### Configurar 2FA

1. Inicia sesión en la aplicación
2. Ve a "Configuración 2FA"
3. Haz clic en "Configurar 2FA"
4. Escanea el código QR con Google Authenticator o Authy
5. Ingresa el código de 6 dígitos para verificar

### Usar 2FA

1. Al iniciar sesión, después de ingresar email y contraseña
2. Si 2FA está habilitado, se solicitará el código
3. Ingresa el código de 6 dígitos de tu app de autenticación

## 🌐 Despliegue en Netlify

### Opción 1: Frontend en Netlify + Backend separado

1. **Backend**: Despliega el backend en un servicio como Heroku, Railway, o Render
2. **Frontend**: 
   ```bash
   cd frontend
   npm run build
   ```
3. Sube la carpeta `frontend/dist` a Netlify
4. Configura la variable de entorno `VITE_API_URL` en Netlify con la URL de tu backend

### Opción 2: Netlify Functions (Serverless)

Puedes convertir el backend a funciones serverless de Netlify. Ver documentación de Netlify Functions.

## 📝 Variables de Entorno

### Backend (.env)

```
PORT=3001
JWT_SECRET=tu_secreto_jwt_muy_seguro_aqui
NODE_ENV=development
DB_PATH=./database/banco.db
```

### Frontend

Crea un archivo `.env` en `frontend/`:

```
VITE_API_URL=http://localhost:3001/api
```

Para producción, usa la URL de tu backend desplegado.

## 👤 Usuarios de Prueba

Puedes crear usuarios directamente desde la aplicación o usando la API:

```bash
# Crear admin
POST /api/auth/register
{
  "email": "admin@banco.com",
  "password": "admin123",
  "nombre": "Admin",
  "apellido": "Sistema",
  "documento": "123456789",
  "tipo_usuario": "admin"
}

# Crear cliente
POST /api/auth/register
{
  "email": "cliente@banco.com",
  "password": "cliente123",
  "nombre": "Juan",
  "apellido": "Pérez",
  "documento": "987654321"
}
```

## 🔌 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/setup-2fa` - Configurar 2FA
- `POST /api/auth/verify-2fa` - Verificar y habilitar 2FA
- `POST /api/auth/disable-2fa` - Deshabilitar 2FA

### Clientes
- `GET /api/clientes` - Listar clientes (admin)
- `POST /api/clientes` - Crear cliente (admin)
- `GET /api/clientes/:id` - Obtener cliente
- `GET /api/clientes/mi-informacion` - Mi información

### Productos
- `GET /api/productos` - Listar productos
- `POST /api/productos` - Crear producto
- `GET /api/productos/:id` - Obtener producto
- `GET /api/productos/:id/saldo` - Verificar saldo

### Transacciones
- `GET /api/transacciones` - Listar transacciones
- `POST /api/transacciones/consignacion` - Realizar consignación
- `POST /api/transacciones/retiro` - Realizar retiro

## 🧪 Testing

```bash
# Backend
cd backend
npm test

# Frontend
cd frontend
npm test
```

## 📄 Licencia

Este proyecto fue desarrollado como proyecto final académico.

## 👨‍💻 Autor

Desarrollado como proyecto final.

---

**Nota**: Esta es una aplicación de demostración. Para uso en producción, considera:
- Usar una base de datos más robusta (PostgreSQL, MySQL)
- Implementar HTTPS
- Añadir validaciones adicionales
- Implementar rate limiting
- Añadir logging y monitoreo
- Revisar y mejorar la seguridad


