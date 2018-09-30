import sys
sys.path.insert(0, "..")

import redis
import logging
import json
import datetime
import time
import requests
from collections import deque
from Open.PpdOpenClient import PpdOpenClient

def test():
    key_name = "loan_listing_ids"
    logger.info("start")
    redisClient = redis.StrictRedis(host='10.164.120.164', port=6379, db=0)
    now = datetime.datetime.now()
    for i in range(0, 10000):
        redisClient.lpush(key_name, json.dumps({"id": now.strftime("%S"), "from": "U1", "time": now.strftime("%Y-%m-%d %H:%M:%S.%f")}))
    logger.info("start")

    p = redisClient.pipeline()
    for i in range(0, redisClient.llen(key_name)):
        item = redisClient.lindex(key_name, i).decode("utf-8")
        p.lpop(key_name)
        # logger.info(json.loads(item))

    p.execute()
    logging.info("end")

global_listing_id_cache = deque(maxlen=200)

def get_expected_loan_list(client: PpdOpenClient, month_list:list, credit_code_list: list):
    loan_infos = client.get_loan_list_items()
    logger.info(f"{loan_infos}")
    if not loan_infos:
        return loan_infos


    listing_ids = [item["ListingId"] for item in loan_infos if
                   item["Months"] in month_list and item["CreditCode"] in credit_code_list and item.get(
                       "RemainFunding", 0) > 50]
    new_listing_id = list(set(listing_ids).difference(global_listing_id_cache))

    if new_listing_id:
        logger.info(
            f"find from O{self.client_index}: {len(new_listing_id)} in {len(listing_ids)}, {len(loan_infos)}  {new_listing_id},{self.loan_list_time_delta_sec}")
        global_listing_id_cache.extendleft(new_listing_id)

    return new_listing_id

def main():
    key_name = "loan_listing_ids"
    client = PpdOpenClient(key_index=1)
    redisClient = redis.StrictRedis(host='10.164.120.164', port=6379, db=0)
    logger.info("start")

    while True:

        loan_list = get_expected_loan_list(client, ["B", "C", "D"], [3, 6])
        logger.info(loan_list)
        if loan_list:
            redisClient.lpush(key_name, loan_list)
        time.sleep(1)

if __name__ == "__main__":
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=20, format=logging_format)
    logger = logging.getLogger(__name__)

    main()
