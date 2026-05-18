import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import { workoutAPI } from '../../services/api';
import Button from '../../components/common/Button';

const WorkoutDetailScreen = ({ route, navigation }) => {
  const [workout, setWorkout] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (route.params?.workout) {
      setWorkout(route.params.workout);
    } else if (route.params?.workoutId) {
      loadWorkout(route.params.workoutId);
    }
  }, [route.params]);

  const loadWorkout = async (id) => {
    try {
      const response = await workoutAPI.getWorkout(id);
      setWorkout(response.data);
    } catch (error) {
      Alert.alert('Ошибка', 'Не удалось загрузить тренировку');
    }
  };

  const handleComplete = async () => {
    if (!workout?.id) return;
    setLoading(true);
    try {
      await workoutAPI.submitFeedback(workout.id, {
        status: 'completed',
        rating: 5,
      });
      Alert.alert('Отлично!', 'Тренировка завершена! 🎉');
      navigation.goBack();
    } catch (error) {
      Alert.alert('Ошибка', 'Не удалось сохранить результат');
    } finally {
      setLoading(false);
    }
  };

  if (!workout) {
    return (
      <View style={styles.center}>
        <Text>Загрузка тренировки...</Text>
      </View>
    );
  }

  const workoutData = workout.workout_data || workout;

  return (
    <ScrollView style={styles.container}>
      {/* Разминка */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔥 Разминка</Text>
        {(workoutData.warmup || []).map((ex, idx) => (
          <View key={idx} style={styles.exerciseCard}>
            <Text style={styles.exerciseName}>{ex.name || ex.exercise}</Text>
            <Text style={styles.exerciseDetail}>{ex.duration}</Text>
          </View>
        ))}
      </View>

      {/* Основная часть */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💪 Основная часть</Text>
        {(workoutData.main_workout || []).map((ex, idx) => (
          <View key={idx} style={styles.exerciseCard}>
            <Text style={styles.exerciseName}>{ex.exercise}</Text>
            <View style={styles.exerciseDetails}>
              <Text style={styles.detail}>{ex.sets} подхода</Text>
              <Text style={styles.detail}>{ex.reps} повторений</Text>
              <Text style={styles.detail}>Отдых: {ex.rest_sec}с</Text>
            </View>
            {ex.technique && (
              <Text style={styles.technique}>{ex.technique}</Text>
            )}
          </View>
        ))}
      </View>

      {/* Заминка */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🧘 Заминка</Text>
        {(workoutData.cooldown || []).map((ex, idx) => (
          <View key={idx} style={styles.exerciseCard}>
            <Text style={styles.exerciseName}>{ex.exercise}</Text>
            <Text style={styles.exerciseDetail}>{ex.duration}</Text>
          </View>
        ))}
      </View>

      {/* Рекомендации */}
      {workoutData.recommendations && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>💡 Рекомендации</Text>
          {workoutData.recommendations.hydration && (
            <Text style={styles.recommendation}>💧 {workoutData.recommendations.hydration}</Text>
          )}
          {workoutData.recommendations.safety && (
            <Text style={styles.recommendation}>⚠️ {workoutData.recommendations.safety}</Text>
          )}
        </View>
      )}

      {/* Кнопка завершения */}
      <View style={styles.actions}>
        <Button
          title="✅ Завершить тренировку"
          onPress={handleComplete}
          loading={loading}
          type="secondary"
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
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  exerciseCard: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  exerciseName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  exerciseDetails: {
    flexDirection: 'row',
    gap: 15,
  },
  exerciseDetail: {
    fontSize: 14,
    color: '#666',
  },
  detail: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '500',
  },
  technique: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
    fontStyle: 'italic',
  },
  recommendation: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    lineHeight: 20,
  },
  actions: {
    padding: 20,
    paddingBottom: 40,
  },
});

export default WorkoutDetailScreen;