import smtplib
import time
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.application import MimeApplication
from typing import Optional, List
import logging

from ..core.base_sender import BaseMessageSender
from ..core.message import Message, MessageType, DeliveryResult
from ..core.exceptions import AuthenticationError, ValidationError

class EmailSender(BaseMessageSender):
    """Отправщик email сообщений"""
    
    def __init__(
        self,
        smtp_server: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        timeout: int = 30,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.timeout = timeout
        
    def send(self, message: Message) -> DeliveryResult:
        """Отправка email"""
        if message.message_type != MessageType.EMAIL:
            raise ValidationError("Некорректный тип сообщения для EmailSender")
        
        return self._execute_with_retry(self._send_email, message)
    
    def _send_email(self, message: Message) -> DeliveryResult:
        """Внутренняя логика отправки email"""
        result = DeliveryResult(success=False, attempts=1)
        
        try:
            # Создание сообщения
            msg = MimeMultipart()
            msg['From'] = self.username
            msg['To'] = message.recipient
            msg['Subject'] = message.subject or "No Subject"
            
            # Добавление текста
            msg.attach(MimeText(message.content, 'plain'))
            
            # Добавление вложений
            if message.attachments:
                for attachment_path in message.attachments:
                    try:
                        with open(attachment_path, 'rb') as file:
                            part = MimeApplication(
                                file.read(),
                                Name=attachment_path.split('/')[-1]
                            )
                        part['Content-Disposition'] = f'attachment; filename="{attachment_path.split("/")[-1]}"'
                        msg.attach(part)
                    except Exception as e:
                        self.logger.warning(f"Не удалось прикрепить файл {attachment_path}: {e}")
            
            # Отправка
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.port, timeout=self.timeout)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.port, timeout=self.timeout)
            
            server.login(self.username, self.password)
            server_response = server.sendmail(self.username, message.recipient, msg.as_string())
            server.quit()
            
            result.success = True
            result.provider_response = {"smtp_response": str(server_response)}
            
        except smtplib.SMTPAuthenticationError as e:
            result.error = f"Ошибка аутентификации: {e}"
            raise AuthenticationError(result.error) from e
        except Exception as e:
            result.error = f"Ошибка отправки email: {e}"
            
        return result
    
    def validate_credentials(self) -> bool:
        """Проверка учетных данных SMTP"""
        try:
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.port, timeout=self.timeout)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.port, timeout=self.timeout)
            
            server.login(self.username, self.password)
            server.quit()
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка валидации учетных данных: {e}")
            return False
