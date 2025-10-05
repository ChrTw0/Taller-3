# GeoAttend Mobile - App Móvil de Asistencia GPS

Aplicación móvil para estudiantes del sistema GeoAttend. Permite registrar asistencia automáticamente mediante geolocalización GPS.

## 🎯 Características

### ✅ Funcionalidades Implementadas

- **Autenticación**
  - Login con email y contraseña
  - Almacenamiento seguro de tokens JWT
  - Sesión persistente

- **Gestión de Cursos**
  - Visualización de cursos inscritos
  - Información detallada de cada curso
  - Radio GPS configurado por curso

- **Registro de Asistencia GPS** 🎯 **CORE**
  - Captura automática de ubicación GPS
  - Validación de proximidad al aula
  - Registro automático de asistencia
  - Estados: Presente/Tarde/Ausente
  - Feedback visual de precisión GPS
  - Visualización de distancia al aula

- **Historial de Asistencias**
  - Lista completa de asistencias registradas
  - Estadísticas generales (Total, Presente, Tarde, Ausente)
  - Tasa de asistencia calculada
  - Filtrado y búsqueda

- **Perfil de Usuario**
  - Información personal
  - Código de estudiante
  - Estado de cuenta

## 📱 Tecnologías

- **React Native** con **Expo**
- **TypeScript**
- **React Navigation** (Stack + Bottom Tabs)
- **Expo Location** (GPS)
- **Axios** (API client)
- **AsyncStorage** (Persistencia local)

## 🚀 Instalación y Uso

### Prerequisitos

- Node.js 16+ instalado
- Expo CLI: `npm install -g expo-cli`
- Expo Go App en tu teléfono móvil (iOS/Android)

### Instalación

```bash
cd mobile-simulator/geoattend-mobile
npm install
```

### Configuración

**IMPORTANTE:** Antes de ejecutar, asegúrate de que:

1. El backend está corriendo en `http://localhost:8000`
2. Tienes usuario creado con rol `student`
3. Estás inscrito en al menos un curso
4. Las aulas tienen coordenadas GPS configuradas

### Ejecutar en Desarrollo

```bash
# Iniciar Expo Dev Server
npm start

# O directamente en plataforma específica
npm run android  # Android
npm run ios      # iOS (requiere Mac)
npm run web      # Web browser
```

### Probar en Dispositivo Móvil

