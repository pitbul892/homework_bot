import logging
import os
import time
from http import HTTPStatus
from json import JSONDecodeError

import requests
import telebot
from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import (Get_Api_Error, JSONError, EndpointError, StatusError)

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
    logger.info('start "check_tokens"')
    pr_token = globals()['PRACTICUM_TOKEN']
    tg_token = globals()['TELEGRAM_TOKEN']
    tg_chat = globals()['TELEGRAM_CHAT_ID']
    if not pr_token:
        token_name = 'PRACTICUM_TOKEN'
        text_error = f'Отсутствует обязательная переменная: "{token_name}"'
        logger.critical(text_error)
    if not tg_token:
        token_name = 'TELEGRAM_TOKEN'
        text_error = f'Отсутствует обязательная переменная: "{token_name}"'
        logger.critical(text_error)
    if not tg_chat:
        token_name = 'TELEGRAM_CHAT_ID'
        text_error = f'Отсутствует обязательная переменная: "{token_name}"'
        logger.critical(text_error)
    if not pr_token or not tg_token or not tg_chat:
        raise SystemExit(text_error)

    logger.info('"check_tokens" completed successfully')


def send_message(bot, message):
    """Отправляет сообщение."""
    logger.info('start "send_message"')
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telebot.apihelper.ApiException as e:
        logger.error(f'Ошибка отправки сообщения: {e}')
    else:
        logger.debug('Сообщение отправлено успешно!')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту."""
    logger.info('start "get_api_answer"')
    try:
        response = requests.get(ENDPOINT, headers=HEADERS,
                                params={'from_date': timestamp})
        if response.status_code != HTTPStatus.OK:
            raise EndpointError(f'Эндпоинт - {ENDPOINT} не доступен')
    except requests.RequestException as error:
        raise Get_Api_Error(f'Ошибка при запросе к основному API: {error}')
    try:
        response = response.json()
    except JSONDecodeError as error:
        raise JSONError(f'Ошибка при обработке JSON: {error}')
        logger.error(f'Ошибка при обработке JSON: {error}')
    logger.info('"get_api_answer" completed successfully')
    return response


def check_response(response):
    """Проверяет, что по ключу 'homeworks' выдает список."""
    logger.info('start "check_response"')
    if not isinstance(response, dict):
        raise TypeError('Полученная структура данных'
                        'не соответствует заданной (dict)')
    if 'homeworks' not in response:
        raise KeyError('Ключ "homeworks" отсутствует')
    if 'current_date' not in response:
        raise KeyError('Ключ "current_date" отсутствует')
    homeworks = response['homeworks']
    current_date = response['current_date']
    if not isinstance(current_date, int):
        raise TypeError('Полученная структура данных ключа "current_date"'
                        'не соответствует заданной (int)')
    if not isinstance(homeworks, list):
        raise TypeError('Полученная структура данных ключа "homeworks"'
                        'не соответствует заданной (list)')
    logger.info('"check_response" completed successfully')
    return homeworks


def parse_status(homework):
    """Извлекает статус из конкретной дз."""
    logger.info('start "parse_status"')
    homework_name = homework.get('homework_name')
    if not homework_name:
        raise KeyError('Ключ "homework_name" отсутствует')
    status = homework.get('status')
    if not status:
        raise KeyError('Ключ "status" отсутствует')
    verdict = HOMEWORK_VERDICTS.get(status)
    if not verdict:
        raise StatusError('Неожиданный статус дз')
    logger.info('"parse_status" completed successfully')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
        except (EndpointError, Get_Api_Error, JSONError) as error:
            send_message(bot, error)
            logger.error(error)
        try:
            verified_hw = check_response(response)
            if verified_hw:
                send_message(bot, parse_status(verified_hw[0]))
            else:
                logger.debug('Новые статусы отсутствуют')
            timestamp = response['current_date']
        except (TypeError, KeyError) as error:
            logger.error(error)
        except Exception as error:
            send_message(bot, error)
            logger.error(f'Сбой в работе программы: {error}')
        finally:
            time.sleep(RETRY_PERIOD)


logging.basicConfig(
    level=logging.DEBUG,
    encoding='utf-8',
    filename='./program.log',
    format='%(asctime)s|%(levelname)s|%(lineno)d|'
    '%(funcName)s|%(message)s|%(name)s'
)

# Здесь установлены настройки логгера для текущего файла :
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    main()
