from celery_app import app
from main import MessageDeliverySystem
from src.core.message import Message, MessageType
from typing import List

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_task(self, message_data: dict, delivery_chain: List[str]):
    """
    Задача Celery для асинхронной отправки уведомления с использованием цепочки провайдеров.
    """
    try:
        system = MessageDeliverySystem('config/default.yaml')
        
        # Преобразование словаря обратно в объект Message
        message_data['message_type'] = MessageType(message_data['message_type'])
        message = Message(**message_data)

        # Преобразование строк в MessageType
        chain = [MessageType(provider) for provider in delivery_chain]

        # Попытка отправить через цепочку
        success = system.send_with_fallback(message, chain)

        if not success:
            raise Exception("Failed to send message through all providers in the chain.")

        return {"status": "Success", "message": f"Message sent to {message.recipient}"}

    except Exception as exc:
        # Повторная попытка задачи в случае неудачи
        self.retry(exc=exc)

def send_message_async(message: Message, delivery_chain: List[MessageType]):
    """
    Хелпер для вызова задачи Celery.
    Преобразует MessageType в строки для сериализации.
    """
    # Преобразование объекта Message в словарь для сериализации
    message_data = {
        "message_type": message.message_type.value,
        "recipient": message.recipient,
        "content": message.content,
        "subject": message.subject,
        "attachments": message.attachments,
        "priority": message.priority.name,
        "metadata": message.metadata,
    }
    
    # Преобразование MessageType в строки
    chain_str = [provider.value for provider in delivery_chain]
    
    send_notification_task.delay(message_data, chain_str)
