import sys
sys.path.insert(0,'..')

import json
import os
import platform
import random
import time
import winsound
import requests

import Utils
import pandas as pd
from FetchFromChromeQuick import FetchFromChromeQuick
from pandas import DataFrame

from Common.UIStrategyFactory import UIStrategyFactory
from collections import deque
from UI.SaveDataTask import SaveDataTask
from UI.SendBidRequestTask import SendBidRequestTask
import queue
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gbk')


def terminate_task(t):
    t.terminate = True


def terminate_signal_triggered():
    with open("terminate.txt") as f:
        terminate_signal = f.read()
        if terminate_signal != "False":
            logger.info("terminate")
            return True

    return False

def test():
    # item = {'借款金额': '¥1,339', '期限': '12个月', "级别": "B", "性别": "女"}
    # logger.info(json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False)
    item = {"listingId":124882894,"借款金额":"600"}
    config = refresh_config()

    with FetchFromChromeQuick(config["Session"]) as fetch_from_chrome:
        # fetch_from_chrome.wait_until_text_present(".filter-total span", "115")
        logger.info("start")
        print(fetch_from_chrome.get_all_listing_items())
        logger.info("end")


def refresh_config():
    with open('UIMain.json') as f:
        data = json.load(f)
        config = data[platform.node()]
        return config


def get_ppd_cookie(driver):
    driver_cookies = driver.get_cookies()
    cookie_list = [f"{cookie['name']}={cookie['value']}" for cookie in driver_cookies]
    cookies = "; ".join(cookie_list)
    return cookies


def totally_main_ui():
    strategy_factory = UIStrategyFactory()
    current_page = 1
    total_page = 1
    no_more_money = False

    q = queue.Queue(maxsize=200)
    save_data_task = SaveDataTask(q)

    task_list = [save_data_task]
    [t.start() for t in task_list]

    config = refresh_config()
    listing_ids_cache = deque(save_data_task.df["listingId"].tail(10000).tolist())

    with FetchFromChromeQuick(config["Session"]) as fetch_from_chrome:
        try:
            fetch_from_chrome.switch_to_window(0)
            while config["Terminate"] == "False":

                sleep_time = config["Sleep"] + random.randint(0, config["RandomSleep"])
                if no_more_money:
                    sleep_time = sleep_time + 3
                # logger.info(f"sleep: {sleep_time}")
                time.sleep(sleep_time)
                config = refresh_config()
                if config["Status"] == "Pause":
                    continue

                cookies = get_ppd_cookie(fetch_from_chrome.driver)
                if fetch_from_chrome.is_account_money_low():
                    no_more_money = True

                # if current_page < total_page:
                #     logger.info(f"click to next page: {current_page} {total_page}")
                #     fetch_from_chrome.click_to_next_page()
                #     time.sleep(0.5)
                # else:
                fetch_from_chrome.refresh_loan_list_page()

                listing_ids, current_page, total_page = fetch_from_chrome.get_all_listing_items()
                logger.debug("iter_listing_item_to_detail_page end")
                if len(listing_ids) == 0:
                    # logger.info(f"can not get listing in: {current_page} {total_page} {listing_ids}")
                    continue

                should_back = len(listing_ids) == 1
                for listing_id in listing_ids:
                    if int(listing_id) in listing_ids_cache:
                        continue

                    listing_ids_cache.append(int(listing_id))
                    if should_back:
                        if not fetch_from_chrome.click_listing_in_listpage(listing_id, None):
                            continue
                    else:
                        fetch_from_chrome.navigate_detail(listing_id)

                    item = fetch_from_chrome.fetch_detail_info(False)
                    if item is None:
                        continue

                    current_time = time.localtime()
                    item["creationDate"] = time.strftime('%Y-%m-%dT%H:%M:%S', current_time)

                    if no_more_money:
                        q.put(item)
                        continue

                    can_bid, first_strategy = strategy_factory.is_item_can_bid(item)
                    if not can_bid:
                        q.put(item)
                        continue

                    filter_success = fetch_from_chrome.filter_item(item)
                    if not filter_success:
                        q.put(item)
                        continue

                    # logger.info("click_not_bid_button")
                    # fetch_from_chrome.click_not_bid_button()
                    logger.info("start check_bid_number")
                    if not fetch_from_chrome.check_bid_number(item):
                        q.put(item)
                        continue

                    logger.info("can bid: %s %s\n%s", item["listingId"], first_strategy, item)

                    if fetch_from_chrome.quick_bid():
                        json_string = json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False)
                        logger.log(21, "bid: %s: %s \n%s \n%s", item["listingId"], first_strategy,
                                   first_strategy.strategy_detail(), json_string)

                    item["strategy"] = first_strategy.name
                    q.put(item)
                    time.sleep(1)
                    fetch_from_chrome.bid_again()
                    time.sleep(0.5)
        except Exception as ex:
            logger.info(ex, exc_info=True)

    print("finish")
    winsound.PlaySound('finish.wav', winsound.SND_LOOP + winsound.SND_ASYNC)
    time.sleep(60 * 10)


