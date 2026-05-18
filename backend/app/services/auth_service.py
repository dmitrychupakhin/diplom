from sqlalchemy.orm import Session
from typing import Optional, Tuple
from datetime import timedelta
import uuid

from ..models.user import User
from ..schemas.user import UserCreate, UserLogin
from ..core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from ..core.config import settings

class AuthService:
    """Сервис для работы с аутентификацией"""
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> Tuple[User, dict]:
        """
        Регистрация нового пользователя
        
        Args:
            db: Сессия БД
            user_data: Данные для регистрации
        
        Returns:
            Кортеж (пользователь, токены)
        
        Raises:
            ValueError: Если email уже занят
        """
        # Проверяем, существует ли пользователь
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Пользователь с таким email уже существует")
        
        # Создаем нового пользователя
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            name=user_data.name
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Создаем токены
        tokens = AuthService._create_tokens(user)
        
        return user, tokens
    
    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> Tuple[User, dict]:
        """
        Вход пользователя
        
        Args:
            db: Сессия БД
            login_data: Данные для входа
        
        Returns:
            Кортеж (пользователь, токены)
        
        Raises:
            ValueError: Если неверный email или пароль
        """
        # Ищем пользователя
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise ValueError("Неверный email или пароль")
        
        # Проверяем пароль
        if not verify_password(login_data.password, user.password_hash):
            raise ValueError("Неверный email или пароль")
        
        # Проверяем, активен ли пользователь
        if user.is_active != 'Y':
            raise ValueError("Аккаунт деактивирован")
        
        # Создаем токены
        tokens = AuthService._create_tokens(user)
        
        return user, tokens
    
    @staticmethod
    def refresh_token(refresh_token: str, db: Session) -> dict:
        """
        Обновляет access токен по refresh токену
        
        Args:
            refresh_token: Refresh токен
            db: Сессия БД
        
        Returns:
            Новые токены
        
        Raises:
            ValueError: Если токен невалидный
        """
        # Проверяем токен
        payload = verify_token(refresh_token)
        if not payload:
            raise ValueError("Невалидный refresh токен")
        
        # Проверяем тип токена
        if payload.get("type") != "refresh":
            raise ValueError("Неверный тип токена")
        
        # Получаем пользователя
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        
        if not user:
            raise ValueError("Пользователь не найден")
        
        # Создаем новые токены
        return AuthService._create_tokens(user)
    
    @staticmethod
    def change_password(
        db: Session,
        user: User,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Смена пароля пользователя
        
        Args:
            db: Сессия БД
            user: Пользователь
            old_password: Старый пароль
            new_password: Новый пароль
        
        Returns:
            True если успешно
        
        Raises:
            ValueError: Если старый пароль неверный
        """
        # Проверяем старый пароль
        if not verify_password(old_password, user.password_hash):
            raise ValueError("Неверный старый пароль")
        
        # Устанавливаем новый пароль
        user.password_hash = get_password_hash(new_password)
        db.commit()
        
        return True
    
    @staticmethod
    def _create_tokens(user: User) -> dict:
        """
        Создает access и refresh токены
        
        Args:
            user: Пользователь
        
        Returns:
            Словарь с токенами
        """
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        refresh_token = create_refresh_token(
            subject=user.id,
            expires_delta=timedelta(days=7)
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
