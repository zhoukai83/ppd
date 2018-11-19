import sys, time, queue
import json
import requests
import os
import traceback
import random
from multiprocessing.managers import BaseManager
import platform
from datetime import datetime
platform.node()

config_file = json.load(open("config.json", "r"))
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


headers["Cookie"] = config_file["Cookie"]


def get_from_url():
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
    post_data = '{"authInfo":"","authenticated":false,"availableBalance":0,"creditCodes":"3","dataList":[],"didIBid":"0","maxAmount":0,"minAmount":0,"months":"1,2","needTotalCount":true,"pageCount":0,"pageIndex":1,"pageSize":10,"rates":"","riskLevelCategory":"1","sort":0,"source":1,"successLoanNum":"2,3","totalCount":0}'

    headers["Cookie"] = config_file["Cookie"]
    session = requests.Session()
    req = session.post(url, data=post_data, headers=headers)
    return req.text


def get_listings():
    listings = []
    json_data = json.loads(get_from_url())
    if "resultContent" not in json_data:
        return []

    if "result" in json_data and json_data["result"] == 1012:
        # result:1012
        # resultContent: null
        # resultMessage:"访问过于频繁，请稍后再试"
        pass

    if "totalCount" in json_data["resultContent"]:
        total_count = json_data["resultContent"]["totalCount"]
        page_count = json_data["resultContent"]["pageCount"]
        print("get page", page_count, total_count)

        for item in json_data["resultContent"]["dataList"]:
            item["fetchTime"] = datetime.utcnow()
            listings.append(item)

    return listings

class QueueManager(BaseManager):
    pass

def main():
    QueueManager.register('get_task_queue')
    QueueManager.register('get_result_queue')

    config_file = json.load(open("config.json", "r"))
    server_addr = config_file["ServerAddr"]
    print('Connect to server %s...' % server_addr)

    m = QueueManager(address=(server_addr, 50083), authkey=b'abc')
    m.connect()

    task = m.get_task_queue()
    result = m.get_result_queue()

    start_time = time.perf_counter()

    try_count = 5
    count = 0
    while try_count > 0:
        number = random.randint(0, 100)
        print(datetime.now().strftime("%H:%M:%S.%f"), number)
        listings = get_listings()
        print(datetime.now().strftime("%H:%M:%S.%f"), number)
        task.put(listings)
        time.sleep(1.5)

    print('worker exit')


def test():
    print(get_from_url())

if __name__ == "__main__":
    test()
