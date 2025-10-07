import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { attendanceApi, courseApi } from '../services/api';
import { MaterialIcons } from '@expo/vector-icons';
import type { AttendanceRecord, Course, AttendanceStats } from '../types';

export default function AttendanceHistoryScreen() {
  const { user } = useAuth();
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [stats, setStats] = useState<AttendanceStats | null>(null);
  const [courses, setCourses] = useState<Map<number, string>>(new Map());
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    if (!user) {
      console.log('❌ No hay usuario autenticado');
      return;
    }

    try {
      console.log('📊 Cargando historial de asistencia para user_id:', user.id);

      const [attendanceData, statsData, coursesData] = await Promise.all([
        attendanceApi.getByUser(user.id, 50),
        attendanceApi.getUserStats(user.id),
        courseApi.getAll(),
      ]);

      console.log('📥 Datos de asistencia:', attendanceData);
      console.log('📈 Estadísticas:', statsData);
      console.log('📚 Cursos cargados:', coursesData.length);

      setAttendance(attendanceData.data);
      setStats(statsData); // Ya viene mapeado desde api.ts

      const courseMap = new Map<number, string>();
      coursesData.forEach(c => courseMap.set(c.id, c.name));
      setCourses(courseMap);

      console.log(`✅ Historial cargado: ${attendanceData.data.length} registros`);
    } catch (error: any) {
      console.error('❌ Error loading attendance:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const onRefresh = () => {
    setIsRefreshing(true);
    loadData();
  };

  const getStatusBadge = (status: string) => {
    const config = {
      present: { label: 'Presente', color: '#10B981', bg: '#D1FAE5' },
      late: { label: 'Tarde', color: '#F59E0B', bg: '#FEF3C7' },
      absent: { label: 'Ausente', color: '#EF4444', bg: '#FEE2E2' },
      excused: { label: 'Justificado', color: '#3B82F6', bg: '#DBEAFE' },
    };

    const { label, color, bg } = config[status as keyof typeof config] || config.absent;

    return (
      <View style={[styles.badge, { backgroundColor: bg }]}>
        <Text style={[styles.badgeText, { color }]}>{label}</Text>
      </View>
    );
  };

  const renderAttendanceItem = ({ item }: { item: AttendanceRecord }) => {
    // Usar actual_arrival si existe, sino class_date
    const displayDate = item.actual_arrival || item.class_date || item.created_at;

    return (
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <View style={styles.cardHeaderLeft}>
            <MaterialIcons name="school" size={24} color="#3B82F6" />
            <View style={styles.cardHeaderText}>
              <Text style={styles.courseCode}>{item.course_code || `Curso ${item.course_id}`}</Text>
              <Text style={styles.courseName}>
                {courses.get(item.course_id) || 'Curso Desconocido'}
              </Text>
            </View>
          </View>
          {getStatusBadge(item.status)}
        </View>

        <View style={styles.cardBody}>
          <View style={styles.infoRow}>
            <MaterialIcons name="access-time" size={16} color="#6B7280" />
            <Text style={styles.infoText}>
              {new Date(displayDate).toLocaleString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Text>
          </View>

          {item.recorded_distance != null && (
            <View style={styles.infoRow}>
              <MaterialIcons name="my-location" size={16} color="#6B7280" />
              <Text style={styles.infoText}>
                Distancia: {Number(item.recorded_distance).toFixed(1)}m
              </Text>
            </View>
          )}

          {item.classroom_name && (
            <View style={styles.infoRow}>
              <MaterialIcons name="meeting-room" size={16} color="#6B7280" />
              <Text style={styles.infoText}>{item.classroom_name}</Text>
            </View>
          )}

          <View style={styles.infoRow}>
            <MaterialIcons
              name={item.source === 'gps_auto' ? 'gps-fixed' : 'edit'}
              size={16}
              color="#6B7280"
            />
            <Text style={styles.infoText}>
              {item.source === 'gps_auto' ? 'GPS Automático' : 'Manual'}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  if (isLoading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#3B82F6" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Stats Card */}
      {stats && (
        <View style={styles.statsCard}>
          <Text style={styles.statsTitle}>Estadísticas Generales</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats.total_records}</Text>
              <Text style={styles.statLabel}>Total</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statValue, { color: '#10B981' }]}>
                {stats.present_count}
              </Text>
              <Text style={styles.statLabel}>Presente</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statValue, { color: '#F59E0B' }]}>
                {stats.late_count}
              </Text>
              <Text style={styles.statLabel}>Tarde</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={[styles.statValue, { color: '#EF4444' }]}>
                {stats.absent_count}
              </Text>
              <Text style={styles.statLabel}>Ausente</Text>
            </View>
          </View>
          <View style={styles.attendanceRate}>
            <Text style={styles.attendanceRateLabel}>Tasa de Asistencia</Text>
            <Text style={styles.attendanceRateValue}>
              {stats.attendance_rate.toFixed(1)}%
            </Text>
          </View>
        </View>
      )}

      {/* Attendance List */}
      <View style={styles.listHeader}>
        <Text style={styles.listTitle}>Historial de Asistencia</Text>
      </View>

      {attendance.length === 0 ? (
        <View style={styles.emptyContainer}>
          <MaterialIcons name="event-busy" size={80} color="#D1D5DB" />
          <Text style={styles.emptyText}>No hay registros de asistencia</Text>
        </View>
      ) : (
        <FlatList
          data={attendance}
          renderItem={renderAttendanceItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsCard: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  statsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  attendanceRate: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  attendanceRateLabel: {
    fontSize: 16,
    color: '#6B7280',
  },
  attendanceRateValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3B82F6',
  },
  listHeader: {
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  listTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  listContainer: {
    padding: 16,
    paddingTop: 8,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    overflow: 'hidden',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#F9FAFB',
  },
  cardHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  cardHeaderText: {
    marginLeft: 12,
    flex: 1,
  },
  courseCode: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
  },
  courseName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  cardBody: {
    padding: 12,
    gap: 8,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  infoText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 16,
  },
});
