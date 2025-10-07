# GeoAttend - Sistema Inteligente de Asistencia por Geocerca

## 📋 Descripción del Proyecto

**GeoAttend** es un sistema de registro automático de asistencia estudiantil mediante geolocalización GPS, implementado con arquitectura de microservicios. El sistema permite a los estudiantes registrar su asistencia a clases únicamente cuando se encuentran físicamente dentro del aula (verificado por GPS) y durante el horario de clase programado.

### Características Principales
- ✅ **Registro de asistencia basado en GPS** con validación de proximidad al aula
- ✅ **Validación de horarios** - Solo permite registro durante horas de clase (±15 min de tolerancia)
- ✅ **Gestión de cursos y aulas** con ubicación GPS y radio de geovalla
- ✅ **Múltiples horarios por curso** con asignación de aulas específicas
- ✅ **Dashboard web administrativo** para gestión completa del sistema
- ✅ **Aplicación móvil** (React Native/Expo) para estudiantes
- ✅ **Autenticación JWT** con roles (admin, teacher, student)
- ✅ **Arquitectura de microservicios** con FastAPI

## 🏗️ Arquitectura del Sistema

### Estilo Arquitectónico
- **Microservicios** con comunicación HTTP/REST
- **API Gateway** como punto de entrada único
- **Base de datos independientes** por microservicio
- **Event-Driven** para notificaciones (en desarrollo)

### Stack Tecnológico

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0 (Async)
- **Base de Datos**: PostgreSQL 15+
- **Autenticación**: JWT (python-jose)
- **Validación**: Pydantic v2

#### Frontend Web
- **Framework**: React + TypeScript + Vite
- **UI Components**: shadcn/ui + Tailwind CSS
- **State Management**: React Context
- **Maps**: Leaflet (React-Leaflet)

#### Frontend Mobile
- **Framework**: React Native + Expo
- **Navigation**: React Navigation
- **Maps**: React Native Maps

## 🚀 Instalación y Configuración

### 1. Prerrequisitos

```bash
# Software requerido
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ (opcional si usas Docker)
```

### 2. Clonar el Repositorio

```bash
git clone <repository-url>
cd Taller3
```

### 3. Configuración de Variables de Entorno

Cada microservicio requiere un archivo `.env`:

#### User Service (.env)
```bash
# user-service/.env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/user_db
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Course Service (.env)
```bash
# course-service/.env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5434/course_db
SECRET_KEY=your-secret-key-min-32-chars
USER_SERVICE_URL=http://localhost:8001
```

#### Attendance Service (.env)
```bash
# attendance-service/.env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5435/attendance_db
SECRET_KEY=your-secret-key-min-32-chars
USER_SERVICE_URL=http://localhost:8001
COURSE_SERVICE_URL=http://localhost:8002
```

#### Notification Service (.env)
```bash
# notification-service/.env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5436/notification_db
SECRET_KEY=your-secret-key-min-32-chars
```

#### API Gateway (.env)
```bash
# api-gateway/.env
SECRET_KEY=your-secret-key-min-32-chars
USER_SERVICE_URL=http://localhost:8001
COURSE_SERVICE_URL=http://localhost:8002
ATTENDANCE_SERVICE_URL=http://localhost:8003
NOTIFICATION_SERVICE_URL=http://localhost:8004
```

### 4. Configurar Docker Compose (Opcional)

Si es tu primera vez configurando el proyecto, puedes copiar el archivo de ejemplo:

```bash
# Copiar docker-compose de ejemplo (opcional)
cp docker-compose.yml.example docker-compose.yml

# Editar docker-compose.yml y reemplazar:
# - YOUR_DB_PASSWORD_HERE con tu contraseña de base de datos
# - YOUR_SECRET_KEY_MIN_32_CHARS_HERE con tu clave secreta (mínimo 32 caracteres)
# - Configuración SMTP si usarás notificaciones por email
# - Configuración FCM si usarás notificaciones push
```

**Nota**: El repositorio ya incluye un `docker-compose.yml` con valores por defecto para desarrollo. Solo usa el `.example` si necesitas una configuración personalizada.

### 5. Levantar Bases de Datos con Docker

```bash
# Levantar todas las bases de datos
docker-compose up -d

# Verificar que estén corriendo
docker-compose ps

# Ver logs de las bases de datos
docker-compose logs -f user-db course-db attendance-db notification-db
```

Las bases de datos estarán disponibles en:
- **user-db**: `localhost:5433`
- **course-db**: `localhost:5434`
- **attendance-db**: `localhost:5435`
- **notification-db**: `localhost:5436`

### 6. Iniciar Microservicios

Abre **5 terminales diferentes** y ejecuta cada servicio:

#### Terminal 1 - User Service (Puerto 8001)
```bash
cd user-service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Terminal 2 - Course Service (Puerto 8002)
```bash
cd course-service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

#### Terminal 3 - Attendance Service (Puerto 8003)
```bash
cd attendance-service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload
```

#### Terminal 4 - Notification Service (Puerto 8004)
```bash
cd notification-service
python -m uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload
```

#### Terminal 5 - API Gateway (Puerto 8000)
```bash
cd api-gateway
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. 🗄️ Inicializar Base de Datos (Primera Vez)

