import logging
import asyncio
from aiohttp import ClientSession
import json


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
            "Cookie": "gr_user_id=11f8ea81-90aa-4c3e-a041-71c51c28ea51; uniqueid=747711b0-faee-473f-96e7-a488248ded5f; __fp=fp; __vid=3407234.1530775507276; _ppdaiWaterMark=15312861763999; _ga=GA1.2.1098278737.1530780657; ppdaiRole=8; openid=cdda7ce1e0bcfdaa2503c4f0770aabe4; ppd_uname=pdu8953799660; regSourceId=0; referID=0; fromUrl=; referDate=2018-8-6%2013%3A57%3A16; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22first_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; token=2fdc8033594dfea0e1aa6a7ef7093f57c0207fbe8c4b646107b590de965acacb9b6548480c27c14b50; __eui=Cel3wwogQQUMvl7O%2BveuJQ%3D%3D; aliyungf_tc=AQAAAPE3XS/iIQcAjlD3PPUGI1ze/SOB; __utmc=1; currentUrl=https%3A%2F%2Finvest.ppdai.com%2Floan%2Flistnew%3Floancategoryid%3D4%26creditcodes%3D%26listtypes%3D%26rates%3D%26months%3D%26authinfo%3D%26borrowcount%3D%26didibid%3D%26sorttype%3D0%26minamount%3D0%26maxamount%3D0; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1534748481; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1535703865; __tsid=262473610; __vsr=1535681360481.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1535688584670.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1535694991046.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1535703859421.refSite%3Dhttps%3A//www.ppdai.com/moneyhistory%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1535706439890.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; __utma=1.1098278737.1530780657.1535682387.1535944602.37; __utmz=1.1535944602.37.37.utmcsr=ppdai.com|utmccn=(referral)|utmcmd=referral|utmcct=/moneyhistory; registerurl=https%3A%2F%2Fpay.ppdai.com%2Fdeposit%2Fprocessing%3Ftradeid%3D180903064000093766; registersourceurl=https%3A%2F%2Fppdai.cloud.cmbchina.com%2Frecharge%3Fsecret%3Db5bhbwmwrxuwsmvvmnqttzvtym1ubpqxim3tftkptfis3f7o42jsgehovtxmi2whk3tycorayylhx%252bgupo6i6%252fsigmo5enlv%252bbfy8w8jw1dms5uaxyw61vdaxvmpyjj2ejyi7zjfthdyqttpn3wkb7hlwfos3lwyskvcjzv9wafyzwkulq8onjrlkpxf%252bzrk7zkx3z%252bc3yozullipwn89hqem%252b1qlukluz9jtajhym1jwjunnp1lczstpoyronejov660lt8vpq%252f849dvxw84n23lxg%252bostb5jhmpwk8uxqloej4lda6il6luosvgxzgp72tycrgrhzpz7qkonluzksq6%252bml84lt7tfavr4onsefmhdmdnbc%252fitgsphv27lw%252fqxsw2hgw72hbujhmf%252flnzop5cpm4voo8urnlgpr69otonzenixsuskr034w34dy9gp77z3ery28wkbsxpai1pdrxsyxyf3clnpywph6npx53luwazmdavgrhid0kt7tbgjby7jigfqntec9fqf5avkqwfcebnitt1ihetpyrjtkatxymevlsf4xq0c5qpicezmuyenu923yle40rwncne42dbcfwbwxz4rvylkhqrizmu%252bqd0vdoxykc7nsr8elcuxujjvdvbse30j%252bobkpacgewazgio5ckduj8e3qkeq%253d; Hm_lvt_aab1030ecb68cd7b5c613bd7a5127a40=1535427469,1535601903,1535682414,1535944641; payDatetimeCookie=2018-09-03+11%3a16%3a22; Hm_lpvt_aab1030ecb68cd7b5c613bd7a5127a40=1535944643; __sid=1535963508544.1.1535963508544; waterMarkTimeCheck1=09%2F03%2F2018+16%3A31%3A49; JSESSIONID=72E1B532B743F4AE17C3A3E6136BB548",
        }

    def change_key(self, item):
        key_dict = {}

        key_dict["amount"] = "借款金额"
        key_dict["creditCode"] = "级别"
        key_dict["showRate"] = "协议利率"   # currentRate
        key_dict["months"] = "期限"
        key_dict["loanUse"] = "借款用途"

        key_dict["gender"] = "性别"
        key_dict["age"] = "年龄"
        key_dict["income"] = "收入情况"
        key_dict["repaymentSourceType"] = "还款来源"
        key_dict["workInfo"] = "工作信息"
        key_dict["registerDateStr"] = "注册时间"

        key_dict["OwingAmount"] = "待还金额"
        key_dict["OverdueLessCount"] = "逾期（0-15天）还清次数"
        key_dict["OverdueMoreCount"] = "逾期（15天以上）还清次数"
        key_dict["SuccessCount"] = "成功借款次数"
        key_dict["NormalCount"] = "正常还清次数"
        key_dict["HighestDebt"] = "历史最高负债"


        key_dict["HighestPrincipal"] = "单笔最高借款金额"
        key_dict["EducationDegree"] = "文化程度"
        key_dict["GraduateSchool"] = "毕业院校"
        key_dict["StudyStyle"] = "学习形式"

        for key, value in key_dict.items():
            if key not in item:
                continue

            item[value] = item[key]
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

        # item["成功还款次数"] = item["正常还清次数"] + item["逾期（0-15天）还清次数"] + item["逾期（15天以上）还清次数"]
        return item

    async def post_data(self, url, data, headers):
        post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        async with ClientSession(headers=headers) as session:
            logger.info(f"{url}, post, {post_data}")
            async with session.post(url, data=post_data) as response:
                logger.info("post finish")
                response = await response.read()
                return response

    async def get_show_listing_base_info(self, listing_id: int):
        self.headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(listing_id)
        url = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showListingBaseInfo"
        data = {
            "listingId": str(listing_id),
            "source": 1}

        result = await self.post_data(url, data, self.headers)
        json_data = json.loads(result)
        with open(f"..\\data\\showListingBaseInfo\\showListingBaseInfo_{listing_id}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(json_data, indent=4, ensure_ascii=False))

        if "result" not in json_data or json_data["result"] != 1:
            logger.warning(f"get_show_listing_base_info f{listing_id}: return f{json_data}")
            return None

        base_info = json_data["resultContent"]["listing"]
        base_info["loanUse"] = json_data["resultContent"]["loanUse"]
        return base_info

    async def get_show_borrower_info(self, listing_id: int):
        self.headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(listing_id)
        url = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showBorrowerInfo"
        data = {
            "listingId": str(listing_id),
            "source": 1}

        result = await self.post_data(url, data, self.headers)
        json_data = json.loads(result)
        with open(f"..\\data\\showBorrowerInfo\\showBorrowerInfo_{listing_id}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(json_data, indent=4, ensure_ascii=False))

        if json_data.get("result", -999) != 1:
            logger.warning(f"get_show_borrower_info f{listing_id}: return f{json_data}")
            return None

        borrower_info = json_data["resultContent"]
        borrower_info["listingId"] = listing_id

        if "userAuthsList" in borrower_info:
            for item in borrower_info["userAuthsList"]:
                borrower_info[item["name"]] = True
        return borrower_info

    async def get_borrower_statistics(self, listing_id: int):
        self.headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(listing_id)
        url = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showBorrowerStatistics"
        data = {
            "listingId": str(listing_id),
            "source": 1}

        result = await self.post_data(url, data, self.headers)
        json_data = json.loads(result)
        with open(f"..\\data\\showBorrowerStatistics\\showBorrowerStatistics_{listing_id}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(json_data, indent=4, ensure_ascii=False))

        if json_data.get("result", -999) != 1:
            logger.warning(f"get_show_borrower_info f{listing_id}: return f{json_data}")
            return None

        borrower_statistics = json_data["resultContent"]
        borrower_statistics["listingId"] = listing_id
        return borrower_statistics

def main():
    tasks = []
    loop = asyncio.get_event_loop()

    logger.info("start send")
    id = 127064996

    client = PpdUISimulationRequest()
    task = asyncio.ensure_future(client.get_show_listing_base_info(id))
    tasks.append(task)

    logger.info("start send")
    task = asyncio.ensure_future(client.get_show_borrower_info(id))
    tasks.append(task)

    logger.info("start send")
    task = asyncio.ensure_future(client.get_borrower_statistics(id))
    tasks.append(task)

    logger.info("finish send")
    result = loop.run_until_complete(asyncio.gather(*tasks))
    logger.info("wait result")
    print(json.dumps(result, ensure_ascii=False))
    print(result)


if __name__ == '__main__':
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=10, format=logging_format)
    logger = logging.getLogger(__name__)
    main()