-- Inicialización de esquemas para GeoAttend System
-- Base de datos: geoattend_db

-- Crear esquemas para cada microservicio
CREATE SCHEMA IF NOT EXISTS user_schema;
CREATE SCHEMA IF NOT EXISTS course_schema;
CREATE SCHEMA IF NOT EXISTS attendance_schema;
CREATE SCHEMA IF NOT EXISTS notification_schema;

-- Configurar permisos para el usuario admin
GRANT ALL PRIVILEGES ON SCHEMA user_schema TO admin;
GRANT ALL PRIVILEGES ON SCHEMA course_schema TO admin;
GRANT ALL PRIVILEGES ON SCHEMA attendance_schema TO admin;
GRANT ALL PRIVILEGES ON SCHEMA notification_schema TO admin;

-- Dar permisos sobre todas las tablas que se crearán en el futuro
ALTER DEFAULT PRIVILEGES IN SCHEMA user_schema GRANT ALL ON TABLES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA course_schema GRANT ALL ON TABLES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA attendance_schema GRANT ALL ON TABLES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA notification_schema GRANT ALL ON TABLES TO admin;

-- Dar permisos sobre todas las secuencias que se crearán en el futuro
ALTER DEFAULT PRIVILEGES IN SCHEMA user_schema GRANT ALL ON SEQUENCES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA course_schema GRANT ALL ON SEQUENCES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA attendance_schema GRANT ALL ON SEQUENCES TO admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA notification_schema GRANT ALL ON SEQUENCES TO admin;

-- Verificación de esquemas creados
SELECT schema_name FROM information_schema.schemata
WHERE schema_name IN ('user_schema', 'course_schema', 'attendance_schema', 'notification_schema');