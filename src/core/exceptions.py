class MessageDeliveryError(Exception):
    """Базовое исключение для ошибок доставки сообщений"""
    pass

class ConfigurationError(MessageDeliveryError):
    """Ошибка конфигурации"""
    pass

class AuthenticationError(MessageDeliveryError):
    """Ошибка аутентификации"""
    pass

class RateLimitError(MessageDeliveryError):
    """Превышен лимит запросов"""
    pass

class NetworkError(MessageDeliveryError):
    """Сетевая ошибка"""
    pass

class ValidationError(MessageDeliveryError):
    """Ошибка валидации данных"""
    pass
