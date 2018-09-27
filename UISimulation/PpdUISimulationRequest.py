import logging
import asyncio
from aiohttp import ClientSession
import json
import requests
import os
from itertools import groupby
from Common import Utils


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
            "Cookie": "uniqueid=2b2b3af5-1115-40e0-a5df-eb96f36181e7; __fp=fp; __vid=496486763.1537346573967; __tsid=262473610; __vsr=1537346573967.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; _ppdaiWaterMark=15373465751035; openid=cdda7ce1e0bcfdaa2503c4f0770aabe4; ppd_uname=pdu8953799660; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%22165f0ff1435204-073bf4f2bb391e-333b5402-2304000-165f0ff1436b4%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%2C%22first_id%22%3A%22165f0ff1435204-073bf4f2bb391e-333b5402-2304000-165f0ff1436b4%22%7D; aliyungf_tc=AQAAAMa01xmjMQ8AjlD3PHgGNLZUbaEJ; JSESSIONID=0F59401BE18E2676499EFF68CA9ED547",
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

        if "educationInfo" in borrower_info:
            for edu_name, edu_value in borrower_info["educationInfo"].items():
                borrower_info[edu_name] = edu_value
        else:
            borrower_info["EducationDegree"] = "无"
            borrower_info["GraduateSchool"] = "无"
            borrower_info["StudyStyle"] = "无"

        return borrower_info

    async def get_borrower_statistics(self, listing_id: int):
        self.headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(listing_id)
        file_path = f"..\\data\\showBorrowerStatistics\\showBorrowerStatistics_{listing_id}.json"
        url = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showBorrowerStatistics"
        data = {
            "listingId": str(listing_id),
            "source": 1}

        # if os.path.exists(file_path):
        #     self.logger.info("get_borrower_statistics from file")
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

        if "loanerStatistics" not in json_data["resultContent"]:
            self.logger.warning(f"Can not get_borrower_statistics {listing_id}")
            return {"listingId": listing_id}

        borrower_statistics = json_data["resultContent"]["loanerStatistics"]
        borrower_statistics["successNum"] = json_data["resultContent"]["loanerStatistics"]["listingStatics"][
            "successNum"]

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
                self.logger.info(json.dumps(item, indent=4,  ensure_ascii=False))
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
                        self.logger.info(json.dumps(item, indent=4, ensure_ascii=False))
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
        else:
            raise ValueError(f"Unknown month type for bid sim: {month}")

        credit_codes = item["级别"]
        if credit_codes == "B":
            data["creditCodes"] = "3"
        elif credit_codes == "C":
            data["creditCodes"] = "4"
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
            "sigleBidAmount": 50,
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
        else:
            raise ValueError(f"Unknown month type for bid sim: {month}")

        credit_codes = item["级别"]
        if credit_codes == "B":
            data["creditCodes"] = "3"
        elif credit_codes == "C":
            data["creditCodes"] = "4"
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

        # self.logger.info(f"bid by request result {listing_id}: {req.text}")
        return True
        pass

    async def aio_bid(self, item):

        pass

def main():
    # tasks = []
    # loop = asyncio.get_event_loop()
    #
    # logger.info("start send")
    id = 129722056

    client = PpdUISimulationRequest()
    json_data = client.get_detail_info(129723136)
    # json_data = client.batch_get_detail_infs([129722481, 129722781])
    # for item in client.batch_get_show_borrower_info([id, 128080987]):
    #     logger.info(json.dumps(client.change_key(item), ensure_ascii=False))
    logger.info(json.dumps(json_data, ensure_ascii=False))
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


if __name__ == '__main__':
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=10, format=logging_format)
    logger = logging.getLogger(__name__)
    main()
