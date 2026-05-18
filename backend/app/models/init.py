# backend/app/models/__init__.py
from .user import User, Injury, Workout

# Экспортируем все модели для удобства импорта
__all__ = ['User', 'Injury', 'Workout']