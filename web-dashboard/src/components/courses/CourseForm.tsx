import { useState, useEffect } from 'react';
import { courseApi, userApi, scheduleApi } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
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
import { ScheduleManager } from './ScheduleManager';
import { ClassroomSelector } from './ClassroomSelector';
import type { Course, CreateCourseData, UpdateCourseData, Schedule } from '@/types/course';
import type { User } from '@/types/auth';

interface CourseFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  course?: Course;
  onSuccess: () => void;
}

export function CourseForm({ open, onOpenChange, course, onSuccess }: CourseFormProps) {
  const isEdit = !!course;
  const [isLoading, setIsLoading] = useState(false);
  const [teachers, setTeachers] = useState<User[]>([]);
  const [schedules, setSchedules] = useState<Omit<Schedule, 'id' | 'course_id' | 'created_at'>[]>([]);
  const [selectedClassroomIds, setSelectedClassroomIds] = useState<number[]>([]);

  const [formData, setFormData] = useState<CreateCourseData>({
    code: '',
    name: '',
    description: '',
    year: new Date().getFullYear().toString(),
    semester: 'A',
    teacher_id: 0,
    teacher_code: '',
    max_students: 30,
    gps_radius: 50,
  });

  useEffect(() => {
    loadTeachers();
  }, []);

  useEffect(() => {
    if (course) {
      // For edit mode, we need to get the teacher's code
      const teacher = teachers.find(t => t.id === course.teacher_id.toString());
      setFormData({
        code: course.code,
        name: course.name,
        description: course.description || '',
        year: course.year,
        semester: course.semester,
        teacher_id: course.teacher_id,
        teacher_code: teacher?.code || '',
        max_students: course.max_students,
        gps_radius: course.gps_radius,
      });
      // Load existing schedules for edit mode
      loadSchedules(course.id);
    } else {
      setFormData({
        code: '',
        name: '',
        description: '',
        year: new Date().getFullYear().toString(),
        semester: 'A',
        teacher_id: 0,
        teacher_code: '',
        max_students: 30,
        gps_radius: 50,
      });
      setSchedules([]);
      setSelectedClassroomIds([]);
    }
  }, [course, open, teachers]);

  const loadTeachers = async () => {
    try {
      const teacherUsers = await userApi.getTeachers();
      setTeachers(teacherUsers);
    } catch (error) {
      console.error('Error loading teachers:', error);
    }
  };

  const loadSchedules = async (courseId: number) => {
    try {
      const existingSchedules = await scheduleApi.getByCourse(courseId);
      setSchedules(existingSchedules.map(s => ({
        day_of_week: s.day_of_week,
        start_time: s.start_time,
        end_time: s.end_time,
        classroom_id: s.classroom_id,
        is_active: s.is_active,
      })));

      // Extract unique classroom IDs from schedules
      const classroomIds = existingSchedules
        .map(s => s.classroom_id)
        .filter((id): id is number => id !== null && id !== undefined);
      const uniqueClassroomIds = Array.from(new Set(classroomIds));
      setSelectedClassroomIds(uniqueClassroomIds);
    } catch (error) {
      console.error('Error loading schedules:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.code || !formData.name || !formData.teacher_id) {
      toast.error('Por favor completa todos los campos obligatorios');
      return;
    }

    if (formData.max_students < 1) {
      toast.error('El máximo de estudiantes debe ser al menos 1');
      return;
    }

    if (formData.gps_radius < 1) {
      toast.error('El radio GPS debe ser al menos 1 metro');
      return;
    }

    if (schedules.length === 0) {
      toast.error('Debes agregar al menos un horario para el curso');
      return;
    }

    setIsLoading(true);
    try {
      if (isEdit && course) {
        // Update course data
        await courseApi.update(course.id, formData as UpdateCourseData);

        // Delete all existing schedules
        const existingSchedules = await scheduleApi.getByCourse(course.id);
        for (const schedule of existingSchedules) {
          try {
            await scheduleApi.delete(schedule.id);
          } catch (error) {
            console.error('Error deleting schedule:', error);
          }
        }

        // Create all new schedules
        for (const schedule of schedules) {
          try {
            await scheduleApi.create(course.id, schedule);
          } catch (error) {
            console.error('Error creating schedule:', error);
          }
        }

        toast.success(`Curso actualizado exitosamente con ${schedules.length} horario(s)`);
      } else {
        // Create course first
        const response = await courseApi.create(formData);
        const newCourseId = response.data.id;

        // Then create all schedules for the new course
        for (const schedule of schedules) {
          try {
            await scheduleApi.create(newCourseId, schedule);
          } catch (error) {
            console.error('Error creating schedule:', error);
          }
        }

        toast.success(`Curso creado exitosamente con ${schedules.length} horario(s)`);
      }
      onSuccess();
      onOpenChange(false);
    } catch (error: any) {
      console.error('Course form error:', error);
      toast.error(error.response?.data?.detail || `Error al ${isEdit ? 'actualizar' : 'crear'} curso`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Editar Curso' : 'Crear Nuevo Curso'}</DialogTitle>
          <DialogDescription>
            {isEdit ? (
              <>
                Modifica los datos del curso.
                <span className="block mt-1 text-amber-600 dark:text-amber-500">
                  ⚠️ Nota: El código, profesor, año y semestre no se pueden cambiar
                </span>
              </>
            ) : (
              'Completa los datos para crear un nuevo curso'
            )}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="code" className={isEdit ? "text-muted-foreground" : ""}>
                Código * {isEdit && <span className="text-xs">(no editable)</span>}
              </Label>
              <Input
                id="code"
                placeholder="CS101"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                disabled={isEdit || isLoading}
                maxLength={20}
                className={isEdit ? "bg-muted cursor-not-allowed" : ""}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="teacher" className={isEdit ? "text-muted-foreground" : ""}>
                Profesor * {isEdit && <span className="text-xs">(no editable)</span>}
              </Label>
              <Select
                value={formData.teacher_id > 0 ? formData.teacher_id.toString() : undefined}
                onValueChange={(value) => {
                  const selectedTeacher = teachers.find(t => t.id.toString() === value);
                  setFormData({
                    ...formData,
                    teacher_id: parseInt(value),
                    teacher_code: selectedTeacher?.code || ''
                  });
                }}
                disabled={isEdit || isLoading}
              >
                <SelectTrigger className={isEdit ? "bg-muted cursor-not-allowed" : ""}>
                  <SelectValue placeholder="Seleccionar profesor" />
                </SelectTrigger>
                <SelectContent>
                  {teachers.map((teacher) => (
                    <SelectItem key={teacher.id} value={teacher.id.toString()}>
                      {teacher.first_name} {teacher.last_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Nombre del Curso * {isEdit && <span className="text-xs text-green-600">(editable)</span>}</Label>
            <Input
              id="name"
              placeholder="Introducción a la Programación"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              disabled={isLoading}
              maxLength={200}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Descripción {isEdit && <span className="text-xs text-green-600">(editable)</span>}</Label>
            <Textarea
              id="description"
              placeholder="Descripción del curso..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              disabled={isLoading}
              rows={3}
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="year" className={isEdit ? "text-muted-foreground" : ""}>
                Año * {isEdit && <span className="text-xs">(no editable)</span>}
              </Label>
              <Input
                id="year"
                type="number"
                placeholder="2025"
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                disabled={isEdit || isLoading}
                min="2020"
                max="2100"
                className={isEdit ? "bg-muted cursor-not-allowed" : ""}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="semester" className={isEdit ? "text-muted-foreground" : ""}>
                Semestre * {isEdit && <span className="text-xs">(no editable)</span>}
              </Label>
              <Select
                value={formData.semester}
                onValueChange={(value) => setFormData({ ...formData, semester: value })}
                disabled={isEdit || isLoading}
              >
                <SelectTrigger className={isEdit ? "bg-muted cursor-not-allowed" : ""}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="A">A</SelectItem>
                  <SelectItem value="B">B</SelectItem>
                  <SelectItem value="Summer">Verano</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="max_students">Máx. Estudiantes * {isEdit && <span className="text-xs text-green-600">(editable)</span>}</Label>
              <Input
                id="max_students"
                type="number"
                placeholder="30"
                value={formData.max_students}
                onChange={(e) => setFormData({ ...formData, max_students: parseInt(e.target.value) || 0 })}
                disabled={isLoading}
                min="1"
                max="200"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="gps_radius">Radio GPS (metros) * {isEdit && <span className="text-xs text-green-600">(editable)</span>}</Label>
            <Input
              id="gps_radius"
              type="number"
              placeholder="2.5"
              value={formData.gps_radius}
              onChange={(e) => setFormData({ ...formData, gps_radius: parseFloat(e.target.value) || 0 })}
              disabled={isLoading}
              min="1"
              max="10"
              step="0.1"
            />
            <p className="text-xs text-muted-foreground">
              Radio de tolerancia para el registro de asistencia por GPS (1-10 metros)
            </p>
          </div>

          {/* Classroom Selector */}
          <div className="border-t pt-4">
            <ClassroomSelector
              selectedClassroomIds={selectedClassroomIds}
              onChange={setSelectedClassroomIds}
              disabled={isLoading}
            />
            <p className="text-xs text-muted-foreground mt-2">
              {isEdit
                ? 'Aulas actualmente vinculadas a través de los horarios del curso'
                : 'Las aulas seleccionadas estarán disponibles para asignar en los horarios del curso'
              }
            </p>
          </div>

          {/* Schedule Manager */}
          <div className="border-t pt-4">
            <ScheduleManager
              schedules={schedules}
              onChange={setSchedules}
              disabled={isLoading}
            />
            {isEdit && (
              <p className="text-xs text-amber-600 dark:text-amber-500 mt-2">
                ⚠️ Los cambios en horarios requieren eliminar y recrear. Use con precaución.
              </p>
            )}
          </div>

          <div className="flex gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              Cancelar
            </Button>
            <Button type="submit" className="flex-1" disabled={isLoading}>
              {isLoading ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                  {isEdit ? 'Actualizando...' : 'Creando...'}
                </>
              ) : (
                isEdit ? 'Actualizar Curso' : 'Crear Curso'
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
