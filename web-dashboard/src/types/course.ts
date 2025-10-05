export interface Course {
  id: number;
  code: string;
  name: string;
  description?: string;
  year: string;
  semester: string;
  teacher_id: number;
  teacher_name?: string;
  max_students: number;
  gps_radius: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  enrollment_count?: number;
}

export interface CourseDetail extends Course {
  classrooms?: Classroom[];
  schedules?: Schedule[];
}

export interface Classroom {
  id: number;
  code: string;
  name: string;
  latitude: number;
  longitude: number;
  gps_radius: number;
  capacity: number;
  is_active: boolean;
}

export interface Schedule {
  id: number;
  day_of_week: number; // 0=Sunday, 1=Monday, etc.
  start_time: string; // "08:00:00"
  end_time: string; // "10:00:00"
  classroom_id?: number;
}

export interface CreateCourseData {
  code: string;
  name: string;
  description?: string;
  year: string;
  semester: string;
  teacher_id: number;
  teacher_code: string;
  max_students: number;
  gps_radius: number;
}

export interface UpdateCourseData {
  code?: string;
  name?: string;
  description?: string;
  year?: string;
  semester?: string;
  teacher_id?: number;
  max_students?: number;
  gps_radius?: number;
  is_active?: boolean;
}

export interface CourseFilters {
  year?: string;
  semester?: string;
  teacher_id?: number;
  is_active?: boolean;
  search?: string;
}
