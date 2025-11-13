# Message Delivery System

Универсальная система доставки сообщений через различные каналы: Email, SMS (Yandex Cloud) и Telegram.

## Возможности

- ✅ Отправка email через SMTP
- ✅ Отправка SMS через Yandex Cloud Notification Service  
- ✅ Отправка уведомлений в Telegram
- ✅ **Надежная доставка**: Автоматический переход к резервному каналу (fallback) при неудаче.
- ✅ **Асинхронная отправка**: Фоновая обработка сообщений с помощью Celery и Redis.
- ✅ Повторные попытки при ошибках
- ✅ Подробное логирование
- ✅ Массовая рассылка
- ✅ Гибкая конфигурация через YAML и переменные окружения.

## Быстрый старт

### 1. Настройка окружения

- **Клонируйте репозиторий** (если вы этого еще не сделали).
- **Установите зависимости**:
  ```bash
  pip install -r requirements.txt
  ```
- **Настройте переменные окружения**:
  - Скопируйте файл `.env.example` в `.env`.
    ```bash
    copy .env.example .env
    ```
  - Откройте файл `.env` и впишите ваши реальные учетные данные (ключи API, пароли и т.д.).

- **Установите и запустите Redis**:
  - Для асинхронной работы требуется Redis. Убедитесь, что он установлен и запущен на `localhost:6379` (или измените адрес в `config/default.yaml`).

### 2. Запуск Celery Worker

Для обработки асинхронных задач необходимо запустить Celery worker. Откройте новый терминал и выполните команду из корня проекта:

```bash
celery -A celery_app worker --loglevel=info
```

Этот worker будет ожидать и выполнять задачи по отправке сообщений.

### 3. Использование системы

Теперь вы можете использовать систему в своем коде.

#### Синхронная отправка с резервированием

```python
from main import MessageDeliverySystem, Message, MessageType

# Инициализация системы
system = MessageDeliverySystem("config/default.yaml")

# Создание сообщения
notification = Message(
    recipient="user_chat_id", # Будет заменен в зависимости от канала
    subject="Важное уведомление",
    content="Проверка работы системы с резервированием."
)

# Определение цепочки: сначала Telegram, потом SMS
delivery_chain = [MessageType.TELEGRAM, MessageType.SMS]

# Отправка
success = system.send_with_fallback(notification, delivery_chain)

if success:
    print("Сообщение успешно отправлено.")
```

#### Асинхронная отправка

```python
from main import MessageDeliverySystem, Message, MessageType

system = MessageDeliverySystem("config/default.yaml")

async_notification = Message(
    recipient="user@example.com",
    subject="Асинхронное уведомление",
    content="Это сообщение будет отправлено в фоновом режиме."
)

# Цепочка для асинхронной отправки
async_chain = [MessageType.EMAIL, MessageType.TELEGRAM]

# Добавление задачи в очередь
system.send_message_async(async_notification, async_chain)
print("Задача на отправку добавлена в очередь.")
```

## Подробная документация

Смотрите папку `docs/` для подробной настройки каждого провайдера.