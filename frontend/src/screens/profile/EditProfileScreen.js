import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../../contexts/AuthContext';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import { GOALS, LEVELS } from '../../utils/constants';

const EditProfileScreen = ({ navigation }) => {
  const { user, updateUser } = useAuth();
  
  const [name, setName] = useState(user?.name || '');
  const [age, setAge] = useState(user?.age?.toString() || '');
  const [weight, setWeight] = useState(user?.weight?.toString() || '');
  const [height, setHeight] = useState(user?.height?.toString() || '');
  const [goal, setGoal] = useState(user?.goal || 'weight_loss');
  const [level, setLevel] = useState(user?.level || 'beginner');
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    
    const data = {
      name: name.trim() || null,
      age: age ? parseInt(age) : null,
      weight: weight ? parseFloat(weight) : null,
      height: height ? parseFloat(height) : null,
      goal,
      level,
    };

    const result = await updateUser(data);
    setLoading(false);

    if (result.success) {
      Alert.alert('Успех', 'Профиль обновлен');
      navigation.goBack();
    } else {
      Alert.alert('Ошибка', result.error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Input
        label="Имя"
        value={name}
        onChangeText={setName}
        placeholder="Ваше имя"
      />

      <Input
        label="Возраст"
        value={age}
        onChangeText={setAge}
        keyboardType="numeric"
        placeholder="25"
      />

      <Input
        label="Вес (кг)"
        value={weight}
        onChangeText={setWeight}
        keyboardType="numeric"
        placeholder="70"
      />

      <Input
        label="Рост (см)"
        value={height}
        onChangeText={setHeight}
        keyboardType="numeric"
        placeholder="175"
      />

      <Text style={styles.label}>Цель</Text>
      <View style={styles.picker}>
        <Picker selectedValue={goal} onValueChange={setGoal}>
          {GOALS.map(g => (
            <Picker.Item key={g.value} label={`${g.icon} ${g.label}`} value={g.value} />
          ))}
        </Picker>
      </View>

      <Text style={styles.label}>Уровень</Text>
      <View style={styles.picker}>
        <Picker selectedValue={level} onValueChange={setLevel}>
          {LEVELS.map(l => (
            <Picker.Item key={l.value} label={l.label} value={l.value} />
          ))}
        </Picker>
      </View>

      <Button
        title="Сохранить"
        onPress={handleSave}
        loading={loading}
        style={{ marginTop: 20 }}
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
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
    marginTop: 15,
  },
  picker: {
    backgroundColor: 'white',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#ddd',
  },
});

export default EditProfileScreen;