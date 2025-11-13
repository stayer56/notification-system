from celery import Celery
from src.utils.config import Config

# Загрузка конфигурации
conf = Config('config/default.yaml')
celery_conf = conf.get('celery', {})

# Создание экземпляра Celery
app = Celery(
    'message_delivery',
    broker=celery_conf.get('broker_url', 'redis://localhost:6379/0'),
    backend=celery_conf.get('result_backend', 'redis://localhost:6379/0'),
    include=['src.tasks']
)

# Загрузка конфигурации из объекта
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone=celery_conf.get('timezone', 'Europe/Moscow'),
    enable_utc=True,
)

if __name__ == '__main__':
    app.start()
