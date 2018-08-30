import sys
sys.path.insert(0,'..')

import json
import os
import platform
import random
import time
import winsound

import Utils
import pandas as pd
from FetchFromChromeQuick import FetchFromChromeQuick
from pandas import DataFrame

from Common.UIStrategyFactory import UIStrategyFactory



data_file_path = "UIOverDue.csv"
def save_to_csv(df, item):
    frame = DataFrame([item])

    if df is None:
        frame.to_csv(data_file_path, encoding="utf-8", index=False)
        df = frame
    else:
        df = pd.concat([df, frame], ignore_index=True, sort=False)
        df.to_csv(data_file_path, encoding="utf-8", index=False)

    return df

def refresh_config():
    with open('UIMain.json') as f:
        data = json.load(f)
        config = data[platform.node()]
        return config


def main_ui():
    df = None
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")

    config = refresh_config()

    with FetchFromChromeQuick(config["Session"]) as fetch_from_chrome:
        fetch_from_chrome.switch_to_window(0)

        for index in range(1, 6):
            url = "https://invdebt.ppdai.com/buy/list?category=4&levels=,B,&overDueDays=&monthGroup=1,2,&rate=&minAmount=&maxAmount=&sortType=-13&minPastDueNumber=&maxPastDueNumber=&minPastDueDay=&maxPastDueDay=&minAllowanceRadio=&maxAllowanceRadio=&isShowMore=&pageIndex=" + str(index)
            fetch_from_chrome.driver.get(url)
            print(url)
            time.sleep(1)
            listing_ids = fetch_from_chrome.get_all_buy_listing_items()
            if len(listing_ids) == 0:
                return

            for listing_id in listing_ids:
                if df is not None and (df["listingId"] == int(listing_id[0])).any():
                    continue

                url = "https:" + listing_id[2]
                fetch_from_chrome.driver.get(url)
                item = fetch_from_chrome.fetch_detail_buy_info()
                item["overDueDays"] = listing_id[1]
                item["listingId"] = listing_id[0]
                item["creationDate"] = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
                df = save_to_csv(df, item)
                time.sleep(0.3)


if __name__ == "__main__":
    # logger = Utils.setup_logging()

    main_ui()
    # test()