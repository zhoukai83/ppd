import sys
sys.path.insert(0, "..")

import redis
import logging
import time

from Open.PpdOpenClient import PpdOpenClient
from Common import Utils as CommonUtils
from collections import deque
import json
import requests
from argparse import ArgumentParser
from UISimulation.PpdUISimulationRequest import PpdNeedSleepException

headers = {
    "Host": "invest.ppdai.com",
    "Connection": "keep-alive",
    "Content-Length": "36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://invest.ppdai.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Referer": "https://invest.ppdai.com/loan/info/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cookie": "sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22164c7266b8346a-02f534edc6d2cf-5b193613-1440000-164c7266b841d2%22%2C%22%24device_id%22%3A%22164c7266b8346a-02f534edc6d2cf-5b193613-1440000-164c7266b841d2%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; uniqueid=da6b9c75-42db-4a50-bdc4-c67a020069a6; aliyungf_tc=AQAAAM5M5jjpFAQAgP8mZbJFwiXe5q4J; regSourceId=0; referID=0; fromUrl=https%3A%2F%2Fwww.ppdai.com%2F; referDate=2018-7-23%2020%3A39%3A30; __fp=fp; __vid=1335039521.1532349573016; __tsid=200643318; __vsr=1532349573016.refSite%3Dhttps%3A//www.ppdai.com/%7Cmd%3Dreferral%7Ccn%3Dreferral; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1532349573; gr_user_id=95487af4-5f8b-4e8f-8d75-1b43b31b83e8; gr_session_id_b9598a05ad0393b9=a96ea6a2-77e9-42e3-b6cf-6ca5a1e0db2a; currentUrl=https%3A%2F%2Finvest.ppdai.com%2Floan%2Finfo%3Fid%3D122266418; gr_session_id_b9598a05ad0393b9_a96ea6a2-77e9-42e3-b6cf-6ca5a1e0db2a=true; __sid=1532349573016.2.1532349576928; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1532349577"
}

def get_from_url(page_index=1):
    headers = {
        "Host": "invest.ppdai.com",
        "Connection": "keep-alive",
        "Content-Length": "297",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://invest.ppdai.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://invest.ppdai.com/loan/listpage/?risk=1&mirror=&pageIndex=1&period=&sex=male&money=,&times=&auth=&rate=",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "aliyungf_tc=AQAAADy/WAbIdQgAjlD3PFdNL6QHjLf8; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22164f43356d917-044d577ffb8d9d-5b193613-2304000-164f43356db7d4%22%2C%22%24device_id%22%3A%22164f43356d917-044d577ffb8d9d-5b193613-2304000-164f43356db7d4%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D",
    }

    url = "https://invest.ppdai.com/api/invapi/ListingListNoAuthService/listingPagerNoAuth"
    data = {
        "authInfo": "",
        "authenticated": False,
        "availableBalance": 0,
        "creditCodes": "",
        "dataList": [],
        "didIBid": "1",  # 仅显末投
        "maxAmount": 0,
        "minAmount": 0,
        "months": "1, 2",  # 1 = 3月，   2=6月
        "needTotalCount": True,
        "pageCount": 0,
        "pageIndex": page_index,
        "pageSize": 10,
        "rates": "",
        "riskLevelCategory": "1",  # 1: 平衡型
        "sort": 0,
        "source": 1,
        "successLoanNum": "3",  # 成功借款次数   3: > 6次
        "totalCount": 0
    }

    post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    # post_data = '{"authInfo":"","authenticated":false,"availableBalance":0,"creditCodes":"","dataList":[],"didIBid":"0","maxAmount":0,"minAmount":0,"months":"1,2","needTotalCount":true,"pageCount":0,"pageIndex":1,"pageSize":10,"rates":"","riskLevelCategory":"1","sort":0,"source":1,"successLoanNum":"3","totalCount":0}'

    session = requests.Session()
    req = session.post(url, data=post_data, headers=headers)
    result = req.text

    try:
        logger.info(result)
        json_data = json.loads(result)

        if json_data.get("result", -999) != 1 or "resultContent" not in json_data or "dataList" not in \
                json_data["resultContent"]:
            logger.warning(f"get list: {json.dumps(result, ensure_ascii=False)}")
            if json_data.get("result") == 1012:
                raise PpdNeedSleepException
            return []

        data_list = json_data["resultContent"]["dataList"]
        not_full_list = [item["listingId"] for item in data_list if item["amount"] > item["funding"]]
        return not_full_list
    except PpdNeedSleepException:
        raise PpdNeedSleepException
    except Exception as ex:
        logger.error(f"check_bid_number {ex} {result}", exc_info=True)

    return []


def test():
    print(get_from_url(page_index=2))

def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--index",
                        dest="client_index", default=2,
                        help="use client index")

    parser.add_argument("-t", "--interval time",
                        dest="interval_time", default=0.5,
                        help="2 request interval")

    args = parser.parse_args()
    interval_time = float(args.interval_time)
    print("use client index:", args.client_index)
    print("2 request interval:", interval_time)

    redis_client = redis.StrictRedis(host='10.164.120.164', port=6379, db=0)
    listing_ids_cache = deque(maxlen=1000)
    last_refresh_list_time = time.time()

    page_index = 15
    while True:
        try:
            logger.info(f"page_index: {page_index}")
            if page_index <= 0:
                break
            time.sleep(20)

            listing_ids = get_from_url(page_index=page_index)
            page_index -= 1
            last_refresh_list_time = time.time()

            if listing_ids:
                redis_listing_ids_str = redis_client.get("loan_listing_ids")
                logging.info(listing_ids)
                logging.info(redis_listing_ids_str)
                if redis_listing_ids_str is None or redis_listing_ids_str == b"None":
                    redis_client.set("loan_listing_ids", listing_ids)
                    logger.info(f"set {listing_ids}")
                else:
                    redis_listing_ids = json.loads(redis_listing_ids_str)
                    new_listing_ids = [item for item in listing_ids if item not in redis_listing_ids]
                    new_len = len(new_listing_ids)
                    new_listing_ids.extend(redis_listing_ids)
                    redis_client.set("loan_listing_ids", new_listing_ids)
                    logger.info(f"extend num:{new_len}  {new_listing_ids}")

            # new_listing_ids = []
            # for listing_id in listing_ids:
            #     if int(listing_id) in listing_ids_cache:
            #         continue
            #
            #     listing_ids_cache.append(int(listing_id))
        except Exception as ex:
            logging.error(ex, exc_info=True)
            break
    pass

if __name__ == "__main__":
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=15, format=logging_format)
    logger = logging.getLogger(__name__)
    main()
    print("done")