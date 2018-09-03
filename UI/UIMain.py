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

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gbk')


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


def convert_month_to_type(text):
    month = Utils.convert_to_int(text)
    if month == 3:
        return 1
    elif month == 6:
        return 2
    else:
        raise ValueError(f"not supported month at present: {text}")


def get_ppd_cookie(driver):
    driver_cookies = driver.get_cookies()
    cookie_list = [f"{cookie['name']}={cookie['value']}" for cookie in driver_cookies]
    cookies = "; ".join(cookie_list)
    return cookies


def check_bid_number(item, cookies):
    logger.info(f"check bid number: {item['listingId']}")
    headers = {
        "Host": "invest.ppdai.com",
        "Connection": "keep-alive",
        "Content-Length": "308",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://invest.ppdai.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://invest.ppdai.com/loan/listpage/?risk=1&mirror=3&pageIndex=1&period=1,2&sex=male&money=5000,6000&times=3&auth=&rate=",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "aliyungf_tc=AQAAADy/WAbIdQgAjlD3PFdNL6QHjLf8; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22164f43356d917-044d577ffb8d9d-5b193613-2304000-164f43356db7d4%22%2C%22%24device_id%22%3A%22164f43356d917-044d577ffb8d9d-5b193613-2304000-164f43356db7d4%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D",
    }
    headers["Cookie"] = cookies

    url = "https://invest.ppdai.com/api/invapi/ListingListAuthService/listingPagerAuth"

    data = {
    "authInfo": "",
    "authenticated": False,
    "availableBalance": 0,
    "creditCodes": "3",
    "dataList": [ ],
    "didIBid": "0",
    "maxAmount": 6000,
    "minAmount": 5000,
    "months": "1,2",
    "needTotalCount": True,
    "pageCount": 0,
    "pageIndex": 1,
    "pageSize": 10,
    "rates": "",
    "riskLevelCategory": "1",
    "sort": 0,
    "source": 1,
    "successLoanNum": "3",
    "totalCount": 0
    }

    loan_amount = Utils.convert_to_int(item["借款金额"])
    data["minAmount"] = loan_amount
    data["maxAmount"] = loan_amount

    post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")

    session = requests.Session()
    req = session.post(url, data=post_data, headers=headers)
    result = req.text

    json_data = json.loads(result)
    listing_id = item['listingId']
    if "result" not in json_data or json_data["result"] != 1 or "resultContent" not in json_data or "dataList" not in json_data["resultContent"]:
        logger.warning(f"check_bid_number {listing_id}: {json.dumps(result, ensure_ascii=False)}")
        return False

    data_list = json_data["resultContent"]["dataList"]
    if len(data_list) != 1:
        logger.warning(f"check_bid_number {listing_id} {loan_amount} count != 1: {json.dumps(data_list, ensure_ascii=False)}")
        return False

    verify_item = data_list[0]
    if verify_item["listingId"] != int(item["listingId"]):
        logger.warning(f"check_bid_number {listing_id} listing id changed to: {verify_item['listingId']}: {json.dumps(result, ensure_ascii=False)}")
        return False

    return True


