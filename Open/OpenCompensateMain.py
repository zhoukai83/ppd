import sys
sys.path.insert(0, "..")

from Open.AioOpenClient import AioOpenClient
import time
import logging
import asyncio
import json

def main():
    ppd_open_client = AioOpenClient(key_index=4)

    loop = asyncio.get_event_loop()
    terminate = False

    success_num = 0

    while True:
        tasks = []
        time.sleep(0.2)

        lists = ppd_open_client.get_loan_list_v2(["AA"], [3, 6])
        if not lists:
            continue

        for item in lists[:10]:
            id = item["ListingId"]

            if item["Months"] == 3 or item["Rate"] > 9.5:
                logger.info(item)

            # ppd_open_client.bid(id, 500)
            # break
            task = asyncio.ensure_future(ppd_open_client.aio_bid(id, 500))
            tasks.append(task)

        aio_bid_results = loop.run_until_complete(asyncio.gather(*tasks))
        for item in aio_bid_results:
            json_data = json.loads(item, encoding="utf-8")

            result_code = json_data.get("Result")
            if result_code != 3005 and result_code != 6001:
                logger.info(json_data)

            if result_code == 9999:
                success_num += 1

            if success_num >= 17:
                terminate = True
                break

            if result_code == 4001:
                terminate = True
                break

        balance_result = ppd_open_client.get_query_balance()
        balance_result = json.loads(balance_result, encoding="utf-8")
        if balance_result.get("Balance") and balance_result.get("Balance")[0].get("Balance") < 200:
            logger.info(balance_result)
            terminate = True

        if terminate:
            break

    pass


if __name__ == "__main__":
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=20, format=logging_format)
    logger = logging.getLogger(__name__)

    main()