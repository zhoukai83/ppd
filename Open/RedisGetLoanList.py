import sys
sys.path.insert(0, "..")

import redis
import logging
import time

from Open.PpdOpenClient import PpdOpenClient
from Common import Utils as CommonUtils
from collections import deque
import json
def main():
    client = PpdOpenClient()
    redis_client = redis.StrictRedis(host='10.164.120.164', port=6379, db=0)
    listing_ids_cache = deque(maxlen=1000)
    while True:
        try:
            listing_ids = client.get_loan_list_ids(["B"], [6])
            if listing_ids:
                logging.info(listing_ids)
                redis_listing_ids_str = redis_client.get("loan_listing_ids")
                if redis_listing_ids_str:
                    redis_listing_ids = json.loads(redis_listing_ids_str)
                    redis_client.set("loan_listing_ids", listing_ids.extend(redis_listing_ids))
                else:
                    redis_client.set("loan_listing_ids", listing_ids)
            # new_listing_ids = []
            # for listing_id in listing_ids:
            #     if int(listing_id) in listing_ids_cache:
            #         continue
            #
            #     listing_ids_cache.append(int(listing_id))

            time.sleep(0.5)
        except Exception as ex:
            logging.error(ex, exc_info=True)
    pass

if __name__ == "__main__":
    logger = CommonUtils.setup_logging()
    main()