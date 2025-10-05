import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { classroomApi } from '@/lib/api';
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
import { toast } from 'sonner';
import { Plus, Search, MapPin, Edit, Trash2, Building2, Users } from 'lucide-react';
import type { Classroom, CreateClassroomData } from '@/types/classroom';
import { LocationPicker } from '@/components/maps/LocationPicker';

export default function Classrooms() {
  const { user } = useAuth();
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [filteredClassrooms, setFilteredClassrooms] = useState<Classroom[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedClassroom, setSelectedClassroom] = useState<Classroom | undefined>();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState<CreateClassroomData>({
    code: '',
    name: '',
    building: '',
    room_number: '',
    floor: 1,
    latitude: -12.046374,
    longitude: -77.042793,
    gps_radius: 50,
    capacity: 30,
  });

  useEffect(() => {
    loadClassrooms();
  }, []);

  useEffect(() => {
    filterClassrooms();
  }, [searchTerm, classrooms]);

  const loadClassrooms = async () => {
    setIsLoading(true);
    try {
      const data = await classroomApi.getAll();
      setClassrooms(data);
    } catch (error: any) {
      console.error('Error loading classrooms:', error);
      toast.error('Error al cargar aulas');
    } finally {
      setIsLoading(false);
    }
  };

  const filterClassrooms = () => {
    if (!searchTerm) {
      setFilteredClassrooms(classrooms);
      return;
    }

    const term = searchTerm.toLowerCase();
    const filtered = classrooms.filter(
      (classroom) =>
        classroom.code.toLowerCase().includes(term) ||
        classroom.name.toLowerCase().includes(term) ||
        classroom.building?.toLowerCase().includes(term)
    );
    setFilteredClassrooms(filtered);
  };

  const handleCreateClassroom = () => {
    setSelectedClassroom(undefined);
    setFormData({
      code: '',
      name: '',
      building: '',
      room_number: '',
      floor: 1,
      latitude: -12.046374,
      longitude: -77.042793,
      gps_radius: 50,
      capacity: 30,
    });
    setIsFormOpen(true);
  };

  const handleEditClassroom = (classroom: Classroom) => {
    setSelectedClassroom(classroom);
    setFormData({
      code: classroom.code,
      name: classroom.name,
      building: classroom.building,
      room_number: classroom.room_number,
      floor: classroom.floor || 1,
      latitude: typeof classroom.latitude === 'string' ? parseFloat(classroom.latitude) : classroom.latitude,
      longitude: typeof classroom.longitude === 'string' ? parseFloat(classroom.longitude) : classroom.longitude,
      gps_radius: typeof classroom.gps_radius === 'string' ? parseFloat(classroom.gps_radius) : classroom.gps_radius,
      capacity: classroom.capacity,
    });
    setIsFormOpen(true);
  };

  const handleDeleteClassroom = async (classroom: Classroom) => {
    if (!confirm(`¿Estás seguro de eliminar el aula "${classroom.name}"?`)) {
      return;
    }

    try {
      await classroomApi.delete(classroom.id);
      toast.success('Aula eliminada exitosamente');
      loadClassrooms();
    } catch (error: any) {
      console.error('Error deleting classroom:', error);
      toast.error(error.response?.data?.detail || 'Error al eliminar aula');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.code || !formData.name || !formData.building || !formData.room_number) {
      toast.error('Por favor completa todos los campos obligatorios');
      return;
    }

    if (formData.capacity < 1) {
      toast.error('La capacidad debe ser al menos 1');
      return;
    }

    if (formData.gps_radius < 10) {
      toast.error('El radio GPS debe ser al menos 10 metros');
      return;
    }

    setIsSubmitting(true);
    try {
      if (selectedClassroom) {
        await classroomApi.update(selectedClassroom.id, formData);
        toast.success('Aula actualizada exitosamente');
      } else {
        await classroomApi.create(formData);
        toast.success('Aula creada exitosamente');
      }
      setIsFormOpen(false);
      loadClassrooms();
    } catch (error: any) {
      console.error('Classroom form error:', error);
      toast.error(error.response?.data?.detail || 'Error al guardar aula');
    } finally {
      setIsSubmitting(false);
    }
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
            <h1 className="text-3xl font-bold text-foreground">Aulas</h1>
            <p className="text-muted-foreground">Gestiona las aulas y su configuración GPS</p>
          </div>
          <Button className="gap-2" onClick={handleCreateClassroom}>
            <Plus className="h-4 w-4" />
            Crear Aula
          </Button>
        </div>

        {/* Search */}
        <Card>
          <CardContent className="pt-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Buscar por código, nombre o edificio..."
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
        {!isLoading && filteredClassrooms.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">
                {searchTerm ? 'No se encontraron aulas' : 'No hay aulas registradas'}
              </p>
              {!searchTerm && (
                <Button className="mt-4" onClick={handleCreateClassroom}>
                  <Plus className="mr-2 h-4 w-4" />
                  Crear Primera Aula
                </Button>
              )}
            </CardContent>
          </Card>
        )}

        {/* Classrooms Grid */}
        {!isLoading && filteredClassrooms.length > 0 && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredClassrooms.map((classroom) => (
              <Card key={classroom.id} className="overflow-hidden transition-all hover:shadow-md">
                <CardHeader className="bg-primary/5 border-b border-border">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <Badge variant="outline" className="mb-2">
                        {classroom.code}
                      </Badge>
                      <CardTitle className="text-lg line-clamp-2">{classroom.name}</CardTitle>
                      <CardDescription className="mt-1">
                        {classroom.building} - Aula {classroom.room_number}
                        {classroom.floor && ` (Piso ${classroom.floor})`}
                      </CardDescription>
                    </div>
                    <Badge className={classroom.is_active ? 'bg-success' : 'bg-muted'}>
                      {classroom.is_active ? 'Activo' : 'Inactivo'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Users className="h-4 w-4" />
                        <span>Capacidad:</span>
                      </div>
                      <span className="font-medium">{classroom.capacity} personas</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <MapPin className="h-4 w-4" />
                        <span>Radio GPS:</span>
                      </div>
                      <span className="font-medium">{classroom.gps_radius}m</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Coordenadas:</span>
                      <span className="font-mono text-xs">
                        {parseFloat(String(classroom.latitude)).toFixed(6)}, {parseFloat(String(classroom.longitude)).toFixed(6)}
                      </span>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-border flex gap-2">
                    <Button
                      variant="outline"
                      className="flex-1"
                      size="sm"
                      onClick={() => handleEditClassroom(classroom)}
                    >
                      <Edit className="mr-1 h-3 w-3" />
                      Editar
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteClassroom(classroom)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Classroom Form Dialog */}
        <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
          <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {selectedClassroom ? 'Editar Aula' : 'Crear Nueva Aula'}
              </DialogTitle>
              <DialogDescription>
                {selectedClassroom
                  ? 'Modifica los datos del aula'
                  : 'Completa los datos para crear una nueva aula'}
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="code">Código *</Label>
                  <Input
                    id="code"
                    placeholder="A-101"
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                    disabled={isSubmitting}
                    maxLength={20}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="capacity">Capacidad *</Label>
                  <Input
                    id="capacity"
                    type="number"
                    placeholder="30"
                    value={formData.capacity}
                    onChange={(e) => setFormData({ ...formData, capacity: parseInt(e.target.value) || 0 })}
                    disabled={isSubmitting}
                    min="1"
                    max="500"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="name">Nombre del Aula *</Label>
                <Input
                  id="name"
                  placeholder="Laboratorio de Computación 1"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  disabled={isSubmitting}
                  maxLength={200}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="building">Edificio *</Label>
                  <Input
                    id="building"
                    placeholder="Edificio A"
                    value={formData.building}
                    onChange={(e) => setFormData({ ...formData, building: e.target.value })}
                    disabled={isSubmitting}
                    maxLength={100}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="room_number">Número de Aula *</Label>
                  <Input
                    id="room_number"
                    placeholder="301"
                    value={formData.room_number}
                    onChange={(e) => setFormData({ ...formData, room_number: e.target.value })}
                    disabled={isSubmitting}
                    maxLength={20}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="floor">Piso</Label>
                <Input
                  id="floor"
                  type="number"
                  placeholder="1"
                  value={formData.floor}
                  onChange={(e) => setFormData({ ...formData, floor: parseInt(e.target.value) || 1 })}
                  disabled={isSubmitting}
                  min="1"
                  max="50"
                />
              </div>

              <div className="space-y-2">
                <Label>Ubicación GPS *</Label>
                <p className="text-xs text-muted-foreground mb-2">
                  Haz clic en el mapa para seleccionar la ubicación exacta del aula
                </p>
                <LocationPicker
                  latitude={formData.latitude}
                  longitude={formData.longitude}
                  radius={formData.gps_radius}
                  onLocationChange={(lat, lng) => {
                    setFormData({ ...formData, latitude: lat, longitude: lng });
                  }}
                  height="350px"
                />
                <div className="grid grid-cols-2 gap-4 mt-2">
                  <div className="space-y-1">
                    <Label htmlFor="latitude" className="text-xs">Latitud</Label>
                    <Input
                      id="latitude"
                      type="number"
                      value={formData.latitude}
                      onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) || 0 })}
                      disabled={isSubmitting}
                      step="0.000001"
                      className="text-xs font-mono"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="longitude" className="text-xs">Longitud</Label>
                    <Input
                      id="longitude"
                      type="number"
                      value={formData.longitude}
                      onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) || 0 })}
                      disabled={isSubmitting}
                      step="0.000001"
                      className="text-xs font-mono"
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="gps_radius">Radio GPS (metros) *</Label>
                <Input
                  id="gps_radius"
                  type="number"
                  placeholder="50"
                  value={formData.gps_radius}
                  onChange={(e) => setFormData({ ...formData, gps_radius: parseFloat(e.target.value) || 0 })}
                  disabled={isSubmitting}
                  min="1"
                  max="1000"
                  step="0.1"
                />
                <p className="text-xs text-muted-foreground">
                  Radio de geovalla para validar la ubicación del estudiante
                </p>
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
                      {selectedClassroom ? 'Actualizando...' : 'Creando...'}
                    </>
                  ) : (
                    selectedClassroom ? 'Actualizar Aula' : 'Crear Aula'
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
