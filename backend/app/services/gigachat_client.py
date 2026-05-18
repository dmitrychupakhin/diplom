import httpx
import json
import time
import uuid
import re
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from ..core.config import settings

class GigaChatError(Exception):
    """Базовое исключение GigaChat"""
    pass

class GigaChatAuthError(GigaChatError):
    """Ошибка аутентификации"""
    pass

class GigaChatAPIError(GigaChatError):
    """Ошибка API"""
    pass

class GigaChatTimeoutError(GigaChatError):
    """Таймаут запроса"""
    pass

class GigaChatClient:
    """
    Клиент для работы с GigaChat API
    
    Использует OAuth2 аутентификацию с client_id и client_secret
    """
    
    def __init__(self):
        self.client_id = settings.GIGACHAT_CLIENT_ID
        self.client_secret = settings.GIGACHAT_CLIENT_SECRET
        self.auth_url = settings.GIGACHAT_AUTH_URL
        self.api_url = settings.GIGACHAT_API_URL
        self.scope = settings.GIGACHAT_SCOPE
        self.model = settings.GIGACHAT_MODEL
        
        # Кэш токена
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
        # HTTP клиент (создается по требованию)
        self._client: Optional[httpx.AsyncClient] = None
        
        print(f"🤖 GigaChatClient инициализирован")
        print(f"   API URL: {self.api_url}")
        print(f"   Модель: {self.model}")
        print(f"   Настроен: {self.is_configured}")
    
    @property
    def is_configured(self) -> bool:
        """Проверяет, что клиент настроен корректно"""
        return bool(self.client_id and self.client_secret)
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Получить или создать HTTP клиент"""
        if self._client is None or self._client.is_closed:
            # Настраиваем таймауты
            timeout = httpx.Timeout(
                connect=10.0,
                read=settings.AI_TIMEOUT_SECONDS,
                write=10.0,
                pool=10.0
            )
            
            self._client = httpx.AsyncClient(
                timeout=timeout,
                verify=False,  # Для тестового окружения
                follow_redirects=True
            )
        
        return self._client
    
    async def _authenticate(self) -> str:
        """
        Получить токен доступа
        
        Returns:
            Access token
            
        Raises:
            GigaChatAuthError: Если аутентификация не удалась
        """
        # Проверяем кэшированный токен (с запасом 5 минут)
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at - timedelta(minutes=5):
                return self._access_token
        
        if not self.is_configured:
            raise GigaChatAuthError("GigaChat не настроен. Укажите GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET")
        
        try:
            client = await self._get_client()
            
            # Формируем данные для аутентификации
            auth_data = {
                "scope": self.scope
            }
            
            # Генерируем уникальный ID запроса
            rquid = str(uuid.uuid4())
            
            print(f"🔐 Запрос токена GigaChat...")
            
            # Отправляем запрос на аутентификацию
            response = await client.post(
                self.auth_url,
                data=auth_data,
                auth=(self.client_id, self.client_secret),
                headers={
                    "RqUID": rquid,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            print(f"   Статус: {response.status_code}")
            
            if response.status_code == 401:
                raise GigaChatAuthError(
                    "Неверные учетные данные GigaChat. Проверьте CLIENT_ID и CLIENT_SECRET"
                )
            
            if response.status_code != 200:
                raise GigaChatAuthError(
                    f"Ошибка аутентификации GigaChat: {response.status_code} - {response.text[:200]}"
                )
            
            # Получаем токен
            token_data = response.json()
            self._access_token = token_data.get("access_token")
            
            if not self._access_token:
                raise GigaChatAuthError("Не получен токен доступа")
            
            # Сохраняем время жизни токена
            expires_in = token_data.get("expires_in", 3600)  # По умолчанию 1 час
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            print(f"✅ Токен получен (действителен {expires_in} сек)")
            
            return self._access_token
            
        except httpx.TimeoutException:
            raise GigaChatTimeoutError("Таймаут при подключении к GigaChat")
        except GigaChatError:
            raise
        except Exception as e:
            raise GigaChatAuthError(f"Ошибка аутентификации: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((GigaChatTimeoutError, GigaChatAPIError))
    )
    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Отправить запрос на генерацию текста
        
        Args:
            messages: Список сообщений
            temperature: Температура (0-1)
            max_tokens: Максимальное количество токенов
            
        Returns:
            Ответ от API
            
        Raises:
            GigaChatAPIError: Ошибка API
            GigaChatTimeoutError: Таймаут
        """
        if not self.is_configured:
            raise GigaChatAPIError("GigaChat не настроен")
        
        try:
            # Получаем токен
            token = await self._authenticate()
            client = await self._get_client()
            
            # Формируем запрос
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or settings.AI_TEMPERATURE,
                "max_tokens": max_tokens or settings.AI_MAX_TOKENS,
                "stream": False
            }
            
            print(f"📤 Отправка запроса к GigaChat API...")
            
            # Отправляем запрос
            response = await client.post(
                f"{self.api_url}/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"📥 Ответ: {response.status_code}")
            
            # Обрабатываем ошибки
            if response.status_code == 401:
                # Токен истек - сбрасываем и пробуем снова
                self._access_token = None
                raise GigaChatAPIError("Токен истек, требуется обновление")
            
            if response.status_code == 429:
                raise GigaChatAPIError("Превышен лимит запросов к GigaChat")
            
            if response.status_code != 200:
                error_text = response.text[:300]
                raise GigaChatAPIError(f"Ошибка API ({response.status_code}): {error_text}")
            
            return response.json()
            
        except httpx.TimeoutException:
            raise GigaChatTimeoutError("Таймаут при ожидании ответа от GigaChat")
        except GigaChatError:
            raise
        except Exception as e:
            raise GigaChatAPIError(f"Неизвестная ошибка: {str(e)}")
    
    async def generate_workout(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Optional[Dict]:
        """
        Сгенерировать тренировку
        
        Args:
            system_prompt: Системный промпт
            user_prompt: Пользовательский промпт
            
        Returns:
            Словарь с тренировкой или None при ошибке
        """
        if not self.is_configured:
            print("⚠️ GigaChat не настроен, пропускаем AI генерацию")
            return None
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.generate_text(messages)
            
            # Извлекаем текст ответа
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not content:
                print("❌ Пустой ответ от GigaChat")
                return None
            
            # Пытаемся извлечь JSON
            workout_data = self._extract_json(content)
            
            if workout_data:
                print(f"✅ Успешно получена тренировка от AI")
                return workout_data
            else:
                print(f"❌ Не удалось извлечь JSON из ответа")
                print(f"   Ответ: {content[:200]}...")
                return None
                
        except GigaChatTimeoutError:
            print("❌ Таймаут GigaChat, используем fallback")
            return None
        except GigaChatAPIError as e:
            print(f"❌ Ошибка GigaChat API: {e}")
            return None
        except Exception as e:
            print(f"❌ Неизвестная ошибка: {e}")
            return None
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """
        Извлечь JSON из текста ответа
        
        Args:
            text: Текст ответа
            
        Returns:
            Словарь с данными или None
        """
        # Убираем markdown-разметку если есть
        text = text.strip()
        
        # Пробуем найти JSON блок
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if json_match:
            text = json_match.group(1)
        
        # Пробуем найти чистый JSON
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Пробуем распарсить весь текст как JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        return None
    
    async def close(self):
        """Закрыть HTTP клиент"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()