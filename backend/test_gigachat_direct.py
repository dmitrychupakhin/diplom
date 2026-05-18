import asyncio
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages


# Загружаем .env
load_dotenv(Path("backend/.env"))


class GigaChatTester:
    def __init__(self):
        self.credentials = os.getenv(
            "GIGACHAT_CREDENTIALS",
            "MDE5YjQ4MGYtNzg2ZS03OTAzLWI0MmItNTI0YjQzM2Y1MTE2OjVjZjIwNmQ4LTM0NDItNGE3NS04MDE2LTgzZWE4ZjNmZDAzMw=="
        )

        self.model = os.getenv(
            "GIGACHAT_MODEL",
            "GigaChat"
        )

        print(f"MODEL: {self.model}")

        # Создаем клиент
        self.giga = GigaChat(
            credentials=self.credentials,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False,
            model=self.model,
        )

    async def test_connection(self):
        """Тест подключения"""

        print("\n" + "=" * 60)
        print("📡 Тест подключения")
        print("=" * 60)

        try:
            response = self.giga.chat(
                "Привет! Ответь одним словом: работает?"
            )

            print("✅ Подключение успешно")
            print("Ответ:", response.choices[0].message.content)

            return True

        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    async def test_json_generation(self):
        """Тест генерации JSON"""

        print("\n" + "=" * 60)
        print("🤖 Тест JSON генерации")
        print("=" * 60)

        prompt = """
Создай короткую тренировку для новичка.

Условия:
- Цель: похудение
- Травмы: боль в коленях
- Оборудование: нет

Ответь СТРОГО в JSON:

{
    "warmup": [
        {
            "name": "упражнение",
            "duration": "время"
        }
    ],
    "main_workout": [
        {
            "exercise": "название",
            "sets": число,
            "reps": "строка",
            "rest_sec": число
        }
    ],
    "cooldown": [
        {
            "exercise": "название",
            "duration": "время"
        }
    ]
}

ВАЖНО:
- Исключи упражнения с нагрузкой на колени
- Не добавляй текст вне JSON
"""

        try:
            messages = [
                Messages(
                    role="system",
                    content="Ты фитнес-тренер. Отвечай только JSON."
                ),
                Messages(
                    role="user",
                    content=prompt
                )
            ]

            chat = Chat(
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )

            response = self.giga.chat(chat)

            content = response.choices[0].message.content

            print("✅ Ответ получен")
            print("\nСырой ответ:")
            print(content[:500])

            # Извлекаем JSON
            json_match = re.search(r"\{.*\}", content, re.DOTALL)

            if not json_match:
                print("❌ JSON не найден")
                return False

            workout = json.loads(json_match.group(0))

            print("\n✅ JSON успешно распарсен")

            print(
                f"Разминка: {len(workout.get('warmup', []))}"
            )

            print(
                f"Основная часть: {len(workout.get('main_workout', []))}"
            )

            print(
                f"Заминка: {len(workout.get('cooldown', []))}"
            )

            # Сохраняем
            with open(
                "test_workout.json",
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    workout,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            print("\n📁 Файл сохранен: test_workout.json")

            return True

        except Exception as e:
            print(f"❌ Ошибка генерации: {e}")
            return False

    async def test_error_handling(self):
        """Тест обработки ошибок"""

        print("\n" + "=" * 60)
        print("🛡️ Тест обработки ошибок")
        print("=" * 60)

        try:
            bad_client = GigaChat(
                credentials="invalid_key",
                verify_ssl_certs=False
            )

            bad_client.chat("test")

            print("⚠️ Ошибка НЕ была выброшена")
            return False

        except Exception as e:
            print("✅ Ошибка корректно обработана")
            print("Текст ошибки:", str(e))

            return True


async def main():
    print("=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ GigaChat")
    print("=" * 60)

    tester = GigaChatTester()

    tests = [
        ("Подключение", tester.test_connection),
        ("JSON генерация", tester.test_json_generation),
        ("Обработка ошибок", tester.test_error_handling),
    ]

    results = []

    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Критическая ошибка {name}: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("📊 ИТОГИ")
    print("=" * 60)

    for name, success in results:
        print(f"{'✅' if success else '❌'} {name}")

    success_count = sum(1 for _, s in results if s)

    print(f"\nУспешно: {success_count}/{len(results)}")

    if success_count == len(results):
        print("🎉 Все тесты пройдены")
    else:
        print("⚠️ Есть ошибки")


if __name__ == "__main__":
    asyncio.run(main())