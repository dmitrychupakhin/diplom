// src/contexts/AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../services/api';

// Создаем контекст
const AuthContext = createContext({});

// Провайдер контекста
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const parseApiError = (err, fallbackMessage) => {
    if (err.response?.data?.detail) {
      return err.response.data.detail;
    }
    if (err.message === 'Network Error') {
      return 'Нет соединения с сервером. Проверьте, что backend запущен и доступен по сети.';
    }
    return err.message || fallbackMessage;
  };

  // При запуске проверяем, есть ли сохраненный токен
  useEffect(() => {
    loadStoredData();
  }, []);

  const loadStoredData = async () => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (token) {
        // Если токен есть, получаем данные пользователя
        const response = await authAPI.getMe();
        setUser(response.data);
        console.log('✅ Пользователь загружен:', response.data.email);
      }
    } catch (err) {
      console.error('❌ Ошибка загрузки данных:', err);
      // Если токен недействителен, очищаем хранилище
      await AsyncStorage.clear();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // Вход
  const login = async (email, password) => {
    setError(null);
    try {
      console.log('🔑 Пытаемся войти...');
      const response = await authAPI.loginJSON({ email, password });
      
      const { access_token, refresh_token } = response.data.tokens;
      const userData = response.data.user;
      
      // Сохраняем токены
      await AsyncStorage.setItem('access_token', access_token);
      await AsyncStorage.setItem('refresh_token', refresh_token);
      
      // Устанавливаем пользователя
      setUser(userData);
      console.log('✅ Вход выполнен:', userData.email);
      
      return { success: true };
    } catch (err) {
      const message = parseApiError(err, 'Ошибка входа. Проверьте email и пароль.');
      console.error('❌ Ошибка входа:', message);
      setError(message);
      return { success: false, error: message };
    }
  };

  // Регистрация
  const register = async (data) => {
    setError(null);
    try {
      console.log('📝 Регистрация...');
      const response = await authAPI.register(data);
      
      const { access_token, refresh_token } = response.data.tokens;
      const userData = response.data.user;
      
      // Сохраняем токены
      await AsyncStorage.setItem('access_token', access_token);
      await AsyncStorage.setItem('refresh_token', refresh_token);
      
      // Устанавливаем пользователя
      setUser(userData);
      console.log('✅ Регистрация успешна:', userData.email);
      
      return { success: true };
    } catch (err) {
      const message = parseApiError(err, 'Ошибка регистрации.');
      console.error('❌ Ошибка регистрации:', message);
      setError(message);
      return { success: false, error: message };
    }
  };

  // Выход
  const logout = async () => {
    try {
      await AsyncStorage.clear();
      setUser(null);
      setError(null);
      console.log('👋 Выход выполнен');
    } catch (err) {
      console.error('Ошибка выхода:', err);
    }
  };

  // Обновление профиля
  const updateUser = (userData) => {
    setUser(userData);
  };

  // Значения, доступные через контекст
  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Хук для использования контекста
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export default AuthContext;
