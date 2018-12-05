import sys
sys.path.insert(0, "..")

import redis
import logging
import time

from Open.PpdOpenClient import PpdOpenClient
from Common import Utils as CommonUtils
from collections import deque
import json
from argparse import ArgumentParser
from Redis.PpdRedisClient import PpdRedisClient

def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--index",
                        dest="client_index", default=1,
                        help="use client index")

    parser.add_argument("-t", "--interval time",
                        dest="interval_time", default=1,
                        help="2 request interval")

    args = parser.parse_args()
    interval_time = float(args.interval_time)
    print("use client index:", args.client_index)
    print("2 request interval:", interval_time)

    client = PpdOpenClient(key_index=int(args.client_index))
    redis_client = redis.StrictRedis(host='10.164.120.164', port=6379, db=0)
    listing_ids_cache = deque(maxlen=1000)
    last_refresh_list_time = time.time()
    ppd_redis_client = PpdRedisClient()

    key_loan_list_add_time = "LoanListAddTime"
    while True:
        try:
            if time.time() - last_refresh_list_time < interval_time:
                time.sleep(0.1)
                continue

            loan_list_items = client.get_loan_list_items()
            if not loan_list_items:
                continue

            last_refresh_list_time = time.time()
            logger.info("start")
            find_new = ppd_redis_client.add_loan_list_items(loan_list_items)
            logger.info(f"end {find_new}")
            # if loan_list_items:
            # find_new = False
            # for item in loan_list_items:
            #     if not redis_client.sismember("LoanListId", item["ListingId"]):
            #         logger.info(f"sadd: {item}")
            #         redis_client.sadd("LoanListId", item["ListingId"])
            #         redis_client.hset("LoanListItem", item["ListingId"], item)
            #         redis_client.zadd("LoanListAddTime", time.time(), item["ListingId"])
            #         find_new = True
            #     # else:
            #     #     logger.info(f"exist {item}")
            #
            # if not find_new:
            #     continue
            #
            # loan_list_count = redis_client.zcard("LoanListAddTime")
            # logger.info(f"total count: {loan_list_count}")
            # id_count = redis_client.scard("LoanListId")
            #
            # if id_count > 1000:
            #     remove_ids = redis_client.zrange(key_loan_list_add_time, 0, id_count - 1000)
            #     logger.info(f"remove: {remove_ids}")
            #     for id in remove_ids:
            #         redis_client.srem("LoanListId", id)
            #         redis_client.hdel("LoanListItem", id)
            #     redis_client.zremrangebyrank("LoanListAddTime", 0, id_count - 1000)

            # logger.info(redis_client.zrange("LoanListAddTime", 0, -1))

        except Exception as ex:
            logging.error(ex, exc_info=True)
            break
    pass

if __name__ == "__main__":
    # logger = CommonUtils.setup_logging()
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=15, format=logging_format)
    logger = logging.getLogger(__name__)
    main()
    print("done")