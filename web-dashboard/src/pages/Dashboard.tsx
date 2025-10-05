import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { StatCard } from '@/components/dashboard/StatCard';
import { WeeklySchedule } from '@/components/dashboard/WeeklySchedule';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, BookOpen, ClipboardCheck, Bell } from 'lucide-react';
import { userApi, courseApi, enrollmentApi, attendanceApi } from '@/lib/api';
import type { AttendanceRecord } from '@/types/attendance';

export default function Dashboard() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [recentAttendance, setRecentAttendance] = useState<AttendanceRecord[]>([]);
  const [users, setUsers] = useState<Map<number, { name: string; code: string }>>(new Map());
  const [courses, setCourses] = useState<Map<number, { name: string; code: string }>>(new Map());

  useEffect(() => {
    if (user) {
      loadDashboardData();
    }
  }, [user?.id]);

  const loadDashboardData = async () => {
    console.log('🔵 Dashboard: loadDashboardData called', { user });
    if (!user) {
      console.log('⚠️ Dashboard: No user found, returning');
      return;
    }

    setIsLoading(true);
    console.log('🔵 Dashboard: Loading started, user role:', user.role);
    try {
      const today = new Date();
      const todayStr = today.toISOString().split('T')[0];
      console.log('🔵 Dashboard: Today date:', todayStr);

      if (user.role === 'admin') {
        console.log('🔵 Dashboard: Loading admin data');
        const [coursesData, attendanceResponse] = await Promise.all([
          courseApi.getAll(),
          attendanceApi.getAll({ start_date: todayStr, limit: 5 })
        ]);
        console.log('✅ Dashboard: Courses loaded:', coursesData.length);
        console.log('✅ Dashboard: Attendance loaded:', attendanceResponse);

        // Crear mapas para cursos
        const courseMap = new Map<number, { name: string; code: string }>();
        coursesData.forEach(c => {
          courseMap.set(c.id, { name: c.name, code: c.code });
        });
        setCourses(courseMap);

        // Cargar usuarios desde las asistencias (solo los que tienen asistencias)
        const userMap = new Map<number, { name: string; code: string }>();
        const uniqueUserIds = [...new Set(attendanceResponse.data.map(a => a.user_id))];

        for (const userId of uniqueUserIds) {
          try {
            const userData = await userApi.getById(userId.toString());
            userMap.set(userData.id, {
              name: `${userData.first_name} ${userData.last_name}`,
              code: userData.code
            });
          } catch (error) {
            console.warn(`Could not load user ${userId}`);
          }
        }
        setUsers(userMap);

        // Intentar cargar todos los usuarios para el conteo
        let totalUsers = 0;
        try {
          const allUsers = await userApi.getAll();
          totalUsers = allUsers.length;
        } catch (error) {
          totalUsers = uniqueUserIds.length;
        }

        const activeCourses = coursesData.filter(c => c.is_active);

        const statsData = [
          { title: 'Usuarios Registrados', value: totalUsers.toString(), icon: Users },
          { title: 'Cursos Activos', value: activeCourses.length.toString(), icon: BookOpen },
          { title: 'Asistencias Hoy', value: attendanceResponse.total.toString(), icon: ClipboardCheck },
          { title: 'Total Cursos', value: coursesData.length.toString(), icon: Bell },
        ];
        console.log('✅ Dashboard: Stats calculated:', statsData);
        setStats(statsData);

        console.log('✅ Dashboard: Setting recent attendance:', attendanceResponse.data.length, 'records');
        setRecentAttendance(attendanceResponse.data);

      } else if (user.role === 'teacher') {
        const [allCourses, allEnrollments, attendanceResponse] = await Promise.all([
          courseApi.getAll(),
          enrollmentApi.getAll(),
          attendanceApi.getAll({ start_date: todayStr, limit: 5 })
        ]);

        // Crear mapas para cursos
        const courseMap = new Map<number, { name: string; code: string }>();
        allCourses.forEach(c => {
          courseMap.set(c.id, { name: c.name, code: c.code });
        });
        setCourses(courseMap);

        // Cargar usuarios desde las asistencias
        const userMap = new Map<number, { name: string; code: string }>();
        const uniqueUserIds = [...new Set(attendanceResponse.data.map(a => a.user_id))];

        for (const userId of uniqueUserIds) {
          try {
            const userData = await userApi.getById(userId.toString());
            userMap.set(userData.id, {
              name: `${userData.first_name} ${userData.last_name}`,
              code: userData.code
            });
          } catch (error) {
            console.warn(`Could not load user ${userId}`);
          }
        }
        setUsers(userMap);

        const teacherCourses = allCourses.filter(c => c.teacher_id === user.id);
        const teacherCourseIds = teacherCourses.map(c => c.id);
        const studentsInCourses = allEnrollments.filter(e =>
          teacherCourseIds.includes(e.course_id) && e.status === 'active'
        );

        const teacherAttendance = attendanceResponse.data.filter(a => teacherCourseIds.includes(a.course_id));

        setStats([
          { title: 'Mis Cursos', value: teacherCourses.length.toString(), icon: BookOpen },
          { title: 'Estudiantes Inscritos', value: studentsInCourses.length.toString(), icon: Users },
          { title: 'Asistencias Hoy', value: teacherAttendance.length.toString(), icon: ClipboardCheck },
          { title: 'Cursos Activos', value: teacherCourses.filter(c => c.is_active).length.toString(), icon: BookOpen },
        ]);

        setRecentAttendance(teacherAttendance);

      } else if (user.role === 'student') {
        console.log('🔵 Dashboard: Loading student data for user ID:', user.id);
        const [myEnrollments, myAttendance] = await Promise.all([
          enrollmentApi.getByStudent(user.id),
          attendanceApi.getByUser(user.id, { limit: 100 })
        ]);
        console.log('✅ Dashboard: Student data loaded - Enrollments:', myEnrollments.length, 'Attendance:', myAttendance.total);

        const activeCourses = myEnrollments.filter(e => e.status === 'active');
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        const weekAgoStr = weekAgo.toISOString();

        const weekAttendance = myAttendance.data.filter(a => new Date(a.timestamp) >= weekAgo);
        console.log('✅ Dashboard: Active courses:', activeCourses.length, 'Week attendance:', weekAttendance.length);

        const statsData = [
          { title: 'Mis Cursos', value: activeCourses.length.toString(), icon: BookOpen },
          { title: 'Total Asistencias', value: myAttendance.total.toString(), icon: ClipboardCheck },
          { title: 'Esta Semana', value: weekAttendance.length.toString(), icon: ClipboardCheck },
          { title: 'Cursos Completados', value: myEnrollments.filter(e => e.status === 'completed').length.toString(), icon: BookOpen },
        ];
        console.log('✅ Dashboard: Student stats calculated:', statsData);
        setStats(statsData);

        setRecentAttendance([]);
      }
    } catch (error) {
      console.error('❌ Dashboard: Error loading dashboard:', error);
      // Fallback to empty stats
      setStats([
        { title: 'Cargando...', value: '0', icon: Users },
        { title: 'Cargando...', value: '0', icon: BookOpen },
        { title: 'Cargando...', value: '0', icon: ClipboardCheck },
        { title: 'Cargando...', value: '0', icon: Bell },
      ]);
    } finally {
      console.log('🔵 Dashboard: Loading finished');
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      present: { label: 'Presente', className: 'bg-success/10 text-success hover:bg-success/20' },
      late: { label: 'Tarde', className: 'bg-warning/10 text-warning hover:bg-warning/20' },
      absent: { label: 'Ausente', className: 'bg-destructive/10 text-destructive hover:bg-destructive/20' },
    };
    const variant = variants[status as keyof typeof variants];
    return <Badge className={variant.className}>{variant.label}</Badge>;
  };

  console.log('🎨 Dashboard: Rendering with state -', { isLoading, hasStats: !!stats, statsLength: stats?.length, recentAttendanceLength: recentAttendance.length });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Bienvenido, {user?.first_name}
          </h1>
          <p className="text-muted-foreground">
            Aquí está el resumen de tu actividad en GeoAttend
          </p>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        )}

        {/* Stats Grid */}
        {!isLoading && stats && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat: any, index: number) => (
              <StatCard key={index} {...stat} />
            ))}
          </div>
        )}

        {/* Weekly Schedule - Only for students */}
        {!isLoading && user?.role === 'student' && (
          <WeeklySchedule userId={user.id} />
        )}

        {/* Recent Activity */}
        {!isLoading && (user?.role === 'admin' || user?.role === 'teacher') && recentAttendance.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Asistencias Recientes</CardTitle>
              <CardDescription>
                Últimos registros de asistencia de hoy
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Estudiante
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Curso
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Fecha/Hora
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Estado
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Distancia
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {recentAttendance.map((record) => (
                      <tr key={record.id} className="hover:bg-muted/50 transition-colors">
                        <td className="py-3 text-sm font-medium">
                          {users.get(record.user_id)?.name || `User ${record.user_id}`}
                        </td>
                        <td className="py-3 text-sm text-muted-foreground">
                          {courses.get(record.course_id)?.name || `Course ${record.course_id}`}
                        </td>
                        <td className="py-3 text-sm text-muted-foreground">
                          {new Date(record.timestamp).toLocaleString('es-ES')}
                        </td>
                        <td className="py-3">{getStatusBadge(record.status)}</td>
                        <td className="py-3 text-sm text-muted-foreground">
                          {record.distance_to_classroom ? `${parseFloat(String(record.distance_to_classroom)).toFixed(1)}m` : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
