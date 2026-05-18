# -*- coding: utf-8 -*-
import asyncio
import json
from app.services.workout_generator import AIWorkoutGenerator
from app.services.gigachat_client import GigaChatClient

# Тестовые данные пользователя
TEST_USER_DATA = {
    "gender": "male",
    "age": 25,
    "weight": 75,
    "height": 180,
    "goal": "weight_loss",
    "level": "beginner",
    "equipment": ["none"],
    "injuries": ["knee_pain"],
    "duration": 45,
    "focus_areas": ["full_body", "abs"]
}

async def test_ai_generation():
    """Тест AI генерации"""
    print("\n" + "="*60)
    print("🤖 ТЕСТИРОВАНИЕ AI ГЕНЕРАЦИИ ТРЕНИРОВОК")
    print("="*60)
    
    # Проверяем статус AI
    client = GigaChatClient()
    print(f"\n📡 Статус GigaChat:")
    print(f"   API ключ: {'✅ Установлен' if client.api_key else '❌ Отсутствует'}")
    print(f"   SDK: {'✅ Доступен' if client.sdk_client else '❌ Недоступен'}")
    
    if not client.api_key:
        print("\n⚠️ API ключ не установлен. AI генерация недоступна.")
        print("Добавьте ключ в .env файл: GIGACHAT_API_KEY=ваш_ключ")
        return
    
    # Тестируем генерацию
    print("\n🔄 Генерация тренировки...")
    
    try:
        # Создаем промпт вручную для теста
        prompt = f"""Создай тренировку для клиента:
        - Цель: похудение
        - Уровень: новичок
        - Ограничения: боль в коленях
        - Оборудование: только вес тела
        - Длительность: 30 минут
        
        Исключи упражнения с нагрузкой на колени.
        """
        
        result = await client.generate_workout(prompt, validate_json=True)
        
        if result.success:
            print("✅ Генерация успешна!")
            print(f"\n📊 Результат:")
            print(f"   Время генерации: {result.generation_time:.2f}с")
            print(f"   Попыток: {result.attempts}")
            
            if result.workout_data:
                print(f"\n💪 Тренировка:")
                print(f"   Разминка: {len(result.workout_data.get('warmup', []))} упр.")
                print(f"   Основная часть: {len(result.workout_data.get('main_workout', []))} упр.")
                print(f"   Заминка: {len(result.workout_data.get('cooldown', []))} упр.")
                
                # Сохраняем результат
                with open("test_workout_result.json", "w", encoding="utf-8") as f:
                    json.dump(result.workout_data, f, ensure_ascii=False, indent=2)
                print(f"\n📁 Результат сохранен в test_workout_result.json")
        else:
            print(f"❌ Генерация не удалась: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def test_fallback():
    """Тест fallback генератора"""
    print("\n" + "="*60)
    print("🔄 ТЕСТИРОВАНИЕ FALLBACK ГЕНЕРАТОРА")
    print("="*60)
    
    generator = AIWorkoutGenerator()
    
    # Тестовый объект пользователя (заглушка)
    class MockUser:
        gender = "male"
        age = 25
        weight = 75
        height = 180
        goal = "weight_loss"
        level = "beginner"
        equipment = ["none"]
        injuries = []
        workouts_per_week = 3
    
    user = MockUser()
    user_data = {
        "gender": user.gender,
        "age": user.age,
        "weight": user.weight,
        "height": user.height,
        "goal": user.goal,
        "level": user.level,
        "equipment": user.equipment,
        "injuries": user.injuries,
        "duration": 30,
        "focus_areas": ["full_body"]
    }
    
    print("\n🔄 Генерация через fallback...")
    workout = await generator.generate(
        user_data=user_data,
        use_ai=False  # Принудительно отключаем AI
    )
    
    print(f"✅ Fallback сработал!")
    print(f"   Упражнений: {len(workout.get('main_workout', []))}")
    print(f"   Генератор: {workout.get('metadata', {}).get('generated_by')}")

if __name__ == "__main__":
    # Запускаем тесты
    asyncio.run(test_ai_generation())
    asyncio.run(test_fallback())
    
    print("\n" + "="*60)
    print("✅ Тестирование завершено!")
    print("="*60)