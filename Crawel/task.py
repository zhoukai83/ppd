import sys, time, queue
import json
import requests
import os
import traceback
import pymongo
from multiprocessing.managers import BaseManager
import platform
from datetime import datetime
platform.node()

conn = pymongo.MongoClient('10.164.120.164', 27017)
db_ppd = conn.ppd
collection_listing_crawl = db_ppd.ListingCrawl


config_file = json.load(open("config.json", "r"))
# hone  sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22164c7266b8346a-02f534edc6d2cf-5b193613-1440000-164c7266b841d2%22%2C%22%24device_id%22%3A%22164c7266b8346a-02f534edc6d2cf-5b193613-1440000-164c7266b841d2%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; uniqueid=da6b9c75-42db-4a50-bdc4-c67a020069a6; aliyungf_tc=AQAAAM5M5jjpFAQAgP8mZbJFwiXe5q4J; regSourceId=0; referID=0; fromUrl=https%3A%2F%2Fwww.ppdai.com%2F; referDate=2018-7-23%2020%3A39%3A30; __fp=fp; __vid=1335039521.1532349573016; __tsid=200643318; __vsr=1532349573016.refSite%3Dhttps%3A//www.ppdai.com/%7Cmd%3Dreferral%7Ccn%3Dreferral; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1532349573; gr_user_id=95487af4-5f8b-4e8f-8d75-1b43b31b83e8; gr_session_id_b9598a05ad0393b9=a96ea6a2-77e9-42e3-b6cf-6ca5a1e0db2a; currentUrl=https%3A%2F%2Finvest.ppdai.com%2Floan%2Finfo%3Fid%3D122266418; gr_session_id_b9598a05ad0393b9_a96ea6a2-77e9-42e3-b6cf-6ca5a1e0db2a=true; __sid=1532349573016.3.1532349625438; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1532349625
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

url = "https://invest.ppdai.com/api/invapi/LoanDetailWithNoAuthPcService/showBaseInfoWithNoAuth"


class QueueManager(BaseManager):
    pass


def flat_json(jsonData, parentKey=None):
    if not jsonData:
        return {}

    flat_dict = {}
    for key in jsonData:
        if type(jsonData[key]).__name__ == 'dict':
            if parentKey:
                temp = flat_json(jsonData[key], parentKey + "_" + key)
                flat_dict = {**flat_dict, **temp}
            else:
                temp = flat_json(jsonData[key], key)
                flat_dict = {**flat_dict, **temp}
        else:
            if parentKey:
                flat_dict[parentKey + "_" + key] = jsonData[key]
            else:
                flat_dict[key] = jsonData[key]

    return flat_dict





def db_retry(func, *args, **kwargs):
    MAX_RETRY = 5
    retry = 0
    while retry < MAX_RETRY:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
        retry += 1

    return None


def db_retry_insert_one(collection, item):
    return db_retry(collection.insert_one, item)


def db_retry_find_one(collection, filter_object):
    return db_retry(collection.find_one, filter_object)


def __get_website(session, id, listing_in_db):
    try:
        # db_with_retry(collection_listing_crawl.find_one, {"listing_listingId":  { "$gt": 98000001}})
        headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(id)
        req = session.post(url, data='{"listingId":"' + str(id) + '","source":1}', headers=headers)
        json_data = json.loads(req.text)
        flat_json_data = flat_json(json_data["resultContent"], None)
        return flat_json_data
    except Exception as e:
        print(e)
        traceback.print_exc(e)
    return None

def listing_exist(listing_in_db, id):
    for item in listing_in_db:
        if item["listing_listingId"] == id:
            print("exist", id)
            return True

    return False

def get_website(start):
    session = requests.Session()

    success = True
    list_crawl  = []
    listing_in_db = list(db_retry(collection_listing_crawl.find, {"listing_listingId": {"$gt": start - 1, "$lt": start + 101}}))
    for index in range(100):
        id = start + index
        file_name = 'data/{0}.json'.format(id)

        try_count = 3
        while try_count > 0:
            if listing_exist(listing_in_db, id):
                break

            result = __get_website(session, id, listing_in_db)
            try_count -= 1
            if result:
                list_crawl.append(result)
                break
            time.sleep(5)

        if try_count == 0:
            print("error", id, start)
            success = False
            break

    if len(list_crawl) > 0:
        print(len(list_crawl))
        db_retry(collection_listing_crawl.insert_many, list_crawl)
    # if not os.path.exists("data_combine_100"):
    #     os.makedirs("data_combine_100")

    # records = []
    # for index in range(100):
    #     try:
    #         id = start + index
    #         file_name = 'data/{0}.json'.format(id)
    #         jsonData = json.load(open(file_name, "r", encoding='utf-8'))
    #         records.append(jsonData)
    #     except Exception as e:
    #         print(id, e)
    #
    # with open('data_combine_100/{0}.json'.format(start), 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(records, ensure_ascii=False))


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
        if task.empty():
            print('task queque is empty')
            time.sleep(1)
            try_count -= 1
            continue

        try:
            n = task.get(timeout=1)
            start_time = time.perf_counter()
            get_website(n)
            print('finish task', n, datetime.now().strftime('%H:%M:%S'), time.perf_counter() - start_time)
            result.put(n)
            count += 1
        except Exception as e:
            print('exception', e)
            try_count -= 1
            time.sleep(5)

    print('worker exit')

if __name__ == "__main__":
    main()
    # get_website(98000301)