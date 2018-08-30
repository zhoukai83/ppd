import sys
sys.path.append("..")

import json
import platform
import logging
from FetchFromChrome import FetchFromChrome
from UI.FetchFromChromeQuick import FetchFromChromeQuick


def refresh_config():
    with open('UIMain.json') as f:
        data = json.load(f)
        config = data[platform.node()]
        return config


def main():
    config = refresh_config()
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=15, format=logging_format)

    logger = logging.getLogger(__name__)

    data = {
        "authInfo": "",
        "authenticated": True,
        "availableBalance": 279.08,
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
            "creditValidate": 1,
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
        "ip": "101.41.247.234",
        "maxAmount": 17400,         # must
        "minAmount": 17400,         # must
        "months": "1,2,3,4",
        "needTotalCount": True,
        "pageCount": 1,
        "pageIndex": 1,
        "pageSize": 10,
        "rates": "",
        "riskLevelCategory": 1,
        "sort": 0,
        "source": 1,
        "successLoanNum": "3",
        "totalCount": 1,
        "userId": 87288708,
        "sigleBidAmount": 50,
        "bidCount": 1,
        "useCoupon": True
    }

    print(json.dumps(data, ensure_ascii=False))

    with FetchFromChromeQuick(config["Session"]) as fetch_from_chrome:
        print(fetch_from_chrome.fetch_detail_info(False))
    #     # fetch_from_chrome.wait_until_text_present(".filter-total span", "115")
    #     # logger.info("can bid: %s %s\n%s", item["listingId"], first_strategy, item)
    #     # fetch_from_chrome.quick_bid()
    #     logger.info("start")
    #     cookies = fetch_from_chrome.driver.get_cookies()
    #     cookie_list = [f"{cookie['name']}={cookie['value']}" for cookie in cookies]
    #     logger.info("; ".join(cookie_list))
    #     logger.info("end")


    pass

if __name__ == "__main__":
    main()
