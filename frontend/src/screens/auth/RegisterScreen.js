import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ScrollView,
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';

const RegisterScreen = ({ navigation }) => {
  const { register } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    // Проверки
    if (!email.trim()) {
      Alert.alert('Ошибка', 'Введите email');
      return;
    }
    if (!password) {
      Alert.alert('Ошибка', 'Введите пароль');
      return;
    }
    if (password.length < 8) {
      Alert.alert('Ошибка', 'Пароль должен быть не менее 8 символов');
      return;
    }
    if (password !== passwordConfirm) {
      Alert.alert('Ошибка', 'Пароли не совпадают');
      return;
    }

    setLoading(true);
    const result = await register({
      email: email.trim(),
      password,
      password_confirm: passwordConfirm,
      name: name.trim() || null,
    });
    setLoading(false);

    if (!result.success) {
      Alert.alert('Ошибка', result.error);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.header}>
          <Text style={styles.logo}>🏋️</Text>
          <Text style={styles.title}>Регистрация</Text>
          <Text style={styles.subtitle}>Создайте аккаунт для начала тренировок</Text>
        </View>

        <View style={styles.form}>
          <Input
            label="Имя (необязательно)"
            value={name}
            onChangeText={setName}
            placeholder="Ваше имя"
          />

          <Input
            label="Email"
            value={email}
            onChangeText={setEmail}
            placeholder="example@mail.com"
            keyboardType="email-address"
          />

          <Input
            label="Пароль"
            value={password}
            onChangeText={setPassword}
            placeholder="Минимум 8 символов"
            secureTextEntry
          />

          <Input
            label="Подтвердите пароль"
            value={passwordConfirm}
            onChangeText={setPasswordConfirm}
            placeholder="Повторите пароль"
            secureTextEntry
          />

          <Button
            title="Зарегистрироваться"
            onPress={handleRegister}
            loading={loading}
          />

          <Button
            title="Уже есть аккаунт? Войти"
            onPress={() => navigation.goBack()}
            type="outline"
            style={{ marginTop: 10 }}
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  logo: {
    fontSize: 48,
    marginBottom: 10,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  form: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
});

export default RegisterScreen;