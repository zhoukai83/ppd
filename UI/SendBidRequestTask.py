import json
import logging
import requests
import time

from Common import Utils
from PpdCommon.PpdTask import PpdTask


class SendBidRequestTask(PpdTask):
    def __init__(self, input_queue, logger=None):
        logger = logger or logging.getLogger(__name__)
        PpdTask.__init__(self, logger=logger)
        self.input_queue = input_queue
        self.cookies = None

    def update_cookie(self, cookies):
        self.cookies = cookies

    def convert_month_to_type(self, text):
        month = Utils.convert_to_int(text)
        if month == 3:
            return 1
        elif month == 6:
            return 2
        else:
            raise ValueError(f"not supported month at present: {text}")

    def check_bid_number(self, item, cookies):
        self.logger.info(f"check bid number: {item['listingId']}")
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
            "dataList": [],
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
        if "result" not in json_data or json_data[
            "result"] != 1 or "resultContent" not in json_data or "dataList" not in json_data["resultContent"]:
            self.logger.warn(f"check_bid_number {listing_id}: {json.dumps(result, ensure_ascii=False)}")
            return False

        data_list = json_data["resultContent"]["dataList"]
        if len(data_list) != 1:
            self.logger.warn(f"check_bid_number {listing_id} count != 1: {json.dumps(data_list, ensure_ascii=False)}")
            return False

        verify_item = data_list[0]
        if verify_item["listingId"] != int(item["listingId"]):
            self.logger.warn(f"check_bid_number {listing_id} listing id changed: {json.dumps(result, ensure_ascii=False)}")
            return False

        return True

    def bid_by_request(self, item, cookies):
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
            "ip": "101.41.247.234",  # must
            "maxAmount": 17400,  # must
            "minAmount": 17400,  # must
            "months": "1,2,3,4",
            "needTotalCount": True,
            "pageCount": 1,
            "pageIndex": 1,
            "pageSize": 10,
            "rates": "",
            "riskLevelCategory": 1,  # must
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
        data["ip"] = "60.247.80.142"  # 60.247.80.142   work    ;      101.41.247.234  hone
        data["riskLevelCategory"] = 1  # 0:  保守； 1:平衡  2：进取
        data["months"] = self.convert_month_to_type(item["期限"])

        data_item = data["dataList"][0]
        data_item["listingId"] = item["listingId"]
        data_item["amount"] = loan_amount
        data_item["borrowerName"] = item["User"]
        data_item["creditCode"] = item["级别"]
        data_item["months"] = Utils.convert_to_int(item["期限"])
        data_item["title"] = item["title"]
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
        listing_id = item['listingId']
        if "result" not in json_data:
            self.logger.warn(f"bid by request result error {listing_id}: {result}")
            return False

        if json_data["result"] != 1:
            self.logger.info(f"bid by request result {listing_id}: {req.text}")
            return False

        self.logger.info(f"bid by request result {listing_id}: {req.text}")
        return True

        # logger.info(f"bid by request: {json.dumps(req.text, ensure_ascii=False)}")
        pass

    def task_body(self):
        try:
            # if self.input_queue.empty():
            #     time.sleep(0.1)
            #     return False

            bid_item = self.input_queue.get(timeout=5)
            if bid_item is None:
                self.logger.info("none")
                return False

            item = bid_item["item"]
            first_strategy = bid_item["strategy"]
            if not self.check_bid_number(item, self.cookies):
                return False

            item["strategy"] = first_strategy.name
            if self.bid_by_request(item, self.cookies):
                json_string = json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False)
                self.logger.log(21, f"bid:{item['listingId']}:{first_strategy}\n{first_strategy.strategy_detail()}\n{json_string}")
        except Exception as ex:
            return False
        return True