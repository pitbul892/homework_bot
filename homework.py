import logging
import os, sys
import requests
import time
from dotenv import load_dotenv
from telebot import TeleBot, types
from logging.handlers import RotatingFileHandler
from exceptions import TokenVariablesError
load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM')
# PRACTICUM_TOKEN = ''
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = 628595727

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    ALL_TOKENS = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for token_name in ALL_TOKENS:
        if not ALL_TOKENS[token_name]:
            raise TokenVariablesError(token_name)
        


def send_message(bot, message):
    ...


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту."""
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params={'from_date': timestamp})
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
    response = response.json()
    # print(response)
    return response
  
def check_response(response):
    """Проверяет, что по ключу 'homeworks' выдает список."""
    # print(response)
    # print(response['homeworks'])
    if not isinstance(response['homeworks'], list):
        print(22)
        raise TypeError

def parse_status(homework):
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    
    try:
        check_tokens()
    except TokenVariablesError as error:
        logger.critical(error.txt)
        sys.exit()

    # Создаем объект класса бота
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:
            print(timestamp)
            response = get_api_answer(timestamp)
            check_response(response)

        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}')
            break
        time.sleep(60)


logging.basicConfig(
    level=logging.DEBUG,
    encoding='utf-8',
    filename='program.log', 
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

# Здесь установлены настройки логгера для текущего файла :
logger = logging.getLogger(__name__)
# Устанавливаем уровень, с которого логи будут сохраняться в файл:
logger.setLevel(logging.INFO)
# Указываем обработчик логов:
handler = RotatingFileHandler('my_logger.log',encoding='utf-8', maxBytes=50000000, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == '__main__':
    main()
