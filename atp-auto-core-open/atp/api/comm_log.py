# -*- coding:utf-8 -*-

import logging
# from logging.handlers import WatchedFileHandler
from atp.api.safe_file_handler import SafeFileHandler
import time

from atp.config.default import get_config

config = get_config()

log_path = config.LOG_PATH

formatter = logging.Formatter('[%(filename)-12s]: [%(levelname)-6s] [%(asctime)s]: %(message)s')

# watched_file_handler = WatchedFileHandler(log_path, encoding="utf-8")
safe_file_handler = SafeFileHandler(log_path, encoding="utf-8")

safe_file_handler.setFormatter(formatter)

safe_file_handler.setLevel(logging.INFO)
# watched_file_handler.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.INFO)

logger.addHandler(safe_file_handler)

if __name__ == "__main__":

    for i in range(10):
        logger.debug("This is debug information")
        logger.info("This is info information")
        logger.error("This is error information")
        time.sleep(.1)
