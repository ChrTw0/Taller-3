import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { enrollmentApi, courseApi, scheduleApi, attendanceApi } from '../services/api';
import { MaterialIcons } from '@expo/vector-icons';
import type { Course, Enrollment } from '../types';

export default function CoursesScreen({ navigation }: any) {
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [schedules, setSchedules] = useState<Map<number, any[]>>(new Map());
  const [attendanceToday, setAttendanceToday] = useState<Set<number>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  // Recargar cuando se vuelva a esta pantalla (después de registrar asistencia)
  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      console.log('📱 Pantalla enfocada, recargando cursos...');
      loadCourses();
    });

    return unsubscribe;
  }, [navigation]);

  const loadCourses = async () => {
    if (!user) return;

    try {
      console.log('📚 Cargando cursos y asistencia...');

      // Obtener inscripciones del estudiante
      const enrollments: Enrollment[] = await enrollmentApi.getByStudent(user.id);
      const activeEnrollments = enrollments.filter(e => e.status === 'active');

      // Obtener todos los cursos
      const allCourses: Course[] = await courseApi.getAll();

      // Filtrar solo los cursos en los que está inscrito
      const enrolledCourseIds = activeEnrollments.map(e => e.course_id);
      const enrolledCourses = allCourses.filter(c => enrolledCourseIds.includes(c.id));

      setCourses(enrolledCourses);

      // Cargar horarios de cada curso
      const schedulesMap = new Map<number, any[]>();
      for (const course of enrolledCourses) {
        try {
          const courseSchedules = await scheduleApi.getByCourse(course.id);
          schedulesMap.set(course.id, courseSchedules);
        } catch (error) {
          console.error(`Error loading schedules for course ${course.id}:`, error);
        }
      }
      setSchedules(schedulesMap);

      // Cargar asistencia del día de hoy
      try {
        const attendanceResponse = await attendanceApi.getByUser(user.id, 100);
        const today = new Date().toISOString().split('T')[0]; // "2025-10-07"

        console.log(`📅 Fecha de hoy: ${today}`);
        console.log(`📋 Total registros: ${attendanceResponse.data.length}`);

        const coursesWithAttendanceToday = new Set<number>();
        attendanceResponse.data.forEach((record: any) => {
          const recordDate = record.created_at.split('T')[0];
          console.log(`  📝 Registro: course_id=${record.course_id}, fecha=${recordDate}, status=${record.status}`);

          if (recordDate === today && record.status === 'present') {
            coursesWithAttendanceToday.add(record.course_id);
            console.log(`    ✅ Agregado curso ${record.course_id} a la lista de asistencia de hoy`);
          }
        });

        setAttendanceToday(coursesWithAttendanceToday);
        console.log(`✅ Asistencia registrada hoy en ${coursesWithAttendanceToday.size} curso(s):`, Array.from(coursesWithAttendanceToday));
      } catch (error) {
        console.error('❌ Error loading attendance:', error);
      }
    } catch (error) {
      console.error('Error loading courses:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const onRefresh = useCallback(() => {
    setIsRefreshing(true);
    loadCourses();
  }, []);

  const formatSchedule = (schedule: any): string => {
    const days = ['LU', 'MA', 'MI', 'JU', 'VI', 'SA', 'DO'];
    const day = days[schedule.day_of_week];
    const start = schedule.start_time.substring(0, 5); // "18:00:00" -> "18:00"
    const end = schedule.end_time.substring(0, 5);
    return `${day} ${start}-${end}`;
  };

  const renderCourseCard = ({ item }: { item: Course }) => {
    const courseSchedules = schedules.get(item.id) || [];
    const hasAttendanceToday = attendanceToday.has(item.id);

    return (
    <View
      style={styles.card}
    >
      <View style={styles.cardHeader}>
        <View style={styles.cardHeaderLeft}>
          <MaterialIcons name="school" size={24} color="#3B82F6" />
          <View style={styles.cardHeaderText}>
            <Text style={styles.courseCode}>{item.code}</Text>
            <Text style={styles.courseName}>{item.name}</Text>
          </View>
        </View>
      </View>

      <View style={styles.cardBody}>
        <View style={styles.infoRow}>
          <MaterialIcons name="person" size={16} color="#6B7280" />
          <Text style={styles.infoText}>
            Profesor ID: {item.teacher_id}
          </Text>
        </View>

        <View style={styles.infoRow}>
          <MaterialIcons name="calendar-today" size={16} color="#6B7280" />
          <Text style={styles.infoText}>
            {item.academic_year} - Semestre {item.semester}
          </Text>
        </View>

        <View style={styles.infoRow}>
          <MaterialIcons name="my-location" size={16} color="#6B7280" />
          <Text style={styles.infoText}>
            Radio: {item.detection_radius}m
          </Text>
        </View>

        {/* Horarios */}
        {courseSchedules.length > 0 && (
          <View style={styles.schedulesSection}>
            <View style={styles.schedulesHeader}>
              <MaterialIcons name="schedule" size={16} color="#3B82F6" />
              <Text style={styles.schedulesTitle}>Horarios:</Text>
            </View>
            <View style={styles.schedulesContainer}>
              {courseSchedules.map((schedule: any, index: number) => (
                <View key={index} style={styles.scheduleChip}>
                  <Text style={styles.scheduleText}>
                    {formatSchedule(schedule)}
                  </Text>
                </View>
              ))}
            </View>
          </View>
        )}
      </View>

      <View style={styles.cardFooter}>
        <TouchableOpacity
          style={[
            styles.attendButton,
            hasAttendanceToday && styles.attendButtonDisabled
          ]}
          onPress={() => {
            if (!hasAttendanceToday) {
              navigation.navigate('AttendanceCapture', { course: item });
            }
          }}
          disabled={hasAttendanceToday}
        >
          <MaterialIcons
            name={hasAttendanceToday ? "check-circle" : "location-on"}
            size={20}
            color="#FFFFFF"
          />
          <Text style={styles.attendButtonText}>
            {hasAttendanceToday ? 'Asistencia Registrada' : 'Registrar Asistencia'}
          </Text>
        </TouchableOpacity>
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
      <View style={styles.header}>
        <Text style={styles.title}>Mis Cursos</Text>
        <Text style={styles.subtitle}>
          Tienes {courses.length} curso{courses.length !== 1 ? 's' : ''} activo{courses.length !== 1 ? 's' : ''}
        </Text>
      </View>

      {courses.length === 0 ? (
        <View style={styles.emptyContainer}>
          <MaterialIcons name="school" size={80} color="#D1D5DB" />
          <Text style={styles.emptyText}>No estás inscrito en ningún curso</Text>
          <Text style={styles.emptySubtext}>
            Contacta con tu administrador para inscribirte
          </Text>
        </View>
      ) : (
        <FlatList
          data={courses}
          renderItem={renderCourseCard}
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
  header: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 4,
  },
  listContainer: {
    padding: 16,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    overflow: 'hidden',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#F3F4F6',
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
    fontSize: 14,
    fontWeight: '600',
    color: '#3B82F6',
  },
  courseName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginTop: 2,
  },
  cardBody: {
    padding: 16,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 8,
  },
  cardFooter: {
    padding: 16,
    paddingTop: 0,
  },
  attendButton: {
    flexDirection: 'row',
    backgroundColor: '#3B82F6',
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  attendButtonDisabled: {
    backgroundColor: '#10B981',
    opacity: 0.8,
  },
  attendButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
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
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 8,
    textAlign: 'center',
  },
  schedulesSection: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  schedulesHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  schedulesTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#3B82F6',
    marginLeft: 6,
  },
  schedulesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  scheduleChip: {
    backgroundColor: '#DBEAFE',
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    marginRight: 6,
    marginBottom: 6,
  },
  scheduleText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1E40AF',
  },
});
