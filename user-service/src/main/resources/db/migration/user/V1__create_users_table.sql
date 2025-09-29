-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(11) UNIQUE NOT NULL, -- Ejemplo: 2020010101A
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'STUDENT',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Crear índices para optimizar consultas
CREATE INDEX idx_users_code ON users(code);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

-- Insertar usuarios de ejemplo
INSERT INTO users (code, name, email, password, role, status) VALUES
-- Contraseña: password123 (será hasheada por BCrypt)
('2020010101A', 'Juan Pérez Estudiante', 'juan.perez@university.edu', '$2a$10$N8rVcAECkgXgGcKOPjEuCuE/QGP6uG9Fvo6NHBwZLfJ8KcMx6YeWO', 'STUDENT', 'ACTIVE'),
('2020010102B', 'María García Estudiante', 'maria.garcia@university.edu', '$2a$10$N8rVcAECkgXgGcKOPjEuCuE/QGP6uG9Fvo6NHBwZLfJ8KcMx6YeWO', 'STUDENT', 'ACTIVE'),
('PROF001', 'Dr. Carlos Rodríguez', 'carlos.rodriguez@university.edu', '$2a$10$N8rVcAECkgXgGcKOPjEuCuE/QGP6uG9Fvo6NHBwZLfJ8KcMx6YeWO', 'PROFESSOR', 'ACTIVE'),
('ADMIN001', 'Ana López Admin', 'admin@university.edu', '$2a$10$N8rVcAECkgXgGcKOPjEuCuE/QGP6uG9Fvo6NHBwZLfJ8KcMx6YeWO', 'ADMIN', 'ACTIVE');

-- Comentarios
COMMENT ON TABLE users IS 'Tabla de usuarios del sistema (estudiantes, profesores, administradores)';
COMMENT ON COLUMN users.code IS 'Código único del usuario (formato: XXXXXXXXXX[A-Z] para estudiantes)';
COMMENT ON COLUMN users.role IS 'Rol del usuario: STUDENT, PROFESSOR, ADMIN';
COMMENT ON COLUMN users.status IS 'Estado del usuario: ACTIVE, INACTIVE, SUSPENDED';