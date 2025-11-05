import { useEffect, useState } from 'react';
import { courseApi, attendanceApi } from '@/services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';
import type { Course } from '@/types/course';
import type { AttendanceRecord } from '@/types/attendance';

const COLORS = {
  present: '#22c55e',
  late: '#f59e0b',
  absent: '#ef4444',
};

interface TeacherChartsProps {
  teacherId: number;
}

export function TeacherCharts({ teacherId }: TeacherChartsProps) {
  const [attendanceByCourseData, setAttendanceByCourseData] = useState<any[]>([]);
  const [attendanceStatusData, setAttendanceStatusData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const allCourses = await courseApi.getAll();
        const teacherCourses = allCourses.filter(c => c.teacher_id === teacherId);
        const teacherCourseIds = teacherCourses.map(c => c.id);

        if (teacherCourseIds.length === 0) {
          setLoading(false);
          return;
        }

        const attendancePromises = teacherCourseIds.map(courseId =>
          attendanceApi.getAll({ course_id: courseId, limit: 1000 })
        );
        const attendanceResponses = await Promise.all(attendancePromises);
        const allTeacherAttendance = attendanceResponses.flatMap(res => res.data);

        // 1. Attendance status distribution (Pie Chart)
        const statusCount = allTeacherAttendance.reduce((acc, record) => {
          const status = record.status === 'present' || record.status === 'late' ? 'present' : record.status;
          acc[status] = (acc[status] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);

        const statusChartData = [
          { name: 'Presentes', value: (statusCount.present || 0) + (statusCount.late || 0), fill: COLORS.present },
          { name: 'Tardanzas', value: statusCount.late || 0, fill: COLORS.late },
          { name: 'Ausentes', value: statusCount.absent || 0, fill: COLORS.absent },
        ].filter(d => d.value > 0);
        setAttendanceStatusData(statusChartData);

        // 2. Attendance rate by course (Bar Chart)
        const courseStats = teacherCourses.map(course => {
          const courseAttendance = allTeacherAttendance.filter(a => a.course_id === course.id);
          const total = courseAttendance.length;
          const present = courseAttendance.filter(a => a.status === 'present' || a.status === 'late').length;
          const rate = total > 0 ? (present / total) * 100 : 0;
          return {
            name: course.code,
            'Tasa de Asistencia': parseFloat(rate.toFixed(1)),
          };
        });
        setAttendanceByCourseData(courseStats);

      } catch (error) {
        console.error("Error fetching teacher chart data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [teacherId]);

  if (loading) {
    return <div className="flex justify-center items-center p-8"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  }

  if (attendanceByCourseData.length === 0 && attendanceStatusData.length === 0) {
    return null; // No mostrar nada si no hay datos
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 mt-6">
      <Card>
        <CardHeader>
          <CardTitle>Tasa de Asistencia por Curso (%)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={attendanceByCourseData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="Tasa de Asistencia" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Distribución de Asistencias</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={attendanceStatusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                {attendanceStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}