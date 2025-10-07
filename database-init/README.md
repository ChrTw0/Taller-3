# 🗄️ Scripts de Inicialización de Base de Datos - GeoAttend

Esta carpeta contiene todos los scripts necesarios para inicializar y poblar las bases de datos de GeoAttend desde cero.

## 📁 Estructura de Archivos

```
database-init/
├── README.md                    # Este archivo
├── 1-init-admin.sh              # Crear admin (Linux/Mac)
├── 1-init-admin.bat             # Crear admin (Windows)
├── 2-populate-db.sh             # Poblar datos (Linux/Mac)
├── 2-populate-db.bat            # Poblar datos (Windows)
├── init-database.sql            # SQL directo para admin
├── generate-admin-hash.py       # Generar hash de password
└── populate-db-curls.txt        # Comandos curl individuales
```

## 🚀 Uso Rápido (Quick Start)

### Windows (CMD)

```bash
# 1. Crear admin
cd database-init
1-init-admin.bat

# 2. Poblar base de datos
2-populate-db.bat
```

### Linux/Mac

```bash
# 1. Dar permisos
cd database-init
chmod +x *.sh

# 2. Crear admin
./1-init-admin.sh

# 3. Poblar base de datos
./2-populate-db.sh
```

## 📊 Datos Creados

### 👥 Usuarios (11 total)

#### Administrador
- **ADMIN001** - admin@test.com - Admin Sistema

#### Profesores (6)
| Código | Email | Nombre |
|--------|-------|--------|
| PROF001 | maria.garcia@test.com | Maria Garcia |
| PROF002 | leonidas.zarate@test.com | Leonidas Benito Zarate Otarola |
| PROF003 | richard.zamora@test.com | Richard Ismael Zamora Yansi |
| PROF004 | hilario.aradiel@test.com | Hilario Aradiel Castaneda |
| PROF005 | javier.canchano@test.com | Javier Tolentino Canchano Caro |
| PROF006 | carlos.ramos@test.com | Carlos Nelson Ramos Montes |

#### Estudiantes (5)
| Código | Email | Nombre |
|--------|-------|--------|
| EST001 | juan.perez@test.com | Juan Perez |
| EST002 | maria.lopez@test.com | Maria Lopez |
| EST003 | pedro.gonzalez@test.com | Pedro Gonzalez |
| EST004 | ana.martinez@test.com | Ana Martinez |
| EST005 | carlos.rodriguez@test.com | Carlos Rodriguez |

**🔑 Contraseña para TODOS:** `Password123!`

### 🏛️ Aulas (8)

| Código | Nombre | GPS | Radio |
|--------|--------|-----|-------|
| FIIS-301 | Aula 301 - Edificio FIIS | -12.0463740, -77.0427930 | 50m |
| FIIS-302 | Aula 302 - Edificio FIIS | -12.0155284, -77.0503485 | 10m |
| FIIS-401 | Aula 401 - Edificio FIIS | -12.0465000, -77.0429000 | 50m |
| FIIS-LAB201 | Laboratorio de Sistemas 201 | -12.0155284, -77.0493508 | 10m |
| A-301 | Aula 301 - Edificio A | -12.0153709, -77.0503292 | 10m |
| A-302 | Aula 302 - Edificio A | -12.0464000, -77.0428000 | 50m |
| B-201 | Aula 201 - Edificio B | -12.0465000, -77.0429000 | 50m |
| LAB-101 | Laboratorio 101 | -12.0155921, -77.0493344 | 10m |

### 📚 Cursos (7)

| Código | Nombre | Profesor | Créditos |
|--------|--------|----------|----------|
| SI807V | Sistemas de Inteligencia de Negocios | PROF006 | 4 |
| GE801U | Planeamiento y Gestión Estratégica | PROF002 | 4 |
| GE803U | Sistemas Analíticos | PROF002 | 4 |
| SI150U | Analítica de Datos | PROF003 | 3 |
| SI801V | Modelo del Sistema Viable | PROF004 | 4 |
| SI805V | Integración de Sistemas | PROF005 | 4 |
| SI806V | Desarrollo Adaptativo e Integrado del SW | PROF005 | 2 |

### 📅 Horarios

| Curso | Día | Horario | Aula |
|-------|-----|---------|------|
| SI807V | Lunes | 08:00-10:00 | FIIS-301 |
| GE801U | Martes | 14:00-16:00 | FIIS-302 |
| GE803U | Miércoles | 10:00-12:00 | FIIS-401 |
| SI150U | Jueves | 16:00-18:00 | FIIS-LAB201 |
| SI801V | Viernes | 08:00-12:00 | A-301 |
| SI805V | Jueves | 18:00-22:00 | A-302 |
| SI806V | Sábado | 09:00-13:00 | B-201 |

**Nota:** Días - 0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, 4=Viernes, 5=Sábado, 6=Domingo

## 🛠️ Métodos Alternativos

### Método 1: SQL Directo (Si los scripts fallan)

```bash
# Generar hash de password
python generate-admin-hash.py

# Conectar a PostgreSQL
docker-compose exec user-db psql -U postgres -d user_db

# Ejecutar SQL
\i /path/to/init-database.sql

# O desde fuera:
docker-compose exec -T user-db psql -U postgres -d user_db < init-database.sql
```

### Método 2: Comandos Manuales

Usa `populate-db-curls.txt` que contiene todos los comandos curl individuales para copiar y pegar.

## 🔍 Verificación

```bash
# Health check de servicios
curl http://localhost:8001/health

# Login como admin
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Password123!"}'

# Ver usuarios (usando token del login)
curl http://localhost:8001/api/v1/users/ \
  -H "Authorization: Bearer {TOKEN}"

# Ver cursos
curl http://localhost:8002/api/v1/courses/ \
  -H "Authorization: Bearer {TOKEN}"

# Ver aulas
curl http://localhost:8002/api/v1/classrooms/ \
  -H "Authorization: Bearer {TOKEN}"
```

## 🧹 Resetear Base de Datos

```bash
# Detener servicios (Ctrl+C en cada terminal)

# Borrar volúmenes de Docker (¡PERDERÁS TODOS LOS DATOS!)
cd ..  # Volver a raíz del proyecto
docker-compose down -v

# Volver a levantar
docker-compose up -d

# Repetir proceso desde Paso 2
```

## ❓ Troubleshooting

### Error: "Connection refused"

**Problema:** Servicios no están corriendo

**Solución:**
```bash
# Verificar health
curl http://localhost:8001/health

# Si falla, revisar que el servicio esté corriendo
```

### Error: "User already exists"

**Problema:** El admin ya fue creado

**Solución:**
- Saltar el paso de init-admin
- Ir directo a poblar datos con `2-populate-db`

### Error: "Database not found"

**Problema:** Docker no está corriendo o BD no está lista

**Solución:**
```bash
# Verificar Docker
docker-compose ps

# Ver logs
docker-compose logs user-db

# Esperar 10 segundos más
```

### Error: teacher_id incorrecto en populate-db

**Problema:** IDs de profesores no son secuenciales

**Solución:**
1. Obtener token
2. Consultar IDs reales:
   ```bash
   curl http://localhost:8001/api/v1/users/ -H "Authorization: Bearer {TOKEN}"
   ```
3. Editar script o usar comandos manuales de `populate-db-curls.txt`

## 📞 Soporte

Si tienes problemas:

1. Verifica que todos los servicios estén corriendo
2. Revisa logs de los servicios
3. Asegúrate de que los puertos 8000-8004 y 5433-5436 estén libres
4. Verifica archivos `.env` en cada microservicio

