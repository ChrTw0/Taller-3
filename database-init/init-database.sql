-- ============================================================================
-- GeoAttend - Script SQL para Inicializar Usuario Admin
-- ============================================================================
-- Este script crea directamente el usuario admin en la base de datos
-- Usar solo si los scripts de inicialización via API no funcionan
-- ============================================================================

-- NOTA: Este script es para PostgreSQL
-- Password hasheado: "Password123!" usando bcrypt

-- Conectar a la base de datos user_db
-- psql -U postgres -d user_db -f init_database.sql

-- O desde Docker:
-- docker-compose exec user-db psql -U postgres -d user_db -f /path/to/init_database.sql

-- ============================================================================
-- Insertar Usuario Administrador
-- ============================================================================

INSERT INTO users (
    code,
    email,
    first_name,
    last_name,
    role,
    hashed_password,
    is_active,
    is_verified,
    created_at,
    updated_at
) VALUES (
    'ADMIN001',
    'admin@test.com',
    'Admin',
    'Sistema',
    'admin',
    -- Password: Password123! (hasheado con bcrypt)
    -- IMPORTANTE: Este hash es específico, genera uno nuevo con:
    -- python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('Password123!'))"
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyB0U/6WxYVm',
    true,
    true,
    NOW(),
    NOW()
)
ON CONFLICT (email) DO NOTHING;

-- Verificar que se insertó
SELECT
    id,
    code,
    email,
    first_name,
    last_name,
    role,
    is_active,
    is_verified,
    created_at
FROM users
WHERE email = 'admin@test.com';

-- ============================================================================
-- Alternativa: Generar nuevo hash de password
-- ============================================================================

-- Si necesitas cambiar la contraseña, genera un nuevo hash usando Python:
/*

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password = "Password123!"
hashed = pwd_context.hash(password)
print(f"Hashed password: {hashed}")

Luego reemplaza el valor de hashed_password arriba

*/

-- ============================================================================
-- Información de la base de datos
-- ============================================================================

-- Ver la estructura de la tabla users
\d users

-- Ver todos los usuarios
SELECT id, code, email, first_name, last_name, role, is_active FROM users;

-- ============================================================================
