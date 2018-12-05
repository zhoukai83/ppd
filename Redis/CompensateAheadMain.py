import sys
sys.path.append("..")

import logging

import time
from Redis.PpdRedisClient import PpdRedisClient


def main():
    redis_client = PpdRedisClient()

    redis_client.get_loan_list_items()

    pass

if __name__ == "__main__":
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=15, format=logging_format)
    logger = logging.getLogger(__name__)

    main()