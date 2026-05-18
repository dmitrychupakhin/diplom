// src/utils/constants.js
import { NativeModules, Platform } from 'react-native';

const API_PORT = 8000;

const trimTrailingSlash = (value) => value.replace(/\/+$/, '');
const isIpv4 = (host) => /^\d{1,3}(\.\d{1,3}){3}$/.test(host);

const getMetroHostIp = () => {
  const scriptURL = NativeModules?.SourceCode?.scriptURL;
  if (!scriptURL) return null;

  const match = scriptURL.match(/^https?:\/\/([^/:]+)/i);
  const host = match?.[1];
  if (!host) return null;

  if (host === 'localhost' || host === '127.0.0.1' || isIpv4(host)) {
    return host;
  }

  return null;
};

const getApiUrl = () => {
  // Явный override для dev/prod окружений
  const envUrl = process.env.EXPO_PUBLIC_API_URL?.trim();
  if (envUrl) {
    return trimTrailingSlash(envUrl);
  }

  // Для dev-сессии берем IP машины из Metro bundle URL
  const metroHostIp = getMetroHostIp();
  if (metroHostIp && metroHostIp !== 'localhost' && metroHostIp !== '127.0.0.1') {
    return `http://${metroHostIp}:${API_PORT}`;
  }

  // Локальные дефолты для симуляторов
  if (Platform.OS === 'android') {
    return `http://10.0.2.2:${API_PORT}`;
  }

  return `http://localhost:${API_PORT}`;
};

export const API_URL = getApiUrl();

export const GOALS = [
  { label: 'Похудение', value: 'weight_loss', icon: '🔥' },
  { label: 'Набор массы', value: 'muscle_gain', icon: '💪' },
  { label: 'Сила', value: 'strength', icon: '🏋️' },
  { label: 'Выносливость', value: 'endurance', icon: '🏃' },
];

export const LEVELS = [
  { label: 'Новичок', value: 'beginner', color: '#4CAF50' },
  { label: 'Средний', value: 'intermediate', color: '#FF9800' },
  { label: 'Продвинутый', value: 'advanced', color: '#F44336' },
];

export const EQUIPMENT = [
  { label: 'Без оборудования', value: 'none', icon: '🧘' },
  { label: 'Гантели', value: 'dumbbells', icon: '🏋️' },
  { label: 'Штанга', value: 'barbell', icon: '🏋️‍♂️' },
  { label: 'Резинки', value: 'resistance_band', icon: '🩹' },
  { label: 'Коврик', value: 'mat', icon: '🧘‍♂️' },
  { label: 'Турник', value: 'pull_up_bar', icon: '🔝' },
];

export const INJURIES = [
  { label: 'Колени', value: 'knee_pain', icon: '🦵' },
  { label: 'Спина', value: 'back_pain', icon: '🔙' },
  { label: 'Плечи', value: 'shoulder_pain', icon: '💪' },
  { label: 'Запястья', value: 'wrist_pain', icon: '🤲' },
  { label: 'Шея', value: 'neck_pain', icon: '🗣️' },
  { label: 'Локти', value: 'elbow_pain', icon: '💪' },
];

export const COLORS = {
  primary: '#007AFF',
  secondary: '#34C759',
  danger: '#FF3B30',
  warning: '#FF9500',
  info: '#5AC8FA',
  light: '#F2F2F7',
  dark: '#1C1C1E',
  white: '#FFFFFF',
  gray: '#8E8E93',
  lightGray: '#E5E5EA',
};
