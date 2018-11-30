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
from collections import deque

def refresh_config():
    with open('GetDebt.json') as f:
        data = json.load(f)
        config = data[platform.node()]
        return config


def restore_config():
    with open('GetDebt.json', "r+") as f:
        data = json.load(f)
        data[platform.node()]["Terminate"] = "False"
        f.seek(0)
        f.write(json.dumps(data, indent=4))


def should_bid(item):
    if item["OwingNumber"] >= 6:
        return False

    if item["OwingNumber"] <= 2:
        return True

    if item["OwingNumber"] >= 3 and item["PriceforSaleRate"] < 10.5:
        return False

    return True


def main():
    ppd_open_client = AioOpenClient(key_index=1)
    ppd_open_client2 = AioOpenClient(key_index=2)
    ppd_open_client3 = AioOpenClient(key_index=3)
    terminate = False

    df = None
    listing_id_cache = deque(maxlen=50)

    data_file_path = "GetDebt.csv"
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")
        listing_id_cache = deque(df["ListingId"].tail(50).tolist(), maxlen=50)

    config = refresh_config()
    current_client_index = 1

    while config["Terminate"] == "False":
        config = refresh_config()
        # logger.info("start")
        time.sleep(0.37)

        try:
            if current_client_index == 1:
                buy_list_str = ppd_open_client.get_buy_list(levels="AA")
                current_client_index = 2
            elif current_client_index == 2:
                buy_list_str = ppd_open_client2.get_buy_list(levels="AA")
                current_client_index = 3
            else:
                buy_list_str = ppd_open_client3.get_buy_list(levels="AA")
                current_client_index = 1

            json_data = json.loads(buy_list_str)

            if not json_data.get("Result") == 1:
                logger.info(f"buy list issue: {json_data}")

            if json_data.get("message") == "您的操作太频繁啦，请喝杯茶后，再来试试吧":
                raise PpdNeedSleepException

            debt_infos = json_data.get("DebtInfos")
            if not debt_infos:
                continue

            new_debt_infos = [item for item in debt_infos if item["ListingId"] not in listing_id_cache]
            if not new_debt_infos:
                continue
            listing_id_cache.extendleft([item["ListingId"] for item in new_debt_infos])
            logger.info(f"Get debt lists: {new_debt_infos}")

            should_bid_new_debt_infos = [item for item in new_debt_infos if should_bid(item)]
            if should_bid_new_debt_infos:
                buy_debt_results = [ppd_open_client.buy_debt(item["DebtdealId"]) for item in should_bid_new_debt_infos]
                logger.log(21, f"buy debt: {json.dumps(buy_debt_results,indent=4, ensure_ascii=False)}")

            df = PandasUtils.save_list_to_csv(data_file_path, df, new_debt_infos)

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
    logger.info("End")
    pass


if __name__ == "__main__":
    # logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    # logging.basicConfig(level=20, format=logging_format)
    # logger = logging.getLogger(__name__)
    logger = CommonUtils.setup_logging(default_path="GetDebt.logging.json")

    main()
    toaster = ToastNotifier()
    toaster.show_toast("Warning", f"This notification is in it's own thread!{111}",
                                       icon_path=None,
                                       duration=5,
                                       threaded=True)
    while toaster.notification_active():
        time.sleep(0.3)