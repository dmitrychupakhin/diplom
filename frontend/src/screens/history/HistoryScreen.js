import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { workoutAPI } from '../../services/api';

const HistoryScreen = ({ navigation }) => {
  const [workouts, setWorkouts] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadWorkouts(1, true);
    }, [])
  );

  const loadWorkouts = async (pageNum = 1, reset = false) => {
    if (loading) return;
    setLoading(true);
    
    try {
      const response = await workoutAPI.getHistory(pageNum, 10);
      const data = response.data;
      
      if (reset) {
        setWorkouts(data.items);
      } else {
        setWorkouts(prev => [...prev, ...data.items]);
      }
      
      setTotal(data.pagination.total);
      setPage(pageNum);
    } catch (error) {
      console.error('Ошибка загрузки:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadWorkouts(1, true);
  };

  const onEndReached = () => {
    if (workouts.length < total) {
      loadWorkouts(page + 1);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#4CAF50';
      case 'in_progress': return '#FF9800';
      case 'skipped': return '#F44336';
      default: return '#666';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return '✅ Выполнена';
      case 'in_progress': return '🔄 В процессе';
      case 'skipped': return '⏭️ Пропущена';
      default: return '📝 Новая';
    }
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.workoutCard}
      onPress={() => navigation.navigate('WorkoutDetail', { workoutId: item.id })}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.date}>
          {new Date(item.created_at).toLocaleDateString('ru-RU')}
        </Text>
        <Text style={[styles.status, { color: getStatusColor(item.status) }]}>
          {getStatusText(item.status)}
        </Text>
      </View>
      
      <View style={styles.cardBody}>
        <Text style={styles.goal}>
          {item.goal === 'weight_loss' ? '🔥 Похудение' :
           item.goal === 'muscle_gain' ? '💪 Набор массы' :
           item.goal === 'strength' ? '🏋️ Сила' : '🏃 Выносливость'}
        </Text>
        <Text style={styles.duration}>{item.duration} мин</Text>
      </View>
      
      <View style={styles.cardFooter}>
        <Text style={styles.exercisesCount}>
          {item.preview?.exercises_count || 0} упражнений
        </Text>
        {item.ai_generated === 'Y' && (
          <Text style={styles.aiBadge}>🤖 AI</Text>
        )}
        {item.feedback_rating && (
          <Text style={styles.rating}>⭐ {item.feedback_rating}/5</Text>
        )}
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {workouts.length === 0 && !loading ? (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>🏋️</Text>
          <Text style={styles.emptyTitle}>Нет тренировок</Text>
          <Text style={styles.emptySubtext}>
            Сгенерируйте первую тренировку на главном экране
          </Text>
        </View>
      ) : (
        <FlatList
          data={workouts}
          renderItem={renderItem}
          keyExtractor={item => item.id}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          onEndReached={onEndReached}
          onEndReachedThreshold={0.5}
          contentContainerStyle={styles.list}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  list: {
    padding: 15,
  },
  workoutCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  date: {
    fontSize: 14,
    color: '#666',
  },
  status: {
    fontSize: 14,
    fontWeight: '600',
  },
  cardBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  goal: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  duration: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
  cardFooter: {
    flexDirection: 'row',
    gap: 10,
    alignItems: 'center',
  },
  exercisesCount: {
    fontSize: 14,
    color: '#666',
  },
  aiBadge: {
    fontSize: 12,
    backgroundColor: '#E3F2FD',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    color: '#007AFF',
  },
  rating: {
    fontSize: 14,
    color: '#FFD700',
  },
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 64,
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 10,
  },
});

export default HistoryScreen;