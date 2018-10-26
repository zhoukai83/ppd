import sys
sys.path.insert(0, "..")

from Open.AioOpenClient import AioOpenClient
import time
import logging
import asyncio
import json

def main():
    ppd_open_client = AioOpenClient(key_index=4)
    ppd_open_bid_client = AioOpenClient(key_index=1)

    loop = asyncio.get_event_loop()
    while True:
        tasks = []
        time.sleep(0.2)

        list = ppd_open_client.get_loan_list_ids(["AA"], [3, 6])
        if not list:
            continue

        for id in list:
            task = asyncio.ensure_future(ppd_open_client.aio_bid(id, 53))
            tasks.append(task)

        aio_bid_results = loop.run_until_complete(asyncio.gather(*tasks))
        for item in aio_bid_results:
            logger.info(json.loads(item, encoding="utf-8"))

        break
    pass


if __name__ == "__main__":
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=20, format=logging_format)
    logger = logging.getLogger(__name__)

    main()