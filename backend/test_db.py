# backend/test_db.py
"""
Скрипт для тестирования подключения к базе данных и создания таблиц
"""
import sys
from pathlib import Path

# Добавляем путь к проекту
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

try:
    from app.core.database import create_tables, check_db_connection, SessionLocal
    from app.models.user import User, Injury, Workout
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Проверьте структуру проекта и наличие __init__.py файлов")
    sys.exit(1)

import uuid

def test_database():
    print("=" * 50)
    print("🧪 ТЕСТИРОВАНИЕ БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    # 1. Проверяем подключение
    print("\n1️⃣ Проверка подключения...")
    if not check_db_connection():
        print("❌ Не удалось подключиться к базе данных")
        return False
    
    # 2. Создаем таблицы
    print("\n2️⃣ Создание таблиц...")
    try:
        create_tables()
        print("✅ Таблицы созданы успешно")
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Тестируем CRUD операции
    print("\n3️⃣ Тестирование CRUD операций...")
    db = SessionLocal()
    
    try:
        # Создаем тестового пользователя
        test_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            password_hash="hashed_password_123",
            name="Test User",
            age=25,
            weight=70.5,
            height=175.0,
            gender="male",
            goal="muscle_gain",
            level="beginner",
            equipment=["dumbbells", "barbell"]
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Создан пользователь: {test_user.email}")
        
        # Создаем травму
        injury = Injury(
            user_id=test_user.id,
            injury_name="Боль в колене",
            body_part="knee",
            severity="mild",
            notes="Беспокоит при приседаниях"
        )
        
        db.add(injury)
        db.commit()
        print(f"✅ Добавлена травма: {injury.injury_name}")
        
        # Создаем тренировку
        workout = Workout(
            user_id=test_user.id,
            workout_json={
                "warmup": [{"name": "Jumping Jacks", "duration": "2 min"}],
                "main_workout": [
                    {"exercise": "Push-ups", "sets": 3, "reps": "12", "rest_sec": 60}
                ],
                "cooldown": [{"exercise": "Stretching", "duration": "5 min"}]
            },
            goal="muscle_gain",
            duration=45,
            status="completed"
        )
        
        db.add(workout)
        db.commit()
        print(f"✅ Создана тренировка")
        
        # Читаем данные
        user = db.query(User).filter(User.email == "test@example.com").first()
        print(f"\n📊 Данные пользователя:")
        print(f"   Имя: {user.name}")
        print(f"   Цель: {user.goal}")
        print(f"   Уровень: {user.level}")
        
        # Проверяем связи
        injuries_count = db.query(Injury).filter(Injury.user_id == user.id).count()
        workouts_count = db.query(Workout).filter(Workout.user_id == user.id).count()
        print(f"   Травмы: {injuries_count}")
        print(f"   Тренировки: {workouts_count}")
        
        # Удаляем тестовые данные в правильном порядке
        db.query(Workout).filter(Workout.user_id == test_user.id).delete()
        db.query(Injury).filter(Injury.user_id == test_user.id).delete()
        db.delete(test_user)
        db.commit()
        print(f"\n🗑️ Тестовые данные удалены")
        
        print("\n" + "=" * 50)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)