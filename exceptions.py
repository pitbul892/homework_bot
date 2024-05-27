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


class CurrentDateKeyError(Exception):
    """Ошибка при отсутствии current_date."""

    pass


class CurrentDatTypeError(Exception):
    """Ошибка при не соответствии типа current_date."""

    pass
