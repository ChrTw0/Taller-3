# API Reference - GeoAttend Microservices

## 📋 Tabla de Contenidos
- [User Service (Puerto 8001)](#user-service-puerto-8001)
- [Course Service (Puerto 8002)](#course-service-puerto-8002)
- [Attendance Service (Puerto 8003)](#attendance-service-puerto-8003)
- [Notification Service (Puerto 8004)](#notification-service-puerto-8004)
- [API Gateway (Puerto 8000)](#api-gateway-puerto-8000)

---

## User Service (Puerto 8001)

### Autenticación

#### POST `/api/v1/auth/register`
**Descripción:** Registrar un nuevo usuario (requiere autenticación como admin)
**Auth:** Bearer Token (admin)
**Body:**
```json
{
  "code": "EST001",
  "email": "user@example.com",
  "password": "Password123!",
  "first_name": "Juan",
  "last_name": "Perez",
  "role": "student|teacher|admin"
}
```
**Response:**
```json
{
  "message": "User registered successfully",
  "data": { ...user }
}
```
**Nota:** Solo administradores pueden registrar nuevos usuarios

#### POST `/api/v1/auth/login`
**Descripción:** Iniciar sesión
**Body:**
```json
{
  "email": "user@example.com",
  "password": "Password123!"
}
```
**Response:**
```json
{
  "message": "Login successful",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 86400
  },
  "user": {
    "id": 1,
    "code": "EST001",
    "first_name": "Juan",
    "last_name": "Perez",
    "role": "student",
    "is_active": true
  }
}
```

#### POST `/api/v1/auth/refresh`
**Descripción:** Refrescar token JWT
**Auth:** Bearer Token
**Response:** `501 Not Implemented` (por implementar)

#### POST `/api/v1/auth/logout`
**Descripción:** Cerrar sesión (cliente maneja token)
**Response:**
```json
{
  "message": "Logout successful"
}
```

### Usuarios

#### POST `/api/v1/users/`
**Descripción:** Crear nuevo usuario
**Auth:** Bearer Token (puede ser público dependiendo de configuración)
**Body:**
```json
{
  "code": "EST001",
  "email": "user@example.com",
  "password": "Password123!",
  "first_name": "Juan",
  "last_name": "Perez",
  "role": "student|teacher|admin"
}
```
**Response:**
```json
{
  "message": "User created successfully",
  "data": { ...user }
}
```

#### GET `/api/v1/users/me`
**Descripción:** Obtener perfil del usuario actual
**Auth:** Bearer Token
**Response:** `UserResponse`

#### PUT `/api/v1/users/me`
**Descripción:** Actualizar perfil del usuario actual
**Auth:** Bearer Token
**Body:** Campos a actualizar (first_name, last_name, password)
**Response:** `UserResponse`

#### GET `/api/v1/users/{id}`
**Descripción:** Obtener usuario por ID (solo información pública)
**Auth:** No requerido
**Response:** `UserPublic` (sin email)

#### GET `/api/v1/users/internal/{id}` 🔧 **INTERNAL**
**Descripción:** Obtener usuario con email (solo inter-servicio)
**Auth:** Bearer Token (inter-service)
**Response:** `UserInternal` (con email)

#### GET `/api/v1/users/code/{code}`
**Descripción:** Obtener usuario por código (público)
**Auth:** No requerido
**Response:** `UserPublic`

#### GET `/api/v1/users/teachers`
**Descripción:** Listar solo profesores y admins (público)
**Auth:** No requerido
**Response:** `UserPublic[]`

#### GET `/api/v1/users/`
**Descripción:** Listar todos los usuarios (solo admin)
**Auth:** Bearer Token (admin)
**Query Params:**
- `skip` (int): Paginación offset
- `limit` (int): Cantidad de resultados (max: 1000)

**Response:** `UserPublic[]`

#### DELETE `/api/v1/users/{id}`
**Descripción:** Desactivar usuario (solo admin)
**Auth:** Bearer Token (admin)
**Response:**
```json
{
  "success": true,
  "message": "User deactivated successfully"
}
```

---

## Course Service (Puerto 8002)

### Cursos

#### GET `/api/v1/courses/`
**Descripción:** Listar cursos con filtros opcionales
**Auth:** Bearer Token
**Query Params:**
- `skip` (int): Paginación offset
- `limit` (int): Cantidad de resultados
- `teacher_id` (int): Filtrar por profesor
- `academic_year` (string): Filtrar por año
- `is_active` (bool): Filtrar por estado activo

**Response:**
```json
{
  "success": true,
  "message": "Courses retrieved successfully",
  "data": [...courses],
  "total": 10,
  "page": 1,
  "per_page": 100
}
```

#### GET `/api/v1/courses/{id}/`
**Descripción:** Obtener curso por ID
**Auth:** Bearer Token
**Query Params:**
- `include_details` (bool): Incluir aulas asignadas

**Response:** `Course`

#### POST `/api/v1/courses/`
**Descripción:** Crear nuevo curso
**Auth:** Bearer Token (admin)
**Body:**
```json
{
  "code": "SI805V",
  "name": "Integración de Sistemas",
  "description": "...",
  "credits": 4,
  "academic_year": "2025",
  "semester": "A",
  "teacher_id": 7,
  "teacher_code": "PROF005",
  "max_students": 35,
  "detection_radius": 2.5
}
```
**Response:**
```json
{
  "success": true,
  "message": "Course created successfully",
  "data": { ...course }
}
```

#### PUT `/api/v1/courses/{id}`
**Descripción:** Actualizar curso
**Auth:** Bearer Token (admin)
**Body:** Campos a actualizar (name, description, max_students, detection_radius, is_active)
**Response:**
```json
{
  "success": true,
  "message": "Course updated successfully",
  "data": { ...course }
}
```

#### DELETE `/api/v1/courses/{id}/`
**Descripción:** Desactivar curso (soft delete)
**Auth:** Bearer Token (admin)
**Response:**
```json
{
  "message": "Course deactivated successfully"
}
```

#### GET `/api/v1/courses/code/{course_code}` 🔧 **SPECIAL**
**Descripción:** Obtener curso por código
**Auth:** Bearer Token
**Response:** `Course`

#### GET `/api/v1/courses/{id}/coordinates` 🔧 **INTERNAL**
**Descripción:** Obtener coordenadas GPS del curso (para Attendance Service)
**Auth:** Bearer Token (inter-service)
**Response:**
```json
{
  "course_id": 2,
  "course_code": "SI805V",
  "detection_radius": 50.0,
  "classrooms": [
    {
      "id": 1,
      "code": "AULA101",
      "latitude": -12.0564,
      "longitude": -77.0844,
      "altitude": 154.5,
      "gps_radius": 50.0
    }
  ]
}
```

### Aulas (Classrooms)

#### GET `/api/v1/classrooms/`
**Descripción:** Listar aulas
**Auth:** Bearer Token
**Query Params:**
- `is_active` (bool): Filtrar por estado
- `building` (string): Filtrar por edificio
- `skip` (int): Paginación
- `limit` (int): Límite

**Response:** `Classroom[]`

#### GET `/api/v1/classrooms/{id}/`
**Descripción:** Obtener aula por ID
**Auth:** Bearer Token
**Response:** `Classroom`

#### POST `/api/v1/classrooms/`
**Descripción:** Crear aula
**Auth:** Bearer Token (admin)
**Body:**
```json
{
  "code": "AULA101",
  "name": "Aula 101",
  "building": "A",
  "room_number": "101",
  "floor": 1,
  "latitude": -12.0564,
  "longitude": -77.0844,
  "altitude": 154.5,
  "gps_radius": 50.0,
  "capacity": 40
}
```
**Response:** `{ success: true, message: "...", data: {...} }`

#### PUT `/api/v1/classrooms/{id}/`
**Descripción:** Actualizar aula
**Auth:** Bearer Token (admin)
**Response:** `{ success: true, message: "...", data: {...} }`

#### DELETE `/api/v1/classrooms/{id}/`
**Descripción:** Desactivar aula (soft delete)
**Auth:** Bearer Token (admin)
**Response:**
```json
{
  "success": true,
  "message": "Classroom {code} deleted successfully"
}
```

### Inscripciones (Enrollments)

#### GET `/api/v1/enrollments/`
**Descripción:** Listar inscripciones con filtros
**Auth:** Bearer Token
**Query Params:**
- `course_id` (int): Filtrar por curso
- `student_id` (int): Filtrar por estudiante
- `status` (string): active|completed|dropped

**Response:** `Enrollment[]`

#### POST `/api/v1/enrollments/course/{course_id}`
**Descripción:** Inscribir estudiante en un curso
**Auth:** Bearer Token (admin)
**Body:**
```json
{
  "student_id": 1,
  "student_code": "EST001",
  "status": "active"
}
```
**Response:** `Enrollment`

#### GET `/api/v1/enrollments/course/{course_id}`
**Descripción:** Obtener todas las inscripciones activas de un curso
**Auth:** Bearer Token
**Response:** `Enrollment[]`

#### GET `/api/v1/enrollments/student/{student_id}`
**Descripción:** Obtener todas las inscripciones activas de un estudiante
**Auth:** Bearer Token
**Response:** `Enrollment[]`

### Horarios de Clase (Schedules)

#### POST `/api/v1/schedules/course/{course_id}`
**Descripción:** Crear horario de clase para un curso
**Auth:** Bearer Token (admin)
**Body:**
```json
{
  "day_of_week": 0,
  "start_time": "10:00:00",
  "end_time": "12:00:00",
  "classroom_id": 1
}
```
**Nota:** `day_of_week`: 0=Lunes, 1=Martes, ..., 6=Domingo
**Response:**
```json
{
  "success": true,
  "message": "Schedule created successfully for course 2",
  "data": {
    "id": 1,
    "course_id": 2,
    "day_of_week": 0,
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "classroom_id": 1,
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z"
  }
}
```

#### GET `/api/v1/schedules/course/{course_id}`
**Descripción:** Obtener todos los horarios de un curso
**Auth:** Bearer Token
**Query Params:**
- `include_inactive` (bool): Incluir horarios inactivos (default: false)

**Response:**
```json
{
  "success": true,
  "message": "Schedules for course 2",
  "data": [
    {
      "id": 1,
      "course_id": 2,
      "day_of_week": 0,
      "start_time": "10:00:00",
      "end_time": "12:00:00",
      "classroom_id": 1,
      "is_active": true,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

#### GET `/api/v1/schedules/course/{course_id}/current` 🎯 **IMPORTANTE**
**Descripción:** Obtener el horario actualmente activo del curso (basado en día y hora actual)
**Auth:** Bearer Token
**Response:**
```json
{
  "success": true,
  "message": "Current active schedule",
  "data": {
    "id": 1,
    "course_id": 2,
    "day_of_week": 0,
    "start_time": "10:00:00",
    "end_time": "12:00:00",
    "classroom_id": 1,
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z"
  }
}
```
**Nota:** Retorna `null` en `data` si no hay clase en el horario actual. Incluye tolerancia de ±15 minutos.

#### GET `/api/v1/schedules/{schedule_id}`
**Descripción:** Obtener horario por ID
**Auth:** Bearer Token
**Response:** `Schedule`

#### PUT `/api/v1/schedules/{schedule_id}`
**Descripción:** Actualizar horario
**Auth:** Bearer Token (admin)
**Body:**
```json
{
  "day_of_week": 2,
  "start_time": "14:00:00",
  "end_time": "16:00:00",
  "classroom_id": 2,
  "is_active": true
}
```
**Response:**
```json
{
  "success": true,
  "message": "Schedule updated successfully",
  "data": { ...schedule }
}
```

#### DELETE `/api/v1/schedules/{schedule_id}`
**Descripción:** Desactivar horario (soft delete)
**Auth:** Bearer Token (admin)
**Response:**
```json
{
  "success": true,
  "message": "Schedule deleted successfully",
  "data": null
}
```

---

## Attendance Service (Puerto 8003)

### Registros de Asistencia

#### GET `/api/v1/attendance/records`
**Descripción:** Listar registros de asistencia
**Auth:** Bearer Token
**Query Params:**
- `user_id` (int): Filtrar por usuario
- `course_id` (int): Filtrar por curso
- `start_date` (datetime): Fecha inicio
- `end_date` (datetime): Fecha fin
- `status_filter` (string): present|late|absent|excused
- `skip` (int): Paginación
- `limit` (int): Límite

**Response:**
```json
{
  "success": true,
  "message": "Attendance records retrieved successfully",
  "data": [...records],
  "total": 10,
  "page": 1,
  "per_page": 100
}
```

#### GET `/api/v1/attendance/course/{course_id}/records`
**Descripción:** Registros de asistencia de un curso
**Auth:** Bearer Token
**Response:** Similar a `/records`

#### GET `/api/v1/attendance/user/{user_id}/stats`
**Descripción:** Estadísticas de asistencia de un usuario
**Auth:** Bearer Token
**Query Params:**
- `course_id` (int): Opcional, filtrar por curso
- `start_date` (string): Fecha inicio
- `end_date` (string): Fecha fin

**Response:**
```json
{
  "user_id": 1,
  "total_records": 10,
  "present_count": 8,
  "late_count": 1,
  "absent_count": 1,
  "attendance_rate": 90.0
}
```

#### GET `/api/v1/attendance/course/{course_id}/stats`
**Descripción:** Estadísticas de asistencia de un curso
**Auth:** Bearer Token
**Query Params:**
- `start_date` (string): Fecha inicio
- `end_date` (string): Fecha fin

**Response:**
```json
{
  "course_id": 2,
  "total_records": 50,
  "present_count": 40,
  "late_count": 5,
  "absent_count": 5,
  "average_attendance_rate": 85.0
}
```

### GPS Events

#### POST `/api/v1/gps/event` 🎯 **CORE ENDPOINT**
**Descripción:** **ENDPOINT PRINCIPAL** - Procesar evento GPS desde app móvil y registrar asistencia automáticamente
**Auth:** Bearer Token
**Body:**
```json
{
  "user_id": 1,
  "course_id": 2,
  "latitude": -12.0464,
  "longitude": -77.0428,
  "accuracy": 5.0,
  "event_timestamp": "2024-10-01T10:30:00Z"
}
```
**Proceso:**
1. Valida coordenadas GPS y precisión
2. Verifica inscripción del usuario en el curso
3. **✨ NUEVO:** Valida que haya un horario de clase activo (±15 min tolerancia)
4. Calcula distancia al aula más cercana
5. Registra asistencia si está dentro del rango
6. Envía notificación al estudiante

**⚠️ IMPORTANTE:** El sistema ahora valida que la asistencia se registre solo durante el horario de clase. Si no hay un horario activo, retornará error 400.

**Response:**
```json
{
  "success": true,
  "message": "GPS event processed successfully",
  "data": {
    "gps_event_id": "uuid",
    "attendance_recorded": true,
    "status": "present|late|absent",
    "distance_meters": 15.5,
    "nearest_classroom": { ...classroom }
  }
}
```

#### POST `/api/v1/gps/validate`
**Descripción:** Validar coordenadas GPS sin procesar asistencia (útil para testing)
**Auth:** Bearer Token
**Body:**
```json
{
  "latitude": -12.0464,
  "longitude": -77.0428,
  "accuracy": 5.0,
  "course_id": 2
}
```
**Response:**
```json
{
  "valid_coordinates": true,
  "course_id": 2,
  "detection_radius": 50.0,
  "nearest_classroom": { ...classroom },
  "distance_meters": 25.50,
  "within_range": true,
  "accuracy": 5.0
}
```

### Reportes de Asistencia

#### GET `/api/v1/reports/attendance-summary`
**Descripción:** Generar reporte de resumen de asistencia
**Auth:** Bearer Token
**Query Params:**
- `course_id` (int): Filtrar por curso
- `start_date` (datetime): Fecha inicio
- `end_date` (datetime): Fecha fin

**Response:**
```json
{
  "summary": "Attendance report for X course(s)",
  "total_records": 100,
  "period": {
    "start_date": "2024-10-01",
    "end_date": "2024-10-31"
  },
  "overall_statistics": {
    "total_records": 100,
    "present_count": 80,
    "late_count": 15,
    "absent_count": 5,
    "attendance_rate": 95.0,
    "punctuality_rate": 80.0
  },
  "by_course": [...]
}
```

#### GET `/api/v1/reports/daily-attendance/{date}`
**Descripción:** Reporte de asistencia diaria
**Auth:** Bearer Token
**Query Params:**
- `course_id` (int): Filtrar por curso

**Response:**
```json
{
  "date": "2024-10-01",
  "total_records": 50,
  "total_courses": 3,
  "courses": [...]
}
```

#### GET `/api/v1/reports/gps-events/recent`
**Descripción:** Obtener eventos GPS recientes para monitoreo
**Auth:** Bearer Token
**Query Params:**
- `limit` (int): Número de eventos (default: 50, max: 500)
- `status_filter` (string): Filtrar por estado

**Response:**
```json
{
  "total_events": 50,
  "status_filter": "processed",
  "events": [...]
}
```

---

## Notification Service (Puerto 8004)

### Notificaciones por Email

#### POST `/api/v1/notifications/email`
**Descripción:** Enviar notificación por email
**Auth:** Bearer Token
**Body:**
```json
{
  "user_id": 1,
  "subject": "Asistencia registrada",
  "message": "Tu asistencia ha sido registrada exitosamente",
  "notification_type": "attendance|course|system",
  "metadata": { ... }
}
```
**Response:**
```json
{
  "success": true,
  "notification_id": 123,
  "message": "Email notification sent successfully",
  "status": "sent"
}
```

### Notificaciones Push

#### POST `/api/v1/notifications/push`
**Descripción:** Enviar notificación push
**Auth:** Bearer Token
**Body:**
```json
{
  "user_id": 1,
  "title": "Asistencia registrada",
  "body": "Tu asistencia ha sido registrada exitosamente",
  "notification_type": "attendance|course|system",
  "metadata": { ... }
}
```
**Response:**
```json
{
  "success": true,
  "notification_id": 124,
  "message": "Push notification sent successfully",
  "status": "sent"
}
```

### Historial de Notificaciones

#### GET `/api/v1/notifications/user/{user_id}`
**Descripción:** Obtener notificaciones de un usuario
**Auth:** Bearer Token
**Query Params:**
- `limit` (int): Cantidad de notificaciones (default: 50)
- `offset` (int): Paginación (default: 0)

**Response:**
```json
{
  "total": 10,
  "notifications": [...]
}
```

### Preferencias de Notificación

#### GET `/api/v1/notifications/preferences/{user_id}`
**Descripción:** Obtener preferencias de notificación del usuario
**Auth:** Bearer Token
**Response:**
```json
{
  "user_id": 1,
  "email_enabled": true,
  "push_enabled": true,
  "sms_enabled": false,
  "attendance_notifications": true,
  "course_notifications": true,
  "system_notifications": true,
  "created_at": "2024-10-01T10:00:00Z",
  "updated_at": "2024-10-01T10:00:00Z"
}
```

#### PUT `/api/v1/notifications/preferences/{user_id}`
**Descripción:** Actualizar preferencias de notificación
**Auth:** Bearer Token
**Body:**
```json
{
  "email_enabled": true,
  "push_enabled": false,
  "attendance_notifications": true
}
```
**Response:** `UserNotificationPreferenceResponse`

### Device Token (Push Notifications)

#### POST `/api/v1/notifications/device-token`
**Descripción:** Actualizar token de dispositivo para notificaciones push
**Auth:** Bearer Token
**Body:**
```json
{
  "user_id": 1,
  "device_token": "fcm-device-token-here",
  "device_type": "android|ios"
}
```
**Response:** `UserNotificationPreferenceResponse`

### Templates de Notificación

#### POST `/api/v1/notifications/templates`
**Descripción:** Crear plantilla de notificación
**Auth:** Bearer Token (admin)
**Body:**
```json
{
  "name": "attendance_confirmation",
  "notification_type": "attendance",
  "template_content": "Tu asistencia en {course_name} ha sido registrada",
  "is_active": true
}
```
**Response:** `NotificationTemplateResponse`

---

## API Gateway (Puerto 8000)

**Nota:** Todos los endpoints anteriores se acceden a través del API Gateway con el prefijo `/api/v1/`

### Rutas del Gateway

| Ruta Original | Gateway Route | Destino |
|--------------|---------------|---------|
| `/users/*` | `/api/v1/users/*` | User Service (8001) |
| `/auth/*` | `/api/v1/auth/*` | User Service (8001) |
| `/courses/*` | `/api/v1/courses/*` | Course Service (8002) |
| `/classrooms/*` | `/api/v1/classrooms/*` | Course Service (8002) |
| `/enrollments/*` | `/api/v1/enrollments/*` | Course Service (8002) |
| `/attendance/*` | `/api/v1/attendance/*` | Attendance Service (8003) |
| `/gps/*` | `/api/v1/gps/*` | Attendance Service (8003) |
| `/reports/*` | `/api/v1/reports/*` | Attendance Service (8003) |
| `/notifications/*` | `/api/v1/notifications/*` | Notification Service (8004) |

### Configuración

- **CORS Origins:** `http://localhost:3000`, `http://localhost:5173`, `http://localhost:8080`
- **Rate Limiting:** 60 requests/minute (configurable)
- **JWT Secret:** `user-service-secret-key-change-in-production` (compartido con todos los servicios)
- **JWT Algorithm:** HS256
- **Token Expiration:** 1440 minutos (24 horas)

---

## 🔐 Autenticación

Todos los endpoints (excepto `/auth/login`, `/auth/register` y `/users/teachers`) requieren autenticación Bearer Token:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📝 Roles de Usuario

- **admin:** Acceso completo a todos los endpoints
- **teacher:** Acceso a sus cursos, estudiantes y asistencias
- **student:** Acceso a sus propios datos, cursos inscritos y asistencias

## 🗄️ Bases de Datos

- **user_db** (Puerto 5433): Usuarios y autenticación
- **course_db** (Puerto 5434): Cursos, aulas e inscripciones
- **attendance_db** (Puerto 5435): Asistencias y eventos GPS
- **notification_db** (Puerto 5436): Notificaciones

## 🔑 SECRET_KEY Compartido

Todos los servicios usan el mismo SECRET_KEY para verificar tokens JWT:
```
SECRET_KEY=user-service-secret-key-change-in-production
```

## 📱 Frontend (Puerto 8080)

El dashboard web consume la API a través del API Gateway en `http://localhost:8000/api/v1/`

---

## 📊 Resumen de Validación

### ✅ Endpoints Validados Correctamente

**User Service:**
- ✅ Auth: `/auth/login`, `/auth/register`, `/auth/refresh`, `/auth/logout`
- ✅ Users: `/users/`, `/users/me`, `/users/{id}`, `/users/code/{code}`, `/users/internal/{id}`, `/users/teachers`

**Course Service:**
- ✅ Courses: `/courses/`, `/courses/{id}`, `/courses/code/{code}`, `/courses/{id}/coordinates`
- ✅ Classrooms: `/classrooms/`, `/classrooms/{id}`
- ✅ Enrollments: `/enrollments/`, `/enrollments/course/{id}`, `/enrollments/student/{id}`

**Attendance Service:**
- ✅ GPS: `/gps/event` (CORE), `/gps/validate`
- ✅ Attendance: `/attendance/records`, `/attendance/course/{id}/records`, `/attendance/user/{id}/stats`, `/attendance/course/{id}/stats`
- ✅ Reports: `/reports/attendance-summary`, `/reports/daily-attendance/{date}`, `/reports/gps-events/recent`

**Notification Service:**
- ✅ Notifications: `/notifications/email`, `/notifications/push`, `/notifications/user/{id}`
- ✅ Preferences: `/notifications/preferences/{id}`, `/notifications/device-token`
- ✅ Templates: `/notifications/templates`

### 🔑 Endpoints Clave por Funcionalidad

**Autenticación y Usuarios:**
1. `POST /api/v1/auth/login` - Login (público)
2. `POST /api/v1/auth/register` - Registro (admin)
3. `GET /api/v1/users/me` - Perfil actual
4. `GET /api/v1/users/teachers` - Lista de profesores (público)

**Gestión de Cursos:**
1. `GET /api/v1/courses/` - Listar cursos
2. `POST /api/v1/courses/` - Crear curso (admin)
3. `GET /api/v1/courses/{id}/coordinates` - Coordenadas GPS (interno)

**Asistencia GPS (CORE):**
1. `POST /api/v1/gps/event` - **ENDPOINT PRINCIPAL** - Procesar GPS y registrar asistencia
2. `POST /api/v1/gps/validate` - Validar coordenadas sin registrar
3. `GET /api/v1/attendance/records` - Obtener registros de asistencia

**Reportes:**
1. `GET /api/v1/reports/attendance-summary` - Resumen general
2. `GET /api/v1/attendance/user/{id}/stats` - Estadísticas de usuario
3. `GET /api/v1/attendance/course/{id}/stats` - Estadísticas de curso

### 🔧 Endpoints Internos (Inter-servicio)

Estos endpoints están marcados con 🔧 y son para comunicación entre microservicios:
- `GET /api/v1/users/internal/{id}` - Obtener usuario con email
- `GET /api/v1/courses/{id}/coordinates` - Obtener coordenadas de curso

### 📝 Notas Importantes

1. **Campo Mapping**: El backend usa `academic_year` y `detection_radius`, pero el frontend mapea a `year` y `gps_radius`
2. **Soft Deletes**: Los DELETE endpoints desactivan registros (is_active=false) en lugar de eliminarlos
3. **Autenticación**: `/auth/register` requiere rol admin, a diferencia de `/users/` que puede ser público según configuración
4. **Endpoints Públicos**: `/auth/login`, `/users/teachers`, `/users/{id}`, `/users/code/{code}` no requieren autenticación
