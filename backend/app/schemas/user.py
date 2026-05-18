from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import re

# ==================== Базовые схемы ====================

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = Field(None, min_length=2, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=14, le=120)
    weight: Optional[float] = Field(None, ge=30, le=300)
    height: Optional[float] = Field(None, ge=100, le=250)
    gender: Optional[str] = Field(None, pattern='^(male|female|other)$')
    goal: Optional[str] = None
    level: Optional[str] = None
    equipment: Optional[List[str]] = None
    workouts_per_week: Optional[int] = Field(None, ge=1, le=7)
    
    @validator('goal')
    def validate_goal(cls, v):
        allowed_goals = ['weight_loss', 'muscle_gain', 'endurance', 'strength']
        if v and v not in allowed_goals:
            raise ValueError(f'Цель должна быть одной из: {allowed_goals}')
        return v
    
    @validator('level')
    def validate_level(cls, v):
        allowed_levels = ['beginner', 'intermediate', 'advanced']
        if v and v not in allowed_levels:
            raise ValueError(f'Уровень должен быть одним из: {allowed_levels}')
        return v

class UserProfile(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str]
    age: Optional[int]
    weight: Optional[float]
    height: Optional[float]
    gender: Optional[str]
    goal: Optional[str]
    level: Optional[str]
    equipment: Optional[List[str]]
    workouts_per_week: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Схемы для травм ====================

class InjuryBase(BaseModel):
    injury_name: str = Field(..., min_length=2, max_length=100)
    body_part: Optional[str] = None
    severity: Optional[str] = Field(None, pattern='^(mild|moderate|severe)$')
    notes: Optional[str] = None

class InjuryCreate(InjuryBase):
    pass

class InjuryResponse(InjuryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Схемы для тренировок ====================

class WorkoutExercise(BaseModel):
    """Схема упражнения в тренировке"""
    name: Optional[str] = None
    exercise: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[str] = None
    rest_sec: Optional[int] = None
    duration: Optional[str] = None
    notes: Optional[str] = None

class WorkoutGenerateRequest(BaseModel):
    """Запрос на генерацию тренировки"""
    goal: Optional[str] = None
    level: Optional[str] = None
    equipment: Optional[List[str]] = None
    injuries: Optional[List[str]] = None
    duration: Optional[int] = Field(45, ge=15, le=120)
    use_ai: Optional[bool] = True
    focus_areas: Optional[List[str]] = None  # ['chest', 'legs', 'back', etc.]
    
    @validator('duration')
    def validate_duration(cls, v):
        if v % 5 != 0:
            raise ValueError('Длительность должна быть кратна 5 минутам')
        return v

class WorkoutData(BaseModel):
    """Данные тренировки"""
    warmup: List[WorkoutExercise]
    main_workout: List[WorkoutExercise]
    cooldown: List[WorkoutExercise]
    notes: Optional[str] = None
    metadata: Optional[dict] = None

class WorkoutResponse(BaseModel):
    """Ответ с тренировкой"""
    id: UUID
    workout_data: WorkoutData
    goal: Optional[str]
    duration: Optional[int]
    status: str
    ai_generated: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class WorkoutHistoryItem(BaseModel):
    """Элемент истории тренировок"""
    id: UUID
    goal: Optional[str]
    duration: Optional[int]
    status: str
    ai_generated: str
    created_at: datetime
    completed_at: Optional[datetime]
    feedback_rating: Optional[int]
    
    class Config:
        from_attributes = True

class WorkoutFeedback(BaseModel):
    """Обратная связь по тренировке"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_text: Optional[str] = None
    status: Optional[str] = Field(None, pattern='^(completed|skipped|in_progress)$')

# ==================== Схемы ответов ====================

class PaginatedResponse(BaseModel):
    """Пагинированный ответ"""
    items: List
    total: int
    page: int
    size: int
    pages: int

class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    detail: str
    success: bool = False

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str