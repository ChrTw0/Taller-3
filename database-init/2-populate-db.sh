#!/bin/bash

# ============================================================================
# GeoAttend - Script de Población de Base de Datos
# ============================================================================
# Este script crea todos los datos de prueba necesarios para el sistema
# GeoAttend usando la API REST a través de comandos curl.
#
# IMPORTANTE: Ejecutar DESPUÉS de 1-init-admin.sh
# ============================================================================

set -e  # Exit on error

# Configuración
API_GATEWAY="http://localhost:8000"
USER_SERVICE="http://localhost:8001/api/v1"
COURSE_SERVICE="http://localhost:8002/api/v1"
ATTENDANCE_SERVICE="http://localhost:8003/api/v1"

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "============================================================================"
echo "  GeoAttend - Database Population Script"
echo "============================================================================"
echo -e "${NC}"

# ============================================================================
# PASO 1: Login como Admin
# ============================================================================
echo -e "${YELLOW}[1/8] Autenticación...${NC}"

LOGIN_RESPONSE=$(curl -s -X POST "${USER_SERVICE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Password123!"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}❌ Error: No se pudo obtener el token de autenticación${NC}"
  echo "Response: $LOGIN_RESPONSE"
  echo ""
  echo "Posible causa: El usuario admin no existe"
  echo "Solución: Ejecuta primero ./1-init-admin.sh"
  exit 1
fi

echo -e "${GREEN}✅ Token obtenido exitosamente${NC}"

# ============================================================================
# PASO 2: Crear Usuarios (Profesores y Estudiantes)
# ============================================================================
echo -e "\n${YELLOW}[2/8] Creando usuarios...${NC}"

# Función para crear usuarios
create_user() {
  local CODE=$1
  local EMAIL=$2
  local FIRST_NAME=$3
  local LAST_NAME=$4
  local ROLE=$5
  local PASSWORD=$6

  echo -e "${BLUE}  Creando usuario: $CODE - $FIRST_NAME $LAST_NAME ($ROLE)${NC}"

  curl -s -X POST "${USER_SERVICE}/auth/register" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"code\": \"$CODE\",
      \"email\": \"$EMAIL\",
      \"first_name\": \"$FIRST_NAME\",
      \"last_name\": \"$LAST_NAME\",
      \"role\": \"$ROLE\",
      \"password\": \"$PASSWORD\"
    }" > /dev/null
}

# Profesores
create_user "PROF001" "maria.garcia@test.com" "Maria" "Garcia" "teacher" "Password123!"
create_user "PROF002" "leonidas.zarate@test.com" "LEONIDAS BENITO" "ZARATE OTAROLA" "teacher" "Password123!"
create_user "PROF003" "richard.zamora@test.com" "RICHARD ISMAEL" "ZAMORA YANSI" "teacher" "Password123!"
create_user "PROF004" "hilario.aradiel@test.com" "HILARIO" "ARADIEL CASTANEDA" "teacher" "Password123!"
create_user "PROF005" "javier.canchano@test.com" "JAVIER TOLENTINO" "CANCHANO CARO" "teacher" "Password123!"
create_user "PROF006" "carlos.ramos@test.com" "CARLOS NELSON" "RAMOS MONTES" "teacher" "Password123!"

# Estudiantes
create_user "EST001" "juan.perez@test.com" "Juan" "Perez" "student" "Password123!"
create_user "EST002" "maria.lopez@test.com" "Maria" "Lopez" "student" "Password123!"
create_user "EST003" "pedro.gonzalez@test.com" "Pedro" "Gonzalez" "student" "Password123!"
create_user "EST004" "ana.martinez@test.com" "Ana" "Martinez" "student" "Password123!"
create_user "EST005" "carlos.rodriguez@test.com" "Carlos" "Rodriguez" "student" "Password123!"

echo -e "${GREEN}✅ Usuarios creados${NC}"

# ============================================================================
# PASO 3: Crear Aulas (Classrooms)
# ============================================================================
echo -e "\n${YELLOW}[3/8] Creando aulas...${NC}"

