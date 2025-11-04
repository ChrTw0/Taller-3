import { useEffect, useState } from 'react';
import { attendanceApi, courseApi, enrollmentApi, userApi } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext'; 
import type { OverallAttendanceStats } from '@/types/kpi';
import { KpiCard } from './KpiCard';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';

export function KpiDashboard() {
  const [stats, setStats] = useState<OverallAttendanceStats | null>(null);
  const { token } = useAuth(); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      if (!token) { // No hacer nada si no hay token
        setError("No se pudo autenticar al usuario para cargar las estadísticas.");
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        // El endpoint getOverallAttendanceStats no existe. Calcularemos las estadísticas manualmente.
        const [attendanceData, coursesResponse, usersData] = await Promise.all([
          attendanceApi.getAll({ limit: 1000 }), 
          courseApi.getAll(),
          userApi.getAll(), // Obtener todos los usuarios
        ]);

        let presentRecords = 0;
        let absentRecords = 0;
        let totalAttendance = 0;

        if (attendanceData?.data && Array.isArray(attendanceData.data)) {
          presentRecords = attendanceData.data.filter(r => r.status === 'present' || r.status === 'late').length;
          absentRecords = attendanceData.data.filter(r => r.status === 'absent').length;
          totalAttendance = presentRecords + absentRecords;
        }

        const presentPercentage = totalAttendance > 0 ? (presentRecords / totalAttendance) * 100 : 0;
        const absentPercentage = totalAttendance > 0 ? (absentRecords / totalAttendance) * 100 : 0;

        const activeCourses = coursesResponse.filter((c: any) => c.is_active).length;
        
        // Contar estudiantes activos directamente desde la lista de usuarios
        const activeStudents = usersData.filter(u => u.role === 'student' && u.is_active).length;

        const totalRecords = attendanceData?.total || 0;

        const overallStats: OverallAttendanceStats = {
          total_attendance_records: totalRecords,
          total_present: presentRecords,
          total_absent: absentRecords,
          present_percentage: presentPercentage,
          absent_percentage: absentPercentage,
          total_students: activeStudents,
          total_courses: activeCourses,
        };

        setStats(overallStats);
      } catch (err) {
        setError('No se pudieron cargar las estadísticas. Verifique que los servicios de backend (attendance, course, enrollment) estén funcionando.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [token]);

  if (loading) {
    return <div className="flex justify-center items-center p-8"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  }

  if (error || !stats) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error || 'No se recibieron datos del servidor.'}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <KpiCard title="Tasa de Asistencia" value={`${stats.present_percentage.toFixed(1)}%`} description={`Basado en ${stats.total_attendance_records} registros`} />
      <KpiCard title="Tasa de Inasistencia" value={`${stats.absent_percentage.toFixed(1)}%`} description="Sobre el total de registros" />
      <KpiCard title="Estudiantes Activos" value={stats.total_students.toString()} description="Con al menos una inscripción activa" />
      <KpiCard title="Cursos Activos" value={stats.total_courses.toString()} description="Cursos actualmente habilitados" />
    </div>
  );
}
