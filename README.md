# GeoAttend - Sistema Inteligente de Asistencia por Geocerca

## 📋 Descripción del Proyecto

Sistema de registro automático de asistencia estudiantil mediante geolocalización, implementando una arquitectura de microservicios que demuestra principios de software adaptativo, modularidad y buenas prácticas de desarrollo.

## 🏗️ Arquitectura

- **Estilo Arquitectónico**: Microservicios con Event-Driven Architecture
- **Service Discovery**: Eureka Server
- **Configuración Centralizada**: Spring Cloud Config
- **API Gateway**: Spring Cloud Gateway
- **Base de Datos**: PostgreSQL con esquemas separados
- **Migraciones**: Flyway (como Django migrations)

## 🚀 Inicio Rápido

### 1. Prerrequisitos
- Java 17+
- Maven 3.8+
- Docker & Docker Compose
- PostgreSQL 15+

### 2. Configuración de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar las variables de entorno
# Configurar tu base de datos PostgreSQL
```

### 3. Configuración de Base de Datos

Crear la base de datos en PostgreSQL:
```sql
CREATE DATABASE Taller_3;
```

### 4. Ejecución con Docker

```bash
# Levantar todos los servicios
docker-compose up -d

# Verificar que todos los servicios estén corriendo
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs -f eureka-server
```

### 5. Ejecución en Desarrollo Local

```bash
# Compilar todos los módulos
mvn clean install

# Ejecutar servicios en orden
mvn spring-boot:run -pl eureka-server
mvn spring-boot:run -pl config-server
mvn spring-boot:run -pl user-service
mvn spring-boot:run -pl course-service
mvn spring-boot:run -pl attendance-service
mvn spring-boot:run -pl api-gateway
```

## 🌐 Servicios y Puertos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **API Gateway** | 8080 | Punto de entrada único |
| **User Service** | 8081 | Gestión de usuarios y autenticación |
| **Course Service** | 8082 | Gestión de cursos y aulas |
| **Attendance Service** | 8083 | Procesamiento GPS y asistencias |
| **Notification Service** | 8084 | Sistema de notificaciones |
| **Config Server** | 8888 | Configuración centralizada |
| **Eureka Server** | 8761 | Service Discovery |
| **PostgreSQL** | 5432 | Base de datos |

## 📊 URLs Importantes

### Dashboards y Monitoreo
- **Eureka Dashboard**: http://localhost:8761
- **API Gateway**: http://localhost:8080
- **Config Server**: http://localhost:8888

### Health Checks
- **Eureka**: http://localhost:8761/actuator/health
- **Config Server**: http://localhost:8888/actuator/health
- **User Service**: http://localhost:8081/actuator/health
- **Course Service**: http://localhost:8082/actuator/health
- **Attendance Service**: http://localhost:8083/actuator/health

### Documentación API (Swagger)
- **User Service**: http://localhost:8081/swagger-ui.html
- **Course Service**: http://localhost:8082/swagger-ui.html
- **Attendance Service**: http://localhost:8083/swagger-ui.html
- **API Gateway**: http://localhost:8080/swagger-ui.html

## 🗄️ Base de Datos

### Esquemas PostgreSQL
- **user_schema**: Usuarios, roles, autenticación
- **course_schema**: Cursos, aulas, horarios
- **attendance_schema**: Eventos GPS, asistencias
- **notification_schema**: Notificaciones, alertas

### Migraciones con Flyway
Las migraciones se ejecutan automáticamente al iniciar cada servicio:
```
src/main/resources/db/migration/
├── user/
│   ├── V1__create_users_table.sql
│   └── V2__create_roles_table.sql
├── course/
│   ├── V1__create_courses_table.sql
│   └── V2__create_classrooms_table.sql
└── attendance/
    ├── V1__create_events_table.sql
    └── V2__create_attendance_table.sql
```

## 🔧 Configuración

### Variables de Entorno (.env)
```bash
# Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Taller_3
DB_USERNAME=postgres
DB_PASSWORD=1234

# Seguridad
JWT_SECRET=tu-jwt-secret
CONFIG_SERVER_USERNAME=config-user
CONFIG_SERVER_PASSWORD=config-pass
```

### Configuración por Perfil
- **dev**: Desarrollo local
- **docker**: Ejecución en contenedores
- **prod**: Producción

## 🧪 Testing

```bash
# Ejecutar todos los tests
mvn test

# Tests de un servicio específico
mvn test -pl user-service

# Tests de integración con TestContainers
mvn test -Dtest=**/*IT
```

## 📱 APIs REST

### User Service
```bash
POST /api/users/register   # Registro de usuarios
POST /api/users/login      # Autenticación
GET  /api/users/profile    # Perfil de usuario
```

### Course Service
```bash
POST /api/courses          # Crear curso
GET  /api/courses          # Listar cursos
PUT  /api/courses/{id}/coordinates  # Actualizar coordenadas
```

### Attendance Service
```bash
POST /api/attendance/events       # Enviar evento GPS
GET  /api/attendance/course/{id}  # Asistencias por curso
GET  /api/attendance/reports      # Reportes
```

## 🔐 Seguridad

- **Autenticación**: JWT tokens
- **Autorización**: Role-based access control
- **HTTPS**: Todas las comunicaciones
- **Rate Limiting**: Prevención de ataques
- **Encriptación**: Datos sensibles en Config Server

## 📈 Monitoreo y Métricas

- **Health Checks**: Actuator endpoints
- **Métricas**: Prometheus endpoints
- **Logging**: Structured logging con niveles configurables
- **Distributed Tracing**: Para debugging de microservicios

## 🚢 Deployment

### Docker Production
```bash
# Build de imágenes
docker-compose -f docker-compose.prod.yml build

# Deploy en producción
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes (Opcional)
Archivos de deployment disponibles en `/k8s/`

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir un Pull Request

## 📚 Documentación Adicional

- [Arquitectura Completa](ARQUITECTURA_COMPLETA.md)
- [Diagramas de Arquitectura](DIAGRAMAS_ARQUITECTURA.md)
- [Eureka Server](eureka-server/README.md)
- [Config Server](config-server/README.md)
- [User Service](user-service/README.md)
- [Course Service](course-service/README.md)
- [Attendance Service](attendance-service/README.md)

## 👥 Equipo

**Taller 3 - Arquitectura de Microservicios**
- Sistema desarrollado para demostrar principios de software adaptativo
- Implementación de patrones de microservicios
- Integración continua y buenas prácticas

## 📄 Licencia

Este proyecto es para fines académicos del Taller 3.

---

**🎯 Objetivo**: Demostrar dominio de arquitectura de microservicios, software adaptativo y buenas prácticas de desarrollo en un sistema real de asistencia por geolocalización.