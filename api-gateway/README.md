# 🌐 API Gateway

Gateway centralizado para todos los microservicios de GeoAttend.

## 📋 Responsabilidades

- ✅ Punto de entrada único para todas las peticiones
- ✅ Enrutamiento a microservicios
- ✅ Validación de JWT (opcional)
- ✅ Rate limiting
- ✅ CORS handling
- ✅ Request/response logging
- ✅ Error handling centralizado

## 🚀 Inicio Rápido

### 1. Configuración

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración
nano .env
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar Gateway

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 Rutas Disponibles

### Autenticación
- `POST /api/v1/auth/login` → User Service
- `POST /api/v1/auth/register` → User Service

### Usuarios
- `GET/POST/PUT/DELETE /api/v1/users/{path}` → User Service

### Cursos
- `GET/POST/PUT/DELETE /api/v1/courses/{path}` → Course Service
- `GET/POST/PUT/DELETE /api/v1/classrooms/{path}` → Course Service
- `GET/POST/PUT/DELETE /api/v1/enrollments/{path}` → Course Service

### Asistencia
- `GET/POST/PUT/DELETE /api/v1/attendance/{path}` → Attendance Service
- `GET/POST/PUT/DELETE /api/v1/gps/{path}` → Attendance Service

### Notificaciones
- `GET/POST/PUT/DELETE /api/v1/notifications/{path}` → Notification Service

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Login via Gateway

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Password123!"
  }'
```

### GPS Event via Gateway

```bash
curl -X POST "http://localhost:8000/api/v1/gps/event" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_id": 1,
    "course_id": 1,
    "latitude": -12.0464,
    "longitude": -77.0428,
    "accuracy": 5.0
  }'
```

## ⚙️ Características

### Rate Limiting
- Configurable por minuto
- Por dirección IP
- Respuesta 429 cuando se excede

### CORS
- Orígenes configurables
- Permite credenciales
- Todos los métodos HTTP

### Security
- JWT validation opcional (permite requests sin autenticación)
- Token verification
- Header forwarding

### Error Handling
- Timeout handling (504)
- Service unavailable (503)
- Microservice errors (proxied)

## 🔧 Configuración Avanzada

### Rate Limiting Personalizado

```python
# Deshabilitar rate limiting
RATE_LIMIT_ENABLED=false

# Cambiar límite
RATE_LIMIT_PER_MINUTE=100
```

### Timeouts

```python
# Aumentar timeout a 60 segundos
REQUEST_TIMEOUT=60
```

### CORS

```python
# Agregar más orígenes
CORS_ORIGINS=http://localhost:3000,https://app.geoattend.com
```

## 📊 Arquitectura

```
Cliente (Mobile/Web)
    ↓
API Gateway (Puerto 8000)
    ├─→ User Service (8001)
    ├─→ Course Service (8002)
    ├─→ Attendance Service (8003)
    └─→ Notification Service (8004)
```

## 🛠️ Stack Tecnológico

- FastAPI 0.115.0
- HTTPX (async HTTP client)
- SlowAPI (rate limiting)
- Python-JOSE (JWT)
- Loguru (logging)

## 📈 Beneficios

- ✅ Single entry point
- ✅ Centralized authentication
- ✅ Rate limiting protection
- ✅ Easy to monitor
- ✅ Simplified client integration
- ✅ Independent scaling

## 🔒 Seguridad

- JWT verification compartida con User Service
- Rate limiting por IP
- CORS configurado
- Request validation
- Error sanitization
