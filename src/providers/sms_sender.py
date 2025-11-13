import requests
import time
from typing import Optional, Dict, Any
import logging

from ..core.base_sender import BaseMessageSender
from ..core.message import Message, MessageType, DeliveryResult
from ..core.exceptions import AuthenticationError, RateLimitError, ValidationError

class YandexCloudSMSSender(BaseMessageSender):
    """Отправщик SMS через Yandex Cloud"""
    
    def __init__(
        self,
        api_key: str,
        folder_id: str,
        sender_id: Optional[str] = None,
        base_url: str = "https://api.cloud.yandex.net/notification/v1",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.folder_id = folder_id
        self.sender_id = sender_id
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Api-Key {api_key}',
            'Content-Type': 'application/json'
        }
        
    def send(self, message: Message) -> DeliveryResult:
        """Отправка SMS"""
        if message.message_type != MessageType.SMS:
            raise ValidationError("Некорректный тип сообщения для SMSSender")
        
        return self._execute_with_retry(self._send_sms, message)
    
    def _send_sms(self, message: Message) -> DeliveryResult:
        """Внутренняя логика отправки SMS"""
        result = DeliveryResult(success=False, attempts=1)
        
        try:
            payload = {
                "folderId": self.folder_id,
                "destination": {"phoneNumber": message.recipient},
                "text": message.content,
                "channel": "SMS"
            }
            
            if self.sender_id:
                payload["sms"] = {"from": self.sender_id}
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                result.success = True
                result.message_id = response_data.get('id')
                result.provider_response = response_data
                
            elif response.status_code == 401:
                result.error = "Ошибка аутентификации: неверный API ключ"
                raise AuthenticationError(result.error)
                
            elif response.status_code == 429:
                result.error = "Превышен лимит запросов"
                raise RateLimitError(result.error)
                
            else:
                result.error = f"Ошибка API: {response.status_code} - {response.text}"
                
        except requests.exceptions.RequestException as e:
            result.error = f"Сетевая ошибка: {e}"
            
        return result
    
    def validate_credentials(self) -> bool:
        """Проверка валидности API ключа"""
        try:
            # Простая проверка через запрос к API
            response = requests.get(
                f"{self.base_url}/senders",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
