import sys
sys.path.insert(0, "..")

from Open.AioOpenClient import AioOpenClient
from UISimulation.PpdUISimulationRequest import PpdUISimulationRequest, PpdNeedSleepException, PpdNotEnoughMoneyException
from UISimulation.FetchFromChrome import FetchFromChrome
from PpdCommon.PpdItem import PpdItemConvertor
from Common import PandasUtils
import time
import logging
import asyncio
import json
import platform
import dateutil.parser
import datetime
import pandas as pd
from pandas import DataFrame
import os
from Common import Utils as CommonUtils
from UISimulation import TokenHelper
from win10toast import ToastNotifier

def refresh_config():
    with open('UISimCompensateAheadMain.json') as f:
        data = json.load(f)
        config = data[platform.node()]
        return config


def restore_config():
    with open('UISimCompensateAheadMain.json', "r+") as f:
        data = json.load(f)
        data[platform.node()]["Terminate"] = "False"
        f.seek(0)
        f.write(json.dumps(data, indent=4))


def may_ahead(item):
    if item.get("owingAmount", 0) > 0 or item.get("previous_listing_0_status", 4) != 12 \
            or item.get("previous_listing_1_status", 4) != 12:
            # or item.get("previous_listing_2_status", 4) != 12:
        return False

    previous_listing_0_date_str = item.get("previous_listing_0_date")
    previous_listing_1_date_str = item.get("previous_listing_1_date")
    # previous_listing_2_date_str = item.get("previous_listing_2_date")
    if not previous_listing_0_date_str or not previous_listing_1_date_str: #or not previous_listing_2_date_str:
        return False

    now = datetime.datetime.now()
    previous_listing_0_date = dateutil.parser.parse(previous_listing_0_date_str)
    if (now - previous_listing_0_date).days > 7:
        return False

    previous_listing_1_date = dateutil.parser.parse(previous_listing_1_date_str)
    if (now - previous_listing_1_date).days > 15:
        return False

    # previous_listing_2_date = dateutil.parser.parse(previous_listing_2_date_str)
    # if (now - previous_listing_2_date).days > 25:
    #     return False
    if item["Months"] <= 6:
        return True

    if item.get("previous_listing_1_status", 4) != 12 or item.get("previous_listing_2_status", 4) != 12:
        return False

    previous_listing_1_date_str = item.get("previous_listing_1_date")
    previous_listing_2_date_str = item.get("previous_listing_2_date")
    if not previous_listing_1_date_str or not previous_listing_2_date_str:
        return False

    previous_listing_1_date = dateutil.parser.parse(previous_listing_1_date_str)
    if (now - previous_listing_1_date).days > 15:
        return False

    previous_listing_2_date = dateutil.parser.parse(previous_listing_2_date_str)
    if (now - previous_listing_2_date).days > 25:
        return False

    return True


def main():
    ppd_open_client = AioOpenClient(key_index=1)
    ppd_sim_client = PpdUISimulationRequest()
    ppd_convertor = PpdItemConvertor()
    loop = asyncio.get_event_loop()
    terminate = False

    month_list = [3, 6]
    df = None

    data_file_path = "UISimCompensateAheadMain.csv"
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")

    success_num = 0
    config = refresh_config()

    token_update_time, token_config = TokenHelper.get_token_from_config()
    ppd_open_client.set_access_token(token_config["AccessToken"])

    with FetchFromChrome(config["Session"]) as fetch_from_chrome:
        cookies = fetch_from_chrome.get_cookie_string()
        ppd_sim_client.update_cookies(cookies)

        while config["Terminate"] == "False":
            tasks = []
            config = refresh_config()

            if datetime.datetime.now() - token_update_time > datetime.timedelta(days=6, hours=23, minutes=31):
                token_update_time, token_config = TokenHelper.get_token_from_config()
                ppd_open_client.set_access_token(token_config["AccessToken"])
                logger.info(f"update token: {token_config}")

            time.sleep(0.4)

            try:
                filter_func = lambda loan_lists, listing_id_cache: [item for item in
                                                                    loan_lists if item["Months"] in month_list
                                                                    and item["CreditCode"] in ["AA"]
                                                                    and item.get("RemainFunding", 0) > 500
                                                                    and item.get("Rate") >= 9.5
                                                                    and item["ListingId"] not in listing_id_cache][:1]
                lists = ppd_open_client.get_loan_list_v3(filter_func)
                if not lists:
                    continue
                may_ahead_lists = []

                # may_ahead_lists = lists
                lists = ppd_open_client.aio_batch_get_listing_info([item["ListingId"] for item in lists])
                success_count_greator_1 = [item for item in lists if item["SuccessCount"] >= 3]

                borrower_statistics = []
                if len(success_count_greator_1) >= 1:
                    tasks = [asyncio.ensure_future(ppd_sim_client.get_borrower_statistics(item["ListingId"])) for item in success_count_greator_1]
                    aio_borrower_statistics_results = loop.run_until_complete(asyncio.gather(*tasks))
                    # logger.info(json.dumps(aio_borrower_statistics_results, ensure_ascii=False))

                    borrower_statistics = [ppd_convertor.convert_open_borrower_statistics_to_flat(item) for item in aio_borrower_statistics_results]
                    # logger.info(json.dumps(borrower_statistics, ensure_ascii=False))
                    may_ahead_lists = [item for item in borrower_statistics if may_ahead(item)]

                if may_ahead_lists:
                    logger.log(21, f"{[item['listingId'] for item in may_ahead_lists]} {json.dumps(may_ahead_lists, indent=4, ensure_ascii=False)}")

                    for borrower_statistics_item in borrower_statistics:
                        [info_item.update(borrower_statistics_item) for info_item in lists if borrower_statistics_item["listingId"] == info_item["ListingId"]]

                tasks = [asyncio.ensure_future(ppd_open_client.aio_bid(item["ListingId"], 500)) for item in may_ahead_lists]
                aio_bid_results = loop.run_until_complete(asyncio.gather(*tasks))
                for item in aio_bid_results:
                    json_data = json.loads(item, encoding="utf-8")
                    logger.log(21, json_data)

                    result_code = json_data.get("Result")

                    # if result_code != 3005 and result_code != 6001:
                    #     logger.log(21, json_data)

                    if result_code == 9999:
                        success_num += 1

                    # if result_code == 4001:    #余额不足
                    #     terminate = True
                    #     break

                logger.info(f"{may_ahead_lists}")
                df = PandasUtils.save_list_to_csv(data_file_path, df, lists)
                # logger.info(f"sleep, {len(success_count_greator_1)}")
                time.sleep(len(success_count_greator_1) * 4)

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

    restore_config()
    pass


if __name__ == "__main__":
    # logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    # logging.basicConfig(level=20, format=logging_format)
    # logger = logging.getLogger(__name__)
    logger = CommonUtils.setup_logging(default_path="UISimCompensateAheadMain.logging.json")

    main()
    toaster = ToastNotifier()
    toaster.show_toast("Warning", f"This notification is in it's own thread!{111}",
                                       icon_path=None,
                                       duration=5,
                                       threaded=True)
    while toaster.notification_active():
        time.sleep(0.3)