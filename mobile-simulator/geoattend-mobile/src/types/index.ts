// User types
export interface User {
  id: number;
  code: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'student' | 'teacher' | 'admin';
  is_active: boolean;
}

export interface LoginResponse {
  message: string;
  data: {
    access_token: string;
    token_type: string;
    expires_in: number;
  };
  user: User;
}

// Course types
export interface Course {
  id: number;
  code: string;
  name: string;
  description?: string;
  teacher_id: number;
  teacher_code: string;
  teacher_name?: string;
  credits: number;
  academic_year: string;
  semester: string;
  max_students: number;
  enrollment_count?: number;
  detection_radius: number | string; // Backend devuelve Decimal como string
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Enrollment types
export interface Enrollment {
  id: number;
  student_id: number;
  course_id: number;
  course_code: string;
  course_name?: string;
  status: 'active' | 'dropped' | 'completed';
  enrolled_at: string;
}

// Attendance types
export interface AttendanceRecord {
  id: number;
  user_id: number;
  user_code: string;
  course_id: number;
  course_code: string;
  status: 'present' | 'late' | 'absent' | 'excused';
  source: 'gps_auto' | 'manual' | 'imported' | 'corrected';
  class_date: string;
  actual_arrival?: string;
  classroom_id?: number;
  classroom_name?: string;
  recorded_distance?: number;
  is_late: boolean;
  minutes_late?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface AttendanceStats {
  user_id: number;
  total_records: number;
  present_count: number;
  late_count: number;
  absent_count: number;
  attendance_rate: number;
}

// GPS types
export interface GPSEventData {
  user_id: number;
  course_id: number;
  latitude: number;
  longitude: number;
  accuracy: number;
  event_timestamp: string;
}

export interface GPSEventResponse {
  success: boolean;
  message: string;
  data: {
    gps_event_id: string;
    attendance_recorded: boolean;
    status: 'present' | 'late' | 'absent';
    distance_meters: number;
    nearest_classroom: {
      id: number;
      code: string;
      name: string;
      latitude: number;
      longitude: number;
    };
  };
}

// Schedule types
export interface Schedule {
  id: number;
  course_id: number;
  day_of_week: number; // 0=Lunes, 1=Martes, ..., 6=Domingo
  start_time: string;
  end_time: string;
  classroom_id: number;
  is_active: boolean;
  created_at: string;
}

// Notification types
export interface Notification {
  id: number;
  user_id: number;
  course_id?: number;
  notification_type: 'attendance' | 'course' | 'system';
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}
