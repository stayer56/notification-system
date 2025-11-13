import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from ..core.exceptions import ConfigurationError

load_dotenv()

class Config:
    """Класс для работы с конфигурацией"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_data = {}
        
        if config_path:
            self.load_from_file(config_path)
        
        self.load_from_env()
    
    def load_from_file(self, config_path: str):
        """Загрузка конфигурации из YAML файла"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_data.update(yaml.safe_load(f) or {})
        except Exception as e:
            raise ConfigurationError(f"Ошибка загрузки конфигурации: {e}")
    
    def load_from_env(self):
        """Загрузка конфигурации из переменных окружения"""
        env_mappings = {
            'EMAIL_SMTP_SERVER': ['email', 'smtp_server'],
            'EMAIL_PORT': ['email', 'port'],
            'EMAIL_USERNAME': ['email', 'username'],
            'EMAIL_PASSWORD': ['email', 'password'],
            'YANDEX_API_KEY': ['sms', 'api_key'],
            'YANDEX_FOLDER_ID': ['sms', 'folder_id'],
            'TELEGRAM_BOT_TOKEN': ['telegram', 'bot_token'],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(self.config_data, config_path, value)
    
    def _set_nested_value(self, data: Dict, path: list, value: Any):
        """Установка значения во вложенной структуре"""
        current = data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        keys = key.split('.')
        current = self.config_data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Получение конфигурации для провайдера"""
        return self.get(provider, {})
