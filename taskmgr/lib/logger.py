import logging
from logging.handlers import RotatingFileHandler
import os
import sys

from taskmgr.lib.variables import CommonVariables


class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno <= self.__level


class AppLogger:
    """
    The log messages with an INFO level are only written to the console. All log messages
    are written to the log file.
    """

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        log_dir = AppLogger.get_dir()
        file_handler = RotatingFileHandler(f"{log_dir}/taskmgr.log", maxBytes=50000000, backupCount=10)
        file_formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.addFilter(MyFilter(logging.INFO))
        console_formatter = logging.Formatter('%(levelname)s : %(name)s : %(message)s')
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    @staticmethod
    def get_dir():
        log_dir = CommonVariables().log_dir
        os.makedirs(f"{log_dir}", 0o777, exist_ok=True)
        return log_dir

    def get_logger(self):
        return self.logger
