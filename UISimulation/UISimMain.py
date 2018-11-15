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
import datetime
import os
import random
import itertools
import winsound
from Open.PpdOpenClient import PpdOpenClient, privatekey_2
from Open.AioOpenClient import AioOpenClient
from win10toast import ToastNotifier
import asyncio
import redis
from UISimulation import TokenHelper

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
    if item.get("NormalCount", 0) < 20:
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
    strategy_factory = UIStrategyFactory()
    ppd_sim_client = PpdUISimulationRequest()
    ppd_open_client = AioOpenClient()
    ppd_open_client_2 = PpdOpenClient(key_index=2)
    ppd_open_client_3 = PpdOpenClient(key_index=3)
    no_more_money = False
    df = None
    toaster = ToastNotifier()
    current_page = 1
    total_page = 1
    get_list_from = "U1"
    expected_ratings = ["A", "B", "C", "D"]
    expected_months = [3, 6]

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

    token_update_time, token_config = TokenHelper.get_token_from_config()
    ppd_open_client.set_access_token(token_config["AccessToken"])

    with FetchFromChrome(config["Session"]) as fetch_from_chrome:
        cookies = fetch_from_chrome.get_cookie_string()
        ppd_sim_client.update_cookies(cookies)

        while config["Terminate"] == "False":
            tasks = []
            try:
                if datetime.datetime.now() - token_update_time > datetime.timedelta(days=6, hours=23, minutes=30):
                    token_update_time, token_config = TokenHelper.refresh_open_client_token(ppd_open_client, token_config, logger)
                    ppd_open_client.set_access_token(token_config["AccessToken"])

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
                elif get_list_from == "O3":
                    redis_loan_listings_str = redis_client.get('loan_listing_ids')
                    if redis_loan_listings_str is not None and redis_loan_listings_str != b"None":
                        redis_loan_listings = json.loads(redis_loan_listings_str)
                        # logger.info(f"fetch redis: {redis_loan_listings}")
                        listing_ids = redis_loan_listings[:20]
                        redis_client.delete("loan_listing_ids")
                        get_list_from = "Redis"
                else:
                    if get_list_from == "Redis":
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

                listing_detail_list = []

                listing_ids = [int(listing_id) for listing_id in listing_ids if int(listing_id) not in listing_ids_cache]
                listing_ids_len = len(listing_ids)
                if listing_ids_len == 0:
                    continue

                if get_list_from == "Redis":
                    logger.info(f"fetch from redis: {listing_ids}")

                listing_ids_cache.extendleft(listing_ids)
                # logger.info(list(listing_ids_cache)[:15])
                if listing_ids_len == 1:
                    item = ppd_sim_client.get_detail_info(listing_ids[0])
                    listing_detail_list.append(item)
                elif listing_ids_len >= 4:
                    listing_detail_list = get_listing_infos_combine_open_ui(ppd_open_client, ppd_sim_client, listing_ids)
                else:
                    listing_detail_list = ppd_sim_client.batch_get_detail_infs(listing_ids)

                listing_detail_list = [item for item in listing_detail_list if item]
                if not no_more_money:
                    for item in listing_detail_list:
                        can_bid, first_strategy = strategy_factory.is_item_can_bid(item)
                        if not can_bid:
                            continue

                        # open_bid_result = ppd_open_client.bid(item['listingId'])
                        # logger.log(21, f"bid open:{open_bid_result}")

                        task = asyncio.ensure_future(ppd_open_client.aio_bid(item['listingId']))
                        tasks.append(task)

                        # if not ppd_sim_client.check_bid_number(item):
                        #     continue
                        #
                        # item["strategy"] = first_strategy.name
                        # if ppd_sim_client.bid_by_request(item):
                        logger.log(21, f"bid from {get_list_from}:{item['listingId']} {first_strategy} \n{first_strategy.strategy_detail()} \n{json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False)}")

                if tasks:
                    aio_bid_result = loop.run_until_complete(asyncio.gather(*tasks))
                    logger.log(21, f"bid open: {aio_bid_result}")

                if listing_detail_list:
                    df = PandasUtils.save_list_to_csv(data_file_path, df, listing_detail_list)

                    len_listing_detail_list = len(listing_detail_list)
                    if len_listing_detail_list >= 5:
                        time.sleep(1.9 * len_listing_detail_list)
                    elif len_listing_detail_list >= 4:
                        time.sleep(1.6 * len_listing_detail_list)
                    elif len_listing_detail_list == 3:
                        time.sleep(1.2 * len_listing_detail_list)

            except PpdNeedSleepException as ex:
                logger.warning(f"NeedSleepException, {ex}")
                time.sleep(60 * 13)
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