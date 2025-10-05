import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type {
  LoginResponse,
  User,
  Course,
  Enrollment,
  AttendanceRecord,
  AttendanceStats,
  GPSEventData,
  GPSEventResponse,
  Notification
} from '../types';

// Configuración de la API
// IMPORTANTE: Si usas dispositivo físico, cambia 'localhost' por la IP de tu PC
// Ejemplo: 'http://192.168.1.100:8000/api/v1'
// Para obtener tu IP en Windows: ipconfig
// Para obtener tu IP en Mac/Linux: ifconfig
const API_BASE_URL = 'http://192.168.137.252:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a las peticiones
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AsyncStorage.removeItem('auth_token');
      await AsyncStorage.removeItem('user');
      // Aquí podrías navegar al login
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  logout: async (): Promise<void> => {
    await AsyncStorage.removeItem('auth_token');
    await AsyncStorage.removeItem('user');
  },
};

// User API
export const userApi = {
  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/users/me');
    return response.data;
  },

  getById: async (id: number): Promise<User> => {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },
};

// Course API
export const courseApi = {
  getAll: async (): Promise<Course[]> => {
    const response = await api.get<{ success: boolean; data: Course[] }>('/courses/');
    return response.data.data;
  },

  getById: async (id: number): Promise<Course> => {
    const response = await api.get<Course>(`/courses/${id}/`);
    return response.data;
  },
};

// Enrollment API
export const enrollmentApi = {
  getByStudent: async (studentId: number): Promise<Enrollment[]> => {
    const response = await api.get<Enrollment[]>(`/enrollments/student/${studentId}`);
    return response.data;
  },
};

// Attendance API
export const attendanceApi = {
  getByUser: async (userId: number, limit = 50): Promise<{data: AttendanceRecord[]; total: number}> => {
    const response = await api.get<{data: AttendanceRecord[]; total: number}>('/attendance/records', {
      params: { user_id: userId, limit },
    });
    return response.data;
  },

  getUserStats: async (userId: number, courseId?: number): Promise<AttendanceStats> => {
    const response = await api.get<any>(`/attendance/user/${userId}/stats`, {
      params: courseId ? { course_id: courseId } : {},
    });
    // El backend devuelve { statistics: {...} }, extraer la parte statistics
    const stats = response.data.statistics || response.data;
    return {
      user_id: response.data.user_id || userId,
      total_records: stats.total_records || 0,
      present_count: stats.present_count || 0,
      late_count: stats.late_count || 0,
      absent_count: stats.absent_count || 0,
      attendance_rate: stats.attendance_rate || 0,
    };
  },
};

// GPS API - ENDPOINT PRINCIPAL
export const gpsApi = {
  sendGPSEvent: async (data: GPSEventData): Promise<GPSEventResponse> => {
    const response = await api.post<GPSEventResponse>('/gps/event', data);
    return response.data;
  },

  validateCoordinates: async (
    latitude: number,
    longitude: number,
    accuracy: number,
    courseId: number
  ): Promise<any> => {
    const response = await api.post('/gps/validate', {
      latitude,
      longitude,
      accuracy,
      course_id: courseId,
    });
    return response.data;
  },
};

// Schedule API
export const scheduleApi = {
  getByCourse: async (courseId: number): Promise<any[]> => {
    const response = await api.get<{ success: boolean; message: string; data: any[] }>(`/schedules/course/${courseId}`);
    return response.data.data;
  },
};

// Notification API
export const notificationApi = {
  getByUser: async (userId: number, unreadOnly = false, limit = 50): Promise<Notification[]> => {
    const response = await api.get<{ total: number; notifications: Notification[] }>(
      `/notifications/user/${userId}`,
      {
        params: { limit, offset: 0 },
      }
    );
    return response.data.notifications;
  },

  markAsRead: async (notificationId: number): Promise<void> => {
    await api.put(`/notifications/${notificationId}/read`);
  },
};

export default api;
