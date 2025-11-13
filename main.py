#!/usr/bin/env python3
"""
Основной модуль системы доставки сообщений
"""

import sys
from pathlib import Path
from typing import List

# Добавляем src в путь для импорта
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src import Message, MessageType, MessagePriority, SenderFactory, Config, setup_logger
from src.tasks import send_message_async as send_async

class MessageDeliverySystem:
    """Основная система доставки сообщений"""
    
    def __init__(self, config_path: str = None):
        self.config = Config(config_path)
        self.logger = setup_logger("MessageSystem", log_file=self.config.get("logging.file", "logs/message_system.log"))
        
        # Инициализация отправщиков
        self.senders = {}
        self._initialize_senders()
    
    def _initialize_senders(self):
        """Инициализация всех отправщиков"""
        for msg_type in MessageType:
            provider_config = self.config.get_provider_config(msg_type.value)
            if provider_config:
                try:
                    # Добавляем общие настройки retry
                    retry_config = self.config.get('retry', {})
                    provider_config.update(retry_config)
                    
                    sender = SenderFactory.create_sender(msg_type, provider_config)
                    if sender.validate_credentials():
                        self.senders[msg_type] = sender
                        self.logger.info(f"Отправщик {msg_type.value} инициализирован")
                    else:
                        self.logger.warning(f"Не удалось валидировать отправщик {msg_type.value}")
                except Exception as e:
                    self.logger.error(f"Ошибка инициализации отправщика {msg_type.value}: {e}")
    
    def send_message(self, message: Message) -> bool:
        """Отправка сообщения через одного провайдера."""
        if message.message_type not in self.senders:
            self.logger.error(f"Отправщик для типа {message.message_type} не настроен")
            return False
        
        try:
            message.validate()
            sender = self.senders[message.message_type]
            result = sender.send(message)
            
            if result.success:
                self.logger.info(f"Сообщение отправлено успешно. ID: {result.message_id}")
            else:
                self.logger.error(f"Ошибка отправки: {result.error}")
            
            return result.success
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке сообщения: {e}")
            return False

    def send_with_fallback(self, message: Message, chain: List[MessageType]) -> bool:
        """
        Отправка сообщения с использованием цепочки резервных провайдеров.
        Пробует отправить сообщение по каждому каналу в цепочке до первого успеха.
        """
        if not chain:
            self.logger.error("Цепочка отправки пуста.")
            return False

        last_error = ""
        for provider_type in chain:
            if provider_type not in self.senders:
                self.logger.warning(f"Провайдер {provider_type.value} не настроен, пропускаем.")
                continue

            self.logger.info(f"Попытка отправки через {provider_type.value}...")
            message.message_type = provider_type # Меняем тип сообщения для текущего провайдера
            
            try:
                message.validate()
                sender = self.senders[provider_type]
                result = sender.send(message)

                if result.success:
                    self.logger.info(f"Сообщение успешно отправлено через {provider_type.value}. ID: {result.message_id}")
                    return True
                else:
                    last_error = result.error
                    self.logger.warning(f"Не удалось отправить через {provider_type.value}: {last_error}")

            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Критическая ошибка при отправке через {provider_type.value}: {last_error}")
        
        self.logger.error(f"Не удалось отправить сообщение по всей цепочке. Последняя ошибка: {last_error}")
        return False

    def send_message_async(self, message: Message, delivery_chain: List[MessageType]):
        """Асинхронная отправка сообщения с использованием Celery."""
        self.logger.info(f"Добавление задачи на асинхронную отправку для {message.recipient}")
        send_async(message, delivery_chain)

    def broadcast(self, messages: list, use_fallback: bool = False, chain: List[MessageType] = None) -> dict:
        """Массовая отправка сообщений"""
        results = {
            'total': len(messages),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for message in messages:
            if use_fallback and chain:
                success = self.send_with_fallback(message, chain)
            else:
                success = self.send_message(message)

            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append({
                'type': message.message_type.value,
                'recipient': message.recipient,
                'success': success
            })
        
        return results

def main():
    """Пример использования системы"""
    # Укажите путь к вашему файлу конфигурации
    system = MessageDeliverySystem("config/default.yaml")
    
    # --- Пример 1: Синхронная отправка с резервированием ---
    print("--- Пример 1: Синхронная отправка с резервированием ---")
    # Создаем универсальное сообщение без указания типа
    notification = Message(
        recipient="+79991234567", # Укажите реальный номер или email
        subject="Важное системное уведомление",
        content="Проверка работы системы уведомлений с резервированием.",
        priority=MessagePriority.HIGH,
        message_type=None # Тип будет устанавливаться в `send_with_fallback`
    )
    
    # Определяем цепочку отправки: сначала Telegram, если не вышло - SMS, потом Email
    delivery_chain = [MessageType.TELEGRAM, MessageType.SMS, MessageType.EMAIL]
    
    # Меняем получателя в зависимости от канала
    # Это упрощение, в реальной системе у пользователя должны быть все его контакты
    # Здесь для примера мы будем менять получателя "на лету"
    
    # Для Telegram (нужен chat_id)
    notification.recipient = "123456789" # Замените на ваш chat_id
    
    # Для SMS
    # notification.recipient = "+79991234567" 
    
    # Для Email
    # notification.recipient = "user@example.com"

    success = system.send_with_fallback(notification, delivery_chain)
    if success:
        print("✅ Сообщение успешно отправлено по одному из каналов.")
    else:
        print("❌ Не удалось отправить сообщение ни по одному из каналов.")

    # --- Пример 2: Асинхронная отправка ---
    print("\n--- Пример 2: Асинхронная отправка через Celery ---")
    
    # Сообщение для асинхронной отправки
    async_notification = Message(
        recipient="user@example.com", # Получатель для первого провайдера в цепочке
        subject="Асинхронное уведомление",
        content="Это сообщение будет отправлено в фоновом режиме.",
        priority=MessagePriority.NORMAL,
        message_type=None 
    )
    
    # Цепочка для асинхронной отправки
    async_chain = [MessageType.EMAIL, MessageType.TELEGRAM]

    # Вызов асинхронной отправки
    system.send_message_async(async_notification, async_chain)
    print("✅ Задача на асинхронную отправку добавлена в очередь.")
    print("Для выполнения задачи запустите Celery worker: celery -A celery_app worker --loglevel=info")


if __name__ == "__main__":
    main()
