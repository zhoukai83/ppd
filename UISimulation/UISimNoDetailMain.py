import sys
sys.path.insert(0, '..')

import json
import platform
from collections import deque
from Common import Utils as CommonUtils
from Common import PandasUtils
from Common.UIStrategyFactory import UIStrategyFactory
from UISimulation.FetchFromChrome import FetchFromChrome
from UISimulation.PpdUISimulationRequest import PpdUISimulationRequest, PpdNeedSleepException, PpdNotEnoughMoneyException
from PpdCommon.PpdItem import PpdItemConvertor
import pandas as pd
import time
import os
import random
import itertools
import winsound
from Open.PpdOpenClient import PpdOpenClient, privatekey_2
from Open.AioOpenClient import AioOpenClient
from win10toast import ToastNotifier
import asyncio

import redis

def refresh_config():
    with open('UISimMain.json') as f:
        data = json.load(f)
        config = data[platform.node()]
        return config


def restore_config():
    with open('UISimMain.json', "r+") as f:
        data = json.load(f)
        data[platform.node()]["Terminate"] = "False"
        f.seek(0)
        f.write(json.dumps(data, indent=4))


def filter_item_if_too_many(item):
    if item.get("NormalCount", 0) < 25:
        return False

    if item["RemainFunding"] == 0:
        return False

    if (item["NormalCount"] * 1.0 / (item["NormalCount"] + item["OverdueLessCount"] + item["OverdueMoreCount"])) < 0.8:
        return False

    # "HighestDebt": "历史最高负债",  "OwingAmount": "待还金额",  "Amount": "借款金额",
    if (item["OwingAmount"] + item["Amount"]) / item["HighestDebt"] >= 1.1:
        return False

    # "HighestPrincipal": "单笔最高借款金额",
    if item["Amount"] / item["HighestPrincipal"] > 1.1:
        return False

    return True


def get_listing_infos_combine_open_ui(ppd_open_client: PpdOpenClient, ppd_sim_client: PpdUISimulationRequest, listing_ids: list):
    open_detail_infos = ppd_open_client.batch_get_listing_info(listing_ids)
    filtered_open_listings = [item for item in open_detail_infos if filter_item_if_too_many(item)]
    filtered_open_listings_ids = [item["ListingId"] for item in filtered_open_listings]

    listing_ids_len = len(listing_ids)
    logger.info(f"filter listing id: {len(filtered_open_listings_ids)}, {listing_ids_len}, {filtered_open_listings_ids}")
    if not filtered_open_listings_ids:
        return []

    ui_show_borrow_infos = ppd_sim_client.batch_get_show_borrower_info(filtered_open_listings_ids)

    # logger.info(f"{json.dumps(ui_show_borrow_infos, ensure_ascii=False)}")
    # logger.info(f"{json.dumps(filtered_open_listings, ensure_ascii=False)}")
    ppd_convertor = PpdItemConvertor()
    result = []
    for open_detail_info in filtered_open_listings:
        ui_item = ppd_convertor.convert_open_to_ui(open_detail_info)

        for ui_show_borrow_info in ui_show_borrow_infos:
            if ui_show_borrow_info["listingId"] == ui_item["listingId"]:
                ui_item = {**ui_item, **ui_show_borrow_info}
                result.append(ui_item)

    logger.info(f"{json.dumps(result, ensure_ascii=False, indent=4)}")
    return result
    pass


def main():
    loop = asyncio.get_event_loop()
    ppd_sim_client = PpdUISimulationRequest()
    ppd_open_client = AioOpenClient()
    ppd_open_client_2 = PpdOpenClient(key_index=2)
    ppd_open_client_3 = PpdOpenClient(key_index=3)
    no_more_money = False
    df = None
    get_list_from = "U1"
    expected_ratings = ["A"]
    expected_months = [3]

    redis_client = redis.StrictRedis(host='10.164.120.164', port=6379, db=0)
    redis_client.delete("loan_listing_ids")

    last_refresh_list_time = time.time()
    data_file_path = "UISimMain.csv"
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")
        listing_ids_cache = deque(df["listingId"].tail(700).tolist(), maxlen=700)
    else:
        listing_ids_cache = deque(maxlen=700)

    config = refresh_config()

    with FetchFromChrome(config["Session"]) as fetch_from_chrome:
        cookies = fetch_from_chrome.get_cookie_string()
        ppd_sim_client.update_cookies(cookies)

        while config["Terminate"] == "False":
            tasks = []
            try:
                sleep_time = config["Sleep"] + random.randint(0, config["RandomSleep"])
                if no_more_money:
                    sleep_time = sleep_time + 3
                time.sleep(sleep_time)
                config = refresh_config()

                if no_more_money:
                    no_more_money = fetch_from_chrome.is_account_money_low()

                # logger.info("...")
                if time.time() - last_refresh_list_time > config["RefreshListTime"]:
                    fetch_from_chrome.refresh_loan_list_page()
                    last_refresh_list_time = time.time()
                    listing_ids, current_page, total_page = fetch_from_chrome.get_all_listing_items()
                    if listing_ids:
                        logger.info(f"get list from U: {listing_ids}")
                    get_list_from = "U"
                else:
                    if get_list_from == "O3":
                        listing_ids = ppd_open_client.get_loan_list_ids(expected_ratings, expected_months)
                        get_list_from = "O1"
                    elif get_list_from == "O1":
                        listing_ids = ppd_open_client_2.get_loan_list_ids(expected_ratings, expected_months)
                        get_list_from = "O2"
                    elif get_list_from == "O2":
                        listing_ids = ppd_open_client_3.get_loan_list_ids(expected_ratings, expected_months)
                        get_list_from = "O3"
                    else:
                        listing_ids = ppd_open_client.get_loan_list_ids(expected_ratings, expected_months)
                        get_list_from = "O1"

                if not listing_ids:
                    continue

                listing_ids = [int(listing_id) for listing_id in listing_ids if int(listing_id) not in listing_ids_cache]
                listing_ids_len = len(listing_ids)
                if listing_ids_len == 0:
                    continue

                if get_list_from == "Redis":
                    logger.info(f"fetch from redis: {listing_ids}")

                listing_ids_cache.extendleft(listing_ids)
                # logger.info(list(listing_ids_cache)[:15])

                if not no_more_money:
                    for id in listing_ids:
                        task = asyncio.ensure_future(ppd_open_client.aio_bid(id, 51))
                        tasks.append(task)

                if tasks:
                    aio_bid_result = loop.run_until_complete(asyncio.gather(*tasks))
                    logger.log(21, f"bid open: {aio_bid_result}")

            except PpdNeedSleepException as ex:
                logger.warning(f"NeedSleepException, {ex}")
                time.sleep(60 * 12)
            except PpdNotEnoughMoneyException as ex:
                no_more_money = True
                logger.info("No more money")
                time.sleep(3)
            except Exception as ex:
                logger.info(ex, exc_info=True)
                time.sleep(3)

    restore_config()
    pass


if __name__ == "__main__":
    logger = CommonUtils.setup_logging()

    main()
    # toaster = ToastNotifier()
    # toaster.show_toast("Example two", f"This notification is in it's own thread!{111}",
    #                                    icon_path=None,
    #                                    duration=2,
    #                                    threaded=True)
    #
    # toaster.show_toast("Example two", f"This notification is in it's own thread!{123}",
    #                                    icon_path=None,
    #                                    duration=2,
    #                                    threaded=True)
    # logger.info("sleep")
    # time.sleep(5)
    logger.info("end")