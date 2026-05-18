import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { useAuth } from '../../contexts/AuthContext';
import { userAPI, workoutAPI } from '../../services/api';
import Button from '../../components/common/Button';

const HomeScreen = ({ navigation }) => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadStats();
    }, [])
  );

  const loadStats = async () => {
    try {
      const response = await userAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStats();
    setRefreshing(false);
  };

  const handleQuickGenerate = async () => {
    setLoading(true);
    try {
      const response = await workoutAPI.quickGenerate(true);
      navigation.navigate('WorkoutDetail', { workout: response.data });
    } catch (error) {
      Alert.alert('Ошибка', 'Не удалось сгенерировать тренировку');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Приветствие */}
      <View style={styles.header}>
        <Text style={styles.greeting}>
          Привет, {user?.name || 'Спортсмен'}! 👋
        </Text>
        <Text style={styles.headerSubtitle}>Готов к тренировке?</Text>
      </View>

      {/* Статистика */}
      {stats && (
        <View style={styles.statsContainer}>
          <Text style={styles.sectionTitle}>📊 Ваша статистика</Text>
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

      {/* Действия */}
      <View style={styles.actions}>
        <Button
          title="🤖 Сгенерировать тренировку с AI"
          onPress={handleQuickGenerate}
          loading={loading}
        />

        <Button
          title="⚙️ Настроить тренировку"
          onPress={() => navigation.navigate('GenerateWorkout')}
          type="secondary"
          style={{ marginTop: 10 }}
        />

        <Button
          title="📋 История тренировок"
          onPress={() => navigation.navigate('History')}
          type="outline"
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
    padding: 20,
    backgroundColor: '#007AFF',
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
  },
  headerSubtitle: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  statsContainer: {
    padding: 20,
    backgroundColor: 'white',
    marginTop: 10,
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
    borderWidth: 1,
    borderColor: '#e9ecef',
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
    padding: 20,
  },
});

export default HomeScreen;