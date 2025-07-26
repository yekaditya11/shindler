// Authentication Context

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { httpClient } from '@/lib/http-client';
import { UserInfo } from '@/types/api';

interface AuthContextType {
  user: UserInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, userInfo: UserInfo) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = httpClient.getToken();
      
      if (token) {
        try {
          // Try to decode JWT token to get user info
          const payload = JSON.parse(atob(token.split('.')[1]));

          setUser({
            user_id: payload.user_id,
            role: payload.role,
            region: payload.region,
          });
        } catch (error) {
          // Token is invalid, clear it
          console.warn('Invalid token found, clearing:', error);
          httpClient.clearToken();
        }
      }
      
      setIsLoading(false);
    };

    checkAuthStatus();
  }, []);

  const login = (token: string, userInfo: UserInfo) => {
    httpClient.setToken(token);
    setUser(userInfo);
  };

  const logout = () => {
    httpClient.clearToken();
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
