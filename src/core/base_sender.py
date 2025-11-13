from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .message import Message, DeliveryResult
from .exceptions import MessageDeliveryError
import time
import logging

class BaseMessageSender(ABC):
    """Абстрактный базовый класс для отправщиков сообщений"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def send(self, message: Message) -> DeliveryResult:
        """Отправка сообщения"""
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Проверка валидности учетных данных"""
        pass
    
    def _execute_with_retry(self, send_func, message: Message) -> DeliveryResult:
        """Выполнение отправки с повторными попытками"""
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                result = send_func(message)
                if result.success:
                    result.delivery_time = time.time() - start_time
                    return result
                
                self.logger.warning(f"Попытка {attempt + 1} не удалась: {result.error}")
                
            except Exception as e:
                self.logger.error(f"Ошибка при попытке {attempt + 1}: {e}")
                result = DeliveryResult(success=False, error=str(e), attempts=attempt + 1)
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        result.timestamp = time.time()
        return result
