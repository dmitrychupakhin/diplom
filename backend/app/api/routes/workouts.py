from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ...core.database import get_db
from ...models.user import User, Workout
from ...schemas.user import (
    WorkoutGenerateRequest,
    WorkoutResponse,
    WorkoutFeedback,
    MessageResponse
)
from ...services.user_service import UserService
from ...services.workout_generator import AIWorkoutGenerator
from ..dependencies import get_current_user

router = APIRouter()

# Создаем генератор
workout_generator = AIWorkoutGenerator()

@router.post(
    "/generate",
    response_model=WorkoutResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Сгенерировать тренировку"
)
async def generate_workout(
    request: WorkoutGenerateRequest = WorkoutGenerateRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Генерация новой тренировки"""
    
    # Собираем данные пользователя
    user_data = {
        "name": current_user.name,
        "age": current_user.age,
        "weight": current_user.weight,
        "height": current_user.height,
        "gender": current_user.gender,
        "goal": request.goal or current_user.goal or "weight_loss",
        "level": request.level or current_user.level or "beginner",
        "equipment": request.equipment or current_user.equipment or ["none"],
        "injuries": request.injuries or [
            injury.injury_name 
            for injury in current_user.injuries 
            if injury.is_active == 'Y'
        ],
        "duration": request.duration or 45,
        "focus_areas": request.focus_areas or ["full_body"],
        "workouts_per_week": current_user.workouts_per_week or 3
    }
    
    # Генерируем тренировку
    workout_data = await workout_generator.generate(
        user_data,
        use_ai=request.use_ai
    )
    
    # Сохраняем в БД
    workout = Workout(
        user_id=current_user.id,
        workout_json=workout_data,
        goal=user_data["goal"],
        duration=user_data["duration"],
        calories_estimate=workout_data.get("metadata", {}).get("estimated_calories"),
        focus_areas=user_data["focus_areas"],
        status="pending",
        ai_generated='Y' if workout_data.get("metadata", {}).get("generated_by") == "ai_generated" else 'N',
        generation_time=workout_data.get("metadata", {}).get("generation_time_seconds")
    )
    
    db.add(workout)
    db.commit()
    db.refresh(workout)
    
    return WorkoutResponse(
        id=workout.id,
        workout_data=workout_data,
        goal=workout.goal,
        duration=workout.duration,
        status=workout.status,
        ai_generated=workout.ai_generated,
        created_at=workout.created_at
    )

@router.get("/history")
async def get_workout_history(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """История тренировок"""
    result = UserService.get_workout_history(db, current_user.id, page=page, size=size)
    return result

@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить тренировку по ID"""
    workout = UserService.get_workout_by_id(db, workout_id, current_user.id)
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тренировка не найдена")
    
    return WorkoutResponse(
        id=workout.id,
        workout_data=workout.workout_json,
        goal=workout.goal,
        duration=workout.duration,
        status=workout.status,
        ai_generated=workout.ai_generated,
        created_at=workout.created_at
    )

@router.put("/{workout_id}/feedback", response_model=MessageResponse)
async def update_workout_feedback(
    workout_id: UUID,
    feedback: WorkoutFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить отзыв о тренировке"""
    workout = UserService.update_workout_feedback(db, workout_id, current_user.id, feedback)
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тренировка не найдена")
    return MessageResponse(message="Отзыв сохранен")