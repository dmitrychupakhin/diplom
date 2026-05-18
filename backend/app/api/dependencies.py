from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Generator, Optional
from jose import JWTError
import uuid

from ..core.database import get_db
from ..core.config import settings
from ..models.user import User
from ..core.security import verify_token

# Схема OAuth2 для получения токена
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT",
    description="Введите JWT токен"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Получает текущего пользователя по JWT токену
    
    Args:
        token: JWT токен из заголовка Authorization
        db: Сессия базы данных
    
    Returns:
        Объект пользователя
    
    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Проверяем токен
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    # Получаем user_id из токена
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Проверяем тип токена
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена"
        )
    
    # Ищем пользователя в БД
    try:
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    except ValueError:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    # Проверяем, активен ли пользователь
    if user.is_active != 'Y':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Проверяет, что пользователь активен
    
    Args:
        current_user: Текущий пользователь
    
    Returns:
        Активный пользователь
    """
    if current_user.is_active != 'Y':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь"
        )
    return current_user

async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Получает пользователя, если токен предоставлен (для опциональной аутентификации)
    """
    if not token:
        return None
    
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
