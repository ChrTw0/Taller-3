# Dockerfile para Eureka Server
FROM openjdk:17-jdk-alpine

# Metadatos
LABEL maintainer="GeoAttend Team"
LABEL service="eureka-server"
LABEL version="1.0.0"

# Variables de entorno
ENV JAVA_OPTS="-Xmx512m -Xms256m"

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivo JAR
COPY target/eureka-server-1.0.0.jar app.jar

# Exponer puerto
EXPOSE 8761

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8761/actuator/health || exit 1

# Comando de inicio
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]