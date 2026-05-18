from typing import Dict, List, Optional
import random
from datetime import datetime


class SimpleWorkoutGenerator:
    """Простой генератор тренировок на основе правил"""
    
    def __init__(self):
        self.warmup_exercises = [
            "Jumping Jacks", "High Knees", "Arm Circles", 
            "Leg Swings", "Torso Twists", "Marching in Place"
        ]
        
        self.cooldown_exercises = [
            "Full Body Stretch", "Hamstring Stretch", "Quad Stretch",
            "Shoulder Stretch", "Child's Pose", "Deep Breathing"
        ]
        
        self.strength_exercises = {
            "chest": ["Push-ups", "Diamond Push-ups", "Wide Push-ups"],
            "back": ["Superman Holds", "Bird Dogs", "Reverse Snow Angels"],
            "legs": ["Bodyweight Squats", "Lunges", "Glute Bridges"],
            "abs": ["Crunches", "Plank", "Leg Raises", "Russian Twists"],
            "arms": ["Tricep Dips", "Arm Circles", "Shoulder Taps"],
            "full_body": ["Burpees", "Mountain Climbers", "Bear Crawls"]
        }
        
        self.cardio_exercises = [
            "High Knees", "Butt Kicks", "Jumping Jacks",
            "Skater Hops", "Fast Feet", "Jump Rope (imaginary)"
        ]
    
    def generate(self, user_data: Dict) -> Dict:
        """Генерирует тренировку на основе данных пользователя"""
        
        goal = user_data.get('goal', 'weight_loss')
        level = user_data.get('level', 'beginner')
        duration = user_data.get('duration', 45)
        focus_areas = user_data.get('focus_areas', ['full_body'])
        injuries = user_data.get('injuries', [])
        
        # Фильтруем упражнения на основе травм
        filtered_exercises = self._filter_by_injuries(injuries)
        
        # Генерируем части тренировки
        warmup = self._generate_warmup(duration)
        main = self._generate_main_workout(goal, level, duration, focus_areas, filtered_exercises)
        cooldown = self._generate_cooldown(duration)
        
        # Рассчитываем метаданные
        total_exercises = len(main)
        estimated_calories = self._estimate_calories(goal, level, duration)
        
        workout = {
            "warmup": warmup,
            "main_workout": main,
            "cooldown": cooldown,
            "notes": self._generate_notes(goal, level, injuries),
            "metadata": {
                "generated_by": "rule_based",
                "goal": goal,
                "level": level,
                "duration_estimate": duration,
                "total_exercises": total_exercises,
                "estimated_calories": estimated_calories,
                "focus_areas": focus_areas,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        return workout
    
    def _filter_by_injuries(self, injuries: List[str]) -> Dict:
        """Фильтрует упражнения на основе травм"""
        restricted = set()
        
        injury_map = {
            "knee_pain": ["legs"],
            "back_pain": ["back", "abs"],
            "shoulder_pain": ["chest", "arms"],
            "wrist_pain": ["arms", "chest"]
        }
        
        for injury in injuries:
            if injury in injury_map:
                restricted.update(injury_map[injury])
        
        allowed = {}
        for muscle, exercises in self.strength_exercises.items():
            if muscle not in restricted:
                allowed[muscle] = exercises
        
        return allowed if allowed else self.strength_exercises
    
    def _generate_warmup(self, duration: int) -> List[Dict]:
        """Генерирует разминку"""
        warmup_duration = max(3, duration // 10)
        exercises_count = min(3, warmup_duration)
        
        selected = random.sample(self.warmup_exercises, exercises_count)
        
        warmup = []
        for ex in selected:
            warmup.append({
                "name": ex,
                "duration": f"{warmup_duration // exercises_count} min",
                "type": "warmup"
            })
        
        return warmup
    
    def _generate_main_workout(
        self, 
        goal: str, 
        level: str, 
        duration: int,
        focus_areas: List[str],
        exercises: Dict
    ) -> List[Dict]:
        """Генерирует основную часть тренировки"""
        
        load_params = {
            "weight_loss": {
                "beginner": {"sets": 3, "reps": "15-20", "rest": 45},
                "intermediate": {"sets": 4, "reps": "15-20", "rest": 30},
                "advanced": {"sets": 5, "reps": "20-25", "rest": 20}
            },
            "muscle_gain": {
                "beginner": {"sets": 3, "reps": "8-12", "rest": 90},
                "intermediate": {"sets": 4, "reps": "8-12", "rest": 60},
                "advanced": {"sets": 5, "reps": "6-12", "rest": 45}
            },
            "strength": {
                "beginner": {"sets": 3, "reps": "5-8", "rest": 120},
                "intermediate": {"sets": 4, "reps": "3-6", "rest": 90},
                "advanced": {"sets": 5, "reps": "1-5", "rest": 180}
            },
            "endurance": {
                "beginner": {"sets": 2, "reps": "12-15", "rest": 60},
                "intermediate": {"sets": 3, "reps": "15-20", "rest": 45},
                "advanced": {"sets": 4, "reps": "20-25", "rest": 30}
            }
        }
        
        params = load_params.get(goal, load_params["weight_loss"]).get(
            level, {"sets": 3, "reps": "12", "rest": 60}
        )
        
        main_workout = []
        exercises_count = min(6, max(3, duration // 10))
        
        for area in focus_areas:
            if area in exercises:
                ex_list = exercises[area]
                if ex_list:
                    exercise = random.choice(ex_list)
                    main_workout.append({
                        "exercise": exercise,
                        "sets": params["sets"],
                        "reps": params["reps"],
                        "rest_sec": params["rest"],
                        "muscle_group": area,
                        "type": "strength"
                    })
        
        if goal in ["weight_loss", "endurance"]:
            for _ in range(exercises_count - len(main_workout)):
                cardio_ex = random.choice(self.cardio_exercises)
                main_workout.append({
                    "exercise": cardio_ex,
                    "duration": "45 sec",
                    "rest_sec": 15,
                    "type": "cardio"
                })
        
        return main_workout[:exercises_count]
    
    def _generate_cooldown(self, duration: int) -> List[Dict]:
        """Генерирует заминку"""
        cooldown_duration = max(3, duration // 15)
        exercises_count = min(3, cooldown_duration)
        
        selected = random.sample(self.cooldown_exercises, exercises_count)
        
        cooldown = []
        for ex in selected:
            cooldown.append({
                "exercise": ex,
                "duration": f"{cooldown_duration // exercises_count} min",
                "type": "cooldown"
            })
        
        return cooldown
    
    def _estimate_calories(self, goal: str, level: str, duration: int) -> int:
        """Примерная оценка калорий"""
        base_calories = {
            "beginner": 5,
            "intermediate": 7,
            "advanced": 9
        }
        
        goal_multiplier = {
            "weight_loss": 1.2,
            "muscle_gain": 0.8,
            "strength": 0.7,
            "endurance": 1.1
        }
        
        calories_per_min = base_calories.get(level, 5)
        multiplier = goal_multiplier.get(goal, 1.0)
        
        return int(calories_per_min * duration * multiplier)
    
    def _generate_notes(self, goal: str, level: str, injuries: List[str]) -> str:
        """Генерирует заметки к тренировке"""
        notes = []
        
        if level == "beginner":
            notes.append("Сосредоточьтесь на правильной технике выполнения")
        
        if goal == "weight_loss":
            notes.append("Поддерживайте умеренную интенсивность для жиросжигания")
        
        if injuries:
            notes.append(f"Учитывайте ограничения: {', '.join(injuries)}")
        
        notes.append("Не забудьте пить воду во время тренировки")
        
        return ". ".join(notes)