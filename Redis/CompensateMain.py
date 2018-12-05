import sys
sys.path.insert(0, "..")

from Open.AioOpenClient import AioOpenClient
from UISimulation.PpdUISimulationRequest import PpdNeedSleepException, PpdNotEnoughMoneyException
import time
import asyncio
import json
import platform
import datetime
import os
from collections import deque
from Common import Utils as CommonUtils
from UISimulation import TokenHelper
from Redis.PpdRedisClient import PpdRedisClient


def refresh_config(file_name):
    with open(file_name) as f:
        data = json.load(f)
        config = data[platform.node()]
        return config


def restore_config(file_name):
    with open(file_name, "r+") as f:
        data = json.load(f)
        data[platform.node()]["Terminate"] = "False"
        f.seek(0)
        f.write(json.dumps(data, indent=4))

def main():
    config_file_name = os.path.basename(__file__).split(".")[0] + ".json"

    ppd_open_client = AioOpenClient(key_index=1)
    ppd_redis_client = PpdRedisClient()
    loop = asyncio.get_event_loop()
    cache_ids = deque(maxlen=200)
    terminate = False
    month_list = [3, 6]

    config = refresh_config(config_file_name)

    # token_update_time, token_config = TokenHelper.get_token_from_config()
    # ppd_open_client.set_access_token(token_config["AccessToken"])
    last_fetch_ids_time = time.time() - 10

    while config["Terminate"] == "False":
        tasks = []
        config = refresh_config(config_file_name)

        # if datetime.datetime.now() - token_update_time > datetime.timedelta(days=6, hours=23, minutes=31):
        #     token_update_time, token_config = TokenHelper.get_token_from_config()
        #     ppd_open_client.set_access_token(token_config["AccessToken"])
        #     logger.info(f"update token: {token_config}")

        time.sleep(0.05)

        try:
            loan_list_ids = ppd_redis_client.get_loan_list_ids_by_time(last_fetch_ids_time)
            last_fetch_ids_time = time.time() - 10

            if not loan_list_ids:
                continue

            new_listing_id = list(set(loan_list_ids).difference(cache_ids))

            if not new_listing_id:
                continue

            cache_ids.extendleft(new_listing_id)
            logger.info(f"find new id: {new_listing_id}")

            new_listing_items = ppd_redis_client.get_loan_list_items(new_listing_id)
            logger.info(f"{new_listing_items}")
            lists = [item for item in new_listing_items if item["Months"] in month_list
                                                                and item["CreditCode"] == "AA"
                                                                and item.get("RemainFunding", 0) > 500
                                                                and item.get("Rate") >= 9]
            if not lists:
                continue

            logger.info(f"find AA: {[item['ListingId'] for item in lists]}")
            # tasks = [asyncio.ensure_future(ppd_open_client.aio_bid(item["ListingId"], 500)) for item in lists]
            #
            # aio_bid_results = loop.run_until_complete(asyncio.gather(*tasks))
            # for item in aio_bid_results:
            #     json_data = json.loads(item, encoding="utf-8")
            #     logger.log(21, json_data)
            #
            #     result_code = json_data.get("Result")
            #
            #     # if result_code != 3005 and result_code != 6001:
            #     #     logger.log(21, json_data)
            #
            #     if result_code == 9999:
            #         success_num += 1
            #
            #     if result_code == 4001:
            #         terminate = True
            #         break
            #
            # df = PandasUtils.save_list_to_csv(data_file_path, df, lists)
            # logger.info(f"sleep, {len(success_count_greator_1)}")
            # time.sleep(len(success_count_greator_1) * 2)

            # balance_result = ppd_open_client.get_query_balance()
            # balance_result = json.loads(balance_result, encoding="utf-8")
            # if balance_result.get("Balance") and balance_result.get("Balance")[0].get("Balance") < 200:
            #     logger.info(balance_result)
            #     terminate = True

        except PpdNeedSleepException as ex:
            logger.warning(f"NeedSleepException, {ex}")
            time.sleep(60 * 13)
        except PpdNotEnoughMoneyException as ex:
            logger.info("No more money")
            time.sleep(3)
        except Exception as ex:
            logger.info(ex, exc_info=True)
            time.sleep(3)

        if terminate:
            break

    restore_config(config_file_name)
    pass


if __name__ == "__main__":
    # logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    # logging.basicConfig(level=20, format=logging_format)
    # logger = logging.getLogger(__name__)
    logging_file_name = os.path.basename(__file__).split(".")[0] + ".logging.json"
    logger = CommonUtils.setup_logging(default_path=logging_file_name)

    main()
    # toaster = ToastNotifier()
    # toaster.show_toast("Warning", f"This notification is in it's own thread!{111}",
    #                                    icon_path=None,
    #                                    duration=5,
    #                                    threaded=True)
    # while toaster.notification_active():
    #     time.sleep(0.3)