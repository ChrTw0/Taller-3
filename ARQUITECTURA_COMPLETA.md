# GeoAttend - Sistema Inteligente de Asistencia por Geocerca

## 1. Información del Proyecto

**Nombre:** GeoAttend - Sistema Inteligente de Asistencia por Geocerca
**Objetivo General:** Desarrollar un sistema adaptativo e integrado que automatice el registro de asistencia estudiantil mediante geolocalización, implementando una arquitectura de microservicios que demuestre principios de software adaptativo, modularidad y buenas prácticas de desarrollo.

## 2. Requisitos Funcionales

- **RF01**: Registro automático de asistencia por proximidad GPS (≤2m del aula)
- **RF02**: Gestión de usuarios (alumnos/profesores) con roles diferenciados
- **RF03**: Administración de cursos con coordenadas de aulas específicas
- **RF04**: Dashboard web para profesores con reportes de asistencia en tiempo real
- **RF05**: API REST para aplicación móvil Android
- **RF06**: Sistema de notificaciones push y alertas
- **RF07**: Generación de reportes estadísticos y exportación
- **RF08**: Configuración adaptativa del radio de detección por curso
- **RF09**: Registro manual de asistencia (backup/override)
- **RF10**: Historial completo de eventos de presencia

## 3. Requisitos No Funcionales

- **RNF01**: **Escalabilidad** - Soportar 1000+ usuarios concurrentes por servicio
- **RNF02**: **Disponibilidad** - 99.5% uptime con tolerancia a fallos
- **RNF03**: **Seguridad** - Autenticación JWT, encriptación HTTPS, validación de datos
- **RNF04**: **Adaptabilidad** - Configuración dinámica sin reiniciar servicios
- **RNF05**: **Rendimiento** - Tiempo de respuesta <2 segundos para operaciones críticas
- **RNF06**: **Portabilidad** - Dockerización completa, deployment en múltiples entornos
- **RNF07**: **Mantenibilidad** - Código modular, documentado y versionado
- **RNF08**: **Usabilidad** - Interfaces intuitivas, experiencia móvil optimizada

## 4. Estilo Arquitectónico

**Microservicios con Event-Driven Architecture + API Gateway Pattern**

### Características:
- **Descomposición por dominio de negocio**
- **Comunicación asíncrona mediante eventos**
- **Independencia de despliegue y escalado**
- **Tolerancia a fallos distribuida**
- **Punto de entrada único (API Gateway)**

## 5. Componentes Clave

### 5.1 Core Services
1. **API Gateway** (Puerto 8080)
   - Enrutamiento inteligente
   - Autenticación centralizada
   - Rate limiting y circuit breaker
   - Agregación de respuestas

2. **User Service** (Puerto 8081)
   - Gestión de usuarios y perfiles
   - Autenticación y autorización
   - Roles y permisos
   - Esquema: `user_schema`

3. **Course Service** (Puerto 8082)
   - CRUD de cursos y secciones
   - Gestión de coordenadas de aulas
   - Horarios y configuraciones
   - Esquema: `course_schema`

4. **Attendance Service** (Puerto 8083)
   - Procesamiento de eventos GPS
   - Cálculo de distancia haversine
   - Registro automático de asistencias
   - Esquema: `attendance_schema`

5. **Notification Service** (Puerto 8084)
   - Push notifications
   - Alertas en tiempo real
   - Sistema de mensajería

### 5.2 Infrastructure Services
1. **Eureka Server** (Puerto 8761)
   - Service discovery y registro
   - Health checks automáticos

2. **Config Server** (Puerto 8888)
   - Configuración centralizada
   - Refresh dinámico

3. **PostgreSQL** (Puerto 5432)
   - Base de datos principal
   - Esquemas separados por servicio

## 6. Comunicación e Interfaces

### 6.1 Patrones de Comunicación
- **Síncrono**: REST APIs para operaciones CRUD
- **Asíncrono**: Message Queues para eventos de asistencia
- **Service Discovery**: Eureka para localización automática

### 6.2 APIs REST Principales

