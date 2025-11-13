import pytest
from src.providers.email_sender import EmailSender
from src.core.message import Message, MessageType

class TestEmailSender:
    def test_send_message_success(self, mocker):
        # Тест успешной отправки email
        pass
    
    def test_send_message_failure(self, mocker):
        # Тест неудачной отправки email
        pass
