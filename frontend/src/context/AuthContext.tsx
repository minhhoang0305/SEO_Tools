import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiPost } from '../api/httpClient';

export interface User {
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string) => Promise<string>;
  completeRegistration: (sessionId: string, name: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface DecodedToken {
  "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"?: string;
  "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"?: string;
  exp?: number;
}

function parseToken(token: string): User | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    // Support unicode decoding by using decodeURIComponent + escape
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      window.atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    
    const payload = JSON.parse(jsonPayload) as DecodedToken;
    
    // Check if token has expired
    if (payload.exp && Date.now() >= payload.exp * 1000) {
      return null;
    }
    
    return {
      name: payload["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"] || 'User',
      email: payload["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"] || '',
    };
  } catch (e) {
    return null;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      const parsedUser = parseToken(token);
      if (parsedUser) {
        setUser(parsedUser);
      } else {
        // Token expired or invalid
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    interface LoginResponse {
      access_token: string;
      refresh_token: string;
      message: string;
    }
    
    const response = await apiPost<any, LoginResponse>('/api/auth/login', {
      email,
      password,
    });

    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    
    const parsedUser = parseToken(response.access_token);
    setUser(parsedUser);
  };

  const register = async (email: string) => {
    interface RegisterResponse {
      sessionId: string;
      message: string;
    }

    const response = await apiPost<any, RegisterResponse>('/api/auth/register', {
      email,
    });

    return response.sessionId;
  };

  const completeRegistration = async (sessionId: string, name: string, password: string) => {
    interface CompleteResponse {
      userId: string;
      message: string;
    }

    await apiPost<any, CompleteResponse>('/api/auth/register/complete', {
      sessionId,
      name,
      password,
    });

    // Directly prompt user to login, or we can auto-login if the backend supported direct token emission.
    // Since the API requires login, the user will be redirected to Login after completion.
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        completeRegistration,
        logout,
      }}
    >
      {!loading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