# Función para crear aulas
create_classroom() {
  local CODE=$1
  local NAME=$2
  local BUILDING=$3
  local ROOM=$4
  local FLOOR=$5
  local LAT=$6
  local LON=$7
  local RADIUS=$8
  local CAPACITY=$9
  local EQUIPMENT="${10}"

  echo -e "${BLUE}  Creando aula: $CODE - $NAME${NC}"

  CLASSROOM_DATA="{
    \"code\": \"$CODE\",
    \"name\": \"$NAME\",
    \"building\": \"$BUILDING\",
    \"room_number\": \"$ROOM\",
    \"floor\": $FLOOR,
    \"latitude\": \"$LAT\",
    \"longitude\": \"$LON\",
    \"gps_radius\": \"$RADIUS\",
    \"capacity\": $CAPACITY"

  if [ -n "$EQUIPMENT" ]; then
    CLASSROOM_DATA="${CLASSROOM_DATA},\"equipment\": \"$EQUIPMENT\""
  fi

  CLASSROOM_DATA="${CLASSROOM_DATA}}"

  curl -s -X POST "${COURSE_SERVICE}/classrooms/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$CLASSROOM_DATA" > /dev/null
}

# Aulas FIIS
create_classroom "FIIS-301" "Aula 301 - Edificio FIIS" "Facultad de Ingenieria Industrial y de Sistemas" "301" 3 "-12.0463740" "-77.0427930" "50.00" 40 "Proyector, Pizarra digital, Sistema de audio"
create_classroom "FIIS-302" "Aula 302 - Edificio FIIS" "Facultad de Ingenieria Industrial y de Sistemas" "302" 3 "-12.0155284" "-77.0503485" "10.00" 35 "Proyector, Pizarra acrilica"
create_classroom "FIIS-401" "Aula 401 - Edificio FIIS" "Facultad de Ingenieria Industrial y de Sistemas" "401" 4 "-12.0465000" "-77.0429000" "50.00" 30 "Proyector, Pizarra acrilica, Aire acondicionado"
create_classroom "FIIS-LAB201" "Laboratorio de Sistemas 201" "Facultad de Ingenieria Industrial y de Sistemas" "LAB-201" 2 "-12.0155284" "-77.0493508" "10.00" 25 "30 Computadoras, Proyector, Pizarra digital, Servidor local"

# Aulas Edificio A
create_classroom "A-301" "Aula 301 - Edificio A" "Edificio A" "301" 3 "-12.0153709" "-77.0503292" "10.00" 40 ""
create_classroom "A-302" "Aula 302 - Edificio A" "Edificio A" "302" 3 "-12.0464000" "-77.0428000" "50.00" 35 ""

# Aulas Edificio B
create_classroom "B-201" "Aula 201 - Edificio B" "Edificio B" "201" 2 "-12.0465000" "-77.0429000" "50.00" 30 ""

# Laboratorios
create_classroom "LAB-101" "Laboratorio 101" "Edificio C" "101" 1 "-12.0155921" "-77.0493344" "10.00" 25 ""

echo -e "${GREEN}✅ Aulas creadas${NC}"

# ============================================================================
# PASO 4: Crear Cursos
# ============================================================================
echo -e "\n${YELLOW}[4/8] Creando cursos...${NC}"

# Función para crear cursos
create_course() {
  local CODE=$1
  local NAME=$2
  local DESCRIPTION=$3
  local CREDITS=$4
  local YEAR=$5
  local SEMESTER=$6
  local MAX_STUDENTS=$7
  local RADIUS=$8
  local TEACHER_ID=$9
  local TEACHER_CODE=${10}

  echo -e "${BLUE}  Creando curso: $CODE - $NAME${NC}"

  curl -s -X POST "${COURSE_SERVICE}/courses/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"code\": \"$CODE\",
      \"name\": \"$NAME\",
      \"description\": \"$DESCRIPTION\",
      \"credits\": $CREDITS,
      \"academic_year\": \"$YEAR\",
      \"semester\": \"$SEMESTER\",
      \"max_students\": $MAX_STUDENTS,
      \"detection_radius\": \"$RADIUS\",
      \"teacher_id\": $TEACHER_ID,
      \"teacher_code\": \"$TEACHER_CODE\"
    }" > /dev/null
}

