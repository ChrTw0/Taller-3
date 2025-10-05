export type EnrollmentStatus = 'active' | 'dropped' | 'completed';

export interface Enrollment {
  id: number;
  student_id: number;
  student_code?: string;
  student_name?: string;
  course_id: number;
  course_code?: string;
  course_name?: string;
  status: EnrollmentStatus;
  enrolled_at: string;
  dropped_at?: string;
  final_grade?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateEnrollmentData {
  student_id: number;
  course_id: number;
}

export interface UpdateEnrollmentData {
  status?: EnrollmentStatus;
  final_grade?: number;
}

export interface EnrollmentFilters {
  student_id?: number;
  course_id?: number;
  status?: EnrollmentStatus;
  search?: string;
}

export interface EnrollmentStats {
  total: number;
  active: number;
  dropped: number;
  completed: number;
}
