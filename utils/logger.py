import gzip
import inspect
import logging
import os
import shutil
import datetime

from colorama import (
    init,
    Fore,
    Style,
)


init(autoreset=True)

LEVEL_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.MAGENTA,
}
LOG_DIR = 'logs'
LOG_DIR_ARCHIVE = 'archive'


class ColorFormatter(logging.Formatter):
    COLOR_CODES = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }

    def get_func_hierarchy(self, record) -> str:
        '''
        Получение иерархии функции

        Args:
            record: запись

        Returns:
            Название фукнции
        '''

        stack = inspect.stack()

        record_file = record.pathname

        for frame in stack[1:]:
            if frame.filename == record_file:
                function_name = frame.function
                if function_name != record.funcName:
                    return function_name
        return ""

    def format(self, record):
        record.func_hierarchy = self.get_func_hierarchy(record)

        levelname = record.levelname
        if levelname in self.COLOR_CODES:
            levelname_color = f"{self.COLOR_CODES[levelname]}{levelname}{Style.RESET_ALL}"
            name_color = f"{self.COLOR_CODES[levelname]}{record.name}{Style.RESET_ALL}"
            record.levelname = levelname_color
            record.name = name_color
        return super().format(record)


def namer(name):
    name = name.replace('.log.', '-')
    path, name = name.split('logs/')
    return f'{LOG_DIR}/{LOG_DIR_ARCHIVE}/{name}.log.gz'


def rotator(source, dest):
    dest_dir = os.path.dirname(dest)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(source, 'rb') as f_in:
        with gzip.open(dest, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(source)


def get_logger(name: str) -> logging.Logger:
    '''
    Получение логгера

    Args:
        name: название модуля

    Returns:
        Объект логгера
    '''

    logger = logging.getLogger(name)
    console_handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    formatter = ColorFormatter(
        '%(asctime)s %(levelname)s %(message)s %(name)s.%(funcName)s %(func_hierarchy)s'
    )
    console_handler.setFormatter(formatter)

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        f"{LOG_DIR}/{name}.log",
        when='midnight',
        interval=1,
        atTime=datetime.time(23, 59, 59),
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.namer = namer
    file_handler.rotator = rotator
    file_handler.setFormatter(formatter)
    logger.handlers = [console_handler, file_handler]
    return logger


def get_log_user_data(user_data: dict) -> dict:
    '''
    Получение данных пользователя для логов

    Args:
        user_data: данные пользователя
            {
              "email": "test_new@cc.com",
              "password": "test123",
              "confirm_password": "test123"
            }

    Returns:
        Словарь данных
        {
          "email": "test_new@cc.com"
        }
    '''
    data = user_data.copy()
    keys = [
        'password',
        'confirm_password',
        'old_password',
        'new_password',
    ]
    for key in keys:
        data.pop(key, None)
    return data
