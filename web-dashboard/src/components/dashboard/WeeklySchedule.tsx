import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, MapPin } from 'lucide-react';
import { courseApi, enrollmentApi, scheduleApi } from '@/services/api';
import type { Course, Schedule } from '@/types/course';

interface ScheduleWithCourse extends Schedule {
  course: Course;
}

const DAYS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const DAY_MAPPING = { 0: 'LU', 1: 'MA', 2: 'MI', 3: 'JU', 4: 'VI', 5: 'SA', 6: 'DO' };

export function WeeklySchedule({ userId }: { userId: number }) {
  const [schedules, setSchedules] = useState<ScheduleWithCourse[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSchedules();
  }, [userId]);

  const loadSchedules = async () => {
    try {
      // 1. Obtener cursos del estudiante
      const enrollments = await enrollmentApi.getByStudent(userId);
      const activeCourseIds = enrollments
        .filter(e => e.status === 'active')
        .map(e => e.course_id);

      // 2. Obtener información de cada curso
      const courses = await courseApi.getAll();
      const studentCourses = courses.filter(c => activeCourseIds.includes(c.id));

      // 3. Obtener horarios de cada curso
      const allSchedules: ScheduleWithCourse[] = [];

      for (const course of studentCourses) {
        try {
          const courseSchedules = await scheduleApi.getByCourse(course.id);
          if (courseSchedules && Array.isArray(courseSchedules)) {
            courseSchedules.forEach(schedule => {
              allSchedules.push({ ...schedule, course });
            });
          }
        } catch (error) {
          console.error(`Error loading schedules for course ${course.code}:`, error);
        }
      }

      setSchedules(allSchedules);
    } catch (error) {
      console.error('Error loading weekly schedule:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getSchedulesForDay = (day: number): ScheduleWithCourse[] => {
    return schedules
      .filter(s => s.day_of_week === day)
      .sort((a, b) => a.start_time.localeCompare(b.start_time));
  };

  const formatTime = (time: string): string => {
    // Convert "18:00:00" to "6:00 PM"
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
    return `${displayHour}:${minutes} ${period}`;
  };

  const getCourseColor = (courseCode: string): string => {
    // Generar color consistente basado en el código del curso
    const colors = [
      'bg-blue-100 text-blue-800 border-blue-300',
      'bg-green-100 text-green-800 border-green-300',
      'bg-purple-100 text-purple-800 border-purple-300',
      'bg-orange-100 text-orange-800 border-orange-300',
      'bg-pink-100 text-pink-800 border-pink-300',
      'bg-indigo-100 text-indigo-800 border-indigo-300',
      'bg-teal-100 text-teal-800 border-teal-300',
    ];
    const index = courseCode.charCodeAt(0) % colors.length;
    return colors[index];
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Mi Horario Semanal</CardTitle>
          <CardDescription>Cargando horarios...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (schedules.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Mi Horario Semanal</CardTitle>
          <CardDescription>No tienes horarios asignados</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Mi Horario Semanal
        </CardTitle>
        <CardDescription>
          Tus clases de la semana - Total: {schedules.length} sesiones
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-7 gap-3">
          {DAYS.map((dayName, dayIndex) => {
            const daySchedules = getSchedulesForDay(dayIndex);

            return (
              <div key={dayIndex} className="border rounded-lg p-3 bg-gray-50">
                <h3 className="font-semibold text-sm text-gray-700 mb-2 text-center">
                  {dayName}
                </h3>
                <div className="space-y-2">
                  {daySchedules.length === 0 ? (
                    <p className="text-xs text-gray-400 text-center py-4">Sin clases</p>
                  ) : (
                    daySchedules.map((schedule, idx) => (
                      <div
                        key={idx}
                        className={`p-2 rounded-md border ${getCourseColor(schedule.course.code)}`}
                      >
                        <div className="font-medium text-xs mb-1">
                          {schedule.course.code}
                        </div>
                        <div className="text-xs text-gray-600 mb-1 line-clamp-2">
                          {schedule.course.name}
                        </div>
                        <div className="flex items-center gap-1 text-xs">
                          <Clock className="h-3 w-3" />
                          <span>
                            {formatTime(schedule.start_time)} - {formatTime(schedule.end_time)}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
