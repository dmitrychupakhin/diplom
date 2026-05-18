import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  TouchableOpacity,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { workoutAPI } from '../../services/api';
import { GOALS, LEVELS, EQUIPMENT, INJURIES } from '../../utils/constants';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';

const GenerateWorkoutScreen = ({ navigation }) => {
  const [goal, setGoal] = useState('weight_loss');
  const [level, setLevel] = useState('beginner');
  const [duration, setDuration] = useState('45');
  const [equipment, setEquipment] = useState([]);
  const [injuries, setInjuries] = useState([]);
  const [useAI, setUseAI] = useState(true);
  const [loading, setLoading] = useState(false);

  const toggleEquipment = (value) => {
    if (equipment.includes(value)) {
      setEquipment(equipment.filter(e => e !== value));
    } else {
      setEquipment([...equipment, value]);
    }
  };

  const toggleInjury = (value) => {
    if (injuries.includes(value)) {
      setInjuries(injuries.filter(i => i !== value));
    } else {
      setInjuries([...injuries, value]);
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await workoutAPI.generate({
        goal,
        level,
        duration: parseInt(duration),
        equipment: equipment.length > 0 ? equipment : ['none'],
        injuries: injuries.length > 0 ? injuries : [],
        use_ai: useAI,
      });
      
      navigation.navigate('WorkoutDetail', { workout: response.data });
    } catch (error) {
      Alert.alert('Ошибка', 'Не удалось сгенерировать тренировку');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Настройка тренировки</Text>

      {/* Цель */}
      <Text style={styles.label}>Цель тренировки</Text>
      <View style={styles.pickerContainer}>
        <Picker selectedValue={goal} onValueChange={setGoal}>
          {GOALS.map(g => (
            <Picker.Item key={g.value} label={`${g.icon} ${g.label}`} value={g.value} />
          ))}
        </Picker>
      </View>

      {/* Уровень */}
      <Text style={styles.label}>Уровень подготовки</Text>
      <View style={styles.pickerContainer}>
        <Picker selectedValue={level} onValueChange={setLevel}>
          {LEVELS.map(l => (
            <Picker.Item key={l.value} label={l.label} value={l.value} />
          ))}
        </Picker>
      </View>

      {/* Длительность */}
      <Input
        label="Длительность (минут)"
        value={duration}
        onChangeText={setDuration}
        keyboardType="numeric"
        placeholder="45"
      />

      {/* Оборудование */}
      <Text style={styles.label}>Доступное оборудование</Text>
      <View style={styles.chipsContainer}>
        {EQUIPMENT.map(eq => (
          <TouchableOpacity
            key={eq.value}
            style={[
              styles.chip,
              equipment.includes(eq.value) && styles.chipSelected,
            ]}
            onPress={() => toggleEquipment(eq.value)}
          >
            <Text style={[
              styles.chipText,
              equipment.includes(eq.value) && styles.chipTextSelected,
            ]}>
              {eq.icon} {eq.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Травмы */}
      <Text style={styles.label}>Ограничения/травмы</Text>
      <View style={styles.chipsContainer}>
        {INJURIES.map(inj => (
          <TouchableOpacity
            key={inj.value}
            style={[
              styles.chip,
              styles.injuryChip,
              injuries.includes(inj.value) && styles.injuryChipSelected,
            ]}
            onPress={() => toggleInjury(inj.value)}
          >
            <Text style={[
              styles.chipText,
              injuries.includes(inj.value) && styles.chipTextInjurySelected,
            ]}>
              {inj.icon} {inj.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* AI переключатель */}
      <View style={styles.aiToggle}>
        <Text style={styles.label}>Использовать AI генерацию</Text>
        <TouchableOpacity
          style={[styles.toggle, useAI && styles.toggleActive]}
          onPress={() => setUseAI(!useAI)}
        >
          <Text style={[styles.toggleText, useAI && styles.toggleTextActive]}>
            {useAI ? '🤖 AI ВКЛ' : '📋 Правила'}
          </Text>
        </TouchableOpacity>
      </View>

      <Button
        title="Сгенерировать тренировку"
        onPress={handleGenerate}
        loading={loading}
        style={{ margin: 20 }}
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    marginTop: 15,
  },
  pickerContainer: {
    backgroundColor: 'white',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#ddd',
    overflow: 'hidden',
  },
  chipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: 'white',
  },
  chipSelected: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  injuryChip: {
    borderColor: '#FF9500',
  },
  injuryChipSelected: {
    backgroundColor: '#FF9500',
    borderColor: '#FF9500',
  },
  chipText: {
    fontSize: 14,
    color: '#333',
  },
  chipTextSelected: {
    color: 'white',
  },
  chipTextInjurySelected: {
    color: 'white',
  },
  aiToggle: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 20,
  },
  toggle: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ddd',
    backgroundColor: 'white',
  },
  toggleActive: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  toggleText: {
    fontSize: 14,
    color: '#333',
  },
  toggleTextActive: {
    color: 'white',
  },
});

export default GenerateWorkoutScreen;