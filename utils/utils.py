import os
import requests
import random
import time
import pytz

from typing import Union
from datetime import datetime


def get_requests(url, city=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1000.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://nlmk.shop',
    }

    cookies = {
        'nlmkB2C-customerLocation': city,
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=(10, 30))
        response.raise_for_status()
    except:
        return False
    return response


def get_current_time(file=False):
    """
    Возвращает текущую дату и время в формате "ГГГГ-ММ-ДД ЧЧ:ММ:СС" или в формате для использования в имени файла.
    Args:
        file (bool): Если True, возвращает дату и время в формате, подходящем для имени файла.
                     Если False (по умолчанию), возвращает дату и время в стандартном формате.
    Returns:
        str: Строка с текущей датой и временем.
    Example:
        get_current_time()  # Возвращает "2023-10-27 15:45:30"
        get_current_time(file=True)  # Возвращает "-2023-10-27-15-45-30-"
    """

    moscow_tz = pytz.timezone('Europe/Moscow')

    current_datetime = datetime.now(moscow_tz)
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    if file:
        formatted_datetime = current_datetime.strftime("-%Y-%m-%d-%H-%M-%S-")
    return formatted_datetime


def print_template(message) -> str:
    """
    Форматирует сообщение с текущей датой и временем и возвращает его как строку.
    Args:
        message (str): Сообщение для форматирования.
    Returns:
        str: Строка с текущей датой и временем, а также переданным сообщением.
    """

    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"\r{current_date}: {message}"
    return message


def check_reports_folder_exist() -> Union[str, bool]:
    """
    Проверяет наличие папки для отчетов и создает ее, если она не существует.
    Returns:
        Union[str, bool]: Возвращает путь к папке для отчетов, если папка успешно создана или уже существует.
                         Возвращает False в случае ошибки.
    """

    try:
        root_folder = os.environ.get('PROJECT_ROOT')
        reports_folder = os.path.join(root_folder, "reports")
        reports_folder_sql = os.path.join(reports_folder, "sqlite")
        reports_folder_json = os.path.join(reports_folder, "json")

        if not os.path.exists(reports_folder):
            os.makedirs(reports_folder)

        if not os.path.exists(reports_folder_sql):
            os.makedirs(reports_folder_sql)

        if not os.path.exists(reports_folder_json):
            os.makedirs(reports_folder_json)

        return reports_folder
    except Exception as e:
        print(print_template("Could not find or create reports folder: {}".format(e)))
        return False


def random_sleep(seconds: int):
    """
    Приостанавливает выполнение программы на случайное количество времени, добавляя случайное значение к указанным секундам.
    Args:
        seconds (int): Количество секунд, на которое следует приостановить выполнение.
    Returns:
        None
    """

    random_value = random.uniform(0.01, 3)
    time.sleep(seconds + random_value)
