# 🔔 Notification Service

Microservicio de notificaciones para GeoAttend - Manejo de emails y push notifications.

## 📋 Responsabilidades

- ✅ Envío de emails (SMTP)
- ✅ Push notifications (Firebase Cloud Messaging)
- ✅ Plantillas de notificaciones
- ✅ Preferencias de usuario
- ✅ Historial de notificaciones
- ✅ Integración con otros servicios

## 🚀 Inicio Rápido

### 1. Base de Datos

```bash
# Agregar a docker-compose.yml
docker-compose up -d notification-db
```

### 2. Configuración

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración SMTP
nano .env
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar Servicio

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload
```

## 📡 API Endpoints

### Notificaciones

- `POST /api/v1/notifications/email` - Enviar email
- `POST /api/v1/notifications/push` - Enviar push notification
- `GET /api/v1/notifications/user/{user_id}` - Obtener notificaciones de usuario

### Plantillas

- `POST /api/v1/notifications/templates` - Crear plantilla

### Preferencias

- `GET /api/v1/notifications/preferences/{user_id}` - Obtener preferencias
- `PUT /api/v1/notifications/preferences/{user_id}` - Actualizar preferencias
- `POST /api/v1/notifications/device-token` - Actualizar token de dispositivo

## 🧪 Testing

### Enviar Email

```bash
curl -X POST "http://localhost:8004/api/v1/notifications/email" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "subject": "Test Email",
    "body": "This is a test email from GeoAttend",
    "recipient_email": "user@example.com"
  }'
```

### Enviar Push Notification

```bash
curl -X POST "http://localhost:8004/api/v1/notifications/push" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "title": "Test Push",
    "body": "This is a test push notification",
    "device_token": "your-fcm-token"
  }'
```

## ⚙️ Configuración SMTP

Para Gmail:
1. Habilitar verificación en 2 pasos
2. Generar contraseña de aplicación
3. Usar en `SMTP_PASSWORD`

## 🔥 Firebase Cloud Messaging

1. Crear proyecto en Firebase Console
2. Descargar archivo de credenciales JSON
3. Configurar `FCM_CREDENTIALS_PATH` en `.env`
4. Establecer `FCM_ENABLED=true`

## 📊 Base de Datos

**Tablas:**
- `notifications` - Registro de todas las notificaciones
- `notification_templates` - Plantillas reutilizables
- `user_notification_preferences` - Preferencias de usuario

## 🔗 Integración con Otros Servicios

- **User Service**: Obtener información de usuario y email
- **Course Service**: Obtener información de cursos
- **Attendance Service**: Notificar asistencias registradas

## 📈 Características

- ✅ Async/await para alto rendimiento
- ✅ Retry automático en fallos
- ✅ Plantillas HTML para emails
- ✅ Validación de preferencias de usuario
- ✅ Logging estructurado con Loguru
- ✅ Base de datos independiente

## 🛠️ Stack Tecnológico

- FastAPI 0.115.0
- SQLAlchemy 2.0.35 (async)
- aiosmtplib 3.0.1 (async SMTP)
- firebase-admin 6.2.0
- PostgreSQL 15
