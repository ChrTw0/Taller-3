@echo off
REM ============================================================================
REM GeoAttend - Script de Población de Base de Datos (Windows)
REM ============================================================================
REM Este script crea todos los datos de prueba necesarios para el sistema
REM GeoAttend usando la API REST a través de comandos curl.
REM ============================================================================

setlocal enabledelayedexpansion

REM Configuración
set API_GATEWAY=http://localhost:8000
set USER_SERVICE=http://localhost:8001/api/v1
set COURSE_SERVICE=http://localhost:8002/api/v1
set ATTENDANCE_SERVICE=http://localhost:8003/api/v1

echo ============================================================================
echo   GeoAttend - Database Population Script
echo ============================================================================
echo.

REM ============================================================================
REM PASO 1: Login como Admin
REM ============================================================================
echo [1/8] Autenticacion...

curl -s -X POST "%USER_SERVICE%/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@test.com\",\"password\":\"Password123\"}" > temp_login.json

REM Extraer token del JSON (requiere jq o PowerShell)
for /f "delims=" %%i in ('powershell -command "(Get-Content temp_login.json | ConvertFrom-Json).data.access_token"') do set TOKEN=%%i
del temp_login.json

if "%TOKEN%"=="" (
  echo ERROR: No se pudo obtener el token de autenticacion
  exit /b 1
)

echo Token obtenido exitosamente
echo.

REM ============================================================================
REM PASO 2: Crear Usuarios (Profesores y Estudiantes)
REM ============================================================================
echo [2/8] Creando usuarios...

REM Profesores
echo   Creando profesor: PROF001 - Maria Garcia
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"PROF001\",\"email\":\"maria.garcia@test.com\",\"first_name\":\"Maria\",\"last_name\":\"Garcia\",\"role\":\"teacher\",\"password\":\"Password123\"}" > nul

echo   Creando profesor: PROF002 - Leonidas Zarate
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"PROF002\",\"email\":\"leonidas.zarate@test.com\",\"first_name\":\"LEONIDAS BENITO\",\"last_name\":\"ZARATE OTAROLA\",\"role\":\"teacher\",\"password\":\"Password123\"}" > nul

echo   Creando profesor: PROF003 - Richard Zamora
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"PROF003\",\"email\":\"richard.zamora@test.com\",\"first_name\":\"RICHARD ISMAEL\",\"last_name\":\"ZAMORA YANSI\",\"role\":\"teacher\",\"password\":\"Password123\"}" > nul

echo   Creando profesor: PROF004 - Hilario Aradiel
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"PROF004\",\"email\":\"hilario.aradiel@test.com\",\"first_name\":\"HILARIO\",\"last_name\":\"ARADIEL CASTANEDA\",\"role\":\"teacher\",\"password\":\"Password123\"}" > nul

echo   Creando profesor: PROF005 - Javier Canchano
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"PROF005\",\"email\":\"javier.canchano@test.com\",\"first_name\":\"JAVIER TOLENTINO\",\"last_name\":\"CANCHANO CARO\",\"role\":\"teacher\",\"password\":\"Password123\"}" > nul

echo   Creando profesor: PROF006 - Carlos Ramos
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"PROF006\",\"email\":\"carlos.ramos@test.com\",\"first_name\":\"CARLOS NELSON\",\"last_name\":\"RAMOS MONTES\",\"role\":\"teacher\",\"password\":\"Password123\"}" > nul

REM Estudiantes
echo   Creando estudiante: EST001 - Juan Perez
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"EST001\",\"email\":\"juan.perez@test.com\",\"first_name\":\"Juan\",\"last_name\":\"Perez\",\"role\":\"student\",\"password\":\"Password123\"}" > nul

echo   Creando estudiante: EST002 - Maria Lopez
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"EST002\",\"email\":\"maria.lopez@test.com\",\"first_name\":\"Maria\",\"last_name\":\"Lopez\",\"role\":\"student\",\"password\":\"Password123\"}" > nul

echo   Creando estudiante: EST003 - Pedro Gonzalez
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"EST003\",\"email\":\"pedro.gonzalez@test.com\",\"first_name\":\"Pedro\",\"last_name\":\"Gonzalez\",\"role\":\"student\",\"password\":\"Password123\"}" > nul

echo   Creando estudiante: EST004 - Ana Martinez
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"EST004\",\"email\":\"ana.martinez@test.com\",\"first_name\":\"Ana\",\"last_name\":\"Martinez\",\"role\":\"student\",\"password\":\"Password123\"}" > nul

echo   Creando estudiante: EST005 - Carlos Rodriguez
curl -s -X POST "%USER_SERVICE%/auth/register" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"EST005\",\"email\":\"carlos.rodriguez@test.com\",\"first_name\":\"Carlos\",\"last_name\":\"Rodriguez\",\"role\":\"student\",\"password\":\"Password123\"}" > nul

echo Usuarios creados
echo.

REM ============================================================================
REM PASO 3: Crear Aulas (Classrooms)
REM ============================================================================
echo [3/8] Creando aulas...

echo   Creando aula: FIIS-301
curl -s -X POST "%COURSE_SERVICE%/classrooms/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"FIIS-301\",\"name\":\"Aula 301 - Edificio FIIS\",\"building\":\"Facultad de Ingenieria Industrial y de Sistemas\",\"room_number\":\"301\",\"floor\":3,\"latitude\":\"-12.0463740\",\"longitude\":\"-77.0427930\",\"gps_radius\":\"50.00\",\"capacity\":40,\"equipment\":\"Proyector, Pizarra digital, Sistema de audio\"}" > nul

echo   Creando aula: FIIS-302
curl -s -X POST "%COURSE_SERVICE%/classrooms/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"FIIS-302\",\"name\":\"Aula 302 - Edificio FIIS\",\"building\":\"Facultad de Ingenieria Industrial y de Sistemas\",\"room_number\":\"302\",\"floor\":3,\"latitude\":\"-12.0155284\",\"longitude\":\"-77.0503485\",\"gps_radius\":\"10.00\",\"capacity\":35,\"equipment\":\"Proyector, Pizarra acrilica\"}" > nul

echo   Creando aula: FIIS-401
curl -s -X POST "%COURSE_SERVICE%/classrooms/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"FIIS-401\",\"name\":\"Aula 401 - Edificio FIIS\",\"building\":\"Facultad de Ingenieria Industrial y de Sistemas\",\"room_number\":\"401\",\"floor\":4,\"latitude\":\"-12.0465000\",\"longitude\":\"-77.0429000\",\"gps_radius\":\"50.00\",\"capacity\":30,\"equipment\":\"Proyector, Pizarra acrilica, Aire acondicionado\"}" > nul

echo   Creando aula: FIIS-LAB201
curl -s -X POST "%COURSE_SERVICE%/classrooms/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"FIIS-LAB201\",\"name\":\"Laboratorio de Sistemas 201\",\"building\":\"Facultad de Ingenieria Industrial y de Sistemas\",\"room_number\":\"LAB-201\",\"floor\":2,\"latitude\":\"-12.0155284\",\"longitude\":\"-77.0493508\",\"gps_radius\":\"10.00\",\"capacity\":25,\"equipment\":\"30 Computadoras, Proyector, Pizarra digital, Servidor local\"}" > nul

echo   Creando aula: A-301
curl -s -X POST "%COURSE_SERVICE%/classrooms/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"A-301\",\"name\":\"Aula 301 - Edificio A\",\"building\":\"Edificio A\",\"room_number\":\"301\",\"floor\":3,\"latitude\":\"-12.0153709\",\"longitude\":\"-77.0503292\",\"gps_radius\":\"10.00\",\"capacity\":40}" > nul

echo   Creando aula: A-302
curl -s -X POST "%COURSE_SERVICE%/classrooms/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"A-302\",\"name\":\"Aula 302 - Edificio A\",\"building\":\"Edificio A\",\"room_number\":\"302\",\"floor\":3,\"latitude\":\"-12.0464000\",\"longitude\":\"-77.0428000\",\"gps_radius\":\"50.00\",\"capacity\":35}" > nul

echo   Creando aula: B-201
curl -s -X POST "%COURSE_SERVICE%/classrooms/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"B-201\",\"name\":\"Aula 201 - Edificio B\",\"building\":\"Edificio B\",\"room_number\":\"201\",\"floor\":2,\"latitude\":\"-12.0465000\",\"longitude\":\"-77.0429000\",\"gps_radius\":\"50.00\",\"capacity\":30}" > nul

