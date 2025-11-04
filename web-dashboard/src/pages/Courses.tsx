import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { CourseForm } from '@/components/courses/CourseForm';
import { courseApi, enrollmentApi, userApi } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Plus, Search, Users, MapPin, Edit, Trash2, Eye } from 'lucide-react';
import type { Course } from '@/types/course';

export default function Courses() {
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [filteredCourses, setFilteredCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<Course | undefined>();
  const [teachers, setTeachers] = useState<Map<number, string>>(new Map());

  const canManageCourses = user?.role === 'admin' || user?.role === 'teacher';
  const isStudent = user?.role === 'student';

  useEffect(() => {
    if (user) {
      loadCourses();
    }
  }, [user?.id]);

  useEffect(() => {
    filterCourses();
  }, [searchTerm, courses]);

  const loadCourses = async () => {
    console.log('🔵 Courses: loadCourses called', { user });
    setIsLoading(true);
    try {
      let coursesData;

      // Cargar cursos según el rol
      if (user?.role === 'student') {
        console.log('🔵 Courses: Loading student courses');
        // Estudiantes: obtener solo los cursos en los que están matriculados
        const enrollments = await enrollmentApi.getByStudent(Number(user.id));
        console.log('✅ Courses: Enrollments loaded:', enrollments.length);
        const allCourses = await courseApi.getAll();
        console.log('✅ Courses: All courses loaded:', allCourses.length);
        const enrolledCourseIds = enrollments
          .filter(e => e.status === 'active')
          .map(e => e.course_id);
        console.log('✅ Courses: Enrolled course IDs:', enrolledCourseIds);
        coursesData = allCourses.filter(c => enrolledCourseIds.includes(c.id));
        console.log('✅ Courses: Filtered student courses:', coursesData.length);

        // Para estudiantes, obtener nombres de profesores de los cursos
        const uniqueTeacherIds = [...new Set(coursesData.map(c => c.teacher_id))];
        const teacherMap = new Map<number, string>();

        // Cargar cada profesor individualmente
        console.log('🔵 Courses: Loading teachers for students:', uniqueTeacherIds);
        for (const teacherId of uniqueTeacherIds) {
          try {
            const teacher = await userApi.getById(teacherId.toString());
            teacherMap.set(Number(teacher.id), `${teacher.first_name} ${teacher.last_name}`);
            console.log('✅ Courses: Teacher loaded:', teacher.id, teacher.first_name);
          } catch (error) {
            console.error(`❌ Courses: Could not load teacher ${teacherId}`, error);
          }
        }
        console.log('✅ Courses: All student teachers loaded:', teacherMap.size);
        setTeachers(teacherMap);
      } else if (user?.role === 'teacher') {
        console.log('🔵 Courses: Loading teacher courses');
        // Profesores: solo sus cursos
        const allCourses = await courseApi.getAll();
        console.log('✅ Courses: All courses loaded:', allCourses.length);
        coursesData = allCourses.filter(course => course.teacher_id === Number(user.id));
        console.log('✅ Courses: Filtered teacher courses:', coursesData.length);

        // Cargar su propio nombre
        const teacherMap = new Map<number, string>();
        teacherMap.set(Number(user.id), `${user.first_name} ${user.last_name}`);
        setTeachers(teacherMap);
      } else {
        console.log('🔵 Courses: Loading admin courses');
        // Admin: todos los cursos
        coursesData = await courseApi.getAll();
        console.log('✅ Courses: All courses loaded:', coursesData.length);

        // Obtener IDs únicos de profesores
        const uniqueTeacherIds = [...new Set(coursesData.map(c => c.teacher_id))];
        const teacherMap = new Map<number, string>();

        // Cargar cada profesor individualmente
        for (const teacherId of uniqueTeacherIds) {
          try {
            const teacher = await userApi.getById(teacherId.toString());
            teacherMap.set(Number(teacher.id), `${teacher.first_name} ${teacher.last_name}`);
          } catch (error) {
            console.warn(`Could not load teacher ${teacherId}`);
          }
        }
        setTeachers(teacherMap);
      }

      console.log('✅ Courses: Setting courses state:', coursesData.length);
      setCourses(coursesData);
    } catch (error: any) {
      console.error('❌ Courses: Error loading courses:', error);
      toast.error('Error al cargar cursos');
    } finally {
      console.log('🔵 Courses: Loading finished');
      setIsLoading(false);
    }
  };

  const filterCourses = () => {
    if (!searchTerm) {
      setFilteredCourses(courses);
      return;
    }

    const term = searchTerm.toLowerCase();
    const filtered = courses.filter(
      (course) => {
        const teacherName = teachers.get(course.teacher_id) || '';
        return (
          course.code.toLowerCase().includes(term) ||
          course.name.toLowerCase().includes(term) ||
          teacherName.toLowerCase().includes(term)
        );
      }
    );
    setFilteredCourses(filtered);
  };

  const handleCreateCourse = () => {
    setSelectedCourse(undefined);
    setIsFormOpen(true);
  };

  const handleEditCourse = (course: Course) => {
    setSelectedCourse(course);
    setIsFormOpen(true);
  };

  const handleDeleteCourse = async (course: Course) => {
    if (!confirm(`¿Estás seguro de eliminar el curso "${course.name}"?`)) {
      return;
    }

    try {
      await courseApi.delete(course.id);
      toast.success('Curso eliminado exitosamente');
      loadCourses();
    } catch (error: any) {
      console.error('Error deleting course:', error);
      toast.error(error.response?.data?.detail || 'Error al eliminar curso');
    }
  };

  const handleFormSuccess = () => {
    loadCourses();
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Cursos</h1>
            <p className="text-muted-foreground">
              {user?.role === 'admin'
                ? 'Gestiona todos los cursos del sistema'
                : user?.role === 'teacher'
                ? 'Gestiona tus cursos asignados'
                : 'Mis cursos matriculados'}
            </p>
          </div>
          {user?.role === 'admin' && (
            <Button className="gap-2" onClick={handleCreateCourse}>
              <Plus className="h-4 w-4" />
              Crear Curso
            </Button>
          )}
        </div>

        {/* Search */}
        <Card>
          <CardContent className="pt-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Buscar por código, nombre o profesor..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
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
        {!isLoading && filteredCourses.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">
                {searchTerm ? 'No se encontraron cursos' : 'No hay cursos registrados'}
              </p>
              {!searchTerm && user?.role === 'admin' && (
                <Button className="mt-4" onClick={handleCreateCourse}>
                  <Plus className="mr-2 h-4 w-4" />
                  Crear Primer Curso
                </Button>
              )}
              {!searchTerm && user?.role === 'student' && (
                <p className="text-sm text-muted-foreground mt-2">
                  No estás matriculado en ningún curso aún.
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Courses Grid */}
        {!isLoading && filteredCourses.length > 0 && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredCourses.map((course) => (
              <Card
                key={course.id}
                className="overflow-hidden transition-all hover:shadow-md"
              >
                <CardHeader className="bg-primary/5 border-b border-border">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <Badge variant="outline" className="mb-2">
                        {course.code}
                      </Badge>
                      <CardTitle className="text-lg line-clamp-2">{course.name}</CardTitle>
                      <CardDescription className="mt-1">
                        {teachers.get(course.teacher_id) || `Profesor ID: ${course.teacher_id}`}
                      </CardDescription>
                    </div>
                    <Badge className={course.is_active ? 'bg-success' : 'bg-muted'}>
                      {course.is_active ? 'Activo' : 'Inactivo'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Período:</span>
                      <span className="font-medium">
                        {course.year} - Sem. {course.semester}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Users className="h-4 w-4" />
                        <span>Estudiantes:</span>
                      </div>
                      <span className="font-medium">
                        {course.enrollment_count || 0}/{course.max_students}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <MapPin className="h-4 w-4" />
                        <span>Radio GPS:</span>
                      </div>
                      <span className="font-medium">{course.gps_radius}m</span>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-border flex gap-2">
                    {user?.role === 'student' ? (
                      <Button variant="outline" className="flex-1" size="sm">
                        <Eye className="mr-1 h-3 w-3" />
                        Ver Detalles
                      </Button>
                    ) : (
                      <>
                        <Button variant="outline" className="flex-1" size="sm">
                          <Eye className="mr-1 h-3 w-3" />
                          Ver
                        </Button>
                        {user?.role === 'admin' && (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEditCourse(course)}
                            >
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteCourse(course)}
                              className="text-destructive hover:text-destructive"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </>
                        )}
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Course Form Dialog */}
        <CourseForm
          open={isFormOpen}
          onOpenChange={setIsFormOpen}
          course={selectedCourse}
          onSuccess={handleFormSuccess}
        />
      </div>
    </DashboardLayout>
  );
}
