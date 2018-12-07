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
from Open.PpdOpenClient import PpdOpenClient
from Open.AioOpenClient import AioOpenClient
import asyncio
from UISimulation import TokenHelper
import re


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


def filter_item_if_too_many(item):
    if item.get("NormalCount", 0) < 25:
        return False

    if item["RemainFunding"] <= 100:
        return False

    if (item["NormalCount"] * 1.0 / (item["NormalCount"] + item["OverdueLessCount"] + item["OverdueMoreCount"])) < 0.9:
        return False

    # "HighestDebt": "历史最高负债",  "OwingAmount": "待还金额",  "Amount": "借款金额",
    if (item["OwingAmount"] + item["Amount"]) / item["HighestDebt"] >= 1:
        return False

    # "HighestPrincipal": "单笔最高借款金额",
    if item["Amount"] / item["HighestPrincipal"] >= 1:
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


def should_bid_without_detail_info(items):
    should_bid_list = []
    for item in items:
        if item["级别"] == "A" and item["期限"] == 3:
            title = item.get("title")
            match = re.search(r"(?<=第)\d+(?=次)", title, re.DOTALL)
            number = 1
            if match:
                result = match.group()
                number = int(result)

            if number >= 4:
                should_bid_list.append(item)

    return should_bid_list

def main():
    ppd_convertor = PpdItemConvertor()
    loop = asyncio.get_event_loop()
    strategy_factory = UIStrategyFactory()
    ppd_sim_client = PpdUISimulationRequest()
    ppd_open_client = AioOpenClient()
    ppd_open_client_2 = AioOpenClient(key_index=2)
    ppd_open_client_3 = AioOpenClient(key_index=3)
    no_more_money = False
    df = None
    get_list_from = "U1"
    expected_ratings = ["A", "B", "C", "D"]
    expected_months = [3, 6]
    config_file_name = os.path.basename(__file__).split(".")[0] + ".json"

    last_refresh_list_time = time.time()
    data_file_path = "UISimMainV2.csv"
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")
        listing_ids_cache = deque(df["listingId"].tail(700).tolist(), maxlen=700)
    else:
        listing_ids_cache = deque(maxlen=700)

    config = refresh_config(config_file_name)

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
                    sleep_time = sleep_time + 30
                time.sleep(sleep_time)
                config = refresh_config(config_file_name)

                if no_more_money:
                    no_more_money = fetch_from_chrome.is_account_money_low()

                # logger.info("...")
                loan_list_items = []
                if time.time() - last_refresh_list_time > config["RefreshListTime"]:
                    last_refresh_list_time = time.time()
                    loan_list_items = ppd_sim_client.listing_pager_auth()
                    loan_list_items = [ppd_convertor.convert_uisim_listing_pager_auth_to_ui(item) for item in loan_list_items if item["amount"] - item["funding"] > 100]
                    get_list_from = "U"
                else:
                    listing_ids = []
                    if get_list_from == "O1":
                        loan_list_items = ppd_open_client_2.get_loan_list_items()
                        get_list_from = "O2"
                    elif get_list_from == "O2":
                        loan_list_items = ppd_open_client_3.get_loan_list_items()
                        get_list_from = "O3"
                    elif get_list_from == "03":
                        loan_list_items = ppd_open_client.get_loan_list_items()
                        get_list_from = "O1"
                    else:
                        loan_list_items = ppd_open_client.get_loan_list_items()
                        get_list_from = "O1"

                    if loan_list_items:
                        loan_list_items = [ppd_convertor.convert_open_loan_list_items_to_ui(item) for item in loan_list_items if item.get("RemainFunding") > 50]

                if not loan_list_items:
                    continue

                # logger.info(f"{get_list_from} {loan_list_items}")
                listing_detail_list = []
                loan_list_items = [item for item in loan_list_items if
                               item["期限"] in expected_months and item["级别"] in expected_ratings and "第1次" not in item.get("title") and "第2次" not in item.get("title") and "第3次" not in item.get("title") and item["listingId"] not in listing_ids_cache]

                loan_list_items = loan_list_items[:4]
                listing_ids = [item["listingId"] for item in loan_list_items]
                listing_ids_len = len(listing_ids)
                if not listing_ids:
                    continue

                logger.info(f"{get_list_from} {listing_ids}, {loan_list_items}")
                listing_ids_cache.extendleft(listing_ids)

                bid_without_detail_list = should_bid_without_detail_info(loan_list_items)
                if bid_without_detail_list:
                    logger.log(21, f"should_bid_without_detail_info, {bid_without_detail_list}")
                    task_list = [asyncio.ensure_future(ppd_open_client.aio_bid(item['listingId'])) for item in bid_without_detail_list]
                    tasks.extend(task_list)
                    listing_ids = [listing_id for listing_id in listing_ids if listing_id not in [item["listingId"] for item in bid_without_detail_list]]
                    listing_ids_len = len(listing_ids)
                    listing_detail_list = []

                # logger.info(list(listing_ids_cache)[:15])
                if listing_ids_len == 1:
                    item = ppd_sim_client.get_detail_info(listing_ids[0])
                    listing_detail_list.append(item)
                elif listing_ids_len >= 3:
                    listing_detail_list = get_listing_infos_combine_open_ui(ppd_open_client, ppd_sim_client, listing_ids)
                else:
                    listing_detail_list = ppd_sim_client.batch_get_detail_infs(listing_ids)
                #
                listing_detail_list = [item for item in listing_detail_list if item]
                # logger.info(f"{listing_detail_list}")
                if not no_more_money:
                    for item in listing_detail_list:
                        can_bid, first_strategy = strategy_factory.is_item_can_bid(item)
                        if not can_bid:
                            continue

                        # open_bid_result = ppd_open_client.bid(item['listingId'])
                        # logger.log(21, f"bid open:{open_bid_result}")

                        task = asyncio.ensure_future(ppd_open_client.aio_bid(item['listingId']))
                        tasks.append(task)

                        task2 = asyncio.ensure_future(ppd_open_client_2.aio_bid(item['listingId']))
                        tasks.append(task2)

                        if not ppd_sim_client.check_bid_number(item):
                            continue

                        item["strategy"] = first_strategy.name
                        if ppd_sim_client.bid_by_request(item):
                            logger.log(21, f"bid from {get_list_from}:{item['listingId']} {first_strategy} \n{first_strategy.strategy_detail()} \n{json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False)}")

                if tasks:
                    aio_bid_result = loop.run_until_complete(asyncio.gather(*tasks))
                    logger.log(21, f"bid open: {aio_bid_result}")

                if listing_detail_list:
                    df = PandasUtils.save_list_to_csv(data_file_path, df, listing_detail_list)

                    len_listing_detail_list = len(listing_detail_list)
                    if len_listing_detail_list >= 5:
                        time.sleep(2.6 * len_listing_detail_list)
                    elif len_listing_detail_list >= 4:
                        time.sleep(2.3 * len_listing_detail_list)
                    elif len_listing_detail_list == 3:
                        time.sleep(2 * len_listing_detail_list)
                    elif len_listing_detail_list == 2:
                        time.sleep(1.5)
                    else:
                        time.sleep(1)

            except PpdNeedSleepException as ex:
                logger.warning(f"NeedSleepException, {ex}")
                time.sleep(60 * 11)
            except PpdNotEnoughMoneyException as ex:
                no_more_money = True
                logger.info("No more money")
                time.sleep(3)
            except Exception as ex:
                logger.info(ex, exc_info=True)
                time.sleep(3)

    restore_config(config_file_name)
    pass


if __name__ == "__main__":
    logging_file_name = os.path.basename(__file__).split(".")[0] + ".logging.json"
    logger = CommonUtils.setup_logging(default_path=logging_file_name)

    main()
    logger.info("end")