Si estás iniciando con bases de datos vacías, ejecuta los scripts de inicialización:

```bash
cd database-init

# Windows - Paso 1: Crear admin
1-init-admin.bat

# Windows - Paso 2: Poblar datos
2-populate-db.bat

# Linux/Mac - Paso 1: Crear admin
chmod +x *.sh
./1-init-admin.sh

# Linux/Mac - Paso 2: Poblar datos
./2-populate-db.sh
```

**Datos creados:**
- 1 Administrador (admin@test.com / Password123!)
- 6 Profesores
- 5 Estudiantes
- 8 Aulas con GPS
- 7 Cursos
- 7 Horarios
- 13 Inscripciones

📖 **Documentación completa:** Ver `database-init/README.md`

### 8. Iniciar Frontend Web

```bash
cd web-dashboard
npm install
npm run dev
```

Accede a: **http://localhost:8080**

### 9. Iniciar Aplicación Móvil (Simulador)

```bash
cd mobile-simulator/geoattend-mobile
npm install
npm start
```

O para web:
```bash
npm run web
```

## 🌐 Servicios y Puertos

| Servicio | Puerto | Descripción | URL |
|----------|--------|-------------|-----|
| **API Gateway** | 8000 | Punto de entrada único | http://localhost:8000 |
| **User Service** | 8001 | Gestión de usuarios y autenticación | http://localhost:8001 |
| **Course Service** | 8002 | Gestión de cursos, aulas y horarios | http://localhost:8002 |
| **Attendance Service** | 8003 | Procesamiento GPS y asistencias | http://localhost:8003 |
| **Notification Service** | 8004 | Sistema de notificaciones | http://localhost:8004 |
| **Web Dashboard** | 8080 | Panel administrativo | http://localhost:8080 |
| **Mobile Simulator** | 19000 | App móvil (Expo) | http://localhost:19000 |

### Bases de Datos (Docker)
| Base de Datos | Puerto | Usuario | Password |
|--------------|--------|---------|----------|
| user-db | 5433 | postgres | postgres |
| course-db | 5434 | postgres | postgres |
| attendance-db | 5435 | postgres | postgres |
| notification-db | 5436 | postgres | postgres |

## 📊 Documentación de APIs

### Swagger/OpenAPI
- **User Service**: http://localhost:8001/docs
- **Course Service**: http://localhost:8002/docs
- **Attendance Service**: http://localhost:8003/docs
- **Notification Service**: http://localhost:8004/docs
- **API Gateway**: http://localhost:8000/docs

### Redoc
- **User Service**: http://localhost:8001/redoc
- **Course Service**: http://localhost:8002/redoc
- **Attendance Service**: http://localhost:8003/redoc

## 🗄️ Estructura de Base de Datos

### User Service (user_db)
- `users` - Información de usuarios (admin, teacher, student)
- `user_profiles` - Perfiles extendidos

### Course Service (course_db)
- `courses` - Cursos académicos
- `classrooms` - Aulas con ubicación GPS
- `schedules` - Horarios de clases
- `enrollments` - Inscripciones de estudiantes
- `course_classrooms` - Relación cursos-aulas (legacy)

### Attendance Service (attendance_db)
- `gps_events` - Eventos GPS recibidos
- `attendance_records` - Registros de asistencia procesados

### Notification Service (notification_db)
- `notifications` - Notificaciones del sistema

## 🔑 Credenciales Iniciales

### Usuarios de Prueba

```bash
# Administrador
Email: admin@test.com
Password: Password123!

# Profesor
Email: teacher@test.com
Password: Password123!

# Estudiante
Email: student@test.com
Password: Password123!
```

## 🧪 Testing

### Backend
```bash
# Ejecutar tests de un servicio
cd user-service
pytest

# Con coverage
pytest --cov=src tests/

# Tests específicos
pytest tests/test_auth.py -v
```

### Frontend Web
```bash
cd web-dashboard
npm test
```

### Mobile
```bash
cd mobile-simulator/geoattend-mobile
npm test
```

## 📱 Funcionalidades Implementadas

### ✅ Completadas

#### Dashboard Web (Admin/Teacher)
- ✅ Autenticación y autorización por roles
- ✅ Gestión completa de usuarios (CRUD)
- ✅ Gestión de cursos con horarios múltiples
- ✅ Gestión de aulas con mapa interactivo (Leaflet)
- ✅ Asignación de horarios a cursos con aulas específicas
- ✅ Gestión de inscripciones (enrollments)
- ✅ Visualización de asistencias y estadísticas
- ✅ Dashboard con métricas por rol

