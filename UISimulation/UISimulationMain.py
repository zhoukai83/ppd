import sys
sys.path.insert(0, '..')

import json
import platform
from collections import deque
from Common import Utils as CommonUtils
from Common.UIStrategyFactory import UIStrategyFactory
from UISimulation.FetchFromChrome import FetchFromChrome
import pandas as pd
import time
import os
import random


def refresh_config():
    with open('UIMain.json') as f:
        data = json.load(f)
        config = data[platform.node()]
        return config


def restore_config():
    with open('UIMain.json', "r+") as f:
        data = json.load(f)
        data[platform.node()]["Terminate"] = "False"
        f.seek(0)
        f.write(json.dumps(data, indent=4))


def main():
    strategy_factory = UIStrategyFactory()
    no_more_money = False
    df = None
    data_file_path = "UISimulationMain.json"
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")
        listing_ids_cache = deque(df["listingId"].tail(10000).tolist())
    else:
        listing_ids_cache = deque(maxlen=1000)

    config = refresh_config()

    with FetchFromChrome(config["Session"]) as fetch_from_chrome:
        try:
            while config["Terminate"] == "False":
                sleep_time = config["Sleep"] + random.randint(0, config["RandomSleep"])
                if no_more_money:
                    sleep_time = sleep_time + 3
                time.sleep(sleep_time)
                config = refresh_config()
                if config["Status"] == "Pause":
                    continue

                cookies = fetch_from_chrome.get_cookie_string()
                print(cookies)
                no_more_money = fetch_from_chrome.is_account_money_low()
                fetch_from_chrome.refresh_loan_list_page()

                listing_ids, current_page, total_page = fetch_from_chrome.get_all_listing_items()
                logger.debug("iter_listing_item_to_detail_page end")
                if len(listing_ids) == 0:
                    # logger.info(f"can not get listing in: {current_page} {total_page} {listing_ids}")
                    continue

                for listing_id in listing_ids:
                    if int(listing_id) in listing_ids_cache:
                        continue

                    listing_ids_cache.append(int(listing_id))
                #     logger.info(f"navigate detail, {should_back}")
                #     if should_back:
                #         if not fetch_from_chrome.click_listing_in_listpage(listing_id, None):
                #             continue
                #     else:
                #         fetch_from_chrome.navigate_detail(listing_id)
                #
                #     logger.info("fetch detail info")
                #     item = fetch_from_chrome.fetch_detail_info(False)
                #     if item is None:
                #         continue
                #
                #     current_time = time.localtime()
                #     item["creationDate"] = time.strftime('%Y-%m-%dT%H:%M:%S', current_time)
                #
                #     if no_more_money:
                #         df = save_to_csv(df, item)
                #         continue
                #
                #     can_bid, first_strategy = strategy_factory.is_item_can_bid(item)
                #     if not can_bid:
                #         df = save_to_csv(df, item)
                #         continue
                #
                #     if not check_bid_number(item, cookies):
                #         df = save_to_csv(df, item)
                #         continue
                #
                #     item["strategy"] = first_strategy.name
                #     if bid_by_request(item, cookies):
                #         logger.log(21, "bid: %s: %s \n%s \n%s", item["listingId"], first_strategy,
                #                    first_strategy.strategy_detail(),
                #                    json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False))
                #     df = save_to_csv(df, item)
        except Exception as ex:
            logger.info(ex, exc_info=True)
    pass

if __name__ == "__main__":
    logger = CommonUtils.setup_logging()

    main()
    logger.info("end")