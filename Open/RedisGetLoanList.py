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


def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--index",
                        dest="client_index", default=2,
                        help="use client index")

    parser.add_argument("-t", "--interval time",
                        dest="interval_time", default=0.5,
                        help="2 request interval")

    args = parser.parse_args()
    interval_time = float(args.interval_time)
    print("use client index:", args.client_index)
    print("2 request interval:", interval_time)

    client = PpdOpenClient(key_index=int(args.client_index))
    redis_client = redis.StrictRedis(host='10.164.120.164', port=6379, db=0)
    listing_ids_cache = deque(maxlen=1000)
    last_refresh_list_time = time.time()

    while True:
        try:
            if time.time() - last_refresh_list_time < interval_time:
                time.sleep(0.1)
                continue

            listing_ids = client.get_loan_list_ids(["A", "B", "C"], [3, 6, 12])
            last_refresh_list_time = time.time()

            if listing_ids:
                redis_listing_ids_str = redis_client.get("loan_listing_ids")
                logging.info(listing_ids)
                logging.info(redis_listing_ids_str)
                if redis_listing_ids_str is None or redis_listing_ids_str == b"None":
                    redis_client.set("loan_listing_ids", listing_ids)
                    logger.info(f"set {listing_ids}")
                else:
                    redis_listing_ids = json.loads(redis_listing_ids_str)
                    new_listing_ids = [item for item in listing_ids if item not in redis_listing_ids]
                    new_len = len(new_listing_ids)
                    new_listing_ids.extend(redis_listing_ids)
                    redis_client.set("loan_listing_ids", new_listing_ids)
                    logger.info(f"extend num:{new_len}  {new_listing_ids}")

            # new_listing_ids = []
            # for listing_id in listing_ids:
            #     if int(listing_id) in listing_ids_cache:
            #         continue
            #
            #     listing_ids_cache.append(int(listing_id))
        except Exception as ex:
            logging.error(ex, exc_info=True)
            break
    pass

if __name__ == "__main__":
    logger = CommonUtils.setup_logging()
    main()
    print("done")