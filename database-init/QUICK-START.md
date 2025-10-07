# ⚡ Quick Start - Inicialización de Base de Datos

## 🎯 Objetivo
Poblar las bases de datos de GeoAttend con datos de prueba en **2 pasos simples**.

---

## 📋 Prerrequisitos

✅ Docker corriendo (`docker-compose up -d`)
✅ Todos los microservicios corriendo (puertos 8001-8004)

---

## 🚀 Ejecución

### Windows

```bash
# Paso 1: Crear admin
1-init-admin.bat

# Paso 2: Poblar datos
2-populate-db.bat
```

### Linux/Mac

```bash
# Dar permisos (solo primera vez)
chmod +x *.sh

# Paso 1: Crear admin
./1-init-admin.sh

# Paso 2: Poblar datos
./2-populate-db.sh
```

---

## ✅ Resultado

Después de ejecutar ambos scripts tendrás:

| Recurso | Cantidad | Detalles |
|---------|----------|----------|
| 👨‍💼 Admin | 1 | admin@test.com / Password123! |
| 👨‍🏫 Profesores | 6 | PROF001-PROF006 / Password123! |
| 👨‍🎓 Estudiantes | 5 | EST001-EST005 / Password123! |
| 🏛️ Aulas | 8 | Con coordenadas GPS |
| 📚 Cursos | 7 | Cursos de postgrado |
| 📅 Horarios | 7 | Horarios semanales |
| 📝 Inscripciones | 13 | Estudiantes en cursos |

---

## 🔐 Credenciales

**Todos los usuarios usan:** `Password123!`

- **Admin:** admin@test.com
- **Profesores:** maria.garcia@test.com, leonidas.zarate@test.com, etc.
- **Estudiantes:** juan.perez@test.com, maria.lopez@test.com, etc.

---

## ❓ ¿Problemas?

### Error: "Connection refused"

**Causa:** Servicios no están corriendo

**Solución:**
```bash
# Verificar que user-service esté activo
curl http://localhost:8001/health
```

### Error: "User already exists"

**Causa:** El admin ya fue creado

**Solución:** Saltar paso 1, ir directo a paso 2

### Error: "Database not found"

**Causa:** Docker no está listo

**Solución:**
```bash
# Verificar Docker
docker-compose ps

# Esperar 10 segundos
```

---

## 📖 Documentación Completa

Para más información, ver: **[README.md](./README.md)**

---

## 🎉 ¡Listo!

Tu sistema ahora tiene datos de prueba. Puedes:

- 🌐 Acceder al dashboard: http://localhost:8080
- 📱 Iniciar la app móvil
- 🔍 Probar las APIs

---

**GeoAttend** - Sistema de Asistencia por Geolocalización
