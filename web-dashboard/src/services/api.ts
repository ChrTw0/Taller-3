import axios from 'axios';
import type { AuthResponse, LoginCredentials, RegisterUserData, User } from '@/types/auth';
import type { Course, CourseDetail, CreateCourseData, UpdateCourseData, CourseFilters, Schedule } from '@/types/course';
import type { Classroom, CreateClassroomData, UpdateClassroomData, ClassroomFilters } from '@/types/classroom';
import type { Enrollment, CreateEnrollmentData, UpdateEnrollmentData, EnrollmentFilters } from '@/types/enrollment';
import type { AttendanceRecord, AttendanceListResponse, AttendanceFilters, UserAttendanceStats, CourseAttendanceStats, CreateAttendanceData } from '@/types/attendance';
import type { OverallAttendanceStats } from '@/types/kpi';

//const API_BASE_URL = 'http://192.168.1.4:8000/api/v1';
const API_BASE_URL = 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', {
      email: credentials.email,
      password: credentials.password,
    });
    return response.data;
  },
  register: async (userData: RegisterUserData): Promise<{ success: boolean; message: string; data: User }> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
};

// User endpoints
export const userApi = {
  getAll: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/users/');
    return response.data;
  },
  getTeachers: async (): Promise<User[]> => {
    const [teachers, admins] = await Promise.all([
      api.get<User[]>('/users/', { params: { role: 'teacher' } }),
      api.get<User[]>('/users/', { params: { role: 'admin' } })
    ]);
    // La respuesta de /users/ es un objeto { data: [...] } o un array directo.
    return [...(Array.isArray(teachers.data) ? teachers.data : []), ...(Array.isArray(admins.data) ? admins.data : [])];
  },
  getById: async (id: string): Promise<User> => {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },
};

// Course endpoints
export const courseApi = {
  getAll: async (filters?: CourseFilters): Promise<Course[]> => {
    console.log('📡 API: courseApi.getAll called', filters);
    const response = await api.get<{success: boolean; message: string; data: Course[]; total: number}>('/courses/', { params: filters });
    console.log('📡 API: courseApi.getAll response:', response.data);
    // Map backend fields to frontend fields
    const mapped = response.data.data.map(course => ({
      ...course,
      year: (course as any).academic_year || course.year,
      gps_radius: (course as any).detection_radius || course.gps_radius,
    }));
    console.log('📡 API: courseApi.getAll mapped:', mapped.length, 'courses');
    return mapped;
  },
  getById: async (id: number, includeDetails = false): Promise<CourseDetail> => {
    const response = await api.get<CourseDetail>(`/courses/${id}`, {
      params: { include_details: includeDetails }
    });
    // Map backend fields to frontend fields
    const course = response.data as any;
    return {
      ...course,
      year: course.academic_year || course.year,
      gps_radius: course.detection_radius || course.gps_radius,
    };
  },
  create: async (data: CreateCourseData): Promise<{ success: boolean; message: string; data: Course }> => {
    // Map frontend fields to backend fields
    const backendData = {
      ...data,
      academic_year: data.year,
      detection_radius: data.gps_radius,
      // teacher_code is already in data from the form
    };
    const response = await api.post('/courses/', backendData);
    return response.data;
  },
  update: async (id: number, data: UpdateCourseData): Promise<{ success: boolean; message: string; data: Course }> => {
    // Map frontend fields to backend fields
    const backendData: any = {};
    if (data.name !== undefined) backendData.name = data.name;
    if (data.description !== undefined) backendData.description = data.description;
    if (data.max_students !== undefined) backendData.max_students = data.max_students;
    if (data.gps_radius !== undefined) backendData.detection_radius = data.gps_radius;
    if (data.is_active !== undefined) backendData.is_active = data.is_active;
    // Note: year, semester, teacher_id cannot be updated per backend schema

    const response = await api.put(`/courses/${id}`, backendData);
    return response.data;
  },
  delete: async (id: number): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/courses/${id}`);
    return response.data;
  },
};

// Schedule endpoints
export const scheduleApi = {
  getByCourse: async (courseId: number): Promise<Schedule[]> => {
    const response = await api.get<{success: boolean; message: string; data: Schedule[]}>(`/schedules/course/${courseId}`);
    return response.data.data;
  },
  create: async (courseId: number, data: Omit<Schedule, 'id'>): Promise<{success: boolean; message: string; data: Schedule}> => {
    const response = await api.post(`/schedules/course/${courseId}`, data);
    return response.data;
  },
  update: async (scheduleId: number, data: Partial<Schedule>): Promise<{success: boolean; message: string; data: Schedule}> => {
    const response = await api.put(`/schedules/${scheduleId}`, data);
    return response.data;
  },
  delete: async (scheduleId: number): Promise<{success: boolean; message: string}> => {
    const response = await api.delete(`/schedules/${scheduleId}`);
    return response.data;
  },
};

// Classroom endpoints
export const classroomApi = {
  getAll: async (filters?: ClassroomFilters): Promise<Classroom[]> => {
    const response = await api.get<Classroom[]>('/classrooms/', { params: filters });
    return response.data;
  },
  getById: async (id: number): Promise<Classroom> => {
    const response = await api.get<Classroom>(`/classrooms/${id}`);
    return response.data;
  },
  create: async (data: CreateClassroomData): Promise<{ success: boolean; message: string; data: Classroom }> => {
    const response = await api.post('/classrooms/', data);
    return response.data;
  },
  update: async (id: number, data: UpdateClassroomData): Promise<{ success: boolean; message: string; data: Classroom }> => {
    const response = await api.put(`/classrooms/${id}`, data);
    return response.data;
  },
  delete: async (id: number): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/classrooms/${id}`);
    return response.data;
  },
};

