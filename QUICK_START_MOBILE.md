# 🚀 Quick Start - GeoAttend Mobile App

## Inicio Rápido en 3 Pasos

### 📱 Paso 1: Instalar Dependencias
```bash
cd mobile-simulator/geoattend-mobile
npm install
```

### 📱 Paso 2: Iniciar Expo
```bash
npm start
```

### 📱 Paso 3: Abrir en tu Teléfono

1. **Instala Expo Go** en tu teléfono:
   - [Android - Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - [iOS - App Store](https://apps.apple.com/app/expo-go/id982107779)

2. **Escanea el QR Code** que aparece en la terminal

3. **La app se abrirá automáticamente** en Expo Go

---

## 🔑 Credenciales de Prueba

```
Email: edgar.ramos@unmsm.edu.pe
Password: Student123!
```

---

## ✅ Verificación Previa

Antes de usar la app, asegúrate de que:

1. ✅ **Backend corriendo:**
   ```bash
   # Desde la raíz del proyecto
   docker-compose up -d
   ```

2. ✅ **Tienes usuarios creados:**
   - Al menos 1 estudiante
   - Con cursos inscritos

3. ✅ **Aulas con GPS configurado:**
   - Latitud, longitud y radio GPS

---

## 📍 Simular GPS (Para Testing)

### En Emulador Android:
1. Abre el emulador
2. Click en `...` (More tools)
3. Location → Custom location
4. Ingresa coordenadas del aula:
   ```
   Latitud: -12.0564
   Longitud: -77.0844
   ```

### En Simulador iOS:
1. Debug → Location → Custom Location
2. Ingresa coordenadas

### En Dispositivo Real:
- Debes estar físicamente en la ubicación
- O usar app de fake GPS (solo testing)

---

## 🎯 Flujo de Uso

1. **Login** con credenciales
2. **Ver cursos** en pantalla principal
3. **Click "Registrar Asistencia"** en un curso
4. **Permitir acceso GPS**
5. **Confirmar ubicación**
6. **Ver resultado** (Presente/Tarde/Fuera de Rango)

---

## 🐛 Troubleshooting Rápido

### "No se conecta al backend"
- Verifica que el backend esté corriendo: `docker-compose ps`
- Si usas dispositivo real, cambia `localhost` por IP de tu PC
  - Edita: `src/services/api.ts`
  - Cambia: `http://localhost:8000` → `http://192.168.X.X:8000`

### "No obtiene ubicación"
- Verifica permisos de ubicación en el dispositivo
- En emulador, configura ubicación manualmente

### "Fuera de Rango"
- Verifica que las coordenadas del aula estén correctas
- Verifica el radio GPS del curso (ej: 50m)
- Asegúrate de estar cerca del aula

---

## 📚 Documentación Completa

- **README completo:** `/mobile-simulator/geoattend-mobile/README.md`
- **Resumen técnico:** `/MOBILE_APP_SUMMARY.md`
- **API Reference:** `/API_REFERENCE.md`

---

## ✨ Comandos Útiles

```bash
# Iniciar en modo desarrollo
npm start

# Limpiar cache
npm start -- --clear

# Ver logs
npm start -- --dev-client

# Web (testing rápido)
npm run web

# Android (requiere emulador)
npm run android

# iOS (solo macOS)
npm run ios
```

---

**¡Listo para usar! 🎉**
