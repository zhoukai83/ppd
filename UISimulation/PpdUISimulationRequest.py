import logging
import asyncio
from aiohttp import ClientSession
import json
import requests
import os
from itertools import groupby
from Common import Utils
import urllib
import time


class PpdNeedSleepException(Exception):
    pass


class PpdResultContentNullException(Exception):
    pass


class PpdNotEnoughMoneyException(Exception):
    pass


class PpdUISimulationRequest:
    def __init__(self, cookies=None, logger=None):
        self.cookies = cookies
        self.logger = logger or logging.getLogger(__name__)

        self.headers = {
            "Host": "invest.ppdai.com",
            "Connection": "keep-alive",
            # "Content-Length": "959",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://invest.ppdai.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://invest.ppdai.com/loan/info/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": "sajssdk_2015_cross_new_user=1; uniqueid=8a367b8a-0a7d-44d5-99f2-e03f73d15362; __fp=fp; __vid=1645850350.1538037802694; __tsid=262473610; __vsr=1538037802694.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; _ppdaiWaterMark=15380378038784; token=7fd38432594dfea0e1aa6a7ef7093f572c179a40ebe342fdec8dc65925247fe04d5706da6c0af32a1e; __eui=Cel3wwogQQUMvl7O%2BveuJQ%3D%3D; openid=cdda7ce1e0bcfdaa2503c4f0770aabe4; ppd_uname=pdu8953799660; __sid=1538037802694.2.1538037823590; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221661a326502475-0110ff68c516d2-333b5402-2304000-1661a326503798%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%2C%22first_id%22%3A%221661a326502475-0110ff68c516d2-333b5402-2304000-1661a326503798%22%7D; waterMarkTimeCheck1=09%2F27%2F2018+16%3A43%3A44; aliyungf_tc=AQAAAGOw5FmQxgsAjlD3PJGuYPXBmXHv; JSESSIONID=A79FBA20C193E347BC54379567574FE3",
        }

    def update_cookies(self, cookies):
        self.cookies = cookies
        self.headers["Cookie"] = self.cookies

    @staticmethod
    def change_key(item):
        key_dict = {}
        key_dict["listingId"] = "listingId"
        key_dict["creationDate"] = "creationDate"
        key_dict["User"] = "User"
        key_dict["title"] = "title"

        key_dict["amount"] = "借款金额"
        key_dict["creditCode"] = "级别"
        key_dict["showRate"] = "协议利率"  # currentRate
        key_dict["months"] = "期限"
        key_dict["loanUse"] = "借款用途"

        # show borrow info
        key_dict["gender"] = "性别"
        key_dict["age"] = "年龄"
        key_dict["income"] = "收入情况"
        key_dict["repaymentSourceType"] = "还款来源"
        key_dict["workInfo"] = "工作信息"
        key_dict["registerDateStr"] = "注册时间"
        key_dict["graduate"] = "毕业院校"
        key_dict["educationDegree"] = "文化程度"
        key_dict["studyStyle"] = "学习形式"
        key_dict["balAmount"] = "网络借贷平台借款余额"

        #
        key_dict["owingAmount"] = "待还金额"
        key_dict["overdueLessNum"] = "逾期（0-15天）还清次数"
        key_dict["overdueMoreNum"] = "逾期（15天以上）还清次数"

        key_dict["firstSuccessDate"] = "第一次成功借款时间"
        key_dict["totalPrincipal"] = "累计借款金额"

        key_dict["successNum"] = "成功借款次数"
        key_dict["normalNum"] = "正常还清次数"

        key_dict["debtAmountMax"] = "历史最高负债"
        key_dict["loanAmountMax"] = "单笔最高借款金额"

        key_dict["EducationDegree"] = "文化程度"
        key_dict["GraduateSchool"] = "毕业院校"
        key_dict["StudyStyle"] = "学习形式"
        new_item = {}
        for key, value in key_dict.items():
            if key not in item:
                continue

            new_item[value] = item[key]
            # if key == "Gender":
            #     if item[value] == 2:
            #         item[value] = "女"
            #     elif item[value] == 1:
            #         item[value] = "男"
            #     else:
            #         raise ValueError(f"does not know geder value {item}")
            # elif key == "EducationDegree":
            #     if item[value] is None:
            #         item[value] = "无"

        if "正常还清次数" in new_item and "逾期（0-15天）还清次数" in new_item and "逾期（15天以上）还清次数" in new_item:
            new_item["成功还款次数"] = new_item["正常还清次数"] + new_item["逾期（0-15天）还清次数"] + new_item["逾期（15天以上）还清次数"]
        return new_item

    async def post_data(self, url, data, headers):
        post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        async with ClientSession(headers=headers) as session:
            self.logger.debug(f"{url}, post, {post_data}")
            async with session.post(url, data=post_data) as response:
                response = await response.read()
                return response

    async def get_show_listing_base_info(self, listing_id: int):
        self.headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(listing_id)
        file_path = f"..\\data\\showListingBaseInfo\\showListingBaseInfo_{listing_id}.json"
        url = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showListingBaseInfo"
        data = {
            "listingId": str(listing_id),
            "source": 1}

        # if os.path.exists(file_path):
        #     self.logger.info("get_show_listing_base_info from file")
        #     with open(file_path, "r", encoding="utf-8") as f:
        #         result = f.read()
        #         json_data = json.loads(result)
        # else:
        result = await self.post_data(url, data, self.headers)
        json_data = json.loads(result)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(json_data, indent=4, ensure_ascii=False))

        result_code = json_data.get("result", -999)
        if result_code != 1:
            self.logger.warning(f"get_show_listing_base_info f{listing_id}: return f{json_data}")

            if result_code == 1012:
                raise PpdNeedSleepException
            return None

        base_info = json_data["resultContent"]["listing"]
        base_info["loanUse"] = json_data["resultContent"]["loanUse"]
        base_info["User"] = json_data["resultContent"]["userInfo"]["userName"]
        return base_info

    async def get_show_borrower_info(self, listing_id: int):
        self.headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(listing_id)
        file_path = f"..\\data\\showBorrowerInfo\\showBorrowerInfo_{listing_id}.json"
        url = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showBorrowerInfo"
        data = {
            "listingId": str(listing_id),
            "source": 1}

        # if os.path.exists(file_path):
        #     self.logger.info("get_show_borrower_info from file")
        #     with open(file_path, "r", encoding="utf-8") as f:
        #         result = f.read()
        #         json_data = json.loads(result)
        # else:
        result = await self.post_data(url, data, self.headers)

        json_data = json.loads(result)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(json_data, indent=4, ensure_ascii=False))

        result_code = json_data.get("result", -999)
        if result_code != 1:
            self.logger.warning(f"get_show_borrower_info f{listing_id}: return f{json_data}")

            if result_code == 1012:
                raise PpdNeedSleepException

        borrower_info = json_data["resultContent"]
        borrower_info["listingId"] = listing_id

        if "userAuthsList" in borrower_info:
            for item in borrower_info["userAuthsList"]:
                borrower_info[item["name"]] = True

        education_info = borrower_info.get("educationInfo")
        if education_info:
            for edu_name, edu_value in education_info.items():
                borrower_info[edu_name] = edu_value
        else:
            borrower_info["EducationDegree"] = "无"
            borrower_info["GraduateSchool"] = "无"
            borrower_info["StudyStyle"] = "无"

        return borrower_info

    async def get_borrower_statistics(self, listing_id: int, use_cache=False):
        self.headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(listing_id)
        file_path = f"..\\data\\showBorrowerStatistics\\showBorrowerStatistics_{listing_id}.json"
        url = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showBorrowerStatistics"
        data = {
            "listingId": str(listing_id),
            "source": 1}

        if use_cache and os.path.exists(file_path):
            # self.logger.info("get_borrower_statistics from file")
            with open(file_path, "r", encoding="utf-8") as f:
                result = f.read()
                json_data = json.loads(result)
        else:
            result = await self.post_data(url, data, self.headers)
            # self.logger.info(f"{listing_id}, {result}")
            json_data = json.loads(result)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(json_data, indent=4, ensure_ascii=False))

        result_code = json_data.get("result", -999)
        if result_code != 1:
            self.logger.warning(f"get_show_borrower_info f{listing_id}: return f{json_data}")

            if result_code == 1012:
                raise PpdNeedSleepException

        if "loanerStatistics" not in json_data["resultContent"]:
            self.logger.warning(f"Can not get_borrower_statistics {listing_id}")
            return {"listingId": listing_id}

        borrower_statistics = json_data["resultContent"]["loanerStatistics"]

        if "listingStatics" in borrower_statistics:
            borrower_statistics["successNum"] = borrower_statistics["listingStatics"].get("successNum", 0)
        else:
            borrower_statistics["successNum"] = 0

        if "firstSuccessDate" in borrower_statistics["listingStatics"]:
            borrower_statistics["firstSuccessDate"] = borrower_statistics["listingStatics"]["firstSuccessDate"]
        else:
            borrower_statistics["firstSuccessDate"] = None
        borrower_statistics["listingId"] = listing_id

        return borrower_statistics

    def get_detail_info(self, listing_id: int):
        item = None
        try:
            tasks = []
            loop = asyncio.get_event_loop()

            task = asyncio.ensure_future(self.get_show_listing_base_info(listing_id))
            tasks.append(task)

            task = asyncio.ensure_future(self.get_show_borrower_info(listing_id))
            tasks.append(task)

            task = asyncio.ensure_future(self.get_borrower_statistics(listing_id))
            tasks.append(task)

            json_data = loop.run_until_complete(asyncio.gather(*tasks))

            if len(json_data) != 3:
                self.logger.warning(json.dumps(json_data, ensure_ascii=False))
            elif "debtAmountMax" in json_data[2]:
                item = self.change_key({**json_data[0], **json_data[1], **json_data[2]})

                if item["正常还清次数"] >= 30:
                    self.logger.info(json.dumps(item, indent=4,  ensure_ascii=False))
                else:
                    self.logger.info(f"{item['listingId']}: {item['级别']} {item['期限']} normal account {item['正常还清次数']}")
            # else:
            #     self.logger.info(f"get_detail_info data loose {json.dumps(json_data, indent=4,  ensure_ascii=False)}")
        except PpdNeedSleepException:
            raise
        except PpdResultContentNullException:
            self.logger.warning(f"can not get {listing_id} detail info:")
        except Exception as ex:
            self.logger.error(f"get {listing_id} detail info: {ex}", exc_info=True)

        return item

    def batch_get_detail_infs(self, listing_ids: list):
        if not listing_ids:
            return []

        item_list = []
        try:
            tasks = []
            loop = asyncio.get_event_loop()

            for listing_id in listing_ids:
                task = asyncio.ensure_future(self.get_show_listing_base_info(listing_id))
                tasks.append(task)

                task = asyncio.ensure_future(self.get_show_borrower_info(listing_id))
                tasks.append(task)

                task = asyncio.ensure_future(self.get_borrower_statistics(listing_id))
                tasks.append(task)

            json_data = loop.run_until_complete(asyncio.gather(*tasks))
            json_data.sort(key=lambda content: content['listingId'])
            groups = groupby(json_data, lambda content: content['listingId'])
            for listing_id, group in groups:
                group = list(group)
                if len(group) != 3:
                    self.logger.warning(json.dumps(group, ensure_ascii=False))
                else:
                    if "debtAmountMax" in group[2]:
                        item = self.change_key({**group[0], **group[1], **group[2]})
                        item_list.append(item)

                        if item["正常还清次数"] >= 30:
                            self.logger.info(json.dumps(item, indent=4, ensure_ascii=False))
                        else:
                            self.logger.info(f"{item['listingId']}: {item['级别']} {item['期限']} normal account {item['正常还清次数']}")
        except PpdNeedSleepException:
            raise
        except PpdResultContentNullException:
            self.logger.warning(f"can not get {listing_ids} detail info:")
        except Exception as ex:
            self.logger.error(f"get {listing_ids} detail info: {ex}", exc_info=True)

        return item_list

    def batch_get_show_borrower_info(self, listing_ids: list):
        item_list = []
        try:
            tasks = []
            loop = asyncio.get_event_loop()

            for listing_id in listing_ids:
                task = asyncio.ensure_future(self.get_show_borrower_info(listing_id))
                tasks.append(task)

            json_data = loop.run_until_complete(asyncio.gather(*tasks))

            for item in json_data:
                item = self.change_key(item)
                item_list.append(item)
            return item_list
        except PpdNeedSleepException:
            raise
        except PpdResultContentNullException:
            self.logger.warning(f"can not get {listing_ids} borrower_statistics:")
        except Exception as ex:
            self.logger.error(f"get {listing_ids} borrower_statistics: {ex}", exc_info=True)

        return item_list
        pass

    def check_bid_number(self, item):
        # loan_amount = Utils.convert_to_int(item["借款金额"])
        loan_amount = item["借款金额"]
        headers = self.headers
        headers["Referer"] = f"https://invest.ppdai.com/loan/listpage/?risk=1&mirror=3&pageIndex=1&times=3&period=2&auth=&money={loan_amount},{loan_amount}"
        url = "https://invest.ppdai.com/api/invapi/ListingListAuthService/listingPagerAuth"

        data = {
            "authInfo": "",
            "authenticated": False,
            "availableBalance": 0,
            "creditCodes": "3",
            "dataList": [],
            "didIBid": "1",
            "maxAmount": 6000,
            "minAmount": 5000,
            "months": "2",
            "needTotalCount": True,
            "pageCount": 0,
            "pageIndex": 1,
            "pageSize": 10,
            "rates": "",
            "riskLevelCategory": "1",
            "sort": 0,
            "source": 1,
            "successLoanNum": "3",
            "totalCount": 1
        }

        data["minAmount"] = loan_amount
        data["maxAmount"] = loan_amount

        # month = Utils.convert_to_int(item["期限"])
        month = item["期限"]
        if month == 3:
            bid_month_type = 1
        elif month == 6:
            bid_month_type = 2
        elif month == 12:
            bid_month_type = 4
        else:
            raise ValueError(f"Unknown month type for bid sim: {month}")

        credit_codes = item["级别"]
        if credit_codes == "B":
            data["creditCodes"] = "3"
        elif credit_codes == "C":
            data["creditCodes"] = "4"
        elif credit_codes == "A":
            data["creditCodes"] = "2"
        else:
            raise ValueError(f"Unsupported creditCodes for bid sim: {month}")

        data["months"] = bid_month_type

        post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        session = requests.Session()
        req = session.post(url, data=post_data, headers=headers)
        result = req.text

        try:
            json_data = json.loads(result)
            listing_id = item['listingId']

            if json_data.get("result", -999) != 1 or "resultContent" not in json_data or "dataList" not in json_data["resultContent"]:
                self.logger.warning(f"check_bid_number {listing_id}: {json.dumps(result, ensure_ascii=False)}")
                if json_data.get("result") == 1012:
                    raise PpdNeedSleepException
                return False

            data_list = json_data["resultContent"]["dataList"]
            not_full_list = data_list
            if len(data_list) != 1:
                not_full_list = [item for item in data_list if item["amount"] > item["funding"]]
                if len(not_full_list) != 1:
                    self.logger.warning(f"check_bid_number {listing_id} {loan_amount} count = {len(not_full_list)},{len(data_list)}: {json.dumps(not_full_list, ensure_ascii=False)}")
                    return False

            verify_item = not_full_list[0]
            if verify_item["listingId"] != int(item["listingId"]):
                self.logger.warning(f"check_bid_number {listing_id} listing id changed: {json.dumps(result, ensure_ascii=False)}")
                return False

            self.logger.info(f"check bid number: {item['listingId']}, {loan_amount}, {len(not_full_list)},{len(data_list)}")
            return True
        except PpdNeedSleepException:
            raise PpdNeedSleepException
        except Exception as ex:
            self.logger.error(f"check_bid_number {ex} {result}", exc_info=True)

        return False

    # {"result": 1006, "resultMessage": "余额不足"}
    def bid_by_request(self, item):
        headers = self.headers
        headers["Referer"] = "https://invest.ppdai.com/loan/listpage/?risk=1&mirror=&pageIndex=1&period=&sex=male&money=,&times=&auth=&rate="
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
                "bids": 5,
                "borrowerName": "pdu0****77408",
                "certificateValidate": 0,
                "creditCode": "B",
                "creditValidate": 0,
                "currentRate": 20,
                "funding": 14,
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
            "months": "2",
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
            "sigleBidAmount": 52,
            "bidCount": 1,
            "useCoupon": True
        }

        data["maxAmount"] = loan_amount
        data["minAmount"] = loan_amount
        # month = Utils.convert_to_int(item["期限"])
        month = item["期限"]
        if month == 3:
            bid_month_type = 1
        elif month == 6:
            bid_month_type = 2
        elif month == 12:
            bid_month_type = 4
        else:
            raise ValueError(f"Unknown month type for bid sim: {month}")

        credit_codes = item["级别"]
        if credit_codes == "B":
            data["creditCodes"] = "3"
        elif credit_codes == "C":
            data["creditCodes"] = "4"
        elif credit_codes == "A":
            data["creditCodes"] = "2"
        else:
            raise ValueError(f"Unsupported creditCodes for bid sim: {month}")

        data["ip"] = "60.247.80.142"  # 60.247.80.142   work    ;      101.41.247.234  hone
        data["riskLevelCategory"] = 1  # 0:  保守； 1:平衡  2：进取
        data["months"] = bid_month_type

        data_item = data["dataList"][0]
        data_item["listingId"] = item["listingId"]
        data_item["amount"] = loan_amount
        data_item["borrowerName"] = item["User"]
        data_item["creditCode"] = item["级别"]
        data_item["months"] = month

        title = item.get("title")
        if title:
            data_item["title"] = title
        # data_item["bids"] = Utils.convert_to_int(item["投标人数"])
        # data_item["funding"] = Utils.convert_to_int(item["进度"]) * loan_amount / 100
        data_item["currentRate"] = Utils.convert_to_int(item["协议利率"])
        # post_data = '{"authInfo":"","authenticated":true,"availableBalance":279.08,"bidStatusDTOs":[],"creditCodes":"3","dataList":[{"bidNum":100,"bidStatusDTO":null,"amount":17400,"bids":233,"borrowerName":"pdu0****77408","certificateValidate":0,"creditCode":"B","creditValidate":1,"currentRate":20,"funding":16484,"isPay":false,"listingId":125233286,"mobileRealnameValidate":1,"months":12,"nCIICIdentityCheck":0,"statusId":1,"title":"手机app用户的第17次闪电借款"}],"didIBid":"1","ip":"101.41.247.234","maxAmount":17400,"minAmount":17400,"months":"1,2,3,4","needTotalCount":true,"pageCount":1,"pageIndex":1,"pageSize":10,"rates":"","riskLevelCategory":1,"sort":0,"source":1,"successLoanNum":"3","totalCount":1,"userId":87288708,"sigleBidAmount":50,"bidCount":1,"useCoupon":true}'

        post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        # logger.info(f"bid by request: {post_data}")

        session = requests.Session()
        req = session.post(url, data=post_data, headers=headers)
        result = req.text

        json_data = json.loads(result)
        listing_id = item['listingId']
        result_code = json_data.get("result", -999)

        if result_code == -999:
            self.logger.warning(f"bid by request result error {listing_id}: {result}")
            return False
        elif result_code == 1006:
            self.logger.warning(f"bid by request not enough money {listing_id}: {result}")
            raise PpdNotEnoughMoneyException
            return False

        if json_data["result"] != 1:
            self.logger.info(f"bid by request result {listing_id}: {req.text}")
            return False

        self.logger.info(f"bid by request result {listing_id}: {req.text}")
        return True
        pass

    def listing_pager_auth(self, page_index=1):
        headers = self.headers
        headers["Referer"] = f"https://invest.ppdai.com/loan/listpage/?risk=1&mirror=&pageIndex=1&showMore=1&period=1,2&times=3"
        headers["Accept"] = "application/json, text/plain, */*"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Accept-Language"] = "en-US,en;q=0.9"
        headers["Content-Length"] = "301"
        headers["Content-Type"] = "application/json;charset=UTF-8"
        headers["Connection"] = "keep-alive"
        headers["Host"] = "invest.ppdai.com"
        headers["Origin"] = "https: // invest.ppdai.com"
        url = "https://invest.ppdai.com/api/invapi/ListingListAuthService/listingPagerAuth"

        data = {
            "authInfo": "",
            "authenticated": False,
            "availableBalance": 0,
            "creditCodes": "",
            "dataList": [],
            "didIBid": "1",    #仅显末投
            "maxAmount": 0,
            "minAmount": 0,
            "months": "1, 2",   # 1 = 3月，   2=6月
            "needTotalCount": True,
            "pageCount": 0,
            "pageIndex": page_index,
            "pageSize": 10,
            "rates": "",
            "riskLevelCategory": "1",     # 1: 平衡型
            "sort": 0,
            "source": 1,
            "successLoanNum": "3",       # 成功借款次数   3: > 6次
            "totalCount": 0
        }

        post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        session = requests.Session()
        self.logger.info(post_data)
        req = session.post(url, data=post_data, headers=headers)
        result = req.text

        try:
            self.logger.info(result)
            json_data = json.loads(result)

            if json_data.get("result", -999) != 1 or "resultContent" not in json_data or "dataList" not in \
                    json_data["resultContent"]:
                self.logger.warning(f"get list: {json.dumps(result, ensure_ascii=False)}")
                if json_data.get("result") == 1012:
                    raise PpdNeedSleepException
                return []

            data_list = json_data["resultContent"]["dataList"]
            not_full_list = [item["listingId"] for item in data_list if item["amount"] > item["funding"]]
            return not_full_list
        except PpdNeedSleepException:
            raise PpdNeedSleepException
        except Exception as ex:
            self.logger.error(f"check_bid_number {ex} {result}", exc_info=True)

        return []

    # def __pre_apply(self, data):
    #     url = "https://invdebt.ppdai.com/Negotiable/preApply"
    #     headers = self.headers
    #     headers["Host"] = "invdebt.ppdai.com"
    #     headers["Origin"] = "https://invdebt.ppdai.com"
    #     headers[
    #         "Referer"] = "https://invdebt.ppdai.com/negotiable/apply?owingNumber=&Sort=&level=%2C&dueDay=&minPrincipal=&maxPrincipal=&Rate="
    #     headers["Cookie"] = "gr_user_id=11f8ea81-90aa-4c3e-a041-71c51c28ea51; uniqueid=747711b0-faee-473f-96e7-a488248ded5f; __fp=fp; __vid=3407234.1530775507276; _ppdaiWaterMark=15312861763999; _ga=GA1.2.1098278737.1530780657; ppdaiRole=8; openid=cdda7ce1e0bcfdaa2503c4f0770aabe4; ppd_uname=pdu8953799660; __utma=1.1098278737.1530780657.1537521814.1537844264.44; __utmz=1.1537844264.44.44.utmcsr=tz.ppdai.com|utmccn=(referral)|utmcmd=referral|utmcct=/investment-record/black-list; registerurl=https%3A%2F%2Fpay.ppdai.com%2Fdeposit%2Fprocessing%3Ftradeid%3D180925064000088903; registersourceurl=https%3A%2F%2Fppdai.cloud.cmbchina.com%2Frecharge%3Fsecret%3Duk1g%252biiu7tt00un1wddj1pecynqmvolok10tfxjv%252bsr0bvxfper%252bgrn3td7d3k3laz9tsjtuutva%252fyngsrscmze6c6m6nqtj5ufk5lx2pojvdwpfonod1zgditv5ehljjyxbvxjhuufqaz50o6zlv3oody57k7sojgmtmr5fjkhmafq5u6vbcqxhgzbr9hq2locwkazfzrbptptqvv02fecslnjehnpautnegau%252bcvqg0npcadupre54jeyolwqzf7ncz83ewwxb%252fsm%252bgv4fhv51vr%252b6qvx%252b7upuv6zfqghshyd6fnubj1yesytrx6xrezdkub2odexsc9qiz2rdqd0qi%252bqcforpgy6%252btyy3%252f%252bt%252balnrhz8fiv8chwx8ld0a10xogvudq4h%252filshktwz0t%252fnbise7i5dgsmvxis9orl4s0v%252bwkklmaq1i0s9se01mw9h5jg58hvxy%252bpbycej3hp7chqdfhwg%252bncxfn%252bbafcu5ehvgx%252fn4%252fizbee2x1jdahtshkqtelmrwoazzba8luzsvi0hty2nxklynjswqsg4vibvmx4urzim9t%252f%252begr%252fs9c5yizcdq%252f3m2wkncyw5iqk2vs3%252bqf%252bxsxei37oeyu7u0ayjxxr7ikeezguoofllynhsbwz%252bzkpqzhtfuo%252fmz%252byah3p5ix6f8xa1zmnlte%253d; Hm_lvt_aab1030ecb68cd7b5c613bd7a5127a40=1537154152,1537521815,1537521846,1537844293; regSourceId=0; referID=0; fromUrl=https%3A%2F%2Fwww.ppdai.com%2Fmoneyhistory; referDate=2018-10-8%2010%3A44%3A40; noticeflag=true; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22first_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; __vsr=1539655504772.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1539666456849.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1539669411885.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1539673759471.refSite%3Dhttps%3A//www.ppdai.com/moneyhistory%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1539743507367.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1537339527,1539574208,1539743508; token=7cddd068594dfea0e1aa6a7ef7093f57ee79fa9d6e9794d11b3fccbc93ade9d562e9cc5d2585d06db2; __eui=Cel3wwogQQUMvl7O%2BveuJQ%3D%3D; __tsid=262473610; aliyungf_tc=AQAAAG4qv2/EfwMAjlD3PL+lxOxQtKu6; gr_session_id_b9598a05ad0393b9=87c7c5fc-b6d9-4d78-b3f9-972523611b95; gr_session_id_b9598a05ad0393b9_87c7c5fc-b6d9-4d78-b3f9-972523611b95=true; currentUrl=https%3A%2F%2Finvdebt.ppdai.com%2Fnegotiable%2Fapply%3Fowingnumber%3D%26sort%3D%26level%3D%252c%26dueday%3D%26minprincipal%3D%26maxprincipal%3D%26rate%3D; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1539849287; __sid=1539846609728.16.1539849286928; waterMarkTimeCheck1=10%2F18%2F2018+15%3A54%3A48"
    #     headers["X-Requested-With"] = "XMLHttpRequest"
    #     headers["Content-Type"] = "application/x-www-form-urlencoded"
    #     headers["Connection"] = "keep-alive"
    #
    #     session = requests.Session()
    #     req = session.post(url, data=data, headers=headers)
    #     result = req.text
    #     return result
    #
    # def pre_apply(self, listing_id):
    #     data = [{"listingId": listing_id, "preDebtdealId": 0, "saleRate": 0}]
    #     post_data = json.dumps(data, ensure_ascii=True)
    #     data = "jsondata=" + post_data
    #     return self.__pre_apply(data)
    #
    # def pre_apply_list(self, listing_ids):
    #     data = []
    #     for listing_id in listing_ids:
    #         data_item = {"listingId": listing_id, "preDebtdealId": 0, "saleRate": 0}
    #         data.append(data_item)
    #
    #     post_data = json.dumps(data, ensure_ascii=True)
    #     data = "jsondata=" + post_data
    #     return self.__pre_apply(data)
    #     pass

    def pre_apply_debt(self, data, cookies):
        url = "https://transfer.ppdai.com/api/debt/pcApplyDebtService/preApplyDebt"
        headers = self.headers
        headers["Host"] = "transfer.ppdai.com"
        headers["Origin"] = "https://transfer.ppdai.com"
        headers[
            "Referer"] = "https://transfer.ppdai.com/menu/negotiable/applyNew"
        headers["Cookie"] = cookies
        # headers["X-Requested-With"] = "XMLHttpRequest"
        headers["Content-Type"] = "application/json;charset=UTF-8"
        headers["Connection"] = "keep-alive"

        session = requests.Session()
        req = session.post(url, data=data, headers=headers)
        result = req.text
        return result

    def pre_apply_debt_list(self, listing_ids, cookies):

        items = []
        for index in range(0, len(listing_ids), 30):
            sub_listing_ids = listing_ids[index:index + 30]
            data = []
            for listing_id in sub_listing_ids:
                data_item = {"listingId": listing_id, "preDebtDealId": 0, "saleRate": 0, "priceForSale": None}
                data.append(data_item)

            post_data = {"dueType": 1, "preApplyRequestList": data}
            post_data = json.dumps(post_data, ensure_ascii=True)
            print(post_data)
            result = self.pre_apply_debt(post_data, cookies)
            print(result)
            json_data = json.loads(result)
            items.extend(json_data["resultContent"]["items"])
            time.sleep(1)

        return items
        pass

    # creditCode: "B"
    # currentDueDay: -1
    # currentRate: 20
    # isPay: false
    # leftRepayDay: 1
    # listingId: 125553141
    # nextRepayDate: "2018-11-20 05:35:36"
    # number: 6
    # owingInterest: 1.41
    # owingNumber: 4
    # owingPrincipal: 33.89
    # pastDueDay: 0
    # pastDueNumber: 0
    # preDebtdealId: 0
    # priceForSale: 33.89
    # rateMaxMultiples: 2
    # rateMinMultiples: 1
    # valuation: 0.943
    # vouch: 0
    def get_apply_list(self, page_index=1):
        url = "https://transfer.ppdai.com/api/debt/pcApplyDebtService/getApplyList"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive",
            "Cookie": "gr_user_id=11f8ea81-90aa-4c3e-a041-71c51c28ea51; uniqueid=747711b0-faee-473f-96e7-a488248ded5f; __fp=fp; __vid=3407234.1530775507276; _ppdaiWaterMark=15312861763999; _ga=GA1.2.1098278737.1530780657; ppdaiRole=8; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1539574208,1539743508; __utmc=1; token=2c8a8463594dfea0e1aa6a7ef7093f57250c226cb354666c78c0d00f64f06067ba05c0ccf2fcae2ca9; __utma=1.1098278737.1530780657.1540786794.1540874893.54; __utmz=1.1540874893.54.54.utmcsr=ppdai.com|utmccn=(referral)|utmcmd=referral|utmcct=/moneyhistory; registerurl=https%3A%2F%2Fpay.ppdai.com%2Fdeposit%2Fprocessing%3Ftradeid%3D181030064000097721; registersourceurl=https%3A%2F%2Fppdai.cloud.cmbchina.com%2Frecharge%3Fsecret%3Dg%252fxkxwv6c3pdlrotntqbgqbeel5%252b92jeasbngsgvhnpq6%252f30pvltbim1yuh7oaz77vptulgyriiqgcthx35992pdfgqfbpfthcqw7eo1eluv8ocoi%252bll96ksxz60eem4tcpa22djtij4oyuqoa3sbpmpghdrqvdonme%252bfkpbm3nfbhxlaivwusi2ctp4xzvutl8wyzk9tieiaythr3zmp6vb08jo0la8p4gpqlfioftldgqxuz3l0dvlftlzejpxssourvhb4lxfwbtsy0ltmuq4jevwjpee7jq6cvjutmztp00sp8ry3gmv96zdsb%252fz6k%252fqt%252baw6n%252bepaehqvpc8uhwpfzzao9faoyyjpuaggzgdoan%252bkxw3uc9eqlzuxvk7n0%252beg0iqxr4aqeu8am74bddo78q7wjl6wm%252fhhp8o%252bjxwrduveo09x7daq3%252fh2bda%252ff0nwd93%252bryatpzeo%252bcxmlgtsqlgfarqh6ih6cse6atcczgqnsdzxg5%252ba6te5exic74y84ehte9dhvp9xr91e1%252bpbdh8pttv%252ft8mqfohjbofsiyo6y%252banqlp8tlcb39txpsrr7wsbsu2bku4tysv0b2k3pklxrxv66yzzoacigm8bnfvgk1nzm%252fjgq9knky0snjrc438dvsdo61x2%252bnaavqqcxqn0mtlvelfkbuvvw%253d; Hm_lvt_aab1030ecb68cd7b5c613bd7a5127a40=1540535505,1540536242,1540786823,1540874918; Hm_lpvt_aab1030ecb68cd7b5c613bd7a5127a40=1540874920; currentUrl=https%3A%2F%2Finvdebt.ppdai.com%2Fnegotiable%2Fapply%3Fowingnumber%3D1%2C%26sort%3D7%26level%3D%2Cb%2C%26dueday%3D%26minprincipal%3D%26maxprincipal%3D%26rate%3D%26pageindex%3D6; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1541145692; aliyungf_tc=AQAAAMf723JYfgMAjlD3PKjIVYIDUr25; __tsid=262473610; __vsr=1542261464583.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1542268940861.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1542273821464.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1542347916369.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1542354647298.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22first_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; __sid=1542594735580.3.1542595509946; waterMarkTimeCheck1=11%2F19%2F2018+10%3A45%3A11",
            "Host": "transfer.ppdai.com",
            "Origin": "https://transfer.ppdai.com",
            "Referer": "https://transfer.ppdai.com/menu/negotiable/applyNew",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Length": "193",
            "Content-Type": "application/json;charset=UTF-8",
        }

        headers["Cookie"] = self.cookies
        data = {"dueType":1,"pageIndex":page_index,"pageSize":30,"rate":"","minPrincipal":"","maxPrincipal":"","sort":7,"owingNumberList":None,"dueDayList":None,"levelList":["A","B","C","D","E"],"overDueDayList":None}

        post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        session = requests.Session()
        self.logger.info(post_data)
        req = session.post(url, data=post_data, headers=headers)
        result = req.text

        try:
            self.logger.info(result)
            json_data = json.loads(result)

            if json_data.get("result", -999) != 1 or "resultContent" not in json_data or "items" not in \
                    json_data["resultContent"]:
                self.logger.warning(f"get_apply_list: {json.dumps(result, ensure_ascii=False)}")
                if json_data.get("result") == 1012:
                    raise PpdNeedSleepException
                return []

            data_list = json_data["resultContent"]["items"]
            return data_list
        except PpdNeedSleepException:
            raise PpdNeedSleepException
        except Exception as ex:
            self.logger.error(f"{ex} {result}", exc_info=True)

        return []


    async def aio_bid(self, item):

        pass