#### Aplicación Móvil (Estudiante)
- ✅ Login de estudiantes
- ✅ Visualización de cursos inscritos
- ✅ Visualización de horarios semanales
- ✅ Visualización de historial de asistencias

#### Backend
- ✅ Arquitectura de microservicios con FastAPI
- ✅ Autenticación JWT compartida entre servicios
- ✅ API Gateway con proxy a microservicios
- ✅ Validación de horarios (±15 min tolerancia)
- ✅ CRUD completo de todos los recursos
- ✅ Comunicación inter-servicios (HTTP)

### 🚧 Pendientes (TODOs)

#### Alta Prioridad
- ⏳ **Sistema de Notificaciones**
  - Envío de notificaciones push a estudiantes
  - Alertas de asistencia registrada
  - Recordatorios de clases próximas
  - Integración con Firebase Cloud Messaging

- ⏳ **GPS de Proximidad en App Móvil**
  - Captura de ubicación GPS del dispositivo
  - Cálculo de distancia al aula
  - Validación de proximidad antes de registrar
  - Visualización de mapa con ubicación del aula y del estudiante
  - Indicador visual de si está dentro del rango

#### Media Prioridad
- ⏳ Reportes avanzados (PDF/Excel)
- ⏳ Gráficos de estadísticas de asistencia
- ⏳ Sistema de justificaciones de ausencias
- ⏳ Notificaciones por email
- ⏳ Exportación de datos

#### Baja Prioridad
- ⏳ Modo offline en app móvil
- ⏳ Soporte multi-idioma
- ⏳ Tema oscuro completo
- ⏳ PWA para dashboard web

## 🔐 Seguridad

- **Autenticación**: JWT tokens con SECRET_KEY compartida
- **Autorización**: Role-based access control (admin, teacher, student)
- **CORS**: Configurado para desarrollo (allow all origins)
- **Password Hashing**: bcrypt
- **SQL Injection**: Prevención con SQLAlchemy ORM
- **Validación**: Pydantic schemas en todos los endpoints

## 📈 Monitoreo

### Health Checks
- User Service: http://localhost:8001/health
- Course Service: http://localhost:8002/health
- Attendance Service: http://localhost:8003/health
- Notification Service: http://localhost:8004/health
- API Gateway: http://localhost:8000/health

### Logs
```bash
# Ver logs de un servicio
docker-compose logs -f user-service

# Ver logs de todas las bases de datos
docker-compose logs -f user-db course-db attendance-db notification-db
```

## 🚢 Despliegue

### Desarrollo Local
Seguir las instrucciones de instalación arriba.

### Docker Compose (Producción)
```bash
# Build de todas las imágenes
docker-compose -f docker-compose.prod.yml build

# Levantar en producción
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Documentación Adicional

- [Arquitectura FastAPI Microservicios](ARQUITECTURA_FASTAPI_MICROSERVICIOS.md)
- [API Reference Completa](API_REFERENCE.md)
- [Guía de Testing](TESTING_GUIDE.md)
- [Mejores Prácticas FastAPI](FASTAPI_MICROSERVICES_BEST_PRACTICES.md)
- [Migración de Bases de Datos](MIGRACION_BASES_DATOS_INDEPENDIENTES.md)

## 🛠️ Comandos Útiles

### Docker
```bash
# Levantar solo bases de datos
docker-compose up -d user-db course-db attendance-db notification-db

# Detener todo
docker-compose down

# Limpiar volúmenes (⚠️ elimina datos)
docker-compose down -v

# Reconstruir imágenes
docker-compose build --no-cache
```

### Base de Datos
```bash
# Conectar a una base de datos
docker-compose exec user-db psql -U postgres -d user_db

# Backup de base de datos
docker-compose exec user-db pg_dump -U postgres user_db > backup.sql

# Restore de backup
docker-compose exec -T user-db psql -U postgres user_db < backup.sql
```

### Instalación de Dependencias
```bash
# Backend (cada servicio)
cd <service-name>
pip install -r requirements.txt

# Frontend Web
cd web-dashboard
npm install

# Mobile
cd mobile-simulator/geoattend-mobile
npm install
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 👥 Equipo

**Taller 3 - Sistemas de Información**
- Sistema de asistencia por geolocalización
- Arquitectura de microservicios con FastAPI
- Aplicación móvil con React Native/Expo
- Dashboard administrativo con React

## 📄 Licencia

Este proyecto es para fines académicos.

---

**🎯 Objetivo**: Demostrar dominio de arquitectura de microservicios, desarrollo full-stack, y sistemas de geolocalización en un sistema real de asistencia académica.
