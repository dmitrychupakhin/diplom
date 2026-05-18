from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime, timedelta
import json

from ..models.user import User, Injury, Workout, UserStats
from ..schemas.user import UserUpdate, InjuryCreate, WorkoutFeedback
from ..core.security import get_password_hash

class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Получить пользователя по ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user(db: Session, user: User, update_data: UserUpdate) -> User:
        """Обновить профиль пользователя"""
        update_dict = update_data.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def delete_user(db: Session, user: User) -> bool:
        """Деактивировать пользователя"""
        user.is_active = 'N'
        user.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def get_user_injuries(db: Session, user_id: UUID) -> List[Injury]:
        """Получить список травм пользователя"""
        return db.query(Injury).filter(
            Injury.user_id == user_id,
            Injury.is_active == 'Y'
        ).all()
    
    @staticmethod
    def add_injury(db: Session, user_id: UUID, injury_data: InjuryCreate) -> Injury:
        """Добавить травму"""
        injury = Injury(
            user_id=user_id,
            **injury_data.dict()
        )
        
        db.add(injury)
        db.commit()
        db.refresh(injury)
        
        return injury
    
    @staticmethod
    def remove_injury(db: Session, injury_id: UUID, user_id: UUID) -> bool:
        """Удалить травму (деактивировать)"""
        injury = db.query(Injury).filter(
            Injury.id == injury_id,
            Injury.user_id == user_id
        ).first()
        
        if injury:
            injury.is_active = 'N'
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_user_stats(db: Session, user_id: UUID) -> Optional[UserStats]:
        """Получить статистику пользователя"""
        return db.query(UserStats).filter(UserStats.user_id == user_id).first()
    
    @staticmethod
    def create_user_stats(db: Session, user_id: UUID) -> UserStats:
        """Создать запись статистики для пользователя"""
        stats = UserStats(user_id=user_id)
        db.add(stats)
        db.commit()
        db.refresh(stats)
        return stats
    
    @staticmethod
    def get_workout_history(
        db: Session, 
        user_id: UUID, 
        page: int = 1, 
        size: int = 10,
        status: Optional[str] = None
    ) -> Dict:
        """Получить историю тренировок с пагинацией"""
        query = db.query(Workout).filter(Workout.user_id == user_id)
        
        if status:
            query = query.filter(Workout.status == status)
        
        total = query.count()
        workouts = query.order_by(Workout.created_at.desc())\
            .offset((page - 1) * size)\
            .limit(size)\
            .all()
        
        return {
            "items": workouts,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
    
    @staticmethod
    def get_workout_by_id(db: Session, workout_id: UUID, user_id: UUID) -> Optional[Workout]:
        """Получить тренировку по ID"""
        return db.query(Workout).filter(
            Workout.id == workout_id,
            Workout.user_id == user_id
        ).first()
    
    @staticmethod
    def update_workout_feedback(
        db: Session, 
        workout_id: UUID, 
        user_id: UUID, 
        feedback: WorkoutFeedback
    ) -> Optional[Workout]:
        """Обновить обратную связь по тренировке"""
        workout = db.query(Workout).filter(
            Workout.id == workout_id,
            Workout.user_id == user_id
        ).first()
        
        if workout:
            if feedback.rating is not None:
                workout.feedback_rating = feedback.rating
            if feedback.feedback_text is not None:
                workout.feedback_text = feedback.feedback_text
            if feedback.status is not None:
                workout.status = feedback.status
                if feedback.status == 'completed':
                    workout.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(workout)
            
            # Обновляем статистику
            UserService._update_stats_after_workout(db, user_id, workout)
        
        return workout
    
    @staticmethod
    def _update_stats_after_workout(db: Session, user_id: UUID, workout: Workout):
        """Обновить статистику после завершения тренировки"""
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        
        if not stats:
            stats = UserStats(user_id=user_id)
            db.add(stats)
            db.flush()
            db.refresh(stats)
        
        if workout.status == 'completed':
            print("completed workouts:", stats.completed_workouts)
            stats.completed_workouts = (stats.completed_workouts or 0) + 1
            stats.total_duration_minutes += workout.duration or 0
            stats.total_calories_burned += workout.calories_estimate or 0
            
            # Обновляем серию тренировок
            today = datetime.utcnow().date()
            if stats.last_workout_date:
                last_date = stats.last_workout_date.date()
                if (today - last_date).days == 1:
                    stats.current_streak += 1
                elif (today - last_date).days > 1:
                    stats.current_streak = 1
            else:
                stats.current_streak = 1
            
            stats.longest_streak = max(stats.current_streak, stats.longest_streak)
            stats.last_workout_date = datetime.utcnow()
        
        stats.total_workouts += 1
        db.commit()