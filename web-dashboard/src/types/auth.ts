export type UserRole = 'admin' | 'teacher' | 'student';

export interface User {
  id: string;
  code: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  data: {
    access_token: string;
    token_type: string;
    expires_in: number;
  };
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterUserData {
  email: string;
  password: string;
  code: string;
  first_name: string;
  last_name: string;
  role: UserRole;
}
