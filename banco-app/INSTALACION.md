# Guía de Instalación - Banco App

## Instalación Rápida

### 1. Instalar Backend

```bash
cd banco-app/backend
npm install
cp .env.example .env
```

Edita el archivo `.env` y configura:
```
JWT_SECRET=tu_secreto_super_seguro_aqui_cambiar_en_produccion
PORT=3001
```

### 2. Iniciar Backend

```bash
npm start
```

El backend estará disponible en `http://localhost:3001`

### 3. Instalar Frontend

En una nueva terminal:

```bash
cd banco-app/frontend
npm install
```

Crea un archivo `.env` en la carpeta `frontend/`:
```
VITE_API_URL=http://localhost:3001/api
```

### 4. Iniciar Frontend

```bash
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

## Crear Primer Usuario

### Opción 1: Desde la Interfaz Web

1. Abre `http://localhost:3000`
2. Si no tienes cuenta, puedes crear una desde el código o usar la API

### Opción 2: Usando la API

```bash
# Crear usuario administrador
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@banco.com",
    "password": "admin123",
    "nombre": "Admin",
    "apellido": "Sistema",
    "documento": "123456789",
    "tipo_usuario": "admin"
  }'

# Crear cliente
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cliente@banco.com",
    "password": "cliente123",
    "nombre": "Juan",
    "apellido": "Pérez",
    "documento": "987654321"
  }'
```

## Configurar 2FA

1. Inicia sesión en la aplicación
2. Ve a la sección "2FA" en el menú
3. Haz clic en "Configurar 2FA"
4. Escanea el código QR con Google Authenticator o Authy
5. Ingresa el código de 6 dígitos para verificar

## Solución de Problemas

### Error: "Cannot find module"
Ejecuta `npm install` en las carpetas `backend` y `frontend`

### Error: "Port already in use"
Cambia el puerto en el archivo `.env` del backend

### La base de datos no se crea
Asegúrate de que la carpeta `backend/database` existe y tiene permisos de escritura

### Error de CORS
Verifica que el frontend esté apuntando a la URL correcta del backend en `.env`

## Próximos Pasos

1. Crea un cliente bancario (si eres admin)
2. Crea productos bancarios para el cliente
3. Realiza consignaciones y retiros
4. Verifica saldos

¡Listo! Tu aplicación bancaria está funcionando.


