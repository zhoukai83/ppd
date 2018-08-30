import json
import os
import platform
import random
import time
import winsound

import Utils
import pandas as pd
from FetchFromChromeQuick import FetchFromChromeQuick
from StrategyFactory import StrategyFactory
from pandas import DataFrame


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

data_file_path = "UIMain.csv"
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


# 1 2  he cai
def main_ui():
    pass


if __name__ == "__main__":
    logger = Utils.setup_logging()

    main_ui()
    # test()