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
            "Cookie": "gr_user_id=11f8ea81-90aa-4c3e-a041-71c51c28ea51; uniqueid=747711b0-faee-473f-96e7-a488248ded5f; __fp=fp; __vid=3407234.1530775507276; _ppdaiWaterMark=15312861763999; _ga=GA1.2.1098278737.1530780657; ppdaiRole=8; openid=cdda7ce1e0bcfdaa2503c4f0770aabe4; ppd_uname=pdu8953799660; regSourceId=0; referID=0; fromUrl=; referDate=2018-8-6%2013%3A57%3A16; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu8953799660%22%2C%22%24device_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22first_id%22%3A%221646959503432e-09fcbfb7c16c45-5b193613-2304000-16469595035ae%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC(%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80)%22%7D%7D; token=2fdc8033594dfea0e1aa6a7ef7093f57c0207fbe8c4b646107b590de965acacb9b6548480c27c14b50; __eui=Cel3wwogQQUMvl7O%2BveuJQ%3D%3D; aliyungf_tc=AQAAAPE3XS/iIQcAjlD3PPUGI1ze/SOB; __utmc=1; payDatetimeCookie=2018-08-30+12%3a04%3a09; currentUrl=https%3A%2F%2Finvest.ppdai.com%2Floan%2Flistnew%3Floancategoryid%3D4%26creditcodes%3D%26listtypes%3D%26rates%3D%26months%3D%26authinfo%3D%26borrowcount%3D%26didibid%3D%26sorttype%3D0%26minamount%3D0%26maxamount%3D0; __utma=1.1098278737.1530780657.1535599919.1535682387.36; __utmz=1.1535682387.36.36.utmcsr=ppdai.com|utmccn=(referral)|utmcmd=referral|utmcct=/moneyhistory; registerurl=https%3A%2F%2Fpay.ppdai.com%2Fdeposit%2Fprocessing%3Ftradeid%3D180831064000061716; registersourceurl=https%3A%2F%2Fppdai.cloud.cmbchina.com%2Frecharge%3Fsecret%3Dkozc8%252f0p0ymmpeomxvpqxioe0ab%252fxljazkis57zonkdqjkdwaofhl9nk9ci%252bfnzb5fuxjj90vr3mrdfph7g%252fxteaklm9rzyw9xyehd6bsjm9ngbi5urara7tipu2hg6pkbl3ihnyzrvynyzxhtu9whn0zoaiip%252fbxnpgbftzmk0eivd4%252fkq3l70kntc1quk%252f3uhr74iesko3ex1hswswjfbxgywp1yaiw74cacrj0e9vtxbgafnvcmg5svlbww%252bnpu7qlrv2ckowlnp36vqtnhq8ne7pt2v7obuc9bzdgindvy%252f%252fyye%252bvovbpzd2qekwpgsgciy56lpir9%252fa0b057xi5z8hzi0jk5id%252fyaipxke%252bsgcaocu20zdpkab8yxyj74myqlvlnurjjn%252fdpwgj13a3zttrtbsciw%252bwcne6xy3srzqxmxywhzazrn04zeavo6p81jbzaccgzhdbfvp6leuhcb1wunhyw8qyevgsuf27lon8uwxf4nd8fckdfgxyh0i9%252fw0aebbizdc1qog7c34mtctthz%252fp2osvxkv5hfcnxw81glutopsqsottjr11ahkkiei1bsiku%252bmzpyxatpecr2bm7%252bbl5rv974mszdy3v18ckgtmiqmhd%252foowmimrme20f8toryja5sxld8vhauogp7sm1he8ynpzg1niya%253d; Hm_lvt_aab1030ecb68cd7b5c613bd7a5127a40=1535340754,1535427469,1535601903,1535682414; Hm_lpvt_aab1030ecb68cd7b5c613bd7a5127a40=1535682417; __tsid=200643318; __vsr=1535605301085.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1535681360481.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1535688584670.refSite%3Dhttps%3A//tz.ppdai.com/account/indexV2%7Cmd%3Dreferral%7Ccn%3Dreferral%3B1535694991046.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect%3B1535703859421.refSite%3Dhttps%3A//www.ppdai.com/moneyhistory%7Cmd%3Dreferral%7Ccn%3Dreferral; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1534748481; gr_session_id_b9598a05ad0393b9=b6b9a95e-a9b4-4db6-910f-8e14ca5bfa06; gr_cs1_b6b9a95e-a9b4-4db6-910f-8e14ca5bfa06=user_name%3Apdu8953799660; gr_session_id_b9598a05ad0393b9_b6b9a95e-a9b4-4db6-910f-8e14ca5bfa06=true; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1535703865; __sid=1535703859421.3.1535704075082; waterMarkTimeCheck1=08%2F31%2F2018+16%3A27%3A57; JSESSIONID=6E2080507F8A3091E7949B174C9E0014",
        }

    async def get_show_listing_base_info(self, listing_id):
        self.headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(listing_id)
        url = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showListingBaseInfo"
        data = {
            "listingId": str(listing_id),
            "source": 1}

        post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        async with ClientSession(headers=self.headers) as session:
            logger.info(f"{url}, post, {post_data}")
            async with session.post(url, data=post_data) as response:
                logger.info("post finish")
                response = await response.read()
                result = json.loads(response, encoding=False)
                return result

    async def get_show_borrower_info(self, listing_id):
        self.headers["Referer"] = "https://invest.ppdai.com/loan/info/" + str(listing_id)
        url = "https://invest.ppdai.com/api/invapi/LoanDetailPcService/showBorrowerInfo"
        data = {
            "listingId": str(listing_id),
            "source": 1}

        post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        async with ClientSession(headers=self.headers) as session:
            logger.info(f"{url}, post, {post_data}")
            async with session.post(url, data=post_data) as response:
                logger.info("post finish")
                response = await response.read()
                result = json.loads(response, encoding=False)
                return result


def main():
    tasks = []
    loop = asyncio.get_event_loop()

    logger.info("start send")
    id = 126748412

    client = PpdUISimulationRequest()
    task = asyncio.ensure_future(client.get_show_listing_base_info(id))
    tasks.append(task)

    logger.info("start send")
    task = asyncio.ensure_future(client.get_show_borrower_info(id))
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