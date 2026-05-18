
import requests
import json
from typing import Dict

BASE_URL = "http://localhost:8000"

class AuthTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
        self.user_data = None
    
    def print_response(self, response: requests.Response, title: str):
        """Красиво выводит ответ"""
        print(f"\n{'='*50}")
        print(f"📡 {title}")
        print(f"Status: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Response: {response.text}")
        print(f"{'='*50}")
    
    def test_register(self):
        """Тест регистрации"""
        data = {
            "email": "test@example.com",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
            "name": "Test User"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/register",
            json=data
        )
        
        self.print_response(response, "Регистрация")
        
        if response.status_code == 201:
            result = response.json()
            self.access_token = result['tokens']['access_token']
            self.refresh_token = result['tokens']['refresh_token']
            self.user_data = result['user']
        
        return response
    
    def test_login(self):
        """Тест входа"""
        data = {
            "email": "test@example.com",
            "password": "TestPassword123"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/login/json",
            json=data
        )
        
        self.print_response(response, "Вход")
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result['tokens']['access_token']
            self.refresh_token = result['tokens']['refresh_token']
        
        return response
    
    def test_get_me(self):
        """Тест получения профиля"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.get(
            f"{self.base_url}/auth/me",
            headers=headers
        )
        
        self.print_response(response, "Профиль пользователя")
        return response
    
    def test_update_profile(self):
        """Тест обновления профиля"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        data = {
            "age": 25,
            "weight": 70.5,
            "height": 175.0,
            "goal": "muscle_gain",
            "level": "beginner",
            "equipment": ["dumbbells", "barbell"]
        }
        
        response = requests.put(
            f"{self.base_url}/users/me",
            headers=headers,
            json=data
        )
        
        self.print_response(response, "Обновление профиля")
        return response
    
    def test_refresh_token(self):
        """Тест обновления токена"""
        data = {"refresh_token": self.refresh_token}
        
        response = requests.post(
            f"{self.base_url}/auth/refresh",
            json=data
        )
        
        self.print_response(response, "Обновление токена")
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result['tokens']['access_token']
            self.refresh_token = result['tokens']['refresh_token']
        
        return response
    
    def test_wrong_password(self):
        """Тест неверного пароля"""
        data = {
            "email": "test@example.com",
            "password": "WrongPassword123"
        }
        
        response = requests.post(
            f"{self.base_url}/auth/login/json",
            json=data
        )
        
        self.print_response(response, "Неверный пароль")
        return response
    
    def test_unauthorized(self):
        """Тест без авторизации"""
        response = requests.get(f"{self.base_url}/auth/me")
        self.print_response(response, "Без авторизации")
        return response
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("\n🧪 ЗАПУСК ТЕСТОВ АУТЕНТИФИКАЦИИ")
        print("="*50)
        
        # Тест 1: Регистрация
        self.test_register()
        
        # Тест 2: Вход
        self.test_login()
        
        # Тест 3: Получение профиля
        self.test_get_me()
        
        # Тест 4: Обновление профиля
        self.test_update_profile()
        
        # Тест 5: Обновление токена
        self.test_refresh_token()
        
        # Тест 6: Неверный пароль
        self.test_wrong_password()
        
        # Тест 7: Без авторизации
        self.test_unauthorized()
        
        print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    tester = AuthTester(BASE_URL)
    tester.run_all_tests()
