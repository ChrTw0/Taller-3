import { useState, useEffect } from 'react';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Plus, X, Building2, MapPin } from 'lucide-react';
import { classroomApi } from '@/services/api';
import type { Classroom } from '@/types/classroom';

interface ClassroomSelectorProps {
  selectedClassroomIds: number[];
  onChange: (classroomIds: number[]) => void;
  disabled?: boolean;
}

export function ClassroomSelector({ selectedClassroomIds, onChange, disabled = false }: ClassroomSelectorProps) {
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');

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

  const handleAddClassroom = () => {
    if (!selectedId) return;

    const id = parseInt(selectedId);
    if (selectedClassroomIds.includes(id)) {
      return; // Already added
    }

    onChange([...selectedClassroomIds, id]);
    setSelectedId('');
  };

  const handleRemoveClassroom = (id: number) => {
    onChange(selectedClassroomIds.filter(cId => cId !== id));
  };

  const getClassroom = (id: number): Classroom | undefined => {
    return classrooms.find(c => c.id === id);
  };

  const availableClassrooms = classrooms.filter(
    c => !selectedClassroomIds.includes(c.id)
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label className="text-sm">Aulas Asignadas</Label>
        <Badge variant="outline">
          {selectedClassroomIds.length} aula{selectedClassroomIds.length !== 1 ? 's' : ''}
        </Badge>
      </div>

      {/* Selected Classrooms */}
      {selectedClassroomIds.length > 0 && (
        <div className="space-y-2">
          {selectedClassroomIds.map((id) => {
            const classroom = getClassroom(id);
            if (!classroom) return null;

            return (
              <div
                key={id}
                className="flex items-center justify-between p-2 border rounded-lg bg-muted/30"
              >
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  <div className="text-sm">
                    <div className="font-medium">{classroom.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {classroom.building} - Aula {classroom.room_number}
                      {classroom.floor && ` (Piso ${classroom.floor})`}
                    </div>
                  </div>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveClassroom(id)}
                  disabled={disabled}
                  className="h-8 w-8 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            );
          })}
        </div>
      )}

      {/* Add New Classroom */}
      {availableClassrooms.length > 0 && (
        <div className="flex gap-2">
          <Select
            value={selectedId}
            onValueChange={setSelectedId}
            disabled={disabled}
          >
            <SelectTrigger className="flex-1">
              <SelectValue placeholder="Seleccionar aula para agregar" />
            </SelectTrigger>
            <SelectContent>
              {availableClassrooms.map((classroom) => (
                <SelectItem key={classroom.id} value={classroom.id.toString()}>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{classroom.building} - {classroom.room_number}</span>
                    <span className="text-xs text-muted-foreground">({classroom.name})</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleAddClassroom}
            disabled={disabled || !selectedId}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      )}

      {selectedClassroomIds.length === 0 && (
        <p className="text-sm text-muted-foreground text-center py-3 border border-dashed rounded-lg">
          No hay aulas asignadas al curso
        </p>
      )}

      {availableClassrooms.length === 0 && selectedClassroomIds.length > 0 && (
        <p className="text-xs text-muted-foreground text-center">
          Todas las aulas disponibles han sido agregadas
        </p>
      )}
    </div>
  );
}
