# Eureka Server - Service Discovery

## Descripción
Servidor de descubrimiento de servicios para el ecosistema de microservicios GeoAttend. Proporciona registro automático, descubrimiento y monitoreo de salud de todos los servicios.

## Características

### ✅ Service Discovery
- Registro automático de microservicios
- Descubrimiento dinámico por nombre de servicio
- Load balancing client-side automático

### ✅ Health Monitoring
- Monitoreo de salud de servicios registrados
- Auto-eliminación de servicios inactivos
- Dashboard web para visualización

### ✅ Production Ready
- Configuración optimizada para desarrollo y producción
- Health checks para Docker
- Métricas y logging detallado

## Configuración

### Puerto
- **Desarrollo**: 8761
- **Docker**: 8761

### Endpoints Importantes
- **Dashboard**: http://localhost:8761
- **Health Check**: http://localhost:8761/actuator/health
- **Métricas**: http://localhost:8761/actuator/metrics

## Ejecución

### Desarrollo Local
```bash
mvn spring-boot:run
```

### Docker
```bash
docker build -t geoattend/eureka-server .
docker run -p 8761:8761 geoattend/eureka-server
```

### Docker Compose
```bash
docker-compose up eureka-server
```

## Dashboard Web

Accede a http://localhost:8761 para ver:
- Servicios registrados
- Estado de salud
- Instancias disponibles
- Configuración del servidor

## Integración con otros servicios

Los microservicios se registran automáticamente incluyendo esta dependencia:

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-netflix-eureka-client</artifactId>
</dependency>
```

Y esta configuración:
```yaml
eureka:
  client:
    service-url:
      defaultZone: http://eureka-server:8761/eureka/
```

## Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Service  │    │ Course Service  │    │Attendance Service│
│    (8081)       │    │     (8082)      │    │     (8083)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              Register │ & Discovery          │
         └───────────────────────┼───────────────────────┘
                                 │
                     ┌─────────────────┐
                     │ Eureka Server   │
                     │    (8761)       │
                     └─────────────────┘
                                 │
                                 │ Service Lookup
                                 ▼
                     ┌─────────────────┐
                     │  API Gateway    │
                     │    (8080)       │
                     └─────────────────┘
```