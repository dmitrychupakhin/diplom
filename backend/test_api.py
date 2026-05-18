import requests
import json
from typing import Dict, Optional
from datetime import datetime

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token = None
        self.test_workout_id = None
    
    def print_result(self, title: str, response: requests.Response):
        """Красиво выводит результат"""
        print(f"\n{'='*60}")
        print(f"📊 {title}")
        print(f"Status: {response.status_code}")
        try:
            data = response.json()
            if isinstance(data, dict) and 'workout_data' in data:
                # Для тренировок показываем краткую информацию
                preview = {
                    "id": data.get("id"),
                    "status": data.get("status"),
                    "goal": data.get("goal"),
                    "duration": data.get("duration"),
                    "exercises": len(data.get("workout_data", {}).get("main_workout", []))
                }
                print(f"Preview: {json.dumps(preview, indent=2, ensure_ascii=False)}")
            else:
                print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response: {response.text[:200]}")
        print(f"{'='*60}")
    
    def register_and_login(self):
        """Регистрация и вход"""
        # Пробуем зарегистрироваться
        register_data = {
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
            "name": "Test User"
        }
        
        response = requests.post(f"{self.base_url}/auth/register", json=register_data)
        
        if response.status_code == 409:  # Пользователь уже существует
            # Входим
            login_data = {
                "email": "test@example.com",
                "password": "TestPassword123"
            }
            response = requests.post(f"{self.base_url}/auth/login/json", json=login_data)
        elif response.status_code == 201:
            pass  # Успешно зарегистрировались
        
        if response.status_code in [200, 201]:
            data = response.json()
            self.access_token = data['tokens']['access_token']
            self.print_result("Авторизация", response)
            return True
        else:
            self.print_result("Ошибка авторизации", response)
            return False
    
    def update_profile(self):
        """Обновление профиля"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        data = {
            "age": 25,
            "weight": 70.5,
            "height": 175.0,
            "goal": "weight_loss",
            "level": "beginner",
            "equipment": ["dumbbells", "none"],
            "workouts_per_week": 4
        }
        
        response = requests.put(
            f"{self.base_url}/users/me",
            headers=headers,
            json=data
        )
        
        self.print_result("Обновление профиля", response)
        return response.status_code == 200
    
    def add_injury(self):
        """Добавление травмы"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        data = {
            "injury_name": "Боль в колене",
            "body_part": "knee",
            "severity": "mild",
            "notes": "Беспокоит при глубоких приседаниях"
        }
        
        response = requests.post(
            f"{self.base_url}/users/me/injuries",
            headers=headers,
            json=data
        )
        
        self.print_result("Добавление травмы", response)
        return response.status_code == 201
    
    def generate_workout(self):
        """Генерация тренировки"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        data = {
            "goal": "weight_loss",
            "level": "beginner",
            "duration": 45,
            "use_ai": False,
            "focus_areas": ["full_body", "abs"],
            "injuries": ["knee_pain"]
        }
        
        response = requests.post(
            f"{self.base_url}/workouts/generate",
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            self.test_workout_id = response.json()["id"]
        
        self.print_result("Генерация тренировки", response)
        return response.status_code == 201
    
    def get_workout_history(self):
        """Получение истории тренировок"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.get(
            f"{self.base_url}/workouts/history?page=1&size=5",
            headers=headers
        )
        
        self.print_result("История тренировок", response)
        return response.status_code == 200
    
    def get_workout_detail(self):
        """Получение деталей тренировки"""
        if not self.test_workout_id:
            print("❌ Нет ID тренировки для просмотра")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.get(
            f"{self.base_url}/workouts/{self.test_workout_id}",
            headers=headers
        )
        
        self.print_result("Детали тренировки", response)
        return response.status_code == 200
    
    def submit_feedback(self):
        """Отправка отзыва о тренировке"""
        if not self.test_workout_id:
            print("❌ Нет ID тренировки для отзыва")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        data = {
            "rating": 4,
            "feedback_text": "Хорошая тренировка, но хотелось бы больше кардио",
            "status": "completed"
        }
        
        response = requests.put(
            f"{self.base_url}/workouts/{self.test_workout_id}/feedback",
            headers=headers,
            json=data
        )
        
        self.print_result("Отзыв о тренировке", response)
        return response.status_code == 200
    
    def get_stats(self):
        """Получение статистики"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        response = requests.get(
            f"{self.base_url}/users/me/stats",
            headers=headers
        )
        
        self.print_result("Статистика", response)
        return response.status_code == 200
    
    def run_full_test(self):
        """Запуск полного теста"""
        print("\n🚀 ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ API")
        print("="*60)
        
        tests = [
            ("Авторизация", self.register_and_login),
            ("Обновление профиля", self.update_profile),
            ("Добавление травмы", self.add_injury),
            ("Генерация тренировки", self.generate_workout),
            ("История тренировок", self.get_workout_history),
            ("Детали тренировки", self.get_workout_detail),
            ("Отзыв о тренировке", self.submit_feedback),
            ("Статистика", self.get_stats)
        ]
        
        results = []
        for name, test_func in tests:
            try:
                success = test_func()
                results.append((name, success))
            except Exception as e:
                print(f"❌ Ошибка в тесте '{name}': {e}")
                results.append((name, False))
        
        print("\n" + "="*60)
        print("📈 ИТОГИ ТЕСТИРОВАНИЯ")
        print("="*60)
        
        for name, success in results:
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {name}")
        
        success_count = sum(1 for _, s in results if s)
        print(f"\nПройдено тестов: {success_count}/{len(results)}")
        
        return success_count == len(results)

if __name__ == "__main__":
    tester = APITester(BASE_URL)
    tester.run_full_test()