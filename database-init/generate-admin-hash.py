#!/usr/bin/env python3
"""
Script para generar hash de password bcrypt para usuario admin.
Útil cuando necesitas insertar el admin directamente en la base de datos.
"""

from passlib.context import CryptContext

# Configuración de bcrypt (debe coincidir con la del backend)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_hash(password: str) -> str:
    """Genera un hash bcrypt de la contraseña."""
    return pwd_context.hash(password)

def verify_hash(password: str, hashed: str) -> bool:
    """Verifica que un hash coincida con la contraseña."""
    return pwd_context.verify(password, hashed)

if __name__ == "__main__":
    import sys

    print("=" * 80)
    print("  GeoAttend - Generador de Hash de Password")
    print("=" * 80)
    print()

    # Password por defecto
    default_password = "Password123!"

    # Permitir password personalizado
    if len(sys.argv) > 1:
        password = sys.argv[1]
        print(f"Generando hash para password personalizado...")
    else:
        password = default_password
        print(f"Generando hash para password por defecto: {default_password}")

    print()

    # Generar hash
    hashed = generate_hash(password)

    print("Hash generado:")
    print(hashed)
    print()

    # Verificar
    is_valid = verify_hash(password, hashed)
    print(f"Verificación: {'✅ Válido' if is_valid else '❌ Inválido'}")
    print()

    # SQL de ejemplo
    print("=" * 80)
    print("SQL para insertar admin en la base de datos:")
    print("=" * 80)
    print()
    print("INSERT INTO users (")
    print("    code, email, first_name, last_name, role,")
    print("    hashed_password, is_active, is_verified, created_at, updated_at")
    print(") VALUES (")
    print("    'ADMIN001',")
    print("    'admin@test.com',")
    print("    'Admin',")
    print("    'Sistema',")
    print("    'admin',")
    print(f"    '{hashed}',")
    print("    true,")
    print("    true,")
    print("    NOW(),")
    print("    NOW()")
    print(") ON CONFLICT (email) DO NOTHING;")
    print()
    print("=" * 80)
    print()

    # Instrucciones
    print("Uso:")
    print("  1. Copia el SQL de arriba")
    print("  2. Conéctate a la base de datos user_db:")
    print("     docker-compose exec user-db psql -U postgres -d user_db")
    print("  3. Pega y ejecuta el SQL")
    print()
    print("O guarda en un archivo y ejecútalo:")
    print("  docker-compose exec -T user-db psql -U postgres -d user_db < init_admin.sql")
    print()
    print("=" * 80)
