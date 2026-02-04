"""
Logger module.

Creates logger with console output and file rotation
"""

import logging
from logging import getLogger, StreamHandler
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
LOG_FORMAT = '%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s'
MAX_BYTES = 1024 * 1024
BACKUP_COUNT = 5
LOG_LEVEL = logging.INFO

def setup_logger():
    """Logger configuration"""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
    except OSError as e:
        print(f"Failed to create log directory: {e}")
        raise

    logger = getLogger(__name__)

    if logger.handlers:
        return logger

    file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "main.log"),
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )

    console_handler = StreamHandler()

    for handler in (file_handler, console_handler):
        handler.setLevel(LOG_LEVEL)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.setLevel(LOG_LEVEL)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()