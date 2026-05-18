from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    # Основные поля
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    
    # Физические параметры
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)  # в кг
    height = Column(Float, nullable=True)  # в см
    gender = Column(String(20), nullable=True)
    
    # Тренировочные параметры
    goal = Column(String(50), nullable=True)
    level = Column(String(20), nullable=True)
    equipment = Column(JSON, nullable=True)
    workouts_per_week = Column(Integer, default=3)
    
    # Дополнительные поля
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Системные поля
    is_active = Column(String(1), default='Y')
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    injuries = relationship("Injury", back_populates="user", cascade="all, delete-orphan")
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    workout_stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}', goal='{self.goal}')>"

class Injury(Base):
    __tablename__ = "injuries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    injury_name = Column(String(100), nullable=False)
    body_part = Column(String(50), nullable=True)
    severity = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(String(1), default='Y')
    
    user = relationship("User", back_populates="injuries")
    
    def __repr__(self):
        return f"<Injury(name='{self.injury_name}', body_part='{self.body_part}')>"

class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Данные тренировки
    workout_json = Column(JSON, nullable=False)
    goal = Column(String(50), nullable=True)
    duration = Column(Integer, nullable=True)
    calories_estimate = Column(Integer, nullable=True)
    focus_areas = Column(JSON, nullable=True)
    
    # Статус и обратная связь
    status = Column(String(20), default='pending')
    feedback_rating = Column(Integer, nullable=True)
    feedback_text = Column(Text, nullable=True)
    
    # Системные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    ai_generated = Column(String(1), default='Y')
    generation_time = Column(Float, nullable=True)  # время генерации в секундах
    
    user = relationship("User", back_populates="workouts")
    
    def __repr__(self):
        return f"<Workout(id='{self.id}', goal='{self.goal}', status='{self.status}')>"

class UserStats(Base):
    __tablename__ = "user_stats"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Статистика тренировок
    total_workouts = Column(Integer, default=0, nullable=False)
    completed_workouts = Column(Integer, default=0, nullable=False)
    total_duration_minutes = Column(Integer, default=0, nullable=False)
    total_calories_burned = Column(Integer, default=0, nullable=False)
    
    # Серии тренировок
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_workout_date = Column(DateTime, nullable=True)
    
    # Уровень и прогресс
    experience_points = Column(Integer, default=0, nullable=False)
    level_progress = Column(Float, default=0.0)  # 0-100%
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="workout_stats")
    
    def __repr__(self):
        return f"<UserStats(user_id='{self.user_id}', workouts='{self.total_workouts}')>"