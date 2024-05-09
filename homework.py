import logging
import os
import sys
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import (
    TokenVariablesError, EndpointError, SendError, StatusError)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность пременных окружения."""
    ALL_TOKENS = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for token_name in ALL_TOKENS:
        if not ALL_TOKENS[token_name]:
            text_error = 'Отсутствует обязательная'
            f'переменная окружения: "{token_name}"'
            logging.critical(text_error)
            raise TokenVariablesError(text_error)


def send_message(bot, message):
    """Отправляет сообщение."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug('Сообщение отправлено успешно!')
        return True
    except SendError:
        logging.error('Ошибка отправки сообщения')
        return False


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту."""
    try:
        response = requests.get(ENDPOINT, headers=HEADERS,
                                params={'from_date': timestamp})
        if response.status_code != HTTPStatus.OK:
            logger.error(f'Эндпоинт - {ENDPOINT} не доступен')
            raise EndpointError(f'Эндпоинт - {ENDPOINT} не доступен')
    except Exception as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')
    response = response.json()
    return response


def check_response(response):
    """Проверяет, что по ключу 'homeworks' выдает список."""
    if not isinstance(response, dict):
        raise TypeError('Полученная структура данных'
                        'не соответствует заданной (dict)')
    if 'homeworks' not in response:
        raise KeyError('Ключ "homeworks" отсутствует')
    if 'current_date' not in response:
        raise KeyError('Ключ "current_date" отсутствует')
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError('Полученная структура данных ключа "homeworks"'
                        'не соответствует заданной (list)')
    return homeworks


def parse_status(homework):
    """Извлекает статус из конкретной дз."""
    homework_name = homework.get('homework_name')
    if not homework_name:
        raise KeyError('Ключ "homework_name" отсутствует')
    status = homework.get('status')
    if not status:
        raise KeyError('Ключ "status" отсутствует')
    verdict = HOMEWORK_VERDICTS.get(status)
    if not verdict:
        raise StatusError('Неожиданный статус дз')
    print(homework, homework_name, status, sep='\n')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    try:
        check_tokens()
    except TokenVariablesError:
        sys.exit()
    bot = TeleBot(token=TELEGRAM_TOKEN)

    while True:
        timestamp = int(time.time())
        try:
            print(timestamp)
            response = get_api_answer(timestamp)
            verified_hw = check_response(response)
            if verified_hw:
                message = send_message(bot, parse_status(verified_hw[0]))
                if message:
                    timestamp = response['current_date']
            else:
                logging.debug('Новые статусы отсутствуют')
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')

        time.sleep(600)


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.INFO,
        encoding='utf-8',
        filename='program.log',
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )

    # Здесь установлены настройки логгера для текущего файла :
    logger = logging.getLogger(__name__)
    # Устанавливаем уровень, с которого логи будут сохраняться в файл:
    logger.setLevel(logging.INFO)
    # Указываем обработчик логов:
    handler = RotatingFileHandler('my_logger.log', encoding='utf-8',
                                  maxBytes=50000000, backupCount=5)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    main()
