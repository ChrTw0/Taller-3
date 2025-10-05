import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { enrollmentApi, courseApi, userApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { toast } from 'sonner';
import { UserPlus, Search, Trash2, BookOpen, Users as UsersIcon } from 'lucide-react';
import type { Enrollment, EnrollmentStatus } from '@/types/enrollment';
import type { Course } from '@/types/course';
import type { User } from '@/types/auth';

export default function Enrollments() {
  const { user } = useAuth();
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [filteredEnrollments, setFilteredEnrollments] = useState<Enrollment[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [students, setStudents] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedCourseFilter, setSelectedCourseFilter] = useState<string>('all');

  const [formData, setFormData] = useState({
    student_id: 0,
    course_id: 0,
  });

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    filterEnrollments();
  }, [searchTerm, selectedCourseFilter, enrollments]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [enrollmentsData, coursesData, usersData] = await Promise.all([
        enrollmentApi.getAll(),
        courseApi.getAll(),
        userApi.getAll(),
      ]);

      setEnrollments(enrollmentsData);
      setCourses(coursesData);
      setStudents(usersData.filter(u => u.role === 'student'));
    } catch (error: any) {
      console.error('Error loading data:', error);
      toast.error('Error al cargar datos');
    } finally {
      setIsLoading(false);
    }
  };

  const filterEnrollments = () => {
    let filtered = enrollments;

    // Filter by course
    if (selectedCourseFilter !== 'all') {
      filtered = filtered.filter(e => e.course_id === parseInt(selectedCourseFilter));
    }

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (enrollment) =>
          enrollment.student_name?.toLowerCase().includes(term) ||
          enrollment.student_code?.toLowerCase().includes(term) ||
          enrollment.course_name?.toLowerCase().includes(term) ||
          enrollment.course_code?.toLowerCase().includes(term)
      );
    }

    setFilteredEnrollments(filtered);
  };

  const handleCreateEnrollment = () => {
    setFormData({ student_id: 0, course_id: 0 });
    setIsFormOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.student_id || !formData.course_id) {
      toast.error('Por favor selecciona un estudiante y un curso');
      return;
    }

    // Check if enrollment already exists
    const existingEnrollment = enrollments.find(
      e => e.student_id === formData.student_id &&
           e.course_id === formData.course_id &&
           e.status === 'active'
    );

    if (existingEnrollment) {
      toast.error('El estudiante ya está inscrito en este curso');
      return;
    }

    setIsSubmitting(true);
    try {
      await enrollmentApi.create(formData);
      toast.success('Estudiante inscrito exitosamente');
      setIsFormOpen(false);
      loadData();
    } catch (error: any) {
      console.error('Enrollment error:', error);
      toast.error(error.response?.data?.detail || 'Error al inscribir estudiante');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDropEnrollment = async (enrollment: Enrollment) => {
    if (!confirm(`¿Estás seguro de dar de baja a ${enrollment.student_name} del curso ${enrollment.course_name}?`)) {
      return;
    }

    try {
      await enrollmentApi.update(enrollment.id, { status: 'dropped' });
      toast.success('Estudiante dado de baja exitosamente');
      loadData();
    } catch (error: any) {
      console.error('Error dropping enrollment:', error);
      toast.error(error.response?.data?.detail || 'Error al dar de baja');
    }
  };

  const handleDeleteEnrollment = async (enrollment: Enrollment) => {
    if (!confirm(`¿Estás seguro de eliminar esta inscripción?`)) {
      return;
    }

    try {
      await enrollmentApi.delete(enrollment.id);
      toast.success('Inscripción eliminada exitosamente');
      loadData();
    } catch (error: any) {
      console.error('Error deleting enrollment:', error);
      toast.error(error.response?.data?.detail || 'Error al eliminar inscripción');
    }
  };

  const getStatusBadge = (status: EnrollmentStatus) => {
    const variants = {
      active: { label: 'Activo', className: 'bg-success/10 text-success' },
      dropped: { label: 'Retirado', className: 'bg-destructive/10 text-destructive' },
      completed: { label: 'Completado', className: 'bg-blue-500/10 text-blue-500' },
    };
    const variant = variants[status];
    return <Badge className={variant.className}>{variant.label}</Badge>;
  };

  const stats = {
    total: enrollments.length,
    active: enrollments.filter(e => e.status === 'active').length,
    dropped: enrollments.filter(e => e.status === 'dropped').length,
    completed: enrollments.filter(e => e.status === 'completed').length,
  };

  if (user?.role !== 'admin') {
    return (
      <DashboardLayout>
        <div className="flex h-96 items-center justify-center">
          <p className="text-muted-foreground">No tienes permisos para acceder a esta página</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Inscripciones</h1>
            <p className="text-muted-foreground">Gestiona las inscripciones de estudiantes a cursos</p>
          </div>
          <Button className="gap-2" onClick={handleCreateEnrollment}>
            <UserPlus className="h-4 w-4" />
            Inscribir Estudiante
          </Button>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total</CardDescription>
              <CardTitle className="text-3xl">{stats.total}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Activos</CardDescription>
              <CardTitle className="text-3xl text-success">{stats.active}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Retirados</CardDescription>
              <CardTitle className="text-3xl text-destructive">{stats.dropped}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Completados</CardDescription>
              <CardTitle className="text-3xl text-blue-500">{stats.completed}</CardTitle>
            </CardHeader>
          </Card>
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
              <Select value={selectedCourseFilter} onValueChange={setSelectedCourseFilter}>
                <SelectTrigger className="w-[250px]">
                  <SelectValue placeholder="Filtrar por curso" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los cursos</SelectItem>
                  {courses.map((course) => (
                    <SelectItem key={course.id} value={course.id.toString()}>
                      {course.code} - {course.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        )}

        {/* Empty State */}
        {!isLoading && filteredEnrollments.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">
                {searchTerm || selectedCourseFilter !== 'all'
                  ? 'No se encontraron inscripciones'
                  : 'No hay inscripciones registradas'}
              </p>
              {!searchTerm && selectedCourseFilter === 'all' && (
                <Button className="mt-4" onClick={handleCreateEnrollment}>
                  <UserPlus className="mr-2 h-4 w-4" />
                  Inscribir Primer Estudiante
                </Button>
              )}
            </CardContent>
          </Card>
        )}

        {/* Enrollments Table */}
        {!isLoading && filteredEnrollments.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Inscripciones Registradas</CardTitle>
              <CardDescription>
                Mostrando {filteredEnrollments.length} de {enrollments.length} inscripciones
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
                        Estado
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Fecha Inscripción
                      </th>
                      <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {filteredEnrollments.map((enrollment) => (
                      <tr key={enrollment.id} className="hover:bg-muted/50 transition-colors">
                        <td className="py-3 text-sm">
                          <div>
                            <div className="font-medium">{enrollment.student_name || 'N/A'}</div>
                            <div className="text-muted-foreground">{enrollment.student_code || `ID: ${enrollment.student_id}`}</div>
                          </div>
                        </td>
                        <td className="py-3 text-sm">
                          <div>
                            <div className="font-medium">{enrollment.course_name || 'N/A'}</div>
                            <div className="text-muted-foreground">{enrollment.course_code || `ID: ${enrollment.course_id}`}</div>
                          </div>
                        </td>
                        <td className="py-3">{getStatusBadge(enrollment.status)}</td>
                        <td className="py-3 text-sm text-muted-foreground">
                          {new Date(enrollment.enrolled_at).toLocaleDateString('es-ES')}
                        </td>
                        <td className="py-3">
                          <div className="flex gap-2">
                            {enrollment.status === 'active' && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDropEnrollment(enrollment)}
                                className="text-warning hover:text-warning"
                              >
                                Dar de Baja
                              </Button>
                            )}
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteEnrollment(enrollment)}
                              className="text-destructive hover:text-destructive"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Enrollment Form Dialog */}
        <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Inscribir Estudiante</DialogTitle>
              <DialogDescription>
                Selecciona un estudiante y un curso para crear la inscripción
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="student">Estudiante *</Label>
                <Select
                  value={formData.student_id.toString()}
                  onValueChange={(value) => setFormData({ ...formData, student_id: parseInt(value) })}
                  disabled={isSubmitting}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar estudiante" />
                  </SelectTrigger>
                  <SelectContent>
                    {students.map((student) => (
                      <SelectItem key={student.id} value={student.id.toString()}>
                        {student.code} - {student.first_name} {student.last_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="course">Curso *</Label>
                <Select
                  value={formData.course_id.toString()}
                  onValueChange={(value) => setFormData({ ...formData, course_id: parseInt(value) })}
                  disabled={isSubmitting}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar curso" />
                  </SelectTrigger>
                  <SelectContent>
                    {courses.filter(c => c.is_active).map((course) => (
                      <SelectItem key={course.id} value={course.id.toString()}>
                        {course.code} - {course.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex gap-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => setIsFormOpen(false)}
                  disabled={isSubmitting}
                >
                  Cancelar
                </Button>
                <Button type="submit" className="flex-1" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                      Inscribiendo...
                    </>
                  ) : (
                    'Inscribir Estudiante'
                  )}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
