// LOGIN AND AUTHENTICATION INTERFACES

export interface LoginFormValues {
  email: string;
  password: string;
  rememberMe: boolean;
}

export type LoginFormData = LoginFormValues;

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role?: string;
  avatarUrl?: string;
}

export interface LoginResponse {
  accessToken: string;
  tokenType: string;
  user?: UserProfile;
}