create_course "SI807V" "Sistemas de Inteligencia de Negocios" "Curso de postgrado que aborda metodologias y tecnologias para la implementacion de sistemas de inteligencia de negocios en organizaciones." 4 "2025" "A" 35 "2.50" 8 "PROF006"
create_course "GE801U" "Planeamiento y Gestion Estrategica" "Curso que desarrolla competencias en planeamiento estrategico, analisis organizacional y gestion de proyectos estrategicos." 4 "2025" "A" 40 "2.50" 4 "PROF002"
create_course "GE803U" "Sistemas Analiticos" "Curso enfocado en el diseno e implementacion de sistemas analiticos para la toma de decisiones basada en datos." 4 "2025" "A" 35 "2.50" 4 "PROF002"
create_course "SI150U" "Analitica de Datos" "Curso que introduce tecnicas de analisis de datos, visualizacion, estadistica aplicada y machine learning." 3 "2025" "A" 40 "2.50" 5 "PROF003"
create_course "SI801V" "Modelo del Sistema Viable" "Curso de postgrado sobre cibernetica organizacional y el Modelo del Sistema Viable de Stafford Beer." 4 "2025" "A" 30 "2.50" 6 "PROF004"
create_course "SI805V" "Integracion de Sistemas" "Curso sobre arquitecturas de integracion, APIs, microservicios y patrones de integracion empresarial." 4 "2025" "A" 35 "2.50" 7 "PROF005"
create_course "SI806V" "Desarrollo Adaptativo e Integrado del SW" "Curso sobre metodologias agiles y desarrollo de software integrado" 2 "2025" "A" 30 "2.50" 7 "PROF005"

echo -e "${GREEN}✅ Cursos creados${NC}"

# ============================================================================
# PASO 5: Crear Horarios para los Cursos
# ============================================================================
echo -e "\n${YELLOW}[5/8] Creando horarios...${NC}"

# Función para crear horarios
create_schedule() {
  local COURSE_ID=$1
  local DAY=$2
  local START_TIME=$3
  local END_TIME=$4
  local CLASSROOM_ID=$5

  echo -e "${BLUE}  Creando horario para curso ID: $COURSE_ID${NC}"

  SCHEDULE_DATA="{
    \"day_of_week\": $DAY,
    \"start_time\": \"$START_TIME\",
    \"end_time\": \"$END_TIME\""

  if [ -n "$CLASSROOM_ID" ] && [ "$CLASSROOM_ID" != "null" ]; then
    SCHEDULE_DATA="${SCHEDULE_DATA},\"classroom_id\": $CLASSROOM_ID"
  fi

  SCHEDULE_DATA="${SCHEDULE_DATA}}"

  curl -s -X POST "${COURSE_SERVICE}/schedules/course/$COURSE_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$SCHEDULE_DATA" > /dev/null
}

# Horarios (asumiendo IDs de cursos 1-7)
# Día: 0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, 4=Viernes, 5=Sábado, 6=Domingo

create_schedule 1 0 "08:00:00" "10:00:00" 1  # SI807V - Lunes 8-10am
create_schedule 2 1 "14:00:00" "16:00:00" 2  # GE801U - Martes 2-4pm
create_schedule 3 2 "10:00:00" "12:00:00" 3  # GE803U - Miércoles 10-12am
create_schedule 4 3 "16:00:00" "18:00:00" 4  # SI150U - Jueves 4-6pm
create_schedule 5 4 "08:00:00" "12:00:00" 5  # SI801V - Viernes 8am-12pm
create_schedule 6 3 "18:00:00" "22:00:00" 6  # SI805V - Jueves 6-10pm
create_schedule 7 5 "09:00:00" "13:00:00" 7  # SI806V - Sábado 9am-1pm

echo -e "${GREEN}✅ Horarios creados${NC}"

# ============================================================================
# PASO 6: Crear Inscripciones (Enrollments)
# ============================================================================
echo -e "\n${YELLOW}[6/8] Creando inscripciones...${NC}"

