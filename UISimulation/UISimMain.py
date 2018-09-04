import sys
sys.path.insert(0, '..')

import json
import platform
from collections import deque
from Common import Utils as CommonUtils
from Common import PandasUtils
from Common.UIStrategyFactory import UIStrategyFactory
from UISimulation.FetchFromChrome import FetchFromChrome
from UISimulation.PpdUISimulationRequest import PpdUISimulationRequest, NeedSleepException
import pandas as pd
import time
import os
import random
import winsound


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


def main():
    strategy_factory = UIStrategyFactory()
    ppd_client = PpdUISimulationRequest()
    no_more_money = False
    df = None
    current_page = 1
    total_page = 1
    data_file_path = "UISimMain.csv"
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")
        listing_ids_cache = deque(df["listingId"].tail(10000).tolist())
    else:
        listing_ids_cache = deque(maxlen=1000)

    config = refresh_config()

    with FetchFromChrome(config["Session"]) as fetch_from_chrome:
        while config["Terminate"] == "False":
            try:
                sleep_time = config["Sleep"] + random.randint(0, config["RandomSleep"])
                if no_more_money:
                    sleep_time = sleep_time + 3
                time.sleep(sleep_time)
                config = refresh_config()
                if config["Status"] == "Pause":
                    continue

                cookies = fetch_from_chrome.get_cookie_string()
                ppd_client.update_cookies(cookies)
                # no_more_money = fetch_from_chrome.is_account_money_low()

                # if current_page < total_page:
                #     logger.info(f"click to next page: {current_page} {total_page}")
                #     fetch_from_chrome.click_to_next_page()
                #     time.sleep(1.5)
                # else:
                fetch_from_chrome.refresh_loan_list_page()

                listing_ids, current_page, total_page = fetch_from_chrome.get_all_listing_items()
                if len(listing_ids) == 0:
                    continue

                send_detail_request_num = 0
                for listing_id in listing_ids:
                    if int(listing_id) in listing_ids_cache:
                        continue

                    listing_ids_cache.append(int(listing_id))
                    item = ppd_client.get_detail_info(listing_id)
                    send_detail_request_num += 1
                    if item is None:
                        continue

                #     if no_more_money:
                #         df = save_to_csv(df, item)
                #         continue
                #
                    can_bid, first_strategy = strategy_factory.is_item_can_bid(item)
                    if not can_bid:
                        df = PandasUtils.save_item_to_csv(data_file_path, df, item)
                        continue

                    winsound.PlaySound('finish.wav', winsound.SND_ASYNC)
                    if not ppd_client.check_bid_number(item):
                        df = PandasUtils.save_item_to_csv(data_file_path, df, item)
                        continue

                    item["strategy"] = first_strategy.name
                    if ppd_client.bid_by_request(item):
                        logger.log(21, f"bid:{item['listingId']} {first_strategy} \n{first_strategy.strategy_detail()} \n{json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False)}")

                    df = PandasUtils.save_item_to_csv(data_file_path, df, item)

                time.sleep(2 * send_detail_request_num)
            except NeedSleepException as ex:
                logger.warning(f"NeedSleepException, {ex}")
                time.sleep(60 * 15)
            except Exception as ex:
                logger.info(ex, exc_info=True)
                time.sleep(60 * 15)

    restore_config()
    pass


if __name__ == "__main__":
    logger = CommonUtils.setup_logging()

    main()
    logger.info("end")