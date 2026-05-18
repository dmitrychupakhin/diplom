from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ...core.database import get_db
from ...models.user import User
from ...schemas.user import (
    UserUpdate, 
    UserProfile,
    InjuryCreate,
    InjuryResponse,
    MessageResponse,
    ErrorResponse
)
from ...services.user_service import UserService
from ..dependencies import get_current_user

router = APIRouter()

@router.get(
    "/me",
    response_model=UserProfile,
    summary="Получить профиль",
    description="Возвращает профиль текущего пользователя"
)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Получение своего профиля"""
    return UserProfile.from_orm(current_user)

@router.put(
    "/me",
    response_model=UserProfile,
    summary="Обновить профиль",
    description="Обновляет данные профиля пользователя"
)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление профиля"""
    updated_user = UserService.update_user(db, current_user, user_update)
    return UserProfile.from_orm(updated_user)

@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Удалить аккаунт",
    description="Деактивирует аккаунт пользователя"
)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление аккаунта"""
    UserService.delete_user(db, current_user)
    return MessageResponse(message="Аккаунт успешно деактивирован")

# ==================== Травмы ====================

@router.get(
    "/me/injuries",
    response_model=List[InjuryResponse],
    summary="Мои травмы",
    description="Получить список травм пользователя"
)
async def get_my_injuries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка травм"""
    injuries = UserService.get_user_injuries(db, current_user.id)
    return [InjuryResponse.from_orm(injury) for injury in injuries]

@router.post(
    "/me/injuries",
    response_model=InjuryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить травму",
    description="Добавляет информацию о травме в профиль"
)
async def add_injury(
    injury_data: InjuryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавление травмы"""
    injury = UserService.add_injury(db, current_user.id, injury_data)
    return InjuryResponse.from_orm(injury)

@router.delete(
    "/me/injuries/{injury_id}",
    response_model=MessageResponse,
    summary="Удалить травму",
    description="Удаляет информацию о травме"
)
async def remove_injury(
    injury_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление травмы"""
    success = UserService.remove_injury(db, injury_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Травма не найдена"
        )
    return MessageResponse(message="Травма удалена")

# ==================== Статистика ====================

@router.get(
    "/me/stats",
    summary="Моя статистика",
    description="Возвращает статистику тренировок пользователя"
)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики"""
    stats = UserService.get_user_stats(db, current_user.id)
    if not stats:
        stats = UserService.create_user_stats(db, current_user.id)
    
    return {
        "total_workouts": stats.total_workouts,
        "completed_workouts": stats.completed_workouts,
        "total_duration_minutes": stats.total_duration_minutes,
        "total_calories_burned": stats.total_calories_burned,
        "current_streak": stats.current_streak,
        "longest_streak": stats.longest_streak,
        "experience_points": stats.experience_points,
        "level_progress": stats.level_progress
    }