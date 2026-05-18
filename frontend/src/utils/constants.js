// src/utils/constants.js

// API URL - меняйте под свое окружение
//export const API_URL = 'http://10.0.2.2:8000'; // Android эмулятор
// export const API_URL = 'http://localhost:8000'; // iOS симулятор
export const API_URL = 'http://192.168.31.217:8000'; // Реальное устройство (замените IP)

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