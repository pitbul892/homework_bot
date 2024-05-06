class TokenVariablesError(Exception):
    def __init__(self, token_name):
        self.txt= f'Отсутствует обязательная переменная окружения: "{token_name}"'