def bid_by_request(item, cookies):
    headers = {
        "Host": "invest.ppdai.com",
        "Connection": "keep-alive",
        "Content-Length": "750",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://invest.ppdai.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://invest.ppdai.com/loan/listpage/?risk=1&mirror=&pageIndex=1&period=&sex=male&money=,&times=&auth=&rate=",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "aliyungf_tc=AQAAADy/WAbIdQgAjlD3PFdNL6QHjLf8; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22164f43356d917-044d577ffb8d9d-5b193613-2304000-164f43356db7d4%22%2C%22%24device_id%22%3A%22164f43356d917-044d577ffb8d9d-5b193613-2304000-164f43356db7d4%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D",
    }
    headers["Cookie"] = cookies

    url = "https://invest.ppdai.com/api/invapi/PcBidService/oneKeyBid"

    loan_amount = Utils.convert_to_int(item["借款金额"])
    data = {
        "authInfo": "",
        "authenticated": True,
        "availableBalance": 79.08,
        "bidStatusDTOs": [],
        "creditCodes": "3",
        "dataList": [{
            "bidNum": 100,
            "bidStatusDTO": None,
            "amount": 17400,
            "bids": 233,
            "borrowerName": "pdu0****77408",
            "certificateValidate": 0,
            "creditCode": "B",
            "creditValidate": 0,
            "currentRate": 20,
            "funding": 16484,
            "isPay": False,
            "listingId": 125233286,
            "mobileRealnameValidate": 1,
            "months": 12,
            "nCIICIdentityCheck": 0,
            "statusId": 1,
            "title": "手机app用户的第17次闪电借款"
        }],
        "didIBid": "1",
        "ip": "101.41.247.234",   # must
        "maxAmount": 17400,  # must
        "minAmount": 17400,  # must
        "months": "1,2,3,4",
        "needTotalCount": True,
        "pageCount": 1,
        "pageIndex": 1,
        "pageSize": 10,
        "rates": "",
        "riskLevelCategory": 1,    # must
        "sort": 0,
        "source": 1,
        "successLoanNum": "3",
        "totalCount": 1,
        "userId": 87288708,
        "sigleBidAmount": 50,
        "bidCount": 1,
        "useCoupon": True
    }

    data["maxAmount"] = loan_amount
    data["minAmount"] = loan_amount
    data["ip"] = "60.247.80.142"     # 60.247.80.142   work    ;      101.41.247.234  hone
    data["riskLevelCategory"] = 1     # 0:  保守； 1:平衡  2：进取
    data["months"] = convert_month_to_type(item["期限"])

    data_item = data["dataList"][0]
    data_item["listingId"] = item["listingId"]
    data_item["amount"] = loan_amount
    data_item["creditCode"] = item["级别"]
    data_item["months"] = Utils.convert_to_int(item["期限"])
    data_item["title"] = item["title"]
    data_item["borrowerName"] = item["User"]
    data_item["bids"] = Utils.convert_to_int(item["投标人数"])
    data_item["funding"] = Utils.convert_to_int(item["进度"]) * loan_amount / 100

    data_item["currentRate"] = Utils.convert_to_int(item["协议利率"])
    # post_data = '{"authInfo":"","authenticated":true,"availableBalance":279.08,"bidStatusDTOs":[],"creditCodes":"3","dataList":[{"bidNum":100,"bidStatusDTO":null,"amount":17400,"bids":233,"borrowerName":"pdu0****77408","certificateValidate":0,"creditCode":"B","creditValidate":1,"currentRate":20,"funding":16484,"isPay":false,"listingId":125233286,"mobileRealnameValidate":1,"months":12,"nCIICIdentityCheck":0,"statusId":1,"title":"手机app用户的第17次闪电借款"}],"didIBid":"1","ip":"101.41.247.234","maxAmount":17400,"minAmount":17400,"months":"1,2,3,4","needTotalCount":true,"pageCount":1,"pageIndex":1,"pageSize":10,"rates":"","riskLevelCategory":1,"sort":0,"source":1,"successLoanNum":"3","totalCount":1,"userId":87288708,"sigleBidAmount":50,"bidCount":1,"useCoupon":true}'

    post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    # logger.info(f"bid by request: {post_data}")

    session = requests.Session()
    req = session.post(url, data=post_data, headers=headers)
    result = req.text

    json_data = json.loads(result)
    if "result" not in json_data:
        logger.warn(f"bid by request result error {item['listingId']}: {result}")
        return False

    if json_data["result"] != 1:
        logger.info(f"bid by request result {item['listingId']}: {req.text}")
        return False

    logger.info(f"bid by request result {item['listingId']}: {req.text}")
    return True

    # logger.info(f"bid by request: {json.dumps(req.text, ensure_ascii=False)}")

    pass

def totally_main_ui():
    strategy_factory = UIStrategyFactory()
    current_page = 1
    total_page = 1
    no_more_money = False
    navigate_details_page_count = 0
    df = None
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")

    config = refresh_config()
    listing_ids_cache = deque(df["listingId"].tail(10000).tolist())

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

                no_more_money = fetch_from_chrome.is_account_money_low()

                # if current_page < total_page:
                #     # fetch_from_chrome.back_until_listing_page(navigate_details_page_count)
                #     # time.sleep(1)
                #
                #     logger.info(f"click to next page: {current_page} {total_page}")
                #     fetch_from_chrome.click_to_next_page()
                #     time.sleep(1.5)
                # else:
                fetch_from_chrome.refresh_loan_list_page()

                listing_ids, current_page, total_page = fetch_from_chrome.get_all_listing_items()
                logger.debug("iter_listing_item_to_detail_page end")
                if len(listing_ids) == 0:
                    # logger.info(f"can not get listing in: {current_page} {total_page} {listing_ids}")
                    continue

                should_back = len(listing_ids) == 1
                navigate_details_page_count = 0
                for listing_id in listing_ids:
                    if int(listing_id) in listing_ids_cache:
                        continue

                    listing_ids_cache.append(int(listing_id))
                    should_back = True
                    if should_back:
                        if not fetch_from_chrome.click_listing_in_listpage(listing_id, None, in_current_tab=True):
                            continue
                    else:
                        fetch_from_chrome.navigate_detail(listing_id)

                    # fetch_from_chrome.switch_to_window(1)
                    item = fetch_from_chrome.fetch_detail_info(False)
                    # fetch_from_chrome.close_window(0)
                    # time.sleep(2)
                    navigate_details_page_count += 1
                    if item is None:
                        continue

                    current_time = time.localtime()
                    item["creationDate"] = time.strftime('%Y-%m-%dT%H:%M:%S', current_time)

                    if no_more_money:
                        df = save_to_csv(df, item)
                        continue

                    can_bid, first_strategy = strategy_factory.is_item_can_bid(item)
                    if not can_bid:
                        df = save_to_csv(df, item)
                        continue

                    filter_success = fetch_from_chrome.filter_item(item)
                    if not filter_success:
                        df = save_to_csv(df, item)
                        continue

                    # logger.info("click_not_bid_button")
                    # fetch_from_chrome.click_not_bid_button()
                    logger.info("start check_bid_number")
                    if not fetch_from_chrome.check_bid_number(item):
                        df = save_to_csv(df, item)
                        continue

                    logger.info("can bid: %s %s\n%s", item["listingId"], first_strategy, item)

                    if fetch_from_chrome.quick_bid():
                        json_string = json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False)
                        logger.log(21, "bid: %s: %s \n%s \n%s", item["listingId"], first_strategy,
                                   first_strategy.strategy_detail(), json_string)

                    item["strategy"] = first_strategy.name
                    df = save_to_csv(df, item)
                    time.sleep(1)
                    fetch_from_chrome.bid_again()
                    time.sleep(0.5)
        except Exception as ex:
            logger.info(ex, exc_info=True)


