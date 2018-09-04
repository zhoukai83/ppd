import sys
sys.path.insert(0,'..')

from datetime import datetime
from datetime import timedelta

import logging
import requests
from Open.RsaClient import rsa_client
import json
from collections import deque

# {"AccessToken":"78d9d769594dfea0e1aa6a7ef7093f57b3e97dcfca2f75129f8f77f112909a473ba2d3be060259a59e2739c846b027aadf4c5e12dc4064cf83842a7c","ExpiresIn":604800,"OpenID":"a27effb5cc9f4d2fad1053642a155fe1","RefreshToken":"2cdb8235594dfea0e1aa6a7ef7093f57dbdb96f607c79bcff16bf076"}
#  {"AccessToken":"748ad369594dfea0e1aa6a7ef7093f572065cc02835959376e2c745e7af2ffd567df49d2191106df32ee26645216404e08ca5c434de837168428b0ca","ExpiresIn":604800,"RefreshToken":"2cdb8235594dfea0e1aa6a7ef7093f57dbdb96f607c79bcff16bf076"}
class PpdOpenClient:
    def __init__(self, logger=None):
        self.session = requests.Session()
        self.appid = "9ed4a9e198384310a12afd69a015787a"
        self.logger = logger or logging.getLogger(__name__)

        # 507d1c7703144dc19ddfd17e8028740b & state =
        self.code = "507d1c7703144dc19ddfd17e8028740b"
        self.access_token = "748ad369594dfea0e1aa6a7ef7093f572065cc02835959376e2c745e7af2ffd567df49d2191106df32ee26645216404e08ca5c434de837168428b0ca"

        self.listing_id_cache = deque(maxlen=1000)
        pass

    def get_loan_list(self):
        url = "https://openapi.ppdai.com/listing/openapiNoAuth/loanList"
        start_date_time = datetime.utcnow()

        data = {
            "PageIndex": "1",
            "StartDateTime": (start_date_time + timedelta(minutes=-10)).strftime('%Y-%m-%d %H:%M:%S')
        }

        result = self.post(url, data=data)
        return result

    def get_listing_info(self, listing_ids):
        if len(listing_ids) > 10:
            raise ValueError(f"get_listing_info() parame listing_ids length > 10,  {len(listing_ids)}, {listing_ids}")

        url = "https://openapi.ppdai.com/listing/openapiNoAuth/batchListingInfo"
        data = {
            "ListingIds": listing_ids
        }

        return self.post(url, data=data)

    def get_buy_list(self, page_index=1, levels=None):
        url = "https://openapi.ppdai.com/debt/openapiNoAuth/buyList"
        data = {
            "PageIndex": page_index,
        }

        if levels is not None:
            data["Levels"] = levels

        return self.post(url, data=data)

    def get_debt_info(self, debt_ids):
        # if len(debt_ids) > 10:
        #     raise ValueError(f"get_listing_info() parame listing_ids length > 10,  {len(debt_ids)}, {debt_ids}")
        url = "https://openapi.ppdai.com/debt/openapiNoAuth/batchDebtInfo"
        data = {
            "DebtIds": debt_ids
        }

        return self.post(url, data=data)

    def get_access_token(self, code):
        url = "https://ac.ppdai.com/oauth2/authorize"
        data = {"AppID": self.appid, "Code": code}
        return self.post(url, data=data)

    def refresh_token(self, openid, token):
        url = "https://ac.ppdai.com/oauth2/refreshtoken"
        data = {"AppID": self.appid, "OpenId": openid, "RefreshToken": token}
        return self.post(url, data=data)

    def get_query_balance(self):
        url = "https://openapi.ppdai.com/balance/balanceService/QueryBalance"
        data = {
        }
        return self.post(url, data=data, access_token=self.access_token)

    def bid(self, listing_id):
        url = "https://openapi.ppdai.com/listing/openapi/bid"
        data = {
            "ListingId": listing_id,
            "Amount": 50,
            "UseCoupon": "true"
        }
        return self.post(url, data, access_token=self.access_token)

    def get_bid_list(self):
        url = "https://openapi.ppdai.com/bid/openapi/bidList"
        start_date_time = datetime.utcnow()
        data = {
            "StartTime": start_date_time.strftime('%Y-%m-%d'),
            "EndTime": start_date_time.strftime('%Y-%m-%d'),
            "PageIndex": 1,
            "PageSize": 20
        }

        return self.post(url, data, access_token=self.access_token)
        pass

    def post(self, url, data, access_token=""):
        start_date_time = datetime.utcnow()
        timestamp = start_date_time.strftime('%Y-%m-%d %H:%M:%S')

        REQUEST_HEADER = {'Connection': 'keep-alive',
                          'Cache-Control': 'max-age=0',
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36',
                          # 'Accept-Encoding': 'gzip, deflate, sdch',
                          'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
                          'Content-Type': 'application/json;charset=utf-8'
                          }

        sort_data = rsa_client.sort(data)
        sign = rsa_client.sign(sort_data)

        REQUEST_HEADER["X-PPD-APPID"] = self.appid
        REQUEST_HEADER["X-PPD-SIGN"] = sign
        REQUEST_HEADER["X-PPD-TIMESTAMP"] = timestamp
        REQUEST_HEADER["X-PPD-TIMESTAMP-SIGN"] = rsa_client.sign("%s%s" % (self.appid, timestamp))
        REQUEST_HEADER["Accept"] = "application/json;charset=UTF-8"

        if access_token.strip():
            REQUEST_HEADER["X-PPD-ACCESSTOKEN"] = access_token

        req = self.session.post(url, data=json.dumps(data), headers=REQUEST_HEADER)
        return req.text
        pass

    def get_loan_list_ids(self):
        new_listing_id = None
        result = self.get_loan_list()
        json_data = json.loads(result)
        if json_data.get("Result", -999) != 1:
            self.logger.error(f"get_loan_list: {json_data}")
            return new_listing_id

        listing_ids = [item["ListingId"] for item in json_data["LoanInfos"]]
        new_listing_id = list(set(listing_ids).difference(self.listing_id_cache))
        if new_listing_id is not None and len(new_listing_id) != 0:
            self.logger.info(f"生产者生产了: {len(new_listing_id)} in {len(listing_ids)},  {new_listing_id}")
        else:
            # self.logger.info("No more data")
            return None

        self.listing_id_cache.extend(new_listing_id)
        return new_listing_id


def main():
    client = PpdOpenClient()
    # print(client.get_listing_info([
    #     126020226,
    #     126020214,
    #     126020222,
    #     126020232,
    #     126020243,
    #     126020245,
    #     126020246,
    #     126020259,
    #     126020273,
    #     126020283,
    # ]))
    try:
        # print(client.get_buy_list(levels="B"))

        # print("")
        # print(client.get_debt_info([118691808, 118691802, 118691801]))

        # openid = "a27effb5cc9f4d2fad1053642a155fe1"
        # refresh_token = "2cdb8235594dfea0e1aa6a7ef7093f57dbdb96f607c79bcff16bf076"
        # print(client.refresh_token(openid, refresh_token))
        print(client.get_bid_list())
    except Exception as ex:
        print(ex)
    pass


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)