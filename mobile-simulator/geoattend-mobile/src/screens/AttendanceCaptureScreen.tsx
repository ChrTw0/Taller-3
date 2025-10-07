import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Dimensions,
  ScrollView,
} from 'react-native';
import * as Location from 'expo-location';
import { WebView } from 'react-native-webview';
import { useAuth } from '../contexts/AuthContext';
import { gpsApi, courseApi, scheduleApi } from '../services/api';
import { MaterialIcons } from '@expo/vector-icons';
import type { Course } from '../types';

interface Props {
  route: {
    params: {
      course: Course;
    };
  };
  navigation: any;
}

interface ClassroomCoordinates {
  id: number;
  latitude: number;
  longitude: number;
  gps_radius: number;
  building: string;
  room_number: string;
  name: string;
}

const { width } = Dimensions.get('window');

export default function AttendanceCaptureScreen({ route, navigation }: Props) {
  const { course } = route.params;
  const { user } = useAuth();
  const webViewRef = useRef<WebView>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [classrooms, setClassrooms] = useState<ClassroomCoordinates[]>([]);
  const [nearestClassroom, setNearestClassroom] = useState<ClassroomCoordinates | null>(null);
  const [distance, setDistance] = useState<number | null>(null);
  const [isWithinRange, setIsWithinRange] = useState(false);
  const [locationSubscription, setLocationSubscription] = useState<Location.LocationSubscription | null>(null);

  useEffect(() => {
    loadClassroomCoordinates();
    requestLocationPermission();

    return () => {
      if (locationSubscription) {
        locationSubscription.remove();
      }
    };
  }, []);

  useEffect(() => {
    if (location && classrooms.length > 0) {
      calculateDistance();
      updateMapLocation();
    }
  }, [location, classrooms]);

  const loadClassroomCoordinates = async () => {
    try {
      const coordinates = await courseApi.getCoordinates(course.id);
      setClassrooms(coordinates.classrooms);
    } catch (error) {
      console.error('Error loading classroom coordinates:', error);
      Alert.alert('Error', 'No se pudieron cargar las coordenadas de las aulas');
    }
  };

  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setLocationError('Permiso de ubicación denegado');
        Alert.alert(
          'Permiso Requerido',
          'Esta aplicación necesita acceso a tu ubicación para registrar asistencia'
        );
        return;
      }

      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.BestForNavigation,
      });
      setLocation(currentLocation);

      const subscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.BestForNavigation,
          timeInterval: 2000,
          distanceInterval: 5,
        },
        (newLocation) => {
          setLocation(newLocation);
        }
      );

      setLocationSubscription(subscription);
    } catch (error) {
      setLocationError('Error al obtener ubicación');
      console.error('Location error:', error);
    }
  };

  const calculateHaversineDistance = (
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
  ): number => {
    const R = 6371e3;
    const φ1 = (lat1 * Math.PI) / 180;
    const φ2 = (lat2 * Math.PI) / 180;
    const Δφ = ((lat2 - lat1) * Math.PI) / 180;
    const Δλ = ((lon2 - lon1) * Math.PI) / 180;

    const a =
      Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
      Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
  };

  const calculateDistance = () => {
    if (!location || classrooms.length === 0) return;

    let minDistance = Infinity;
    let closest: ClassroomCoordinates | null = null;

    classrooms.forEach((classroom) => {
      const dist = calculateHaversineDistance(
        location.coords.latitude,
        location.coords.longitude,
        classroom.latitude,
        classroom.longitude
      );

      if (dist < minDistance) {
        minDistance = dist;
        closest = classroom;
      }
    });

    setDistance(minDistance);
    setNearestClassroom(closest);

    if (closest) {
      const withinRange = minDistance <= closest.gps_radius;
      setIsWithinRange(withinRange);
    }
  };

  const updateMapLocation = () => {
    if (!location || !webViewRef.current) return;

    const updateScript = `
      if (typeof updateUserLocation === 'function') {
        updateUserLocation(${location.coords.latitude}, ${location.coords.longitude});
      }
      true;
    `;

    webViewRef.current.injectJavaScript(updateScript);
  };

  const handleCaptureAttendance = async () => {
    console.log('🎯 handleCaptureAttendance: Iniciando registro de asistencia');

    if (!location) {
      console.log('❌ Error: No hay ubicación disponible');
      Alert.alert('Error', 'No se pudo obtener tu ubicación');
      return;
    }

    if (!user) {
      console.log('❌ Error: Usuario no autenticado');
      Alert.alert('Error', 'Usuario no autenticado');
      return;
    }

    console.log(`📍 Ubicación: ${location.coords.latitude}, ${location.coords.longitude}`);
    console.log(`📊 Precisión GPS: ${location.coords.accuracy}m`);

    setIsLoading(true);
    try {
      // Validar que haya un horario activo antes de enviar GPS
      console.log(`⏰ Validando horario activo para curso ${course.id}...`);
      const currentSchedule = await scheduleApi.getCurrentSchedule(course.id);

      if (!currentSchedule) {
        console.log('⏰ No hay horario activo en este momento');
        Alert.alert(
          '⏰ Sin Clase Programada',
          'No hay clase en este momento. La asistencia solo puede registrarse durante el horario de clase (±15 min de tolerancia).',
          [{ text: 'Entendido' }]
        );
        setIsLoading(false);
        return;
      }

      console.log(`✅ Horario activo encontrado: ${currentSchedule.day_of_week}, ${currentSchedule.start_time}-${currentSchedule.end_time}`);

      const gpsData = {
        user_id: user.id,
        course_id: course.id,
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        accuracy: location.coords.accuracy || 10,
        event_timestamp: new Date().toISOString(),
      };

      console.log('📡 Enviando evento GPS al servidor...', gpsData);
      const response = await gpsApi.sendGPSEvent(gpsData);

      console.log('📥 Respuesta del servidor:', response);

      if (response.success && response.data) {
        const { data } = response;

        // Validar que los datos existan antes de acceder a ellos
        const status = data.status || 'unknown';
        const distanceMeters = data.distance_meters || 0;
        const nearestClassroomName = data.nearest_classroom?.name || data.nearest_classroom?.room_number || 'Desconocida';
        const attendanceRecorded = data.attendance_recorded || false;

        console.log(`✅ Estado: ${status}, Distancia: ${distanceMeters}m, Aula: ${nearestClassroomName}, Registrado: ${attendanceRecorded}`);

        let title = 'Asistencia Registrada';
        let message = `Estado: ${status.toUpperCase()}\nDistancia: ${distanceMeters.toFixed(1)}m\nAula: ${nearestClassroomName}`;

        if (attendanceRecorded) {
          if (status === 'present') {
            title = '✅ Presente';
            console.log('🎉 Asistencia registrada como PRESENTE');
          } else if (status === 'late') {
            title = '⏰ Tardanza';
            console.log('⚠️ Asistencia registrada como TARDANZA');
          }
        } else {
          title = '❌ Fuera de Rango';
          const maxDistance = nearestClassroom?.gps_radius || course.detection_radius || 50;
          message = `No estás dentro del radio GPS del aula.\nDistancia: ${distanceMeters.toFixed(1)}m (Máx: ${maxDistance}m)`;
          console.log(`❌ Fuera de rango: ${distanceMeters}m > ${maxDistance}m`);
        }

        Alert.alert(title, message, [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]);
      } else {
        console.log('⚠️ Respuesta del servidor sin datos:', response);
        Alert.alert('Error', 'No se recibió respuesta válida del servidor');
      }
    } catch (error: any) {
      console.error('❌ Error capturing attendance:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });

      const errorMessage = error.response?.data?.detail || error.message || 'Error al registrar asistencia';

      Alert.alert(
        'Error al Registrar',
        errorMessage,
        [{ text: 'OK' }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  const getAccuracyColor = (accuracy: number | undefined) => {
    if (!accuracy) return '#9CA3AF';
    if (accuracy < 10) return '#10B981';
    if (accuracy < 30) return '#F59E0B';
    return '#EF4444';
  };

  const getAccuracyText = (accuracy: number | undefined) => {
    if (!accuracy) return 'Desconocida';
    if (accuracy < 10) return 'Excelente';
    if (accuracy < 30) return 'Buena';
    return 'Pobre';
  };

  // Mapa mejorado con mejores tiles y diseño
  const generateMapHTML = () => {
    const userLat = location?.coords.latitude || -16.409;
    const userLng = location?.coords.longitude || -71.537;
    const classroomsJSON = JSON.stringify(classrooms);

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <title>GeoAttend Map</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
          body { margin: 0; padding: 0; }
          #map { height: 100vh; width: 100%; }
        </style>
      </head>
      <body>
        <div id="map"></div>
        <script>
          console.log('Initializing map...');

          var map = L.map('map', {
            zoomControl: true,
            attributionControl: true
          }).setView([${userLat}, ${userLng}], 17);

          console.log('User location:', ${userLat}, ${userLng});

          // Tiles de Carto Voyager
          L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap, © CARTO',
            maxZoom: 20,
          }).addTo(map);

          // Marcador del usuario con círculo azul simple
          var userCircle = L.circleMarker([${userLat}, ${userLng}], {
            color: '#FFFFFF',
            fillColor: '#3B82F6',
            fillOpacity: 1,
            radius: 10,
            weight: 3
          }).addTo(map);

          userCircle.bindPopup('<strong>📍 Tu ubicación</strong>');

          console.log('User marker added');

          var classrooms = ${classroomsJSON};
          var circles = [];
          var classroomMarkers = [];

          console.log('Classrooms:', classrooms.length);

          classrooms.forEach(function(classroom, idx) {
            console.log('Adding classroom ' + idx + ':', classroom.name, classroom.latitude, classroom.longitude);

            // Círculo de geofence
            var circle = L.circle([classroom.latitude, classroom.longitude], {
              color: '#3B82F6',
              fillColor: '#3B82F6',
              fillOpacity: 0.15,
              radius: classroom.gps_radius,
              weight: 2
            }).addTo(map);

            circles.push(circle);

            // Marcador del aula con ícono rojo estándar
            var marker = L.marker([classroom.latitude, classroom.longitude], {
              icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
              })
            }).addTo(map);

            marker.bindPopup(
              '<div style="text-align: center;">' +
              '<strong>🏫 ' + classroom.name + '</strong><br>' +
              '<span>' + classroom.building + ' - ' + classroom.room_number + '</span><br>' +
              '<span style="color: #10B981;">Radio: ' + classroom.gps_radius + 'm</span>' +
              '</div>'
            );

            classroomMarkers.push(marker);
          });

          console.log('All markers added');

          function updateUserLocation(lat, lng) {
            console.log('Updating user location to:', lat, lng);
            userCircle.setLatLng([lat, lng]);
            map.setView([lat, lng], map.getZoom());

            classrooms.forEach(function(classroom, index) {
              var distance = map.distance([lat, lng], [classroom.latitude, classroom.longitude]);
              var isWithinRange = distance <= classroom.gps_radius;

              circles[index].setStyle({
                color: isWithinRange ? '#10B981' : '#EF4444',
                fillColor: isWithinRange ? '#10B981' : '#EF4444',
                fillOpacity: isWithinRange ? 0.2 : 0.1,
                weight: isWithinRange ? 3 : 2
              });
            });
          }
        </script>
      </body>
      </html>
    `;
  };

  return (
    <View style={styles.container}>
      {/* Course Header */}
      <View style={styles.header}>
        <Text style={styles.courseCode}>{course.code}</Text>
        <Text style={styles.courseName}>{course.name}</Text>
      </View>

      {/* Map View */}
      {!locationError && location && classrooms.length > 0 ? (
        <View style={styles.mapContainer}>
          <WebView
            ref={webViewRef}
            style={styles.map}
            originWhitelist={['*']}
            source={{ html: generateMapHTML() }}
            javaScriptEnabled={true}
            domStorageEnabled={true}
            scrollEnabled={false}
          />
        </View>
      ) : (
        <View style={styles.loadingMapContainer}>
          <ActivityIndicator size="large" color="#3B82F6" />
          <Text style={styles.loadingText}>
            {locationError || 'Cargando mapa...'}
          </Text>
        </View>
      )}

      {/* Status Info */}
      <ScrollView style={styles.infoContainer}>
        {/* Distance Indicator */}
        {distance !== null && nearestClassroom && (
          <View
            style={[
              styles.distanceCard,
              isWithinRange ? styles.distanceCardSuccess : styles.distanceCardError,
            ]}
          >
            <View style={styles.distanceHeader}>
              <MaterialIcons
                name={isWithinRange ? 'check-circle' : 'error'}
                size={32}
                color={isWithinRange ? '#10B981' : '#EF4444'}
              />
              <View style={styles.distanceInfo}>
                <Text style={[
                  styles.distanceText,
                  isWithinRange ? styles.distanceTextSuccess : styles.distanceTextError,
                ]}>
                  {distance.toFixed(1)}m
                </Text>
                <Text style={styles.distanceLabel}>
                  {isWithinRange ? 'Dentro del rango' : 'Fuera del rango'}
                </Text>
              </View>
            </View>
            <Text style={styles.classroomName}>
              {nearestClassroom.name}
            </Text>
            <Text style={styles.classroomDetails}>
              Radio permitido: {nearestClassroom.gps_radius}m
            </Text>
          </View>
        )}

        {/* GPS Status */}
        {location && (
          <View style={styles.statusCard}>
            <Text style={styles.statusTitle}>Estado del GPS</Text>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Latitud:</Text>
              <Text style={styles.infoValue}>
                {location.coords.latitude.toFixed(6)}
              </Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Longitud:</Text>
              <Text style={styles.infoValue}>
                {location.coords.longitude.toFixed(6)}
              </Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Precisión:</Text>
              <Text
                style={[
                  styles.infoValue,
                  { color: getAccuracyColor(location.coords.accuracy) },
                ]}
              >
                ±{location.coords.accuracy?.toFixed(1) || 'N/A'}m (
                {getAccuracyText(location.coords.accuracy)})
              </Text>
            </View>
          </View>
        )}

        {/* Instructions */}
        <View style={styles.instructionsCard}>
          <MaterialIcons name="info-outline" size={24} color="#3B82F6" />
          <Text style={styles.instructionsText}>
            {isWithinRange
              ? 'Estás dentro del área permitida. Puedes registrar tu asistencia.'
              : `Acércate al aula para registrar asistencia. Distancia requerida: ${nearestClassroom?.gps_radius || course.detection_radius}m`}
          </Text>
        </View>
      </ScrollView>

      {/* Capture Button */}
      <TouchableOpacity
        style={[
          styles.captureButton,
          (!location || isLoading) && styles.captureButtonDisabled,
          isWithinRange && styles.captureButtonSuccess,
        ]}
        onPress={handleCaptureAttendance}
        disabled={!location || isLoading}
      >
        {isLoading ? (
          <ActivityIndicator color="#FFFFFF" />
        ) : (
          <>
            <MaterialIcons name="check-circle" size={24} color="#FFFFFF" />
            <Text style={styles.captureButtonText}>
              {isWithinRange ? 'Registrar Asistencia' : 'Intentar Registrar'}
            </Text>
          </>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    backgroundColor: '#3B82F6',
    padding: 16,
    alignItems: 'center',
  },
  courseCode: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
    opacity: 0.9,
  },
  courseName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 4,
    textAlign: 'center',
  },
  mapContainer: {
    height: 300,
    position: 'relative',
  },
  map: {
    width: '100%',
    height: '100%',
  },
  loadingMapContainer: {
    height: 300,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#E5E7EB',
  },
  loadingText: {
    marginTop: 12,
    color: '#6B7280',
  },
  infoContainer: {
    flex: 1,
    padding: 16,
  },
  distanceCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 2,
  },
  distanceCardSuccess: {
    borderColor: '#10B981',
    backgroundColor: '#ECFDF5',
  },
  distanceCardError: {
    borderColor: '#EF4444',
    backgroundColor: '#FEF2F2',
  },
  distanceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  distanceInfo: {
    marginLeft: 12,
    flex: 1,
  },
  distanceText: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  distanceTextSuccess: {
    color: '#10B981',
  },
  distanceTextError: {
    color: '#EF4444',
  },
  distanceLabel: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  classroomName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  classroomDetails: {
    fontSize: 14,
    color: '#6B7280',
  },
  statusCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  statusTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  infoLabel: {
    fontSize: 14,
    color: '#6B7280',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  instructionsCard: {
    flexDirection: 'row',
    backgroundColor: '#EFF6FF',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#BFDBFE',
    marginBottom: 16,
  },
  instructionsText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 14,
    color: '#1E40AF',
    lineHeight: 20,
  },
  captureButton: {
    flexDirection: 'row',
    backgroundColor: '#3B82F6',
    margin: 16,
    padding: 18,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  captureButtonSuccess: {
    backgroundColor: '#10B981',
  },
  captureButtonDisabled: {
    opacity: 0.5,
  },
  captureButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});
