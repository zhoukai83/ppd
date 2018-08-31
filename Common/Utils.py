from re import sub
from decimal import Decimal
import logging
import logging.config
import os
import json
import io


def convert_currency_to_float(currency):
    return float(Decimal(sub(r'[^\d.]', '', currency)))


def convert_to_int(temp):
    temp = str(temp)
    return int(Decimal(sub(r'[^\d.]', '', temp)))


def convert_to_float(temp):
    temp = str(temp)
    return float(Decimal(sub(r'[^\d.]', '', temp)))


def setup_logging(default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    logger = logging.getLogger(__name__)
    logger.info("start")
    return logger


def get_211_school():
    with io.open("211.txt", mode="r", encoding="utf-8") as f:
        content = f.read()

    return content.split("\n")


class AutoDispose:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
