class TokenVariablesError(Exception):
    """Ошибка отсутствия переменных окружения."""

    pass


class EndpointError(Exception):
    """Ошибка при запросе к эндпоинту."""

    pass


class SendError(Exception):
    """Ошибка при отправке сообщения."""

    pass


class GetApiError(Exception):
    """Ошибка при запросе к эндпоинту."""

    pass


class JSONError(Exception):
    """Ошибка при обработке JSON."""

    pass
