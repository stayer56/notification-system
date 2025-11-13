import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import Message, MessageType, MessagePriority
from main import MessageDeliverySystem

def main():
    # Инициализация системы
    system = MessageDeliverySystem()
    
    # Создание telegram сообщения
    message = Message(
        message_type=MessageType.TELEGRAM,
        recipient="123456789",
        content="Добрый день! Это тестовое уведомление от нашей системы.",
        priority=MessagePriority.HIGH
    )
    
    # Отправка сообщения
    success = system.send_message(message)
    
    if success:
        print("✅ Telegram отправлен успешно!")
    else:
        print("❌ Ошибка отправки Telegram")

if __name__ == "__main__":
    main()
