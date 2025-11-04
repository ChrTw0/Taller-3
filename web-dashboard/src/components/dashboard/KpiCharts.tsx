import { useEffect, useState } from 'react';
import { userApi, courseApi, enrollmentApi } from '@/services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

const COLORS = {
  active: '#22c55e',
  dropped: '#ef4444',
  completed: '#3b82f6',
  admin: '#8b5cf6',
  teacher: '#3b82f6',
  student: '#22c55e',
};

export function KpiCharts() {
  const [userData, setUserData] = useState<any[]>([]);
  const [enrollmentData, setEnrollmentData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [users, courses] = await Promise.all([
          userApi.getAll(),
          courseApi.getAll(),
        ]);

        // User role distribution
        const rolesCount = users.reduce((acc, user) => {
          acc[user.role] = (acc[user.role] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);

        const userChartData = [
          { name: 'Admin', count: rolesCount.admin || 0, fill: COLORS.admin },
          { name: 'Profesores', count: rolesCount.teacher || 0, fill: COLORS.teacher },
          { name: 'Estudiantes', count: rolesCount.student || 0, fill: COLORS.student },
        ];
        setUserData(userChartData);

        // Enrollment status distribution
        const enrollmentPromises = courses.map(course => enrollmentApi.getByCourse(course.id).catch(() => []));
        const enrollmentsByCourse = await Promise.all(enrollmentPromises);
        const allEnrollments = enrollmentsByCourse.flat().filter(e => e);

        const statusCount = allEnrollments.reduce((acc, enrollment) => {
          acc[enrollment.status] = (acc[enrollment.status] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);

        const enrollmentChartData = [
          { name: 'Activas', value: statusCount.active || 0 },
          { name: 'Retirados', value: statusCount.dropped || 0 },
          { name: 'Completadas', value: statusCount.completed || 0 },
        ];
        setEnrollmentData(enrollmentChartData);

      } catch (error) {
        console.error("Error fetching chart data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="flex justify-center items-center p-8"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Distribución de Usuarios por Rol</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={userData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" name="Cantidad" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Estado de las Inscripciones</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={enrollmentData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                {enrollmentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.name.toLowerCase() as keyof typeof COLORS]} />
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

export default KpiCharts;