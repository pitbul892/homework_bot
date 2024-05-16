class TokenVariablesError(Exception):
    """Ошибка отсутствия переменных окружения."""

    pass


class EndpointError(Exception):
    """Ошибка при запросе к эндпоинту."""

    pass


class StatusError(Exception):
    """Ошибка статуса."""

    pass


class SendError(Exception):
    """Ошибка при отправке сообщения."""

    pass


class Get_Api_Error(Exception):
    """Ошибка при запросе к эндпоинту."""

    pass


class JSONError(Exception):
    """Ошибка при обработке JSON."""

    pass