# Config Server - Configuración Centralizada

## Descripción
Servidor de configuración centralizada para el ecosistema de microservicios GeoAttend. Proporciona gestión externa de configuraciones, encriptación de datos sensibles y refresh dinámico.

## Características

### ✅ Configuración Centralizada
- Configuraciones específicas por servicio
- Configuración común compartida
- Perfiles de entorno (dev, test, prod)

### ✅ Seguridad
- Autenticación básica para acceso
- Encriptación de datos sensibles
- Configuración de CORS y JWT centralizada

### ✅ Refresh Dinámico
- Actualización de configuraciones sin reinicio
- Endpoint `/actuator/refresh` para cada servicio
- Notificación automática de cambios

### ✅ Integration Ready
- Registro automático en Eureka
- Health checks para Docker
- Métricas y monitoreo

## Estructura de Configuraciones

```
config-server/src/main/resources/config/
├── application.yml          # Configuración común
├── user-service.yml        # Configuración específica User Service
├── course-service.yml       # Configuración específica Course Service
├── attendance-service.yml   # Configuración específica Attendance Service
└── api-gateway.yml         # Configuración específica API Gateway
```

## Configuración por Servicio

### User Service
- Configuración JWT específica
- Validación de códigos de usuario
- Rate limiting para endpoints de autenticación
- Esquema de base de datos: `user_schema`

### Course Service
- Configuración geoespacial
- Validación de coordenadas
- Configuración de horarios académicos
- Esquema de base de datos: `course_schema`

### Attendance Service
- Algoritmos de geolocalización (Haversine)
- Configuración de asistencia automática
- Procesamiento de eventos GPS
- Configuración de notificaciones
- Esquema de base de datos: `attendance_schema`

### API Gateway
- Rutas y balanceadores
- Circuit breakers
- Rate limiting global
- Configuración CORS

## Ejecución

### Desarrollo Local
```bash
mvn spring-boot:run
```

### Docker
```bash
docker build -t geoattend/config-server .
docker run -p 8888:8888 geoattend/config-server
```

### Acceso a Configuraciones

- **Usuario**: config-user
- **Password**: config-pass

### Endpoints Importantes

- **Config User Service**: http://localhost:8888/user-service/default
- **Config Course Service**: http://localhost:8888/course-service/default
- **Config Attendance Service**: http://localhost:8888/attendance-service/default
- **Config API Gateway**: http://localhost:8888/api-gateway/default
- **Health Check**: http://localhost:8888/actuator/health
- **Refresh**: http://localhost:8888/actuator/refresh

## Encriptación de Datos Sensibles

### Encriptar valores sensibles:
```bash
curl -u config-user:config-pass -X POST \
  http://localhost:8888/encrypt \
  -H "Content-Type: text/plain" \
  -d "password123"
```

### Usar en configuración:
```yaml
spring:
  datasource:
    password: '{cipher}AQATzPqKz8wGRQq9Vx...'
```

### Desencriptar:
```bash
curl -u config-user:config-pass -X POST \
  http://localhost:8888/decrypt \
  -H "Content-Type: text/plain" \
  -d "AQATzPqKz8wGRQq9Vx..."
```

## Refresh de Configuraciones

Para actualizar configuraciones sin reiniciar servicios:

```bash
# Actualizar configuración de un servicio específico
curl -X POST http://localhost:8081/actuator/refresh

# Actualizar todas las configuraciones
curl -X POST http://localhost:8888/actuator/bus-refresh
```

## Integración con Servicios

Los microservicios obtienen configuración agregando:

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-config</artifactId>
</dependency>
```

```yaml
spring:
  config:
    import: "configserver:http://config-server:8888"
  cloud:
    config:
      username: config-user
      password: config-pass
```

## Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Service  │    │ Course Service  │    │Attendance Service│
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              Get Config from                  │
         └───────────────────────┼───────────────────────┘
                                 │
                     ┌─────────────────┐
                     │ Config Server   │
                     │   (8888)        │
                     │                 │
                     │ ┌─────────────┐ │
                     │ │application  │ │
                     │ │.yml (común) │ │
                     │ └─────────────┘ │
                     │ ┌─────────────┐ │
                     │ │user-service │ │
                     │ │.yml         │ │
                     │ └─────────────┘ │
                     │ ┌─────────────┐ │
                     │ │course-service│ │
                     │ │.yml         │ │
                     │ └─────────────┘ │
                     └─────────────────┘
                                 │
                                 │ Register with
                                 ▼
                     ┌─────────────────┐
                     │ Eureka Server   │
                     │    (8761)       │
                     └─────────────────┘
```

## Ventajas del Config Server

### 🔧 Gestión Centralizada
- Una sola ubicación para todas las configuraciones
- Versionado de configuraciones
- Rollback fácil de cambios

### 🔒 Seguridad
- Encriptación de datos sensibles
- Control de acceso centralizado
- Separación de configuración y código

### 🔄 Flexibilidad
- Configuraciones por entorno
- Refresh dinámico sin downtime
- Configuración específica por servicio

### 📊 Monitoreo
- Health checks integrados
- Métricas de uso
- Logging detallado