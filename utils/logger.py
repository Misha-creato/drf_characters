import gzip
import inspect
import logging
import os
import shutil
from datetime import datetime

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


class ColorFormatter(logging.Formatter):
    COLOR_CODES = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }

    def format(self, record):
        stack = inspect.stack()

        function_hierarchy = []
        record_file = record.pathname

        for frame in stack[1:]:
            if frame.filename == record_file:
                function_name = frame.function
                function_hierarchy.append(function_name)

        if len(function_hierarchy) > 1:
            record.funcName = " -> ".join(function_hierarchy)
        else:
            record.funcName = function_hierarchy[-1] if function_hierarchy else record.funcName

        levelname = record.levelname
        if levelname in self.COLOR_CODES:
            levelname_color = f"{self.COLOR_CODES[levelname]}{levelname}{Style.RESET_ALL}"
            name_color = f"{self.COLOR_CODES[levelname]}{record.name}{Style.RESET_ALL}"
            record.levelname = levelname_color
            record.name = name_color
        return super().format(record)


def namer(name):
    name = name.split('.log')[0]
    path, name = name.split('logs/')
    time = datetime.now().strftime('%Y-%m-%d')
    return f'{LOG_DIR}/archive/{name}-{time}.log.gz'


def rotator(source, dest):
    with open(source, 'rb') as f_in:
        with gzip.open(dest, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(source)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    console_handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    formatter = ColorFormatter(
        '%(asctime)s %(levelname)s %(message)s %(name)s.%(funcName)s'
    )
    console_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        f"{LOG_DIR}/{name}.log",
        maxBytes=512000,
        backupCount=5,
    )
    file_handler.namer = namer
    file_handler.rotator = rotator
    file_handler.setFormatter(formatter)
    logger.handlers = [console_handler, file_handler]
    return logger


def get_log_user_data(user_data: dict) -> dict:
    data = user_data.copy()
    keys = [
        'password',
        'confirm_password',
        'new_password',
    ]
    for key in keys:
        data.pop(key, None)
    return data
