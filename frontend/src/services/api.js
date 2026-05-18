import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_URL } from '../utils/constants';
import { Alert } from 'react-native';

console.log('🌐 API URL:', API_URL);

// Создаем экземпляр axios
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000, // 10 секунд
  headers: {
    'Content-Type': 'application/json',
  },
});

// Перехватчик запросов - добавляем токен и логируем
api.interceptors.request.use(
  async (config) => {
    console.log(`📤 ${config.method?.toUpperCase()} ${config.url}`);
    
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Ошибка получения токена:', error);
    }
    return config;
  },
  (error) => {
    console.error('❌ Ошибка запроса:', error);
    return Promise.reject(error);
  }
);

// Перехватчик ответов
api.interceptors.response.use(
  (response) => {
    console.log(`📥 ${response.status} ${response.config.url}`);
    return response;
  },
  async (error) => {
    console.error('❌ Ошибка ответа:', error.response?.status, error.message);
    
    if (error.response) {
      console.error('📋 Данные ошибки:', error.response.data);
    } else if (error.request) {
      console.error('🔌 Нет ответа от сервера. Проверьте:');
      console.error('1. Сервер запущен?');
      console.error('2. Правильный ли API URL?');
      console.error('3. Устройство в той же сети?');
      console.error(`4. Текущий API URL: ${API_URL}`);
      Alert.alert(
        'Ошибка подключения',
        `Не удалось подключиться к серверу.\n\nURL: ${API_URL}\n\nПроверьте, что сервер запущен и адрес доступен с устройства.`
      );
    }
    
    const originalRequest = error.config;

    // Если ошибка 401 и это не повторный запрос
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data.tokens;
          
          await AsyncStorage.setItem('access_token', access_token);
          await AsyncStorage.setItem('refresh_token', refresh_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.error('Ошибка обновления токена:', refreshError);
        await AsyncStorage.clear();
      }
    }

    return Promise.reject(error);
  }
);

// ==================== Auth API ====================
export const authAPI = {
  register: (data) => {
    console.log('📝 Отправка регистрации:', data);
    return api.post('/auth/register', data);
  },
  
  login: (email, password) => 
    api.post('/auth/login', 
      `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
      {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      }
    ),
  
  loginJSON: (data) => {
    console.log('🔑 Отправка входа:', { email: data.email });
    return api.post('/auth/login/json', data);
  },
  
  refreshToken: (refreshToken) => 
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  
  getMe: () => api.get('/auth/me'),
  
  checkToken: () => api.get('/auth/check'),
};

// ==================== User API ====================
export const userAPI = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data) => api.put('/users/me', data),
  deleteAccount: () => api.delete('/users/me'),
  getInjuries: () => api.get('/users/me/injuries'),
  addInjury: (data) => api.post('/users/me/injuries', data),
  removeInjury: (id) => api.delete(`/users/me/injuries/${id}`),
  getStats: () => api.get('/users/me/stats'),
};

// ==================== Workout API ====================
export const workoutAPI = {
  generate: (data) => api.post('/workouts/generate', data),
  quickGenerate: (useAI = true) => 
    api.post(`/workouts/generate/quick?use_ai=${useAI}`),
  preview: (params) => api.get('/workouts/generate/preview', { params }),
  getHistory: (page = 1, size = 10) => 
    api.get('/workouts/history', { params: { page, size } }),
  getWorkout: (id) => api.get(`/workouts/${id}`),
  submitFeedback: (id, data) => 
    api.put(`/workouts/${id}/feedback`, data),
  deleteWorkout: (id) => api.delete(`/workouts/${id}`),
  checkAIStatus: () => api.get('/workouts/ai/status'),
};

export default api;
