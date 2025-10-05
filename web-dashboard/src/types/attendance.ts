export type AttendanceStatus = 'present' | 'late' | 'absent' | 'excused';
export type AttendanceSource = 'gps_auto' | 'manual' | 'qr_code';

export interface AttendanceRecord {
  id: number;
  user_id: number;
  course_id: number;
  timestamp: string;
  status: AttendanceStatus;
  source: AttendanceSource;
  gps_latitude?: number | string;
  gps_longitude?: number | string;
  gps_accuracy?: number | string;
  distance_to_classroom?: number | string;
  classroom_id?: number;
  notes?: string;
  verified: boolean;
  created_at: string;
  updated_at: string;

  // Populated fields
  student_name?: string;
  student_code?: string;
  course_name?: string;
  course_code?: string;
  classroom_name?: string;
}

export interface AttendanceListResponse {
  success: boolean;
  message: string;
  data: AttendanceRecord[];
  total: number;
  page: number;
  per_page: number;
}

export interface AttendanceStats {
  attendance_rate: number;
  punctuality_rate: number;
  present_count: number;
  late_count: number;
  absent_count: number;
}

export interface UserAttendanceStats {
  user_id: number;
  user_code: string;
  course_id?: number;
  period: {
    start_date?: string;
    end_date?: string;
  };
  statistics: AttendanceStats;
}

export interface CourseAttendanceStats {
  course_id: number;
  course_code: string;
  course_name: string;
  total_students: number;
  total_records: number;
  period: {
    start_date?: string;
    end_date?: string;
  };
  statistics: AttendanceStats;
}

export interface AttendanceFilters {
  user_id?: number;
  course_id?: number;
  start_date?: string;
  end_date?: string;
  status_filter?: AttendanceStatus;
  skip?: number;
  limit?: number;
}

export interface CreateAttendanceData {
  user_id: number;
  course_id: number;
  gps_latitude: number;
  gps_longitude: number;
  gps_accuracy?: number;
  classroom_id?: number;
  source?: AttendanceSource;
  notes?: string;
}
