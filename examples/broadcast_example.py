import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import Message, MessageType, MessagePriority
from main import MessageDeliverySystem

def main():
    # Инициализация системы
    system = MessageDeliverySystem("config/default.yaml")
    
    # Пример отправки email
    email_message = Message(
        message_type=MessageType.EMAIL,
        recipient="user@example.com",
        subject="Тестовое сообщение",
        content="Это тестовое email сообщение",
        priority=MessagePriority.NORMAL
    )
    
    # Пример отправки SMS
    sms_message = Message(
        message_type=MessageType.SMS,
        recipient="+79123456789",
        content="Тестовое SMS сообщение",
        priority=MessagePriority.HIGH
    )
    
    # Пример отправки в Telegram
    telegram_message = Message(
        message_type=MessageType.TELEGRAM,
        recipient="123456789",
        content="Тестовое сообщение в Telegram",
        subject="Уведомление"
    )
    
    # Отправка всех сообщений
    messages = [email_message, sms_message, telegram_message]
    results = system.broadcast(messages)
    
    print("Результаты рассылки:")
    print(f"Всего: {results['total']}")
    print(f"Успешно: {results['successful']}")
    print(f"Неудачно: {results['failed']}")

if __name__ == "__main__":
    main()
