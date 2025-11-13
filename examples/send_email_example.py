import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import Message, MessageType, MessagePriority
from main import MessageDeliverySystem

def main():
    # Инициализация системы
    system = MessageDeliverySystem()
    
    # Создание email сообщения
    message = Message(
        message_type=MessageType.EMAIL,
        recipient="test@example.com",
        subject="Важное уведомление",
        content="Добрый день! Это тестовое уведомление от нашей системы.",
        priority=MessagePriority.HIGH,
        attachments=["/path/to/file.pdf"]  # опционально
    )
    
    # Отправка сообщения
    success = system.send_message(message)
    
    if success:
        print("✅ Email отправлен успешно!")
    else:
        print("❌ Ошибка отправки email")

if __name__ == "__main__":
    main()
