import random
import time
from typing import Dict, List, Optional
from datetime import datetime

class AIWorkoutGenerator:
    """
    Генератор тренировок на основе правил.
    Не требует AI, работает всегда.
    """
    
    def __init__(self):
        # База упражнений
        self.warmup_exercises = [
            "Jumping Jacks", "High Knees", "Arm Circles", 
            "Leg Swings", "Torso Twists", "Marching in Place",
            "Shoulder Rolls", "Hip Circles"
        ]
        
        self.cooldown_exercises = [
            "Full Body Stretch", "Hamstring Stretch", "Quad Stretch",
            "Shoulder Stretch", "Child's Pose", "Deep Breathing",
            "Cat-Cow Stretch", "Standing Forward Bend"
        ]
        
        self.strength_exercises = {
            "chest": ["Push-ups", "Diamond Push-ups", "Wide Push-ups", "Incline Push-ups"],
            "back": ["Superman Holds", "Bird Dogs", "Reverse Snow Angels", "Prone Y Raises"],
            "legs": ["Bodyweight Squats", "Lunges", "Glute Bridges", "Wall Sit"],
            "abs": ["Crunches", "Plank", "Leg Raises", "Russian Twists", "Dead Bug"],
            "arms": ["Tricep Dips", "Arm Circles", "Shoulder Taps", "Plank Shoulder Taps"],
            "full_body": ["Burpees", "Mountain Climbers", "Bear Crawls", "Jump Squats"]
        }
        
        self.cardio_exercises = [
            "High Knees", "Butt Kicks", "Jumping Jacks",
            "Skater Hops", "Fast Feet", "Jump Rope (imaginary)",
            "Lateral Shuffles", "Box Jumps (low)"
        ]
    
    async def generate(self, user_data: Dict, use_ai: bool = False) -> Dict:
        """
        Генерирует тренировку
        
        Args:
            user_data: Данные пользователя
            use_ai: Использовать ли AI (опционально)
            
        Returns:
            Словарь с тренировкой
        """
        goal = user_data.get('goal', 'weight_loss')
        level = user_data.get('level', 'beginner')
        duration = user_data.get('duration', 45)
        focus_areas = user_data.get('focus_areas', ['full_body'])
        injuries = user_data.get('injuries', [])
        
        # Фильтруем упражнения с учетом травм
        allowed_exercises = self._filter_by_injuries(injuries)
        
        # Генерируем тренировку
        workout_name = self._generate_workout_name(goal, focus_areas)
        warmup = self._generate_warmup(duration)
        main = self._generate_main_workout(goal, level, duration, focus_areas, allowed_exercises)
        cooldown = self._generate_cooldown(duration)
        
        # Оцениваем калории
        estimated_calories = self._estimate_calories(goal, level, duration)
        
        workout = {
            "workout_name": workout_name,
            "description": f"Тренировка для {self._translate_goal(goal)}",
            "warmup": warmup,
            "main_workout": main,
            "cooldown": cooldown,
            "notes": self._generate_notes(goal, level, injuries),
            "recommendations": {
                "hydration": "Пейте воду до, во время и после тренировки",
                "breathing": "Выдыхайте на усилии, вдыхайте на расслаблении",
                "safety": "При боли или дискомфорте прекратите упражнение"
            },
            "metadata": {
                "generated_by": "rule_based",
                "goal": goal,
                "level": level,
                "duration_estimate": duration,
                "total_exercises": len(main),
                "estimated_calories": estimated_calories,
                "focus_areas": focus_areas,
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        return workout
    
    def _filter_by_injuries(self, injuries: List[str]) -> Dict:
        """Фильтрует упражнения на основе травм"""
        if not injuries:
            return self.strength_exercises
        
        restricted_muscles = set()
        
        injury_map = {
            "knee_pain": ["legs"],
            "back_pain": ["back", "abs"],
            "shoulder_pain": ["chest", "arms", "shoulders"],
            "wrist_pain": ["arms", "chest"],
            "neck_pain": ["arms", "shoulders"],
            "ankle_pain": ["legs"]
        }
        
        for injury in injuries:
            injury_lower = injury.lower()
            for key, muscles in injury_map.items():
                if key in injury_lower:
                    restricted_muscles.update(muscles)
        
        allowed = {}
        for muscle, exercises in self.strength_exercises.items():
            if muscle not in restricted_muscles:
                allowed[muscle] = exercises
        
        return allowed if allowed else self.strength_exercises
    
    def _generate_workout_name(self, goal: str, focus_areas: List[str]) -> str:
        """Генерирует название тренировки"""
        names = {
            "weight_loss": ["Жиросжигающая", "Кардио-интенсив", "Сжигатель калорий"],
            "muscle_gain": ["Силовая", "Массонаборная", "Мышечный пампинг"],
            "strength": ["Силовой прорыв", "Пауэрлифтинг", "Базовая сила"],
            "endurance": ["Выносливость", "Марафонская", "Стайерская"]
        }
        
        name_list = names.get(goal, ["Тренировка"])
        name = random.choice(name_list)
        
        if "full_body" in focus_areas:
            name += " на всё тело"
        elif len(focus_areas) == 1:
            translations = {
                "chest": "на грудь",
                "back": "на спину",
                "legs": "на ноги",
                "abs": "на пресс",
                "arms": "на руки"
            }
            name += f" {translations.get(focus_areas[0], '')}"
        
        return name
    
    def _generate_warmup(self, duration: int) -> List[Dict]:
        """Генерирует разминку"""
        warmup_duration = max(5, duration // 10)
        exercises_count = min(4, warmup_duration)
        
        selected = random.sample(self.warmup_exercises, exercises_count)
        time_per_exercise = warmup_duration // exercises_count
        
        warmup = []
        for ex in selected:
            warmup.append({
                "name": ex,
                "duration": f"{time_per_exercise} min",
                "intensity": "low",
                "notes": "Выполняйте плавно, без резких движений"
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
        
        # Параметры нагрузки
        load_params = {
            "weight_loss": {
                "beginner": {"sets": 3, "reps": "15-20", "rest_sec": 45},
                "intermediate": {"sets": 4, "reps": "15-20", "rest_sec": 30},
                "advanced": {"sets": 5, "reps": "20-25", "rest_sec": 20}
            },
            "muscle_gain": {
                "beginner": {"sets": 3, "reps": "8-12", "rest_sec": 90},
                "intermediate": {"sets": 4, "reps": "8-12", "rest_sec": 60},
                "advanced": {"sets": 5, "reps": "6-12", "rest_sec": 45}
            },
            "strength": {
                "beginner": {"sets": 3, "reps": "5-8", "rest_sec": 120},
                "intermediate": {"sets": 4, "reps": "3-6", "rest_sec": 90},
                "advanced": {"sets": 5, "reps": "1-5", "rest_sec": 180}
            },
            "endurance": {
                "beginner": {"sets": 2, "reps": "12-15", "rest_sec": 60},
                "intermediate": {"sets": 3, "reps": "15-20", "rest_sec": 45},
                "advanced": {"sets": 4, "reps": "20-25", "rest_sec": 30}
            }
        }
        
        params = load_params.get(goal, load_params["weight_loss"]).get(level, {})
        params.setdefault("sets", 3)
        params.setdefault("reps", "12")
        params.setdefault("rest_sec", 60)
        
        # Выбираем упражнения
        main_workout = []
        max_exercises = min(8, max(3, duration // 7))
        
        # Добавляем силовые упражнения по зонам фокуса
        for area in focus_areas:
            if area in exercises and exercises[area]:
                ex = random.choice(exercises[area])
                main_workout.append({
                    "exercise": ex,
                    "sets": params["sets"],
                    "reps": params["reps"],
                    "rest_sec": params["rest_sec"],
                    "muscle_group": area,
                    "tempo": "2-0-2",
                    "notes": "Следите за техникой"
                })
        
        # Если нужно похудение или выносливость, добавляем кардио
        if goal in ["weight_loss", "endurance"]:
            remaining = max_exercises - len(main_workout)
            for _ in range(min(remaining, 3)):
                cardio = random.choice(self.cardio_exercises)
                main_workout.append({
                    "exercise": cardio,
                    "duration": "45 sec",
                    "rest_sec": 15,
                    "muscle_group": "cardio",
                    "notes": "Высокая интенсивность"
                })
        
        # Если наоборот, мало упражнений, добавляем еще
        while len(main_workout) < max_exercises:
            for area in focus_areas:
                if area in exercises and exercises[area] and len(main_workout) < max_exercises:
                    ex = random.choice(exercises[area])
                    if not any(w.get("exercise") == ex for w in main_workout):
                        main_workout.append({
                            "exercise": ex,
                            "sets": params["sets"],
                            "reps": params["reps"],
                            "rest_sec": params["rest_sec"],
                            "muscle_group": area,
                            "tempo": "2-0-2",
                            "notes": "Контролируйте движение"
                        })
                if len(main_workout) >= max_exercises:
                    break
        
        return main_workout[:max_exercises]
    
    def _generate_cooldown(self, duration: int) -> List[Dict]:
        """Генерирует заминку"""
        cooldown_duration = max(5, duration // 10)
        exercises_count = min(4, cooldown_duration)
        
        selected = random.sample(self.cooldown_exercises, exercises_count)
        time_per_exercise = cooldown_duration // exercises_count
        
        cooldown = []
        for ex in selected:
            cooldown.append({
                "exercise": ex,
                "duration": f"{time_per_exercise} min",
                "notes": "Дышите глубоко, растягивайтесь плавно"
            })
        
        return cooldown
    
    def _estimate_calories(self, goal: str, level: str, duration: int) -> int:
        """Оценка сжигаемых калорий"""
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
        """Генерирует заметки"""
        notes = []
        
        if level == "beginner":
            notes.append("Сосредоточьтесь на правильной технике выполнения")
            notes.append("Не стесняйтесь делать дополнительные перерывы")
        
        if goal == "weight_loss":
            notes.append("Поддерживайте умеренную интенсивность для оптимального жиросжигания")
        elif goal == "muscle_gain":
            notes.append("Работайте до мышечного отказа в последних повторениях")
        elif goal == "strength":
            notes.append("Делайте большие перерывы между подходами для восстановления")
        
        if injuries:
            notes.append(f"Учитывайте ограничения: {', '.join(injuries)}")
        
        notes.append("Не забывайте пить воду!")
        
        return ". ".join(notes)
    
    def _translate_goal(self, goal: str) -> str:
        """Перевод цели"""
        translations = {
            "weight_loss": "похудения",
            "muscle_gain": "набора массы",
            "strength": "увеличения силы",
            "endurance": "развития выносливости"
        }
        return translations.get(goal, goal)