# Función para crear inscripciones
create_enrollment() {
  local COURSE_ID=$1
  local STUDENT_ID=$2
  local STUDENT_CODE=$3

  echo -e "${BLUE}  Inscribiendo estudiante $STUDENT_CODE en curso ID: $COURSE_ID${NC}"

  curl -s -X POST "${COURSE_SERVICE}/enrollments/course/$COURSE_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"student_id\": $STUDENT_ID,
      \"student_code\": \"$STUDENT_CODE\"
    }" > /dev/null
}

# Inscribir estudiante EST001 (ID 1) en varios cursos
create_enrollment 1 1 "EST001"
create_enrollment 2 1 "EST001"
create_enrollment 3 1 "EST001"
create_enrollment 4 1 "EST001"
create_enrollment 5 1 "EST001"
create_enrollment 6 1 "EST001"
create_enrollment 7 1 "EST001"

# Inscribir otros estudiantes
create_enrollment 1 2 "EST002"
create_enrollment 1 3 "EST003"
create_enrollment 2 2 "EST002"
create_enrollment 3 4 "EST004"
create_enrollment 4 5 "EST005"

echo -e "${GREEN}✅ Inscripciones creadas${NC}"

# ============================================================================
# PASO 7: Verificar datos creados
# ============================================================================
echo -e "\n${YELLOW}[7/8] Verificando datos creados...${NC}"

# Contar usuarios
USER_COUNT=$(curl -s -X GET "${USER_SERVICE}/users/" \
  -H "Authorization: Bearer $TOKEN" | grep -o '"id":' | wc -l)

# Contar cursos
COURSE_RESPONSE=$(curl -s -X GET "${COURSE_SERVICE}/courses/" \
  -H "Authorization: Bearer $TOKEN")
COURSE_COUNT=$(echo $COURSE_RESPONSE | grep -o '"total":[0-9]*' | grep -o '[0-9]*')

# Contar aulas
CLASSROOM_COUNT=$(curl -s -X GET "${COURSE_SERVICE}/classrooms/" \
  -H "Authorization: Bearer $TOKEN" | grep -o '"id":' | wc -l)

# Contar inscripciones
ENROLLMENT_COUNT=$(curl -s -X GET "${COURSE_SERVICE}/enrollments/" \
  -H "Authorization: Bearer $TOKEN" | grep -o '"id":' | wc -l)

echo -e "${BLUE}  📊 Resumen:${NC}"
echo -e "  - Usuarios: $USER_COUNT"
echo -e "  - Cursos: $COURSE_COUNT"
echo -e "  - Aulas: $CLASSROOM_COUNT"
echo -e "  - Inscripciones: $ENROLLMENT_COUNT"

echo -e "${GREEN}✅ Verificación completada${NC}"

# ============================================================================
# PASO 8: Información de credenciales
# ============================================================================
echo -e "\n${YELLOW}[8/8] Información de acceso${NC}"
echo -e "${BLUE}"
echo "============================================================================"
echo "  Credenciales de Prueba"
echo "============================================================================"
echo ""
echo "  👨‍💼 ADMINISTRADOR:"
echo "    Email:    admin@test.com"
echo "    Password: Password123!"
echo ""
echo "  👨‍🏫 PROFESORES:"
echo "    Email:    maria.garcia@test.com (y otros PROF*@test.com)"
echo "    Password: Password123!"
echo ""
echo "  👨‍🎓 ESTUDIANTES:"
echo "    Email:    juan.perez@test.com (EST001)"
echo "    Email:    maria.lopez@test.com (EST002)"
echo "    Email:    pedro.gonzalez@test.com (EST003)"
echo "    Email:    ana.martinez@test.com (EST004)"
echo "    Email:    carlos.rodriguez@test.com (EST005)"
echo "    Password: Password123!"
echo ""
echo "============================================================================"
echo -e "${NC}"

echo -e "${GREEN}"
echo "============================================================================"
echo "  ✅ Base de datos poblada exitosamente!"
echo "============================================================================"
echo -e "${NC}"

exit 0