def main():
    # tasks = []
    # loop = asyncio.get_event_loop()
    #
    # logger.info("start send")
    id = 129722056

    cookies = "gr_user_id=11f8ea81-90aa-4c3e-a041-71c51c28ea51; uniqueid=747711b0-faee-473f-96e7-a488248ded5f; __fp=fp; __vid=3407234.1530775507276; _ppdaiWaterMark=15312861763999; _ga=GA1.2.1098278737.1530780657; ppdaiRole=8; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1539574208,1539743508; __utmc=1; token=2c8a8463594dfea0e1aa6a7ef7093f57250c226cb354666c78c0d00f64f06067ba05c0ccf2fcae2ca9; __utma=1.1098278737.1530780657.1540786794.1540874893.54; __utmz=1.1540874893.54.54.utmcsr=ppdai.com|utmccn=(referral)|utmcmd=referral|utmcct=/moneyhistory; registerurl=https%3A%2F%2Fpay.ppdai.com%2Fdeposit%2Fprocessing%3Ftradeid%3D181030064000097721; registersourceurl=https%3A%2F%2Fppdai.cloud.cmbchina.com%2Frecharge%3Fsecret%3Dg%252fxkxwv6c3pdlrotntqbgqbeel5%252b92jeasbngsgvhnpq6%252f30pvltbim1yuh7oaz77vptulgyriiqgcthx35992pdfgqfbpfthcqw7eo1eluv8ocoi%252bll96ksxz60eem4tcpa22djtij4oyuqoa3sbpmpghdrqvdonme%252bfkpbm3nfbhxlaivwusi2ctp4xzvutl8wyzk9tieiaythr3zmp6vb08jo0la8p4gpqlfioftldgqxuz3l0dvlftlzejpxssourvhb4lxfwbtsy0ltmuq4jevwjpee7jq6cvjutmztp00sp8ry3gmv96zdsb%252fz6k%252fqt%252baw6n%252bepaehqvpc8uhwpfzzao9faoyyjpuaggzgdoan%252bkxw3uc9eqlzuxvk7n0%252beg0iqxr4aqeu8am74bddo78q7wjl6wm%252fhhp8o%252bjxwrduveo09x7daq3%252fh2bda%252ff0nwd93%252bryatpzeo%252bcxmlgtsqlgfarqh6ih6cse6atcczgqnsdzxg5%252ba6te5exic74y84ehte9dhvp9xr91e1%252bpbdh8pttv%252ft8mqfohjbofsiyo6y%252banqlp8tlcb39txpsrr7wsbsu2bku4tysv0b2k3pklxrxv66yzzoacigm8bnfvgk1nzm%252fjgq9knky0snjrc438dvsdo61x2%252bnaavqqcxqn0mtlvelfkbuvvw%253d; Hm_lvt_aab1030ecb68cd7b5c613bd7a5127a40=1540535505,1540536242,1540786823,1540874918; Hm_lpvt_aab1030ecb68cd7b5c613bd7a5127a40=1540874920; currentUrl=https%3A%2F%2Finvdebt.ppdai.com%2Fnegotiable%2Fapply%3Fowingnumber%3D1%2C%26sort%3D7%26level%3D%2Cb%2C%26dueday%3D%26minprincipal%3D%26maxprincipal%3D%26rate%3D%26pageindex%3D6; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1541145692; aliyungf_tc=AQAAAMf723JYfgMAjlD3PKjIVYIDUr25; __tsid=262473610; __vsr=1542261464583.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1542268940861.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1542273821464.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1542347916369.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1542354647298.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22first_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; __sid=1542594735580.3.1542595509946; waterMarkTimeCheck1=11%2F19%2F2018+10%3A45%3A11"
    client = PpdUISimulationRequest(cookies=cookies)
    # json_data = client.get_detail_info(129854214)
    # json_data = client.batch_get_detail_infs([129722481, 129722781])
    # for item in client.batch_get_show_borrower_info([id, 128080987]):
    #     logger.info(json.dumps(client.change_key(item), ensure_ascii=False))
    # logger.info(json.dumps(json_data, ensure_ascii=False))
    # task = asyncio.ensure_future(client.get_show_listing_base_info(id))
    # tasks.append(task)
    #
    # logger.info("start send")
    # task = asyncio.ensure_future(client.get_show_borrower_info(id))
    # tasks.append(task)
    #
    # logger.info("start send")
    # task = asyncio.ensure_future(client.get_borrower_statistics(id))
    # tasks.append(task)
    #
    # logger.info("finish send")
    # result = loop.run_until_complete(asyncio.gather(*tasks))
    # logger.info("wait result")
    # print(json.dumps(result, ensure_ascii=False))
    # print(result)

    # data = {"dueType": 1,"preApplyRequestList":[{"listingId":125339395,"preDebtDealId":0,"saleRate":0,"priceForSale":None}, {"listingId":125321081,"preDebtDealId":0,"saleRate":0,"priceForSale":None}]}
    # print(client.pre_apply_debt(json.dumps(data)))

    # print(client.listing_pager_auth(1))

    print(client.get_apply_list())

if __name__ == '__main__':
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=10, format=logging_format)
    logger = logging.getLogger(__name__)
    main()
