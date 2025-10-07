import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Plus, Trash2, Clock, Building2 } from 'lucide-react';
import { classroomApi } from '@/services/api';
import type { Schedule } from '@/types/course';
import type { Classroom } from '@/types/classroom';

interface ScheduleManagerProps {
  schedules: Omit<Schedule, 'id' | 'course_id' | 'created_at'>[];
  onChange: (schedules: Omit<Schedule, 'id' | 'course_id' | 'created_at'>[]) => void;
  disabled?: boolean;
}

const DAYS = [
  { value: 0, label: 'Lunes' },
  { value: 1, label: 'Martes' },
  { value: 2, label: 'Miércoles' },
  { value: 3, label: 'Jueves' },
  { value: 4, label: 'Viernes' },
  { value: 5, label: 'Sábado' },
  { value: 6, label: 'Domingo' },
];

export function ScheduleManager({ schedules, onChange, disabled = false }: ScheduleManagerProps) {
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [newSchedule, setNewSchedule] = useState<Omit<Schedule, 'id' | 'course_id' | 'created_at'>>({
    day_of_week: 0,
    start_time: '08:00:00',
    end_time: '10:00:00',
    classroom_id: null,
    is_active: true,
  });

  useEffect(() => {
    loadClassrooms();
  }, []);

  const loadClassrooms = async () => {
    try {
      const data = await classroomApi.getAll();
      setClassrooms(data.filter(c => c.is_active));
    } catch (error) {
      console.error('Error loading classrooms:', error);
    }
  };

  const handleAddSchedule = () => {
    // Validar que la hora de inicio sea antes que la hora de fin
    if (newSchedule.start_time >= newSchedule.end_time) {
      alert('La hora de inicio debe ser anterior a la hora de fin');
      return;
    }

    // Verificar que no haya duplicados
    const isDuplicate = schedules.some(
      s => s.day_of_week === newSchedule.day_of_week &&
           s.start_time === newSchedule.start_time &&
           s.end_time === newSchedule.end_time
    );

    if (isDuplicate) {
      alert('Este horario ya existe');
      return;
    }

    onChange([...schedules, { ...newSchedule }]);
  };

  const handleRemoveSchedule = (index: number) => {
    onChange(schedules.filter((_, i) => i !== index));
  };

  const formatTime = (time: string): string => {
    // "18:00:00" -> "18:00" or "6:00 PM"
    const [hours, minutes] = time.split(':');
    return `${hours}:${minutes}`;
  };

  const getDayLabel = (dayOfWeek: number): string => {
    return DAYS.find(d => d.value === dayOfWeek)?.label || '';
  };

  const getClassroomLabel = (classroomId: number | null | undefined): string => {
    if (!classroomId) return 'Sin aula asignada';
    const classroom = classrooms.find(c => c.id === classroomId);
    if (!classroom) return 'Aula no encontrada';
    return `${classroom.building} - ${classroom.room_number}`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Label className="text-base">Horarios del Curso</Label>
        <Badge variant="outline">
          {schedules.length} horario{schedules.length !== 1 ? 's' : ''}
        </Badge>
      </div>

      {/* Existing Schedules */}
      {schedules.length > 0 && (
        <div className="space-y-2">
          {schedules.map((schedule, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 border rounded-lg bg-muted/30"
            >
              <div className="flex items-center gap-3 flex-1">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <div className="font-medium">
                    {getDayLabel(schedule.day_of_week)}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {formatTime(schedule.start_time)} - {formatTime(schedule.end_time)}
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                    <Building2 className="h-3 w-3" />
                    <span>{getClassroomLabel(schedule.classroom_id)}</span>
                  </div>
                </div>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => handleRemoveSchedule(index)}
                disabled={disabled}
                className="text-destructive hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* Add New Schedule */}
      <div className="border rounded-lg p-4 bg-muted/10">
        <Label className="text-sm mb-3 block">Agregar Horario</Label>
        <div className="grid grid-cols-2 gap-3 mb-3">
          <div className="space-y-2">
            <Label htmlFor="day" className="text-xs">Día</Label>
            <Select
              value={newSchedule.day_of_week.toString()}
              onValueChange={(value) =>
                setNewSchedule({ ...newSchedule, day_of_week: parseInt(value) })
              }
              disabled={disabled}
            >
              <SelectTrigger id="day">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {DAYS.map((day) => (
                  <SelectItem key={day.value} value={day.value.toString()}>
                    {day.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="classroom" className="text-xs">Aula</Label>
            <Select
              value={newSchedule.classroom_id?.toString() || 'none'}
              onValueChange={(value) =>
                setNewSchedule({
                  ...newSchedule,
                  classroom_id: value === 'none' ? null : parseInt(value)
                })
              }
              disabled={disabled}
            >
              <SelectTrigger id="classroom">
                <SelectValue placeholder="Seleccionar aula" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Sin aula asignada</SelectItem>
                {classrooms.map((classroom) => (
                  <SelectItem key={classroom.id} value={classroom.id.toString()}>
                    {classroom.building} - {classroom.room_number} ({classroom.name})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="start_time" className="text-xs">Hora Inicio</Label>
            <Input
              id="start_time"
              type="time"
              value={newSchedule.start_time.substring(0, 5)}
              onChange={(e) =>
                setNewSchedule({ ...newSchedule, start_time: `${e.target.value}:00` })
              }
              disabled={disabled}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="end_time" className="text-xs">Hora Fin</Label>
            <Input
              id="end_time"
              type="time"
              value={newSchedule.end_time.substring(0, 5)}
              onChange={(e) =>
                setNewSchedule({ ...newSchedule, end_time: `${e.target.value}:00` })
              }
              disabled={disabled}
            />
          </div>
        </div>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleAddSchedule}
          disabled={disabled}
          className="mt-3 w-full"
        >
          <Plus className="h-4 w-4 mr-2" />
          Agregar Horario
        </Button>
      </div>

      {schedules.length === 0 && (
        <p className="text-sm text-muted-foreground text-center py-4">
          No hay horarios asignados. Agrega al menos un horario para el curso.
        </p>
      )}
    </div>
  );
}
