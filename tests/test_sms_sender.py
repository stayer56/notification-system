import pytest
from src.providers.sms_sender import YandexCloudSMSSender
from src.core.message import Message, MessageType

class TestYandexCloudSMSSender:
    def test_send_message_success(self, mocker):
        # Тест успешной отправки sms
        pass
    
    def test_send_message_failure(self, mocker):
        # Тест неудачной отправки sms
        pass
