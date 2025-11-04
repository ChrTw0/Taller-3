@echo off
REM ============================================================================
REM GeoAttend - Script de Inicializacion de Admin (Windows)
REM ============================================================================
REM Este script crea el usuario administrador inicial en una base de datos vacia
REM Ejecutar PRIMERO antes de 2-populate-db.bat
REM ============================================================================

setlocal enabledelayedexpansion

set USER_SERVICE=http://localhost:8001/api/v1

echo ============================================================================
echo   GeoAttend - Inicializacion de Usuario Administrador
echo ============================================================================
echo.

echo Creando usuario administrador inicial...
echo.

REM Crear admin usando el endpoint publico (no requiere autenticacion)
curl -s -X POST "%USER_SERVICE%/users/" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"ADMIN001\",\"email\":\"admin@test.com\",\"first_name\":\"Admin\",\"last_name\":\"Sistema\",\"role\":\"admin\",\"password\":\"Password123\"}" > temp_response.json

REM Verificar respuesta
findstr /C:"success" temp_response.json >nul
if %errorlevel% equ 0 (
  echo Usuario administrador creado exitosamente
  echo.
  echo Credenciales:
  echo   Email:    admin@test.com
  echo   Password: Password123
  echo   Codigo:   ADMIN001
  echo   Rol:      admin
  echo.
  echo ============================================================================
  echo   Siguiente paso: Ejecutar 2-populate-db.bat
  echo ============================================================================
) else (
  echo Error al crear administrador
  echo Respuesta del servidor:
  type temp_response.json
  echo.
  echo Posibles causas:
  echo   1. El usuario ya existe (puedes saltar este paso^)
  echo   2. El servicio no esta corriendo en el puerto 8001
  echo   3. La base de datos no esta disponible
  echo.
  echo Solucion:
  echo   - Verifica: curl http://localhost:8001/health
  echo   - Si el admin ya existe, ejecuta: 2-populate-db.bat
  del temp_response.json
  exit /b 1
)

del temp_response.json
echo.
echo ============================================================================

endlocal
