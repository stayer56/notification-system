from typing import Dict, Any, Optional
from ..core.base_sender import BaseMessageSender
from ..core.message import MessageType
from ..core.exceptions import ConfigurationError
from .email_sender import EmailSender
from .sms_sender import YandexCloudSMSSender
from .telegram_sender import TelegramSender

class SenderFactory:
    """Фабрика для создания отправщиков сообщений"""
    
    _senders = {
        MessageType.EMAIL: EmailSender,
        MessageType.SMS: YandexCloudSMSSender,
        MessageType.TELEGRAM: TelegramSender
    }
    
    @classmethod
    def create_sender(
        cls, 
        message_type: MessageType, 
        config: Dict[str, Any]
    ) -> BaseMessageSender:
        """Создание отправщика по типу сообщения"""
        sender_class = cls._senders.get(message_type)
        if not sender_class:
            raise ConfigurationError(f"Неизвестный тип сообщения: {message_type}")
        
        return sender_class(**config)
    
    @classmethod
    def register_sender(cls, message_type: MessageType, sender_class):
        """Регистрация нового типа отправщика"""
        cls._senders[message_type] = sender_class
