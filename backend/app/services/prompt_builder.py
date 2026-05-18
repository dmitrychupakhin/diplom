from typing import Dict, List, Optional
from datetime import datetime


class PromptBuilder:
    """Строитель промптов для AI генерации тренировок"""
    
    def __init__(self):
        self.goal_descriptions = {
            "weight_loss": "похудение и сжигание жира",
            "muscle_gain": "набор мышечной массы и гипертрофия",
            "strength": "увеличение силовых показателей",
            "endurance": "развитие выносливости и кардио"
        }
        
        self.level_descriptions = {
            "beginner": "новичок (опыт менее 3 месяцев, осваивает базовую технику)",
            "intermediate": "средний уровень (опыт 3-12 месяцев, стабильная техника)",
            "advanced": "продвинутый (опыт более года, высокая техника выполнения)"
        }
    
    def build_full_prompt(
        self,
        user_data: Dict,
        allowed_exercises: List[Dict],
        include_safety: bool = True
    ) -> str:
        """
        Создает полный промпт для генерации тренировки
        
        Args:
            user_data: Данные пользователя
            allowed_exercises: Список разрешенных упражнений
            include_safety: Включать ли инструкции по безопасности
            
        Returns:
            Полный промпт для GigaChat
        """
        prompt_parts = []
        
        # 1. Информация о пользователе
        prompt_parts.append(self._build_user_section(user_data))
        
        # 2. Цели и ограничения
        prompt_parts.append(self._build_goals_section(user_data))
        
        # 3. Доступные упражнения
        prompt_parts.append(self._build_exercises_section(allowed_exercises))
        
        # 4. Требования к тренировке
        prompt_parts.append(self._build_requirements_section(user_data))
        
        # 5. Инструкции по безопасности
        if include_safety and user_data.get('injuries'):
            prompt_parts.append(self._build_safety_section(user_data))
        
        # 6. Формат ответа
        prompt_parts.append(self._build_format_section())
        
        return "\n\n".join(prompt_parts)
    
    def _build_user_section(self, data: Dict) -> str:
        """Создает секцию с информацией о пользователе"""
        gender_map = {
            "male": "Мужчина",
            "female": "Женщина",
            "other": "Пол не указан"
        }
        
        section = "## ПРОФИЛЬ КЛИЕНТА\n"
        
        if data.get('gender'):
            section += f"- Пол: {gender_map.get(data['gender'], data['gender'])}\n"
        if data.get('age'):
            section += f"- Возраст: {data['age']} лет\n"
        if data.get('weight') and data.get('height'):
            bmi = data['weight'] / ((data['height']/100) ** 2)
            section += f"- Вес: {data['weight']} кг\n"
            section += f"- Рост: {data['height']} см\n"
            section += f"- ИМТ: {bmi:.1f} кг/м²\n"
        
        return section
    
    def _build_goals_section(self, data: Dict) -> str:
        """Создает секцию с целями и ограничениями"""
        section = "## ЦЕЛИ И УСЛОВИЯ\n"
        
        goal = data.get('goal', 'weight_loss')
        level = data.get('level', 'beginner')
        
        section += f"- Основная цель: {self.goal_descriptions.get(goal, goal)}\n"
        section += f"- Уровень подготовки: {self.level_descriptions.get(level, level)}\n"
        section += f"- Количество тренировок в неделю: {data.get('workouts_per_week', 3)}\n"
        section += f"- Длительность тренировки: {data.get('duration', 45)} минут\n"
        
        if data.get('focus_areas'):
            areas = ", ".join(data['focus_areas'])
            section += f"- Фокус на группы мышц: {areas}\n"
        
        if data.get('equipment'):
            equipment = ", ".join(data['equipment'])
            section += f"- Доступное оборудование: {equipment}\n"
        else:
            section += "- Оборудование: только вес тела (без оборудования)\n"
        
        if data.get('injuries'):
            injuries = ", ".join(data['injuries'])
            section += f"- ⚠️ ТРАВМЫ И ОГРАНИЧЕНИЯ: {injuries}\n"
            section += "- ВАЖНО: Исключи все упражнения, которые нагружают травмированные области!\n"
        
        return section
    
    def _build_exercises_section(self, exercises: List[Dict]) -> str:
        """Создает секцию с доступными упражнениями"""
        section = "## ДОСТУПНЫЕ УПРАЖНЕНИЯ\n"
        section += "Используй ТОЛЬКО эти упражнения или их прямые аналоги:\n\n"
        
        # Группируем по типу
        by_type = {}
        for ex in exercises[:20]:  # Ограничиваем количество для читаемости
            ex_type = ex.get('type', 'strength')
            if ex_type not in by_type:
                by_type[ex_type] = []
            by_type[ex_type].append(ex)
        
        for ex_type, ex_list in by_type.items():
            section += f"**{ex_type.upper()}**:\n"
            for ex in ex_list:
                section += f"- {ex['name']}"
                if ex.get('muscle_groups'):
                    section += f" (мышцы: {', '.join(ex['muscle_groups'])})"
                section += "\n"
            section += "\n"
        
        return section
    
    def _build_requirements_section(self, data: Dict) -> str:
        """Создает секцию с требованиями к тренировке"""
        duration = data.get('duration', 45)
        goal = data.get('goal', 'weight_loss')
        
        section = "## ТРЕБОВАНИЯ К ТРЕНИРОВКЕ\n"
        section += f"- Общая длительность: ровно {duration} минут\n"
        section += f"- Разминка: {max(3, duration // 10)} минут\n"
        section += f"- Основная часть: {duration - 10} минут\n"
        section += f"- Заминка: {max(3, duration // 15)} минут\n\n"
        
        # Специфика по целям
        if goal == "weight_loss":
            section += "- Используй круговой метод тренировки\n"
            section += "- Минимальный отдых между упражнениями (30-45 сек)\n"
            section += "- Высокая интенсивность, много повторений (15-20)\n"
        elif goal == "muscle_gain":
            section += "- Используй сплит-тренировку\n"
            section += "- Достаточный отдых между подходами (60-90 сек)\n"
            section += "- Среднее количество повторений (8-12)\n"
        elif goal == "strength":
            section += "- Фокус на базовые упражнения\n"
            section += "- Длительный отдых между подходами (90-180 сек)\n"
            section += "- Малое количество повторений (3-8)\n"
        elif goal == "endurance":
            section += "- Длительная нагрузка низкой интенсивности\n"
            section += "- Минимальный отдых (15-30 сек)\n"
            section += "- Высокое количество повторений (15-25)\n"
        
        return section
    
    def _build_safety_section(self, data: Dict) -> str:
        """Создает секцию с инструкциями по безопасности"""
        section = "## ⚠️ ИНСТРУКЦИИ ПО БЕЗОПАСНОСТИ\n"
        
        injuries = data.get('injuries', [])
        
        safety_rules = {
            "knee_pain": [
                "Избегай глубоких приседаний",
                "Исключи прыжковые упражнения",
                "Не используй упражнения с ударной нагрузкой на колени",
                "Предпочитай упражнения лежа или сидя для ног"
            ],
            "back_pain": [
                "Избегай упражнений с наклоном вперед",
                "Исключи скручивания позвоночника",
                "Не используй упражнения с осевой нагрузкой",
                "Предпочитай упражнения с поддержкой спины"
            ],
            "shoulder_pain": [
                "Избегай упражнений над головой",
                "Исключи жимы и тяги сверху",
                "Не используй упражнения с широкой амплитудой в плечах",
                "Предпочитай изолированные упражнения"
            ],
            "wrist_pain": [
                "Избегай упоров на руки",
                "Исключи планки и отжимания от пола",
                "Не используй упражнения с нагрузкой на запястья",
                "Предпочитай упражнения с опорой на предплечья"
            ]
        }
        
        for injury in injuries:
            if injury in safety_rules:
                section += f"\nПри {injury}:\n"
                for rule in safety_rules[injury]:
                    section += f"- {rule}\n"
        
        return section
    
    def _build_format_section(self) -> str:
        """Создает секцию с требованиями к формату ответа"""
        section = "## ФОРМАТ ОТВЕТА\n"
        section += "Ответь СТРОГО в формате JSON без дополнительного текста:\n\n"
        section += """```json
{
    "warmup": [
        {
            "name": "название",
            "duration": "X min",
            "intensity": "low/medium"
        }
    ],
    "main_workout": [
        {
            "exercise": "название",
            "sets": число,
            "reps": "строка",
            "rest_sec": число,
            "muscle_group": "группа мышц"
        }
    ],
    "cooldown": [
        {
            "exercise": "название",
            "duration": "X min"
        }
    ],
    "recommendations": {
        "hydration": "совет",
        "safety": "меры предосторожности"
    }
}
```"""
        return section