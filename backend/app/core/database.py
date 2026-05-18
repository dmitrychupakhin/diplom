from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import sys

# Создаем движок базы данных
try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
except Exception as e:
    print(f"Ошибка создания движка базы данных: {e}")
    sys.exit(1)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection():
    """Проверка подключения к базе данных"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("Подключение к базе данных успешно")
            return True
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        print("\n Проверьте:")
        print("1. Запущен ли Docker с PostgreSQL?")
        print("2. Правильный ли пароль в DATABASE_URL?")
        print("3. Соответствует ли хост и порт?")
        return False


def create_tables():
    """Создание всех таблиц"""
    from app.models.user import User, Injury, Workout
    Base.metadata.create_all(bind=engine)