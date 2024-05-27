import logging
import os
import time
from collections import namedtuple
from http import HTTPStatus
from json import JSONDecodeError

import requests
import telebot
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import (CurrentDateKeyError, CurrentDatTypeError,
                        GetApiError, JSONError, EndpointError)

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
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}


def check_tokens():
    """Проверяет доступность пременных окружения."""
    logger.info('check')
    TOKEN_MAMES = ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
    empty_tokens = [
        token for token in TOKEN_MAMES
        if not globals()[token]
    ]
    if empty_tokens:
        text_error = (f'Отсутствуют обязательные переменные:'
                      f' "{", ".join(empty_tokens)}"')
        logger.critical(text_error)
        raise SystemExit(text_error)


def send_message(bot, message):
    """Отправляет сообщение."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telebot.apihelper.ApiException as e:
        logger.error(f'Ошибка отправки сообщения: {e}')
    else:
        logger.debug('Сообщение отправлено успешно!')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту."""
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        )
        if response.status_code != HTTPStatus.OK:
            raise EndpointError(f'Эндпоинт - {ENDPOINT} не доступен')
        return response.json()
    except requests.RequestException as error:
        raise GetApiError(f'Ошибка при запросе к основному API: {error}')
    except JSONDecodeError as error:
        raise JSONError(f'Ошибка при обработке JSON: {error}')


def check_response(response):
    """Проверяет, что по ключу 'homeworks' выдает список."""
    if not isinstance(response, dict):
        raise TypeError(
            'Полученная структура данных' 'не соответствует заданной (dict)'
        )
    if 'homeworks' not in response:
        raise KeyError('Ключ "homeworks" отсутствует')
    if 'current_date' not in response:
        raise CurrentDateKeyError('Ключ "current_date" отсутствует')
    homeworks = response['homeworks']
    current_date = response['current_date']
    if not isinstance(current_date, int):
        raise CurrentDatTypeError(
            'Полученная структура данных ключа "current_date"'
            'не соответствует заданной (int)'
        )
    if not isinstance(homeworks, list):
        raise TypeError(
            'Полученная структура данных ключа "homeworks"'
            'не соответствует заданной (list)'
        )
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
        raise ValueError('Неожиданный статус дз')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            verified_hw = check_response(response)
            if verified_hw:
                send_message(bot, parse_status(verified_hw[0]))
            else:
                logger.debug('Новые статусы отсутствуют')
            timestamp = response['current_date']
        except (CurrentDatTypeError, CurrentDateKeyError) as error:
            logger.error(error)
        except Exception as error:
            send_message(bot, error)
            logger.error(f'Сбой в работе программы: {error}')
        finally:
            time.sleep(RETRY_PERIOD)


def log_settings():
    """Настройка логгера."""
    logging.basicConfig(
        level=logging.DEBUG,
        encoding='utf-8',
        filename=os.path.dirname(__file__) + '\program.log',
        format='%(asctime)s|%(levelname)s|%(lineno)d|'
        '%(funcName)s|%(message)s|%(name)s',
    )


# Здесь установлены настройки логгера для текущего файла :
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    log_settings()
    main()
