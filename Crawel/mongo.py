import pymongo
import requests
import json
import time
import datetime

conn = pymongo.MongoClient('10.164.120.164', 27017)
db_ppd = conn.ppd
collection_listing = db_ppd.Listing
config_file = json.load(open("config.json", "r"))

def get_from_url(pageIndex):
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
    post_data = '{"authInfo":"","authenticated":false,"availableBalance":0,"creditCodes":"","dataList":[],"didIBid":"0","maxAmount":0,"minAmount":0,"months":"","needTotalCount":true,"pageCount":0,"pageIndex":'+ str(pageIndex) +',"pageSize":10,"rates":"","riskLevelCategory":"1","sort":0,"source":1,"successLoanNum":"","totalCount":0}'

    headers["Cookie"] = config_file["Cookie"]
    session = requests.Session()
    req = session.post(url, data=post_data, headers=headers)
    return req.text


def insert_listing(item):
    MAX_RETRY = 5
    retry = 0
    while retry < MAX_RETRY:
        try:
            x = collection_listing.insert_many(item)
            print(x.inserted_ids)
            return True
        except Exception as e:
            print(e)
        retry += 1

    return False


def get_all_listing():
    page_count = 1
    current_page = 1
    last_total_count = 0

    bulk_items = []
    listings = fetch_latest_from_db()
    if len(listings) == 0:
        return

    while current_page <= page_count:
        json_data = json.loads(get_from_url(current_page))
        if "resultContent" not in json_data:
            continue

        if "totalCount" in json_data["resultContent"]:
            total_count = json_data["resultContent"]["totalCount"]
            page_count = json_data["resultContent"]["pageCount"]
            last_total_count = json_data["resultContent"]["totalCount"]
            print("get page", current_page, page_count, total_count)

            for item in json_data["resultContent"]["dataList"]:
                if not listing_exist(item, listings):
                    item["fetchTime"] = datetime.datetime.utcnow()
                    bulk_items.append(item)

        if len(bulk_items) >= 10:
            if insert_listing(bulk_items):
                bulk_items = []
        current_page += 1

    if len(bulk_items) > 0:
        insert_listing(bulk_items)

    return last_total_count


def fetch_latest_from_db():
    MAX_RETRY = 5
    retry = 0
    while retry < MAX_RETRY:
        try:
            return list(collection_listing.find().sort('_id', pymongo.DESCENDING).limit(1000))
        except Exception as e:
            print(e)
        retry += 1
        time.sleep(1)

    return []

def listing_exist(listing, db_list):
    for item in db_list:
        if listing["listingId"] == item["listingId"]:
            return True

    return False


def main():

    while True:
        get_all_listing()
        time.sleep(5)


if __name__ == "__main__":
    main()
