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

            if number >= 3:
                should_bid_list.append(item)
        
        if item["级别"] == "B" and item["期限"] == 3:
            title = item.get("title")
            match = re.search(r"(?<=第)\d+(?=次)", title, re.DOTALL)
            number = 1
            if match:
                result = match.group()
                number = int(result)

            if number >= 12:
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
    bid_amount = 81
    config_file_name = os.path.basename(__file__).split(".")[0] + ".json"

    last_refresh_list_time = time.time()
    data_file_path = "UISimMainV2.csv"
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")
        listing_ids_cache = deque(df["listingId"].tail(700).tolist(), maxlen=700)
    else:
        listing_ids_cache = deque(maxlen=700)

    config = refresh_config(config_file_name)

    # token_update_time, token_config = TokenHelper.get_token_from_config()
    # ppd_open_client.set_access_token(token_config["AccessToken"])

    cookies = "gr_user_id=11f8ea81-90aa-4c3e-a041-71c51c28ea51; uniqueid=747711b0-faee-473f-96e7-a488248ded5f; __fp=fp; __vid=3407234.1530775507276; _ppdaiWaterMark=15312861763999; _ga=GA1.2.1098278737.1530780657; ppdaiRole=8; __utma=1.1098278737.1530780657.1540786794.1540874893.54; __utmz=1.1540874893.54.54.utmcsr=ppdai.com|utmccn=(referral)|utmcmd=referral|utmcct=/moneyhistory; Hm_lvt_aab1030ecb68cd7b5c613bd7a5127a40=1540535505,1540536242,1540786823,1540874918; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1543218607,1545375211; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1545375211; token=78dc8134594dfea0e1aa6a7ef7093f571b2f1889019a69a6bf0e5b219cdb1e387519fb7ccea5ac481e; aliyungf_tc=AQAAAPKxcnMI/goAjlD3PAt3MySMqUqH; __tsid=225271519; __vsr=1546505854605.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV3%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1546508350726.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1546581498720.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV3%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1546586577544.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1546827928367.refSite%3Dhttps%3A//pay.ppdai.com/Withdraw/CashSuc%7Cmd%3Dreferral%7Ccn%3Dreferral; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22first_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; __sid=1546827928367.12.1546829014789; waterMarkTimeCheck1=01%2F07%2F2019+10%3A43%3A35"
    ppd_sim_client.update_cookies(cookies)

    while config["Terminate"] == "False":
        tasks = []
        try:
            # if datetime.datetime.now() - token_update_time > datetime.timedelta(days=6, hours=23, minutes=30):
            #     token_update_time, token_config = TokenHelper.refresh_open_client_token(ppd_open_client, token_config, logger)
            #     ppd_open_client.set_access_token(token_config["AccessToken"])

            sleep_time = config["Sleep"] + random.randint(0, config["RandomSleep"])
            if no_more_money:
                sleep_time = sleep_time + 30
            time.sleep(sleep_time)
            config = refresh_config(config_file_name)

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

            loan_list_items = loan_list_items[:3]
            listing_ids = [item["listingId"] for item in loan_list_items]
            listing_ids_len = len(listing_ids)
            if not listing_ids:
                continue

            logger.info(f"{get_list_from} {listing_ids}, {loan_list_items}")
            listing_ids_cache.extendleft(listing_ids)

            bid_without_detail_list = should_bid_without_detail_info(loan_list_items)
            if bid_without_detail_list:
                logger.log(21, f"should_bid_without_detail_info from {get_list_from}: {[item['listingId'] for item in bid_without_detail_list]}")
                task_list = [asyncio.ensure_future(ppd_open_client.aio_bid(item['listingId'], 52)) for item in bid_without_detail_list]
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

                    task = asyncio.ensure_future(ppd_open_client.aio_bid(item['listingId'], bid_amount))
                    tasks.append(task)

                    if not ppd_sim_client.check_bid_number(item):
                        continue

                    item["strategy"] = first_strategy.name
                    if ppd_sim_client.bid_by_request(item, bid_amount+1):
                        logger.log(21, f"bid from {get_list_from}:{item['listingId']} {first_strategy} \n{first_strategy.strategy_detail()} \n{json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False)}")

            if tasks:
                aio_bid_result = loop.run_until_complete(asyncio.gather(*tasks))
                logger.log(21, f"bid open from {get_list_from}: {aio_bid_result}")

                if bid_without_detail_list and get_list_from == "U":
                    for item in aio_bid_result:
                        json_data = json.loads(item, encoding="utf-8")

                        result_code = json_data.get("Result", -1)
                        if result_code != 2002:   #标的不存在
                            continue

                        listing_id = json_data.get("ListingId")
                        listing_item = next((item for item in bid_without_detail_list if item["listingId"] == listing_id), None)
                        if not listing_item:
                            continue

                        logger.info(f"bid again with U: {listing_item['listingId']}")
                        if not ppd_sim_client.check_bid_number(listing_item):
                            continue

                        if ppd_sim_client.bid_by_request(listing_item):
                            logger.log(21, f"bid again from {get_list_from}: {listing_item}")

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
                    time.sleep(2.3 * len_listing_detail_list)
                else:
                    time.sleep(2)

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