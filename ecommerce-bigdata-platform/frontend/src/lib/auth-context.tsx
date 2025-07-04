'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from './api';
import { User, Token } from '@/types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: { email: string; password: string; name: string; role?: string }) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const checkAuth = async () => {
      try {
        const storedToken = localStorage.getItem('auth_token');
        if (storedToken) {
          api.setAuthToken(storedToken);
          const currentUser = await api.getCurrentUser();
          setUser(currentUser);
          setToken(storedToken);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        api.logout();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const tokenData = await api.login(email, password);
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
      setToken(tokenData.access_token);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (userData: { email: string; password: string; name: string; role?: string }) => {
    try {
      const tokenData = await api.register(userData);
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
      setToken(tokenData.access_token);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
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