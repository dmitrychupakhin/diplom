import sys
import os
from pathlib import Path

def find_project_root():
    """Автоматически находит корень проекта"""
    # Проверяем текущую директорию
    current = Path.cwd()
    
    # Признаки, что мы в корне проекта
    root_indicators = ['backend', 'docker-compose.yml', '.git']
    # Признаки, что мы в backend
    backend_indicators = ['app/main.py', 'app/core', '.env', 'requirements.txt']
    
    # Проверяем, не в backend ли мы уже
    if any((current / ind).exists() for ind in backend_indicators):
        return current, current  # Мы в backend
    
    # Проверяем, не в корне ли мы
    if any((current / ind).exists() for ind in root_indicators):
        backend = current / 'backend'
        if backend.exists():
            return current, backend
    
    # Ищем backend рядом
    for parent in [current] + list(current.parents)[:3]:
        backend = parent / 'backend'
        if backend.exists() and (backend / 'app').exists():
            return parent, backend
    
    return current, None

def main():
    print("=" * 60)
    print("🔍 ДИАГНОСТИКА ПРОЕКТА")
    print("=" * 60)
    
    root, backend = find_project_root()
    
    print(f"\n📍 Текущая директория: {Path.cwd()}")
    print(f"📍 Корень проекта: {root}")
    
    if backend:
        print(f"📍 Backend директория: {backend}")
    else:
        print("❌ Backend директория не найдена!")
        return
    
    # Проверка .env файла
    print("\n" + "=" * 60)
    print("📁 ПРОВЕРКА ФАЙЛОВ")
    print("=" * 60)
    
    # Ищем .env в нескольких местах
    env_locations = [
        backend / '.env',
        root / '.env',
        Path('.env'),
        Path.cwd() / '.env',
    ]
    
    env_found = False
    for loc in env_locations:
        if loc.exists():
            print(f"✅ .env найден: {loc}")
            print(f"   Размер: {loc.stat().st_size} байт")
            
            # Показываем содержимое (скрывая ключи)
            with open(loc) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key = line.split('=')[0]
                            value = line.split('=')[1] if len(line.split('=')) > 1 else ''
                            if 'KEY' in key or 'SECRET' in key or 'PASSWORD' in key:
                                print(f"   🔑 {key}=***скрыто***")
                            else:
                                print(f"   {key}={value}")
            env_found = True
            break
    
    if not env_found:
        print("❌ .env файл не найден!")
        print(f"   Ожидаемые расположения:")
        for loc in env_locations:
            print(f"   - {loc} {'✅' if loc.exists() else '❌'}")
    
    # Проверка структуры backend
    print("\n📁 Структура backend:")
    if backend.exists():
        for item in sorted(backend.rglob("*.py")):
            rel_path = item.relative_to(backend)
            if '__pycache__' not in str(rel_path):
                print(f"   📄 {rel_path}")
    else:
        print("   ❌ Директория backend не найдена")
    
    # Проверка ключевых файлов
    print("\n🔑 КЛЮЧЕВЫЕ ФАЙЛЫ:")
    key_files = [
        'app/main.py',
        'app/core/config.py',
        'app/core/database.py',
        'app/models/user.py',
        'app/services/gigachat_client.py',
        'app/services/workout_generator.py',
    ]
    
    for f in key_files:
        path = backend / f
        if path.exists():
            print(f"   ✅ {f}")
        else:
            print(f"   ❌ {f} - ОТСУТСТВУЕТ")
    
    # Проверка Python окружения
    print("\n🐍 PYTHON ОКРУЖЕНИЕ:")
    print(f"   Версия: {sys.version}")
    print(f"   Исполняемый файл: {sys.executable}")
    
    # Проверка зависимостей
    print("\n📦 ЗАВИСИМОСТИ:")
    deps = ['fastapi', 'uvicorn', 'sqlalchemy', 'httpx', 'pydantic', 'gigachat']
    for dep in deps:
        try:
            mod = __import__(dep)
            version = getattr(mod, '__version__', 'установлен')
            print(f"   ✅ {dep}: {version}")
        except ImportError:
            print(f"   ❌ {dep}: не установлен")
    
    print("\n" + "=" * 60)
    print("💡 РЕКОМЕНДАЦИИ:")
    print("=" * 60)
    
    if not env_found:
        print("1. Создайте .env файл в директории backend:")
        print(f"   touch {backend}/.env")
        print("2. Добавьте в него необходимые переменные")
    
    if not (backend / 'app/main.py').exists():
        print("3. Убедитесь, что структура проекта правильная:")
        print("   backend/app/main.py должен существовать")

if __name__ == "__main__":
    main()