from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
from functools import lru_cache

class Settings(BaseSettings):
  
    DATABASE_URL: str = "postgresql://postgres:12345678@localhost:5432/fitness_ai"
    
    # JWT
    SECRET_KEY: str = "my-super-secret-key-change-in-production-123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # GigaChat API
    GIGACHAT_CLIENT_ID: Optional[str] = None
    GIGACHAT_CLIENT_SECRET: Optional[str] = None
    GIGACHAT_AUTH_URL: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    GIGACHAT_API_URL: str = "https://gigachat.devices.sberbank.ru/api/v1"
    GIGACHAT_SCOPE: str = "GIGACHAT_API_PERS"
    GIGACHAT_MODEL: str = "GigaChat:latest"
    
    # Настройки AI генерации
    AI_MAX_RETRIES: int = 3
    AI_TIMEOUT_SECONDS: int = 30
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2000
    
    # App
    APP_NAME: str = "Fitness AI Generator"
    DEBUG: bool = True
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Игнорируем лишние переменные из .env

@lru_cache()
def get_settings() -> Settings:
    """Получить настройки с кэшированием"""
    return Settings()

# Создаем экземпляр для использования
settings = get_settings()

# Проверяем конфигурацию при запуске
if settings.DEBUG:
    print("🔧 Загружена конфигурация:")
    print(f"  📦 База данных: {settings.DATABASE_URL}")
    print(f"  🔑 GigaChat настроен: {bool(settings.GIGACHAT_CLIENT_ID and settings.GIGACHAT_CLIENT_SECRET)}")
    print(f"  🤖 AI генерация: {'включена' if settings.GIGACHAT_CLIENT_ID else 'выключена (используется fallback)'}")