1. Instala **Expo Go** desde:
   - [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent) (Android)
   - [Apple App Store](https://apps.apple.com/app/expo-go/id982107779) (iOS)

2. Ejecuta `npm start`

3. Escanea el QR code:
   - **Android**: Usa la cámara de Expo Go
   - **iOS**: Usa la cámara del iPhone

## 📖 Guía de Uso

### 1. Iniciar Sesión

- Ingresa tu email y contraseña de estudiante
- Ejemplo: `edgar.ramos@unmsm.edu.pe` / `Student123!`

### 2. Ver Cursos

- La pantalla principal muestra tus cursos inscritos
- Cada curso tiene un botón "Registrar Asistencia"

### 3. Registrar Asistencia (CORE)

**Proceso Automático:**

1. Click en "Registrar Asistencia" en un curso
2. La app solicita permisos de ubicación (acepta)
3. Se obtiene tu ubicación GPS actual
4. Se muestra:
   - Coordenadas GPS (latitud/longitud)
   - Precisión del GPS
   - Radio GPS del aula
5. Click en "Registrar Asistencia"
6. El sistema:
   - Envía las coordenadas al backend
   - Calcula distancia al aula más cercana
   - Registra asistencia si estás dentro del radio
   - Muestra resultado (Presente/Tarde/Fuera de Rango)

**Estados de Asistencia:**
- ✅ **Presente**: Dentro del radio GPS y a tiempo
- ⏰ **Tarde**: Dentro del radio pero fuera de horario
- ❌ **Fuera de Rango**: Muy lejos del aula

### 4. Ver Historial

- Tab "Historial" muestra todas tus asistencias
- Estadísticas generales en la parte superior
- Lista detallada de cada registro

## 🔧 Estructura del Proyecto

```
geoattend-mobile/
├── src/
│   ├── screens/              # Pantallas de la app
│   │   ├── LoginScreen.tsx
│   │   ├── CoursesScreen.tsx
│   │   ├── AttendanceCaptureScreen.tsx  # 🎯 CORE
│   │   ├── AttendanceHistoryScreen.tsx
│   │   └── ProfileScreen.tsx
│   ├── navigation/
│   │   └── AppNavigator.tsx  # Navegación principal
│   ├── contexts/
│   │   └── AuthContext.tsx   # Estado de autenticación
│   ├── services/
│   │   └── api.ts            # Cliente API
│   └── types/
│       └── index.ts          # TypeScript types
├── App.tsx                   # Entry point
├── app.json                  # Configuración Expo
└── package.json
```

## 🌐 API Endpoints Utilizados

### Autenticación
- `POST /api/v1/auth/login` - Login

### Cursos
- `GET /api/v1/courses/` - Listar cursos
- `GET /api/v1/enrollments/student/{id}` - Inscripciones del estudiante

### Asistencia (CORE)
- `POST /api/v1/gps/event` - **Registrar evento GPS** 🎯
- `GET /api/v1/attendance/records` - Historial de asistencia
- `GET /api/v1/attendance/user/{id}/stats` - Estadísticas

### Usuario
- `GET /api/v1/users/me` - Perfil del usuario

## 🔑 Datos de Prueba

### Usuarios de Prueba

```javascript
// Estudiante 1
Email: edgar.ramos@unmsm.edu.pe
Password: Student123!
Código: EST001

// Estudiante 2
Email: maria.torres@unmsm.edu.pe
Password: Student123!
Código: EST002
```

### Aulas con GPS (Ejemplos)

```javascript
// Aula 101 - FIIS
Latitud: -12.0564
Longitud: -77.0844
Radio GPS: 50m

// Aula 202
Latitud: -12.0465
Longitud: -77.0429
Radio GPS: 30m
```

## 📍 Simulación de GPS

### Para Testing Local

Si estás en tu computadora y quieres simular GPS:

1. **Android Emulator**:
   - Abre el panel extendido (...)
   - Ir a "Location"
   - Ingresar coordenadas del aula

2. **iOS Simulator**:
   - Debug → Location → Custom Location
   - Ingresar coordenadas

3. **Expo Go en Dispositivo Real**:
   - Debes estar físicamente cerca del aula
   - O usar herramientas de fake GPS (solo para testing)

### Coordenadas de Prueba (FIIS - UNMSM)

```
Edificio A: -12.0564, -77.0844
Edificio B: -12.0565, -77.0845
Patio Central: -12.0566, -77.0846
```

## ⚙️ Configuración de Permisos

### Android (Automático)

Los permisos se solicitan automáticamente:
- `ACCESS_FINE_LOCATION` - GPS preciso
- `ACCESS_COARSE_LOCATION` - Ubicación aproximada

### iOS (Automático)

Se solicita mediante diálogos nativos con mensajes personalizados.

## 🐛 Troubleshooting

### Error: "No se pudo obtener ubicación"

**Solución:**
1. Verifica que los permisos de ubicación estén activos
2. En emulador, configura ubicación manual
3. En dispositivo real, activa GPS

### Error: "Fuera de Rango"

**Solución:**
1. Verifica las coordenadas del aula en el backend
2. Asegúrate de estar dentro del radio GPS (ej: 50m)
3. Verifica la precisión del GPS (debe ser < 30m idealmente)

### Error: "Error al registrar asistencia"

**Solución:**
1. Verifica que el backend esté corriendo
2. Revisa la consola para ver el error exacto
3. Asegúrate de estar inscrito en el curso
4. Verifica que el curso tenga un aula asignada con GPS

### Backend no responde

**Solución:**
1. Verifica que todos los servicios estén corriendo:
   ```bash
   # En el directorio raíz del proyecto
   docker-compose ps
   ```

2. Si usas localhost en dispositivo físico:
   - Cambia `http://localhost:8000` por la IP de tu PC
   - Ejemplo: `http://192.168.1.100:8000`
   - Actualiza en `src/services/api.ts`

## 📊 Flujo de Registro de Asistencia

```
1. Estudiante abre la app
   ↓
2. Selecciona curso
   ↓
3. Click "Registrar Asistencia"
   ↓
4. App solicita permisos GPS
   ↓
5. Obtiene ubicación actual (lat, lon, accuracy)
   ↓
6. Muestra info GPS al usuario
   ↓
7. Usuario confirma registro
   ↓
8. POST /api/v1/gps/event
   {
     user_id, course_id,
     latitude, longitude,
     accuracy, event_timestamp
   }
   ↓
9. Backend calcula distancia
   ↓
10. Si está dentro del radio → Registra asistencia
    ↓
11. App muestra resultado
```

## 🎨 Paleta de Colores

```javascript
Primary: #3B82F6    // Azul
Success: #10B981    // Verde
Warning: #F59E0B    // Amarillo
Error: #EF4444      // Rojo
Gray-50: #F9FAFB
Gray-600: #6B7280
Gray-900: #1F2937
```

## 📝 Notas Importantes

1. **Precisión GPS**:
   - Ideal: < 10m (Excelente)
   - Aceptable: 10-30m (Buena)
   - Pobre: > 30m (Puede fallar)

2. **Radio GPS del Aula**:
   - Configurable por curso en el backend
   - Típicamente: 30-50 metros
   - Considerar tamaño del edificio

3. **Testing**:
   - Mejor usar dispositivo real
   - Emuladores pueden simular GPS
   - Expo Go facilita testing rápido

4. **Seguridad**:
   - Tokens JWT en AsyncStorage
   - Comunicación HTTPS en producción
   - Permisos de ubicación solo cuando se usa

## 🚀 Próximas Mejoras

- [ ] Notificaciones push cuando se registra asistencia
- [ ] Modo offline (guardar y sincronizar después)
- [ ] Visualización en mapa de aulas cercanas
- [ ] Soporte para múltiples idiomas
- [ ] Tema oscuro
- [ ] Biometría para login

## 📞 Soporte

Para problemas o preguntas:
1. Revisa este README
2. Consulta el API_REFERENCE.md en la raíz del proyecto
3. Revisa los logs en la consola de Expo

---

**Desarrollado con ❤️ usando Expo y React Native**
