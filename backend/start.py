import sys
import os
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

def check_environment():
    """Проверка окружения перед запуском"""
    print("=" * 60)
    print("🔍 ПРОВЕРКА ОКРУЖЕНИЯ")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # Проверяем .env файл
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env файл найден")
    else:
        warnings.append(".env файл не найден, используются значения по умолчанию")
    
    # Проверяем Python зависимости
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
    except ImportError:
        errors.append("FastAPI не установлен")
    
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError:
        errors.append("SQLAlchemy не установлен")
    
    # Проверяем GigaChat настройки
    from app.core.config import settings
    if settings.GIGACHAT_CLIENT_ID and settings.GIGACHAT_CLIENT_SECRET:
        print("✅ GigaChat настроен")
    else:
        warnings.append("GigaChat не настроен (AI генерация будет недоступна)")
    
    # Проверяем базу данных
    try:
        from app.core.database import check_db_connection
        if check_db_connection():
            print("✅ База данных доступна")
        else:
            warnings.append("База данных недоступна")
    except Exception as e:
        warnings.append(f"Ошибка подключения к БД: {e}")
    
    # Выводим результаты
    print("\n" + "=" * 60)
    
    if errors:
        print("❌ КРИТИЧЕСКИЕ ОШИБКИ:")
        for error in errors:
            print(f"   - {error}")
        print("\nИсправьте ошибки перед запуском!")
        return False
    
    if warnings:
        print("⚠️ ПРЕДУПРЕЖДЕНИЯ:")
        for warning in warnings:
            print(f"   - {warning}")
    
    print("✅ Проверка завершена, можно запускать приложение")
    return True

if __name__ == "__main__":
    if check_environment():
        print("\n🚀 Запуск приложения...")
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )