# Dockerfile para User Service
FROM openjdk:17-jdk-alpine

# Metadatos
LABEL maintainer="GeoAttend Team"
LABEL service="user-service"
LABEL version="1.0.0"

# Variables de entorno
ENV JAVA_OPTS="-Xmx512m -Xms256m"

# Instalar curl para health checks
RUN apk add --no-cache curl

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivo JAR
COPY target/user-service-1.0.0.jar app.jar

# Exponer puerto
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8081/actuator/health || exit 1

# Comando de inicio
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]