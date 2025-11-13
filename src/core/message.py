from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

class MessageType(Enum):
    EMAIL = "email"
    SMS = "sms"
    TELEGRAM = "telegram"

class MessagePriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

@dataclass
class Message:
    """Универсальный класс сообщения"""
    message_type: MessageType
    recipient: str
    content: str
    subject: Optional[str] = None
    attachments: Optional[List[str]] = None
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Optional[Dict[str, Any]] = None
    
    def validate(self) -> bool:
        """Валидация сообщения"""
        if not self.recipient:
            raise ValidationError("Получатель не может быть пустым")
        if not self.content:
            raise ValidationError("Содержимое сообщения не может быть пустым")
        return True

@dataclass
class DeliveryResult:
    """Результат доставки сообщения"""
    success: bool
    message_id: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempts: int = 1
    timestamp: float = 0.0
    delivery_time: Optional[float] = None
