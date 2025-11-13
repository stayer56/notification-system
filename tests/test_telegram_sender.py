import pytest
from src.providers.telegram_sender import TelegramSender
from src.core.message import Message, MessageType

class TestTelegramSender:
    def test_send_message_success(self, mocker):
        # Тест успешной отправки telegram
        pass
    
    def test_send_message_failure(self, mocker):
        # Тест неудачной отправки telegram
        pass
