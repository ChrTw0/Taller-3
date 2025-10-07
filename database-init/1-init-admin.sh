#!/bin/bash

# ============================================================================
# GeoAttend - Script de Inicialización de Admin
# ============================================================================
# Este script crea el usuario administrador inicial en una base de datos vacía
# Ejecutar PRIMERO antes de 2-populate-db.sh
# ============================================================================

set -e

USER_SERVICE="http://localhost:8001/api/v1"

echo "============================================================================"
echo "  GeoAttend - Inicialización de Usuario Administrador"
echo "============================================================================"
echo ""

echo "Creando usuario administrador inicial..."
echo ""

# Crear admin usando el endpoint público (no requiere autenticación)
RESPONSE=$(curl -s -X POST "${USER_SERVICE}/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ADMIN001",
    "email": "admin@test.com",
    "first_name": "Admin",
    "last_name": "Sistema",
    "role": "admin",
    "password": "Password123!"
  }')

# Verificar si fue exitoso
if echo "$RESPONSE" | grep -q '"success":true'; then
  echo "✅ Usuario administrador creado exitosamente"
  echo ""
  echo "Credenciales:"
  echo "  Email:    admin@test.com"
  echo "  Password: Password123!"
  echo "  Código:   ADMIN001"
  echo "  Rol:      admin"
  echo ""
  echo "============================================================================"
  echo "  ✅ Siguiente paso: Ejecutar ./2-populate-db.sh"
  echo "============================================================================"
else
  echo "❌ Error al crear administrador"
  echo "Respuesta del servidor:"
  echo "$RESPONSE"
  echo ""
  echo "Posibles causas:"
  echo "  1. El usuario ya existe (puedes saltar este paso)"
  echo "  2. El servicio no está corriendo en el puerto 8001"
  echo "  3. La base de datos no está disponible"
  echo ""
  echo "Solución:"
  echo "  - Verifica: curl http://localhost:8001/health"
  echo "  - Si el admin ya existe, ejecuta: ./2-populate-db.sh"
  exit 1
fi

echo ""
echo "============================================================================"

exit 0
