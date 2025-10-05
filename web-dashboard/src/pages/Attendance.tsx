import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { RefreshCw, Download, Search, Filter } from 'lucide-react';
import { attendanceApi, userApi, courseApi, classroomApi } from '@/lib/api';
import { toast } from 'sonner';
import type { AttendanceRecord, AttendanceStatus } from '@/types/attendance';

export default function Attendance() {
  const { user } = useAuth();
  const [attendanceRecords, setAttendanceRecords] = useState<AttendanceRecord[]>([]);
  const [filteredRecords, setFilteredRecords] = useState<AttendanceRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [users, setUsers] = useState<Map<number, { name: string; code: string }>>(new Map());
  const [courses, setCourses] = useState<Map<number, { name: string; code: string }>>(new Map());
  const [classrooms, setClassrooms] = useState<Map<number, string>>(new Map());
  const [stats, setStats] = useState({
    total: 0,
    present: 0,
    late: 0,
    absent: 0,
  });

  useEffect(() => {
    loadAttendance();
  }, []);

  useEffect(() => {
    filterRecords();
  }, [searchTerm, attendanceRecords]);

  const loadAttendance = async () => {
    console.log('🔵 Attendance: loadAttendance called');
    setIsLoading(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      console.log('🔵 Attendance: Today date:', today);

      const [response, coursesData, classroomsData] = await Promise.all([
        attendanceApi.getAll({ start_date: today, limit: 100 }),
        courseApi.getAll(),
        classroomApi.getAll()
      ]);
      console.log('✅ Attendance: Data loaded - Records:', response.total, 'Courses:', coursesData.length, 'Classrooms:', classroomsData.length);

      // Crear mapas para cursos y aulas
      const courseMap = new Map<number, { name: string; code: string }>();
      coursesData.forEach(c => {
        courseMap.set(c.id, { name: c.name, code: c.code });
      });
      setCourses(courseMap);

      const classroomMap = new Map<number, string>();
      classroomsData.forEach(c => {
        classroomMap.set(c.id, c.name);
      });
      setClassrooms(classroomMap);

      // Cargar usuarios desde las asistencias (solo los que tienen asistencias)
      const userMap = new Map<number, { name: string; code: string }>();
      const uniqueUserIds = [...new Set(response.data.map(a => a.user_id))];

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
      console.log('✅ Attendance: Setting attendance records:', response.data.length);
      setAttendanceRecords(response.data);

      // Calculate stats
      const present = response.data.filter(r => r.status === 'present').length;
      const late = response.data.filter(r => r.status === 'late').length;
      const absent = response.data.filter(r => r.status === 'absent').length;

      const statsData = {
        total: response.total,
        present,
        late,
        absent,
      };
      console.log('✅ Attendance: Stats calculated:', statsData);
      setStats(statsData);
    } catch (error: any) {
      console.error('❌ Attendance: Error loading attendance:', error);
      toast.error('Error al cargar asistencias');
    } finally {
      console.log('🔵 Attendance: Loading finished');
      setIsLoading(false);
    }
  };

  const filterRecords = () => {
    if (!searchTerm) {
      setFilteredRecords(attendanceRecords);
      return;
    }

    const term = searchTerm.toLowerCase();
    const filtered = attendanceRecords.filter(
      (record) => {
        const studentName = users.get(record.user_id)?.name || '';
        const studentCode = users.get(record.user_id)?.code || '';
        const courseName = courses.get(record.course_id)?.name || '';
        const courseCode = courses.get(record.course_id)?.code || '';

        return (
          studentName.toLowerCase().includes(term) ||
          studentCode.toLowerCase().includes(term) ||
          courseName.toLowerCase().includes(term) ||
          courseCode.toLowerCase().includes(term)
        );
      }
    );
    setFilteredRecords(filtered);
  };


  const getStatusBadge = (status: string) => {
    const variants = {
      present: { label: 'Presente', className: 'bg-success/10 text-success hover:bg-success/20' },
      late: { label: 'Tarde', className: 'bg-warning/10 text-warning hover:bg-warning/20' },
      absent: { label: 'Ausente', className: 'bg-destructive/10 text-destructive hover:bg-destructive/20' },
      excused: { label: 'Justificado', className: 'bg-blue-500/10 text-blue-500 hover:bg-blue-500/20' },
    };
    const variant = variants[status as keyof typeof variants];
    return <Badge className={variant.className}>{variant.label}</Badge>;
  };

  const getSourceBadge = (source: string) => {
    const variants = {
      gps_auto: { label: 'GPS Auto', className: 'bg-primary/10 text-primary' },
      manual: { label: 'Manual', className: 'bg-muted text-muted-foreground' },
      qr_code: { label: 'QR Code', className: 'bg-accent/10 text-accent' },
    };
    const variant = variants[source as keyof typeof variants];
    return <Badge variant="outline" className={variant.className}>{variant.label}</Badge>;
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Asistencias</h1>
            <p className="text-muted-foreground">
              Monitoreo en tiempo real de registros de asistencia
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="gap-2" onClick={loadAttendance} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              Actualizar
            </Button>
            <Button variant="outline" className="gap-2">
              <Download className="h-4 w-4" />
              Exportar
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Buscar por estudiante o curso..."
                  className="pl-10"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button variant="outline" className="gap-2">
                <Filter className="h-4 w-4" />
                Filtros
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Hoy</CardDescription>
              <CardTitle className="text-3xl">{stats.total}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Presentes</CardDescription>
              <CardTitle className="text-3xl text-success">{stats.present}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Tardanzas</CardDescription>
              <CardTitle className="text-3xl text-warning">{stats.late}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Ausentes</CardDescription>
              <CardTitle className="text-3xl text-destructive">{stats.absent}</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        )}

        {/* Empty State */}
        {!isLoading && filteredRecords.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">
                {searchTerm ? 'No se encontraron registros de asistencia' : 'No hay registros de asistencia hoy'}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Records Table */}
        {!isLoading && filteredRecords.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Registros de Asistencia</CardTitle>
              <CardDescription>
                Mostrando {filteredRecords.length} de {attendanceRecords.length} registros de hoy
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Fecha/Hora
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Estudiante
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Curso
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Estado
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Fuente
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Distancia
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Aula
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {filteredRecords.map((record) => (
                      <tr key={record.id} className="hover:bg-muted/50 transition-colors">
                        <td className="py-3 text-sm">
                          <div>
                            <div className="font-medium">
                              {new Date(record.timestamp).toLocaleDateString('es-ES')}
                            </div>
                            <div className="text-muted-foreground">
                              {new Date(record.timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
                            </div>
                          </div>
                        </td>
                        <td className="py-3 text-sm">
                          <div>
                            <div className="font-medium">{users.get(record.user_id)?.name || 'N/A'}</div>
                            <div className="text-muted-foreground">{users.get(record.user_id)?.code || `ID: ${record.user_id}`}</div>
                          </div>
                        </td>
                        <td className="py-3 text-sm">
                          <div>
                            <div className="font-medium">{courses.get(record.course_id)?.name || 'N/A'}</div>
                            <div className="text-muted-foreground">{courses.get(record.course_id)?.code || `ID: ${record.course_id}`}</div>
                          </div>
                        </td>
                        <td className="py-3">{getStatusBadge(record.status)}</td>
                        <td className="py-3">{getSourceBadge(record.source)}</td>
                        <td className="py-3 text-sm text-muted-foreground">
                          {record.distance_to_classroom ? `${parseFloat(String(record.distance_to_classroom)).toFixed(1)}m` : 'N/A'}
                        </td>
                        <td className="py-3 text-sm text-muted-foreground">
                          {record.classroom_id ? (classrooms.get(record.classroom_id) || `Aula ${record.classroom_id}`) : 'N/A'}
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