# 1 2  he cai
def main_ui():
    strategy_factory = UIStrategyFactory()
    no_more_money = False

    queue_save_csv_file = queue.Queue(maxsize=200)
    queue_send_bid_request = queue.Queue(maxsize=200)
    save_data_task = SaveDataTask(queue_save_csv_file)
    send_bid_request_task = SendBidRequestTask(queue_send_bid_request)

    task_list = [save_data_task, send_bid_request_task]
    [t.start() for t in task_list]

    config = refresh_config()
    listing_ids_cache = deque(save_data_task.df["listingId"].tail(10000).tolist())

    with FetchFromChromeQuick(config["Session"]) as fetch_from_chrome:
        try:
            fetch_from_chrome.switch_to_window(0)
            while config["Terminate"] == "False":
                sleep_time = config["Sleep"] + random.randint(0, config["RandomSleep"])
                if no_more_money:
                    sleep_time = sleep_time + 3
                time.sleep(sleep_time)
                config = refresh_config()
                if config["Status"] == "Pause":
                    continue

                send_bid_request_task.update_cookie(get_ppd_cookie(fetch_from_chrome.driver))
                if fetch_from_chrome.is_account_money_low():
                    no_more_money = True

                fetch_from_chrome.refresh_loan_list_page()

                listing_ids, current_page, total_page = fetch_from_chrome.get_all_listing_items()
                logger.debug("iter_listing_item_to_detail_page end")
                if len(listing_ids) == 0:
                    continue

                should_back = len(listing_ids) == 1
                for listing_id in listing_ids:
                    if int(listing_id) in listing_ids_cache:
                        continue

                    listing_ids_cache.append(int(listing_id))
                    if should_back:
                        if not fetch_from_chrome.click_listing_in_listpage(listing_id, None):
                            continue
                    else:
                        fetch_from_chrome.navigate_detail(listing_id)

                    # logger.info("start fetch detail info")
                    item = fetch_from_chrome.fetch_detail_info(False)
                    if item is None:
                        continue
                    # logger.info("finish fetch detail info")

                    current_time = time.localtime()
                    item["creationDate"] = time.strftime('%Y-%m-%dT%H:%M:%S', current_time)

                    if no_more_money:
                        queue_save_csv_file.put(item)
                        continue

                    can_bid, first_strategy = strategy_factory.is_item_can_bid(item)
                    if not can_bid:
                        queue_save_csv_file.put(item)
                        continue

                    item["strategy"] = first_strategy.name
                    queue_send_bid_request.put({"strategy": first_strategy, "item": item})
                    queue_save_csv_file.put(item)

        except Exception as ex:
            logger.info(ex, exc_info=True)

    print("finish")
    [terminate_task(t) for t in task_list]
    winsound.PlaySound('finish.wav', winsound.SND_LOOP + winsound.SND_ASYNC)
    time.sleep(2)


if __name__ == "__main__":
    logger = Utils.setup_logging()

    main_ui()
    # test()