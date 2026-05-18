from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

# Контекст для хеширования паролей
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Количество раундов хеширования
)

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создает JWT токен доступа
    
    Args:
        subject: Идентификатор субъекта (обычно user_id)
        expires_delta: Время жизни токена
    
    Returns:
        Закодированный JWT токен
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создает refresh токен для обновления access токена
    
    Args:
        subject: Идентификатор субъекта
        expires_delta: Время жизни токена
    
    Returns:
        Закодированный refresh токен
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля хешу
    
    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хешированный пароль
    
    Returns:
        True если пароль верный
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Хеширует пароль
    
    Args:
        password: Пароль в открытом виде
    
    Returns:
        Хешированный пароль
    """
    return pwd_context.hash(password)

def verify_token(token: str) -> Optional[dict]:
    """
    Проверяет и декодирует JWT токен
    
    Args:
        token: JWT токен
    
    Returns:
        Декодированные данные токена или None
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
