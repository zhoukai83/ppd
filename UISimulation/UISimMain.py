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
import pandas as pd
import time
import os
import random
import winsound
from Open.PpdOpenClient import PpdOpenClient
from win10toast import ToastNotifier

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
    ppd_sim_client = PpdUISimulationRequest()
    ppd_open_client = PpdOpenClient()
    no_more_money = False
    df = None
    toaster = ToastNotifier()
    current_page = 1
    total_page = 1

    last_refresh_list_time = time.time()
    data_file_path = "UISimMain.csv"
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")
        listing_ids_cache = deque(df["listingId"].tail(1000).tolist(), maxlen=1000)
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
                # logger.info(sleep_time)
                config = refresh_config()
                if config["Status"] == "Pause":
                    continue

                cookies = fetch_from_chrome.get_cookie_string()
                ppd_sim_client.update_cookies(cookies)

                if no_more_money:
                    no_more_money = fetch_from_chrome.is_account_money_low()

                # if current_page < total_page:
                #     logger.info(f"click to next page: {current_page} {total_page}")
                #     fetch_from_chrome.click_to_next_page()
                #     time.sleep(1.5)
                # else:

                # logger.info("...")
                if time.time() - last_refresh_list_time > config["RefreshTime"]:
                    fetch_from_chrome.refresh_loan_list_page()
                    last_refresh_list_time = time.time()
                    listing_ids, current_page, total_page = fetch_from_chrome.get_all_listing_items()
                else:
                    listing_ids = ppd_open_client.get_loan_list_ids("B", 6)

                if not listing_ids:
                    continue

                send_detail_request_num = 0
                for listing_id in listing_ids:
                    if int(listing_id) in listing_ids_cache:
                        continue

                    listing_ids_cache.append(int(listing_id))
                    item = ppd_sim_client.get_detail_info(listing_id)
                    send_detail_request_num += 1
                    if item is None:
                        continue

                    if no_more_money:
                        df = PandasUtils.save_item_to_csv(data_file_path, df, item)
                        continue

                    can_bid, first_strategy = strategy_factory.is_item_can_bid(item)
                    if not can_bid:
                        df = PandasUtils.save_item_to_csv(data_file_path, df, item)
                        continue

                    if not ppd_sim_client.check_bid_number(item):
                        df = PandasUtils.save_item_to_csv(data_file_path, df, item)
                        # toaster.show_toast("Example two", f"This notification is in it's own thread!{listing_id}",
                        #                    icon_path=None,
                        #                    duration=10,
                        #                    threaded=True)
                        fetch_from_chrome.driver.get(f"https://invest.ppdai.com/loan/info/{listing_id}")
                        continue

                    item["strategy"] = first_strategy.name
                    if ppd_sim_client.bid_by_request(item):
                        logger.log(21, f"bid:{item['listingId']} {first_strategy} \n{first_strategy.strategy_detail()} \n{json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False)}")

                    # toaster.show_toast("Example two", f"This notification is in it's own thread!{listing_id}",
                    #                    icon_path=None,
                    #                    duration=10,
                    #                    threaded=True)
                    fetch_from_chrome.driver.get(f"https://invest.ppdai.com/loan/info/{listing_id}")
                    df = PandasUtils.save_item_to_csv(data_file_path, df, item)

                time.sleep(2 * send_detail_request_num)
            except PpdNeedSleepException as ex:
                logger.warning(f"NeedSleepException, {ex}")
                time.sleep(60 * 15)
            except PpdNotEnoughMoneyException as ex:
                no_more_money = True
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