echo   Creando aula: LAB-101
curl -s -X POST "%COURSE_SERVICE%/classrooms/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"LAB-101\",\"name\":\"Laboratorio 101\",\"building\":\"Edificio C\",\"room_number\":\"101\",\"floor\":1,\"latitude\":\"-12.0155921\",\"longitude\":\"-77.0493344\",\"gps_radius\":\"10.00\",\"capacity\":25}" > nul

echo Aulas creadas
echo.

REM ============================================================================
REM PASO 4: Crear Cursos
REM ============================================================================
echo [4/8] Creando cursos...

echo   Creando curso: SI807V
curl -s -X POST "%COURSE_SERVICE%/courses/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"SI807V\",\"name\":\"Sistemas de Inteligencia de Negocios\",\"description\":\"Curso de postgrado que aborda metodologias y tecnologias para la implementacion de sistemas de inteligencia de negocios en organizaciones.\",\"credits\":4,\"academic_year\":\"2025\",\"semester\":\"A\",\"max_students\":35,\"detection_radius\":\"2.50\",\"teacher_id\":7,\"teacher_code\":\"PROF006\"}" > nul

echo   Creando curso: GE801U
curl -s -X POST "%COURSE_SERVICE%/courses/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"GE801U\",\"name\":\"Planeamiento y Gestion Estrategica\",\"description\":\"Curso que desarrolla competencias en planeamiento estrategico, analisis organizacional y gestion de proyectos estrategicos.\",\"credits\":4,\"academic_year\":\"2025\",\"semester\":\"A\",\"max_students\":40,\"detection_radius\":\"2.50\",\"teacher_id\":3,\"teacher_code\":\"PROF002\"}" > nul

echo   Creando curso: GE803U
curl -s -X POST "%COURSE_SERVICE%/courses/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"GE803U\",\"name\":\"Sistemas Analiticos\",\"description\":\"Curso enfocado en el diseno e implementacion de sistemas analiticos para la toma de decisiones basada en datos.\",\"credits\":4,\"academic_year\":\"2025\",\"semester\":\"A\",\"max_students\":35,\"detection_radius\":\"2.50\",\"teacher_id\":3,\"teacher_code\":\"PROF002\"}" > nul

echo   Creando curso: SI150U
curl -s -X POST "%COURSE_SERVICE%/courses/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"SI150U\",\"name\":\"Analitica de Datos\",\"description\":\"Curso que introduce tecnicas de analisis de datos, visualizacion, estadistica aplicada y machine learning.\",\"credits\":3,\"academic_year\":\"2025\",\"semester\":\"A\",\"max_students\":40,\"detection_radius\":\"2.50\",\"teacher_id\":4,\"teacher_code\":\"PROF003\"}" > nul

echo   Creando curso: SI801V
curl -s -X POST "%COURSE_SERVICE%/courses/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"SI801V\",\"name\":\"Modelo del Sistema Viable\",\"description\":\"Curso de postgrado sobre cibernetica organizacional y el Modelo del Sistema Viable de Stafford Beer.\",\"credits\":4,\"academic_year\":\"2025\",\"semester\":\"A\",\"max_students\":30,\"detection_radius\":\"2.50\",\"teacher_id\":5,\"teacher_code\":\"PROF004\"}" > nul

echo   Creando curso: SI805V
curl -s -X POST "%COURSE_SERVICE%/courses/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"SI805V\",\"name\":\"Integracion de Sistemas\",\"description\":\"Curso sobre arquitecturas de integracion, APIs, microservicios y patrones de integracion empresarial.\",\"credits\":4,\"academic_year\":\"2025\",\"semester\":\"A\",\"max_students\":35,\"detection_radius\":\"2.50\",\"teacher_id\":6,\"teacher_code\":\"PROF005\"}" > nul

echo   Creando curso: SI806V
curl -s -X POST "%COURSE_SERVICE%/courses/" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"code\":\"SI806V\",\"name\":\"Desarrollo Adaptativo e Integrado del SW\",\"description\":\"Curso sobre metodologias agiles y desarrollo de software integrado\",\"credits\":2,\"academic_year\":\"2025\",\"semester\":\"A\",\"max_students\":30,\"detection_radius\":\"2.50\",\"teacher_id\":6,\"teacher_code\":\"PROF005\"}" > nul