# 1 2  he cai
def main_ui():
    strategy_factory = UIStrategyFactory()
    no_more_money = False
    df = None
    if os.path.exists(data_file_path):
        df = pd.read_csv(data_file_path, encoding="utf-8")

    config = refresh_config()
    listing_ids_cache = deque(df["listingId"].tail(10000).tolist())

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

                cookies = get_ppd_cookie(fetch_from_chrome.driver)
                no_more_money = fetch_from_chrome.is_account_money_low()
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
                    logger.info(f"navigate detail, {should_back}")
                    if should_back:
                        if not fetch_from_chrome.click_listing_in_listpage(listing_id, None):
                            continue
                    else:
                        fetch_from_chrome.navigate_detail(listing_id)

                    logger.info("fetch detail info")
                    item = fetch_from_chrome.fetch_detail_info(False)
                    if item is None:
                        continue

                    current_time = time.localtime()
                    item["creationDate"] = time.strftime('%Y-%m-%dT%H:%M:%S', current_time)

                    if no_more_money:
                        df = save_to_csv(df, item)
                        continue

                    can_bid, first_strategy = strategy_factory.is_item_can_bid(item)
                    if not can_bid:
                        df = save_to_csv(df, item)
                        continue

                    if not check_bid_number(item, cookies):
                        df = save_to_csv(df, item)
                        continue

                    item["strategy"] = first_strategy.name
                    if bid_by_request(item, cookies):
                        logger.log(21, "bid: %s: %s \n%s \n%s", item["listingId"], first_strategy,
                                   first_strategy.strategy_detail(), json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False))
                    df = save_to_csv(df, item)
        except Exception as ex:
            logger.info(ex, exc_info=True)


def bid_today():
    sf = UIStrategyFactory()
    df = pd.read_csv("..\\UI\\UIMain.csv", encoding="utf-8")
    df = df[df["期限"] != "12个月"]

    series_creation_date = pd.to_datetime(df["creationDate"])
    current_day = pd.to_datetime('today').strftime("%m/%d/%Y")
    print(current_day)

    next_day = pd.Timestamp(current_day) + pd.DateOffset(1)
    df = df[(series_creation_date > pd.Timestamp(current_day)) & (series_creation_date < next_day)]
    # print(df.shape)

    config = refresh_config()
    with FetchFromChromeQuick(config["Session"]) as fetch_from_chrome:
        cookies = get_ppd_cookie(fetch_from_chrome.driver)
        for item in df.to_dict('records'):
            can_bid, first_strategy = sf.is_item_can_bid(item, False)
            time.sleep(1.5)
            if can_bid:
                if not check_bid_number(item, cookies):
                    continue

                print(f"bid: {item['listingId']} \t {first_strategy}")
                item["strategy"] = first_strategy.name
                if bid_by_request(item, cookies):
                    logger.log(21, "bid: %s: %s \n%s \n%s", item["listingId"], first_strategy,
                               first_strategy.strategy_detail(),
                               json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False))

                break



if __name__ == "__main__":
    logger = Utils.setup_logging()

    totally_main_ui()
    # test()

    # bid_today()

    print("finish")
    winsound.PlaySound('finish.wav', winsound.SND_LOOP + winsound.SND_ASYNC)

    time.sleep(0.8)

    with open('UIMain.json', "r+") as f:
        data = json.load(f)
        data[platform.node()]["Terminate"] = "False"
        f.seek(0)
        f.write(json.dumps(data, indent=4))