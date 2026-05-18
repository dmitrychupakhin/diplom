import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { userAPI } from '../../services/api';
import Button from '../../components/common/Button';
import { GOALS, LEVELS } from '../../utils/constants';

const ProfileScreen = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await userAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Выход',
      'Вы уверены, что хотите выйти?',
      [
        { text: 'Отмена', style: 'cancel' },
        { text: 'Выйти', style: 'destructive', onPress: logout },
      ]
    );
  };

  const getGoalLabel = (value) => {
    const goal = GOALS.find(g => g.value === value);
    return goal ? `${goal.icon} ${goal.label}` : value;
  };

  const getLevelLabel = (value) => {
    const level = LEVELS.find(l => l.value === value);
    return level ? level.label : value;
  };

  return (
    <ScrollView style={styles.container}>
      {/* Информация о пользователе */}
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {(user?.name || user?.email || 'U')[0].toUpperCase()}
          </Text>
        </View>
        <Text style={styles.name}>{user?.name || 'Пользователь'}</Text>
        <Text style={styles.email}>{user?.email}</Text>
      </View>

      {/* Параметры */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📋 Параметры</Text>
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Цель</Text>
          <Text style={styles.paramValue}>{getGoalLabel(user?.goal)}</Text>
        </View>
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Уровень</Text>
          <Text style={styles.paramValue}>{getLevelLabel(user?.level)}</Text>
        </View>
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Возраст</Text>
          <Text style={styles.paramValue}>{user?.age || '-'} лет</Text>
        </View>
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Вес</Text>
          <Text style={styles.paramValue}>{user?.weight || '-'} кг</Text>
        </View>
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Рост</Text>
          <Text style={styles.paramValue}>{user?.height || '-'} см</Text>
        </View>
        
        <View style={styles.paramRow}>
          <Text style={styles.paramLabel}>Тренировок в неделю</Text>
          <Text style={styles.paramValue}>{user?.workouts_per_week || 3}</Text>
        </View>
      </View>

      {/* Статистика */}
      {stats && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📊 Статистика</Text>
          
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.completed_workouts || 0}</Text>
              <Text style={styles.statLabel}>Тренировок</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.current_streak || 0}</Text>
              <Text style={styles.statLabel}>Дней подряд</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.total_duration_minutes || 0}</Text>
              <Text style={styles.statLabel}>Минут</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statNumber}>{stats.total_calories_burned || 0}</Text>
              <Text style={styles.statLabel}>Ккал</Text>
            </View>
          </View>
        </View>
      )}

      {/* Кнопки */}
      <View style={styles.actions}>
        <Button
          title="✏️ Редактировать профиль"
          onPress={() => navigation.navigate('EditProfile')}
        />
        
        <Button
          title="🚪 Выйти"
          onPress={handleLogout}
          type="danger"
          style={{ marginTop: 10 }}
        />
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    alignItems: 'center',
    padding: 30,
    backgroundColor: '#007AFF',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255,255,255,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
  },
  avatarText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
  },
  name: {
    fontSize: 22,
    fontWeight: 'bold',
    color: 'white',
  },
  email: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 5,
  },
  section: {
    backgroundColor: 'white',
    margin: 15,
    padding: 20,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  paramRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  paramLabel: {
    fontSize: 16,
    color: '#666',
  },
  paramValue: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  actions: {
    padding: 15,
    paddingBottom: 40,
  },
});

export default ProfileScreen;