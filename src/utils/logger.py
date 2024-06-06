"""
A module for setting up logging.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name):
    """Setup logging configuration."""
    logger = logging.getLogger(name)

    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Validate log level
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        log_level = 'INFO'

    logger.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(log_level)

    # file handler with rotation
    log_file_path = os.getenv('LOG_FILE_PATH', 'application.log')
    fh = RotatingFileHandler(filename=log_file_path, maxBytes=1024*1024*5, backupCount=5)
    fh.setFormatter(formatter)
    fh.setLevel(log_level)

    # Add handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


if __name__ == '__main__':
    logger = setup_logger(__name__)
    logger.info('This is a test log message')
