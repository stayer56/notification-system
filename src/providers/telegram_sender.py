import requests
import time
from typing import Optional, Dict, Any, Union
import logging

from ..core.base_sender import BaseMessageSender
from ..core.message import Message, MessageType, DeliveryResult
from ..core.exceptions import AuthenticationError, ValidationError

class TelegramSender(BaseMessageSender):
    """Отправщик сообщений в Telegram"""
    
    def __init__(
        self,
        bot_token: str,
        base_url: str = "https://api.telegram.org/bot",
        timeout: int = 30,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.bot_token = bot_token
        self.base_url = f"{base_url}{bot_token}"
        self.timeout = timeout
        
    def send(self, message: Message) -> DeliveryResult:
        """Отправка сообщения в Telegram"""
        if message.message_type != MessageType.TELEGRAM:
            raise ValidationError("Некорректный тип сообщения для TelegramSender")
        
        return self._execute_with_retry(self._send_telegram, message)
    
    def _send_telegram(self, message: Message) -> DeliveryResult:
        """Внутренняя логика отправки в Telegram"""
        result = DeliveryResult(success=False, attempts=1)
        
        try:
            payload = {
                'chat_id': message.recipient,
                'text': message.content,
                'disable_web_page_preview': True
            }
            
            if message.subject:
                payload['parse_mode'] = 'HTML'
                payload['text'] = f"<b>{message.subject}</b>\n\n{message.content}"
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=self.timeout
            )
            
            response_data = response.json()
            
            if response_data.get('ok'):
                message_data = response_data['result']
                result.success = True
                result.message_id = str(message_data['message_id'])
                result.provider_response = message_data
                
            else:
                error_description = response_data.get('description', 'Unknown error')
                
                if "chat not found" in error_description.lower():
                    result.error = "Чат не найден"
                elif "bot was blocked" in error_description.lower():
                    result.error = "Бот заблокирован пользователем"
                else:
                    result.error = f"Telegram API error: {error_description}"
                    
        except requests.exceptions.RequestException as e:
            result.error = f"Сетевая ошибка: {e}"
            
        return result
    
    def validate_credentials(self) -> bool:
        """Проверка валидности токена бота"""
        try:
            response = requests.get(
                f"{self.base_url}/getMe",
                timeout=self.timeout
            )
            data = response.json()
            return data.get('ok', False)
        except Exception:
            return False