echo Cursos creados
echo.

REM ============================================================================
REM PASO 5: Crear Horarios para los Cursos
REM ============================================================================
echo [5/8] Creando horarios...

echo   Creando horarios para cursos...
curl -s -X POST "%COURSE_SERVICE%/schedules/course/1" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"day_of_week\":0,\"start_time\":\"08:00:00\",\"end_time\":\"10:00:00\",\"classroom_id\":1}" > nul
curl -s -X POST "%COURSE_SERVICE%/schedules/course/2" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"day_of_week\":1,\"start_time\":\"14:00:00\",\"end_time\":\"16:00:00\",\"classroom_id\":2}" > nul
curl -s -X POST "%COURSE_SERVICE%/schedules/course/3" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"day_of_week\":2,\"start_time\":\"10:00:00\",\"end_time\":\"12:00:00\",\"classroom_id\":3}" > nul
curl -s -X POST "%COURSE_SERVICE%/schedules/course/4" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"day_of_week\":3,\"start_time\":\"16:00:00\",\"end_time\":\"18:00:00\",\"classroom_id\":4}" > nul
curl -s -X POST "%COURSE_SERVICE%/schedules/course/5" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"day_of_week\":4,\"start_time\":\"08:00:00\",\"end_time\":\"12:00:00\",\"classroom_id\":5}" > nul
curl -s -X POST "%COURSE_SERVICE%/schedules/course/6" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"day_of_week\":3,\"start_time\":\"18:00:00\",\"end_time\":\"22:00:00\",\"classroom_id\":6}" > nul
curl -s -X POST "%COURSE_SERVICE%/schedules/course/7" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"day_of_week\":5,\"start_time\":\"09:00:00\",\"end_time\":\"13:00:00\",\"classroom_id\":7}" > nul

echo Horarios creados
echo.

REM ============================================================================
REM PASO 6: Crear Inscripciones (Enrollments)
REM ============================================================================
echo [6/8] Creando inscripciones...

echo   Inscribiendo estudiante EST001 en cursos...
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/1" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":8,\"student_code\":\"EST001\"}" > nul
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/2" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":8,\"student_code\":\"EST001\"}" > nul
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/3" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":8,\"student_code\":\"EST001\"}" > nul
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/4" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":8,\"student_code\":\"EST001\"}" > nul
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/5" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":8,\"student_code\":\"EST001\"}" > nul
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/6" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":8,\"student_code\":\"EST001\"}" > nul
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/7" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":8,\"student_code\":\"EST001\"}" > nul

echo   Inscribiendo otros estudiantes...
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/1" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":9,\"student_code\":\"EST002\"}" > nul
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/1" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":10,\"student_code\":\"EST003\"}" > nul
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/2" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":9,\"student_code\":\"EST002\"}" > nul
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/3" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":11,\"student_code\":\"EST004\"}" > nul
curl -s -X POST "%COURSE_SERVICE%/enrollments/course/4" -H "Authorization: Bearer %TOKEN%" -H "Content-Type: application/json" -d "{\"student_id\":12,\"student_code\":\"EST005\"}" > nul

echo Inscripciones creadas
echo.

REM ============================================================================
REM PASO 7: Verificar datos creados
REM ============================================================================
echo [7/8] Verificando datos creados...
echo   (Ejecute manualmente consultas GET para verificar)
echo.

REM ============================================================================
REM PASO 8: Información de credenciales
REM ============================================================================
echo [8/8] Informacion de acceso
echo ============================================================================
echo   Credenciales de Prueba
echo ============================================================================
echo.
echo   ADMINISTRADOR:
echo     Email:    admin@test.com
echo     Password: Password123
echo.
echo   PROFESORES:
echo     Email:    maria.garcia@test.com (y otros PROF*@test.com)
echo     Password: Password123
echo.
echo   ESTUDIANTES:
echo     Email:    juan.perez@test.com (EST001)
echo     Email:    maria.lopez@test.com (EST002)
echo     Email:    pedro.gonzalez@test.com (EST003)
echo     Email:    ana.martinez@test.com (EST004)
echo     Email:    carlos.rodriguez@test.com (EST005)
echo     Password: Password123
echo.
echo ============================================================================

echo.
echo ============================================================================
echo   Base de datos poblada exitosamente
echo ============================================================================
echo.

endlocal
