# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .core.database import create_tables, check_db_connection, engine, Base
from .api.routes import auth, users, workouts

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Жизненный цикл приложения.
    Выполняется при запуске и завершении.
    """
    # Действия при запуске
    print("🚀 Запуск Fitness AI Generator...")
    
    # Создаем таблицы
    create_tables()
    
    # Проверяем подключение к БД
    check_db_connection()
    
    yield
    
    # Действия при завершении
    print("👋 Завершение работы...")

# Создаем приложение
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="""
    ## AI-Powered Workout Generation System
    
    Интеллектуальная система для генерации персонализированных тренировок.
    
    ### Возможности:
    - 🤖 AI-генерация тренировок через GigaChat
    - 📊 Учет физических параметров и ограничений
    - 📝 История тренировок
    - 👤 Управление профилем
    
    ### Технологии:
    - FastAPI + SQLAlchemy + PostgreSQL
    - GigaChat API для AI-генерации
    - JWT аутентификация
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(auth.router, prefix="/auth", tags=["🔐 Аутентификация"])
app.include_router(users.router, prefix="/users", tags=["👤 Пользователи"])
app.include_router(workouts.router, prefix="/workouts", tags=["💪 Тренировки"])

# Корневой эндпоинт
@app.get("/", tags=["📚 Общее"])
async def root():
    """Корневой эндпоинт с информацией о системе"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "🟢 Online",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "users": "/users",
            "workouts": "/workouts"
        }
    }

# Эндпоинт проверки здоровья
@app.get("/health", tags=["📚 Общее"])
async def health_check():
    """Проверка здоровья системы"""
    db_status = check_db_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "version": "1.0.0"
    }

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )