from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from ...core.database import get_db
from ...schemas.user import (
    UserCreate, 
    UserLogin, 
    Token, 
    TokenRefresh,
    UserProfile,
    MessageResponse,
    ErrorResponse
)
from ...services.auth_service import AuthService
from ..dependencies import get_current_user
from ...models.user import User

router = APIRouter()

@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="""
    Регистрирует нового пользователя в системе.
    
    Требования к паролю:
    - Минимум 8 символов
    - Хотя бы одна заглавная буква
    - Хотя бы одна строчная буква
    - Хотя бы одна цифра
    """,
    responses={
        201: {"description": "Пользователь успешно создан"},
        400: {"model": ErrorResponse, "description": "Ошибка валидации"},
        409: {"model": ErrorResponse, "description": "Email уже занят"}
    }
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Регистрация нового пользователя
    
    - **email**: Email пользователя
    - **password**: Пароль (мин. 8 символов, заглавные и строчные буквы, цифры)
    - **password_confirm**: Подтверждение пароля
    - **name**: Имя пользователя (опционально)
    """
    try:
        user, tokens = AuthService.register_user(db, user_data)
        
        return {
            "success": True,
            "message": "Регистрация успешна",
            "user": UserProfile.from_orm(user),
            "tokens": tokens
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.post(
    "/login",
    response_model=dict,
    summary="Вход в систему",
    description="Аутентифицирует пользователя и возвращает JWT токены",
    responses={
        200: {"description": "Успешный вход"},
        401: {"model": ErrorResponse, "description": "Неверные учетные данные"}
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Вход в систему
    
    Использует OAuth2 форму:
    - **username**: Email пользователя
    - **password**: Пароль
    """
    try:
        login_data = UserLogin(
            email=form_data.username,
            password=form_data.password
        )
        
        user, tokens = AuthService.login_user(db, login_data)
        
        return {
            "success": True,
            "message": "Вход выполнен успешно",
            "user": UserProfile.from_orm(user),
            "tokens": tokens
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post(
    "/login/json",
    response_model=dict,
    summary="Вход в систему (JSON)",
    description="Альтернативный вход через JSON тело запроса",
    responses={
        200: {"description": "Успешный вход"},
        401: {"model": ErrorResponse, "description": "Неверные учетные данные"}
    }
)
async def login_json(
    login_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Вход в систему через JSON
    
    - **email**: Email пользователя
    - **password**: Пароль
    """
    try:
        user, tokens = AuthService.login_user(db, login_data)
        
        return {
            "success": True,
            "message": "Вход выполнен успешно",
            "user": UserProfile.from_orm(user),
            "tokens": tokens
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post(
    "/refresh",
    response_model=dict,
    summary="Обновление токена",
    description="Обновляет access токен используя refresh токен",
    responses={
        200: {"description": "Токены обновлены"},
        401: {"model": ErrorResponse, "description": "Невалидный refresh токен"}
    }
)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
) -> Any:
    """
    Обновление токенов
    
    - **refresh_token**: Действующий refresh токен
    """
    try:
        tokens = AuthService.refresh_token(token_data.refresh_token, db)
        
        return {
            "success": True,
            "message": "Токены обновлены",
            "tokens": tokens
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Смена пароля",
    description="Изменяет пароль текущего пользователя"
)
async def change_password(
    old_password: str = Body(..., description="Старый пароль"),
    new_password: str = Body(..., description="Новый пароль"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Смена пароля
    
    - **old_password**: Текущий пароль
    - **new_password**: Новый пароль
    """
    try:
        AuthService.change_password(db, current_user, old_password, new_password)
        return MessageResponse(
            message="Пароль успешно изменен",
            success=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/me",
    response_model=UserProfile,
    summary="Текущий пользователь",
    description="Возвращает профиль текущего авторизованного пользователя"
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение профиля текущего пользователя
    
    Требуется авторизация (JWT токен в заголовке Authorization)
    """
    return UserProfile.from_orm(current_user)

@router.get(
    "/check",
    response_model=dict,
    summary="Проверка токена",
    description="Проверяет валидность JWT токена"
)
async def check_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Проверка валидности токена
    
    Возвращает информацию о пользователе, если токен валидный
    """
    return {
        "success": True,
        "message": "Токен валидный",
        "user_id": str(current_user.id),
        "email": current_user.email
    }
