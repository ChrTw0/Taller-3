import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import * as Location from 'expo-location';
import { useAuth } from '../contexts/AuthContext';
import { gpsApi } from '../services/api';
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

export default function AttendanceCaptureScreen({ route, navigation }: Props) {
  const { course } = route.params;
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);

  useEffect(() => {
    requestLocationPermission();
  }, []);

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

      // Obtener ubicación actual
      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.BestForNavigation,
      });
      setLocation(currentLocation);
    } catch (error) {
      setLocationError('Error al obtener ubicación');
      console.error('Location error:', error);
    }
  };

  const handleCaptureAttendance = async () => {
    if (!location) {
      Alert.alert('Error', 'No se pudo obtener tu ubicación');
      return;
    }

    if (!user) {
      Alert.alert('Error', 'Usuario no autenticado');
      return;
    }

    setIsLoading(true);
    try {
      const gpsData = {
        user_id: user.id,
        course_id: course.id,
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        accuracy: location.coords.accuracy || 10,
        event_timestamp: new Date().toISOString(),
      };

      console.log('Sending GPS data:', gpsData);

      const response = await gpsApi.sendGPSEvent(gpsData);

      if (response.success) {
        const { data } = response;

        // Determinar el mensaje según el resultado
        let title = 'Asistencia Registrada';
        let message = `Estado: ${data.status.toUpperCase()}\nDistancia: ${data.distance_meters.toFixed(1)}m\nAula: ${data.nearest_classroom.name}`;

        if (data.attendance_recorded) {
          if (data.status === 'present') {
            title = '✅ Presente';
          } else if (data.status === 'late') {
            title = '⏰ Tardanza';
          }
        } else {
          title = '❌ Fuera de Rango';
          message = `No estás dentro del radio GPS del aula.\nDistancia: ${data.distance_meters.toFixed(1)}m (Máx: ${course.gps_radius}m)`;
        }

        Alert.alert(title, message, [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]);
      }
    } catch (error: any) {
      console.error('Error capturing attendance:', error);
      Alert.alert(
        'Error',
        error.response?.data?.detail || 'Error al registrar asistencia'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const getAccuracyColor = (accuracy: number | undefined) => {
    if (!accuracy) return '#9CA3AF';
    if (accuracy < 10) return '#10B981'; // Excelente
    if (accuracy < 30) return '#F59E0B'; // Bueno
    return '#EF4444'; // Pobre
  };

  const getAccuracyText = (accuracy: number | undefined) => {
    if (!accuracy) return 'Desconocida';
    if (accuracy < 10) return 'Excelente';
    if (accuracy < 30) return 'Buena';
    return 'Pobre';
  };

  return (
    <View style={styles.container}>
      {/* Course Info */}
      <View style={styles.header}>
        <Text style={styles.courseCode}>{course.code}</Text>
        <Text style={styles.courseName}>{course.name}</Text>
      </View>

      {/* GPS Status */}
      <View style={styles.statusCard}>
        <View style={styles.statusHeader}>
          <MaterialIcons name="my-location" size={32} color="#3B82F6" />
          <Text style={styles.statusTitle}>Estado del GPS</Text>
        </View>

        {locationError ? (
          <View style={styles.errorContainer}>
            <MaterialIcons name="error-outline" size={48} color="#EF4444" />
            <Text style={styles.errorText}>{locationError}</Text>
            <TouchableOpacity
              style={styles.retryButton}
              onPress={requestLocationPermission}
            >
              <Text style={styles.retryButtonText}>Reintentar</Text>
            </TouchableOpacity>
          </View>
        ) : location ? (
          <View style={styles.locationInfo}>
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

            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Radio GPS Aula:</Text>
              <Text style={styles.infoValue}>{course.gps_radius}m</Text>
            </View>
          </View>
        ) : (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#3B82F6" />
            <Text style={styles.loadingText}>Obteniendo ubicación...</Text>
          </View>
        )}
      </View>

      {/* Instructions */}
      <View style={styles.instructionsCard}>
        <MaterialIcons name="info-outline" size={24} color="#3B82F6" />
        <Text style={styles.instructionsText}>
          Asegúrate de estar dentro del aula o cerca de ella (radio de{' '}
          {course.gps_radius}m) para registrar tu asistencia exitosamente.
        </Text>
      </View>

      {/* Capture Button */}
      <TouchableOpacity
        style={[
          styles.captureButton,
          (!location || isLoading) && styles.captureButtonDisabled,
        ]}
        onPress={handleCaptureAttendance}
        disabled={!location || isLoading}
      >
        {isLoading ? (
          <ActivityIndicator color="#FFFFFF" />
        ) : (
          <>
            <MaterialIcons name="check-circle" size={24} color="#FFFFFF" />
            <Text style={styles.captureButtonText}>Registrar Asistencia</Text>
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
    padding: 24,
    alignItems: 'center',
  },
  courseCode: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
    opacity: 0.9,
  },
  courseName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 4,
    textAlign: 'center',
  },
  statusCard: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  statusTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    marginLeft: 12,
  },
  errorContainer: {
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: '#EF4444',
    marginTop: 12,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 16,
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: '#3B82F6',
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  locationInfo: {
    gap: 12,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  infoLabel: {
    fontSize: 16,
    color: '#6B7280',
  },
  infoValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 12,
    color: '#6B7280',
  },
  instructionsCard: {
    flexDirection: 'row',
    backgroundColor: '#EFF6FF',
    margin: 16,
    marginTop: 0,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#BFDBFE',
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
    backgroundColor: '#10B981',
    margin: 16,
    padding: 18,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
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