// Enrollment endpoints
export const enrollmentApi = {
  getAll: async (filters?: EnrollmentFilters): Promise<Enrollment[]> => {
    const response = await api.get<any>('/enrollments/', { params: filters });
    if (Array.isArray(response.data)) {
      return response.data;
    }
    if (response.data && Array.isArray(response.data.data)) {
      return response.data.data;
    }
    return []; 
  },
  getById: async (id: number): Promise<Enrollment> => {
    const response = await api.get<Enrollment>(`/enrollments/${id}`);
    return response.data;
  },
  getByCourse: async (courseId: number): Promise<Enrollment[]> => {
    const response = await api.get<any>(`/enrollments/course/${courseId}`);
    if (Array.isArray(response.data)) {
      return response.data;
    }
    if (response.data && Array.isArray(response.data.data)) {
      return response.data.data;
    }
    return [];
  },
  getByStudent: async (studentId: number): Promise<Enrollment[]> => {
    const response = await api.get<any>(`/enrollments/`, { params: { student_id: studentId } });
    if (Array.isArray(response.data)) {
      return response.data;
    }
    if (response.data && Array.isArray(response.data.data)) {
      return response.data.data;
    }
    return []; 
  },
  create: async (data: CreateEnrollmentData): Promise<{ success: boolean; message: string; data: Enrollment }> => {
    const response = await api.post('/enrollments/', data);
    return response.data;
  },
  update: async (id: number, data: UpdateEnrollmentData): Promise<{ success: boolean; message: string; data: Enrollment }> => {
    const response = await api.put(`/enrollments/${id}`, data);
    return response.data;
  },
  delete: async (id: number): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/enrollments/${id}`);
    return response.data;
  },
};

// Attendance endpoints
export const attendanceApi = {
  getAll: async (filters?: AttendanceFilters): Promise<AttendanceListResponse> => {
    const response = await api.get<AttendanceListResponse>('/attendance/records', { params: filters });
    return response.data;
  },
  getByUser: async (userId: number, filters?: AttendanceFilters): Promise<AttendanceListResponse> => {
    const response = await api.get<AttendanceListResponse>('/attendance/records', {
      params: { ...filters, user_id: userId }
    });
    return response.data;
  },
  getByCourse: async (courseId: number, filters?: AttendanceFilters): Promise<AttendanceListResponse> => {
    const response = await api.get<AttendanceListResponse>(`/attendance/course/${courseId}/records`, { params: filters });
    return response.data;
  },
  getUserStats: async (userId: number, courseId?: number, startDate?: string, endDate?: string): Promise<UserAttendanceStats> => {
    const response = await api.get<UserAttendanceStats>(`/attendance/user/${userId}/stats`, {
      params: { course_id: courseId, start_date: startDate, end_date: endDate }
    });
    return response.data;
  },
  getCourseStats: async (courseId: number, startDate?: string, endDate?: string): Promise<CourseAttendanceStats> => {
    const response = await api.get<CourseAttendanceStats>(`/attendance/course/${courseId}/stats`, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  },
  create: async (data: CreateAttendanceData): Promise<{ success: boolean; message: string; data: AttendanceRecord }> => {
    const response = await api.post('/attendance/process', data);
    return response.data;
  },
  getOverallStats: async (startDate?: string, endDate?: string): Promise<OverallAttendanceStats> => {
    const response = await api.get<OverallAttendanceStats>('/attendance/stats/overall', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },
};