#### User Service API
```
POST   /api/users/register
POST   /api/users/login
GET    /api/users/profile/{id}
PUT    /api/users/profile/{id}
```

#### Course Service API
```
POST   /api/courses
GET    /api/courses
GET    /api/courses/{id}
PUT    /api/courses/{id}/coordinates
```

#### Attendance Service API
```
POST   /api/attendance/events
GET    /api/attendance/course/{courseId}
GET    /api/attendance/reports/{courseId}
```

### 6.3 Event-Driven Architecture
```
GPS Event → Attendance Service → Attendance Registered Event → Notification Service
```

## 7. Tecnologías y Herramientas

### 7.1 Backend Stack
- **Framework**: Spring Boot 3.2.0
- **Service Discovery**: Spring Cloud Netflix Eureka
- **API Gateway**: Spring Cloud Gateway
- **Configuration**: Spring Cloud Config
- **Security**: Spring Security + JWT
- **Persistence**: Spring Data JPA + PostgreSQL
- **Documentation**: OpenAPI 3.0 (Swagger)

### 7.2 Infrastructure
- **Containerización**: Docker + Docker Compose
- **Base de Datos**: PostgreSQL 15
- **Message Broker**: RabbitMQ (opcional)
- **Monitoring**: Spring Boot Actuator

### 7.3 Frontend/Mobile
- **Web Dashboard**: React.js + Axios
- **Mobile App**: Android (Simulado para demo)

### 7.4 Development Tools
- **Build**: Maven
- **Version Control**: Git
- **IDE**: IntelliJ IDEA / Eclipse
- **Testing**: JUnit 5 + Mockito

## 8. Seguridad y Rendimiento

### 8.1 Seguridad
- **Autenticación**: JWT con refresh tokens
- **Autorización**: Role-based access control (RBAC)
- **Comunicación**: HTTPS en todas las interfaces
- **Validación**: Input validation en todos los endpoints
- **Rate Limiting**: Prevención de ataques DDoS

### 8.2 Rendimiento
- **Caching**: Redis para datos frecuentes
- **Database**: Índices optimizados, connection pooling
- **Load Balancing**: Eureka client-side load balancing
- **Circuit Breaker**: Hystrix para tolerancia a fallos

## 9. Aspectos de Software Adaptativo

### 9.1 Configuración Dinámica
- Radio de detección GPS configurable por curso
- Horarios de clases adaptables
- Reglas de validación personalizables

### 9.2 Escalabilidad Automática
- Auto-scaling horizontal de servicios
- Database connection pooling dinámico
- Load balancing adaptativo

### 9.3 Tolerancia a Fallos
- Circuit breaker patterns
- Retry mechanisms
- Graceful degradation

## 10. Estructura del Proyecto

```
geoattend-system/
├── docs/                           # Documentación completa
├── eureka-server/                  # Service Discovery
├── config-server/                 # Configuración centralizada
├── api-gateway/                   # API Gateway
├── user-service/                  # Gestión de usuarios
├── course-service/                # Gestión de cursos
├── attendance-service/            # Procesamiento asistencias
├── notification-service/          # Sistema de notificaciones
├── web-dashboard/                 # Frontend React
├── mobile-simulator/              # Simulador Android
├── docker-compose.yml             # Orquestación completa
├── README.md                      # Guía principal
└── DEPLOYMENT.md                  # Guía de despliegue
```

## 11. Plan de Desarrollo (2 Semanas)

### Semana 1: Core Architecture
- **Días 1-2**: Setup inicial + Eureka + Config Server
- **Días 3-4**: User Service + Course Service
- **Días 5-7**: Attendance Service + API Gateway

### Semana 2: Integration & Frontend
- **Días 8-9**: Notification Service + Web Dashboard
- **Días 10-11**: Mobile Simulator + Testing integrado
- **Días 12-14**: Documentación + Deployment + Demo

## 12. Entregables Académicos

1. **Código fuente completo** (GitHub)
2. **Documentación arquitectónica** (este documento)
3. **Diagramas de arquitectura** (C4 Model)
4. **Manual de instalación y uso**
5. **Video demo funcional**
6. **Reporte de testing y métricas**
7. **Presentación técnica**