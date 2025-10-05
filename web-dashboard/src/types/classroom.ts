export interface Classroom {
  id: number;
  code: string;
  name: string;
  building: string;
  room_number: string;
  floor?: number;
  latitude: number | string;  // Backend returns as string (Decimal)
  longitude: number | string; // Backend returns as string (Decimal)
  altitude?: number | string;
  gps_radius: number | string; // Backend returns as string (Decimal)
  capacity: number;
  equipment?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CourseClassroomAssignment {
  id: number;
  course_id: number;
  classroom_id: number;
  classroom?: Classroom;
  day_of_week?: number;
  start_time?: string;
  end_time?: string;
  is_primary: boolean;
  is_active: boolean;
  created_at: string;
}

export interface CreateClassroomData {
  code: string;
  name: string;
  building: string;
  room_number: string;
  floor?: number;
  latitude: number;
  longitude: number;
  altitude?: number;
  gps_radius: number;
  capacity: number;
  equipment?: string;
}

export interface UpdateClassroomData {
  name?: string;
  building?: string;
  room_number?: string;
  floor?: number;
  latitude?: number;
  longitude?: number;
  altitude?: number;
  gps_radius?: number;
  capacity?: number;
  equipment?: string;
  is_active?: boolean;
}

export interface ClassroomFilters {
  building?: string;
  is_active?: boolean;
  search?: string;
}
