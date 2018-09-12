import sys
sys.path.insert(0,'..')

from datetime import datetime
from datetime import timedelta

import logging
import requests
from Open.RsaClient import RsaClient
import json
from collections import deque

privatekey = '''
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDDN2K33KPvgHUff4Ta29qvpgmvXvYUwSGoJoBznu7LMmdYZBx+YKUpN8ij7N+dbA1aewb2AG/QlQ6WLUifVw6RhJ6s5V6NoWewes8Pe4NGk6HW8bp4PcxkUVavIOU/YZQHxiNnmeN1Y/X0Dpiuytz7JPg8gq5jbfVX90NKag8VrwIDAQABAoGAXxYxPYF5UIVvh0Ijwj7ojDoB6awFjSJtdGwckTTO96a7c/B/eIc2q5cCYeZVHWauMm5Oe7DGxgB0tG2mPAa5jwlQSJUP19laCBjmc/pnzyY2c1OiGnaTo5AswUmGrO3sz4DoHj2o6WMKTWoZL8VkuCdlq4SNZ6qrKPCR02mnsFECQQDzGfqKhad20Y5R39a494jeoiJAaUm9cTA6SBVoxAixCs4EIZwE63YWPFgeO6uMDzvyD8iefFBT/0ORhjbh2k3VAkEAzZL9BakD3HYC9NXG084+IcNe1a6sOfW5FnYGXadL/BUPHLYMp4AtRaTRnlnB/l7ngRFkpwf4YTNFn6Ix5fIjcwJBALOaturOshnr2s0MphRD9aAeg1W5NBy9WldE2GRtqMo8ZFbTCfTsjXMCJEw545T30F8XYC4PRD26sw357eRRJ/0CQHwub8QMjjWN4ElQHhRygNvabh48rvMwOYeU8lF+rwrvGbrpSgmhBzgL0UiLxgFICSbRf/DagrMMyuEclHHobHsCQQCIxPQdcZ0iXTBN6iGuE6XwXfHFL9zjOVrWhfqTCCs/NMtZmC0uVLYcY1tRjabBJg543Zo9RO356GtWTaQkHgIK
-----END RSA PRIVATE KEY-----
'''


privatekey_2 = '''
-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQC3b6GQxhVufoR6naWN3kr0q33cocQmKsdtjOamGMJoyaLD+72GW72Sxg0Q76YdwWMiZWJra+1dC6pxMJYB7DIkko58DoN3SVm1LjdkPXaq+OAFcWUUtnCaTL/i3p11knW8XmgyYyYEireBFGwFaw/zKxm9Nhbg5uGOwaPuP4/iQQIDAQABAoGAVvEL7KhWBBbnB46spv8TG8AkWWw6obRo7V14/ISDsFLRWH56p7HXujcwfjR30WaVa/oNmch/qjgbQqa6kpK2eJ2lT19tW8rxmdnAQqImT48YrAJXFWBpvKGRrGmij1fHuyieksMLaNnSXeCWIbrz3oDXNnbOBRrOhfmmnKw+llkCQQDbyKEafNJvWSpUN0VkxVO0EQTDa7taVdilzDJ6tI+6HFDfarFMvpD4LbHTp/qQq0LZssEQUGOOjknuozG14sGPAkEA1am1y0o/cdViBzJGjQ9ppwNtLg5AhhgtLXO2witAQKEhYoaqbjEoIqP8wVFiBgtFpkr8XJgn/QcxToXaEY2XLwJAcp2JLmgD0d+dDHgabzfcs93gLw1CkhSMu8HmXUlGXtcfcbORLKWAsnwZ7Xf/WmyFm0P2HMzfbltTwOhIJ0NOjwJAcMoZ8arMOydNjEb5/1T3jPa+F+XmIeN5VdkTzQRP8s4cdYppRaolacPvlY2ElXQ13EcRWT/pPCUj3jPCnimEeQJAE+ukIXgNEkF2tZxf4SAbBqCCOVmFzSkZmJLYzbPjfTg4NMBZqT/9BMeh16mMcjZBio8ClYJV8XFqoZ7v9WWN7g==
-----END RSA PRIVATE KEY-----
'''

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

        self.listing_id_cache = deque(maxlen=100)

        self.loan_list_time_delta_sec = -60 * 50
        self.rsa_client = RsaClient(privatekey)
        self.request_exceptin_count = 0
        pass

    def get_loan_list(self, page_index=1, time_delta_secs=-300, timeout=None):
        url = "https://openapi.ppdai.com/listing/openapiNoAuth/loanList"
        # start_date_time = datetime.utcnow()
        start_date_time = datetime.now() + timedelta(seconds=time_delta_secs)
        data = {
            "PageIndex": page_index,
            "StartDateTime": (start_date_time + timedelta(seconds=-3)).strftime('%Y-%m-%d %H:%M:%S')
        }

        result = self.post(url, data=data, timeout=timeout)
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

    def get_bid_list(self, start_date_time):
        url = "https://openapi.ppdai.com/bid/openapi/bidList"
        end_date_time = start_date_time + timedelta(days=30)
        data = {
            "StartTime": start_date_time.strftime('%Y-%m-%d'),
            "EndTime":  end_date_time.strftime('%Y-%m-%d'),
            "PageIndex": 1,
            "PageSize": 5000
        }

        return self.post(url, data, access_token=self.access_token)
        pass

    def post(self, url, data, access_token="", timeout=None):
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

        sort_data = self.rsa_client.sort(data)
        sign = self.rsa_client.sign(sort_data)

        REQUEST_HEADER["X-PPD-APPID"] = self.appid
        REQUEST_HEADER["X-PPD-SIGN"] = sign
        REQUEST_HEADER["X-PPD-TIMESTAMP"] = timestamp
        REQUEST_HEADER["X-PPD-TIMESTAMP-SIGN"] = self.rsa_client.sign("%s%s" % (self.appid, timestamp))
        REQUEST_HEADER["Accept"] = "application/json;charset=UTF-8"

        if access_token.strip():
            REQUEST_HEADER["X-PPD-ACCESSTOKEN"] = access_token

        req = self.session.post(url, data=json.dumps(data), headers=REQUEST_HEADER, timeout=timeout)
        return req.text
        pass

    def get_loan_list_ids(self, credit_code_list: str, month_list: int):
        new_listing_id = None
        try:
            result = self.get_loan_list(time_delta_secs=self.loan_list_time_delta_sec, timeout=0.5)
            json_data = json.loads(result)
            if json_data.get("Result", -999) != 1:
                self.logger.error(f"get_loan_list: {json_data}")
                return new_listing_id

            loan_infos = json_data["LoanInfos"]
            loan_infos_len = len(loan_infos)

            if loan_infos_len < 180:
                self.loan_list_time_delta_sec *= 1.1
                # self.logger.info(f"{loan_infos_len} {self.loan_list_time_delta_sec} +")
            elif loan_infos_len >= 200:
                self.loan_list_time_delta_sec *= 0.9
                # self.logger.info(f"{loan_infos_len} {self.loan_list_time_delta_sec} -")

            listing_ids = [item["ListingId"] for item in loan_infos if item["Months"] in month_list and item["CreditCode"] in credit_code_list]
            new_listing_id = list(set(listing_ids).difference(self.listing_id_cache))
            if new_listing_id is not None and len(new_listing_id) != 0:
                self.logger.info(f"生产者生产了: {len(new_listing_id)} in {len(listing_ids)}, {loan_infos_len}  {new_listing_id}")
            else:
                # self.logger.info("No more data")
                return None

            self.listing_id_cache.extendleft(new_listing_id)
        except requests.exceptions.Timeout as ex:
            self.request_exceptin_count += 1
            if self.request_exceptin_count == 30:
                self.logger.info(f"get_loan_list_ids ReadTimeout: {ex}")
                self.request_exceptin_count = 0
        except requests.exceptions.ConnectionError as ex:
            self.logger.info(f"get_loan_list_ids ConnectionError: {ex}")
        except requests.exceptions.RequestException as e:
            self.logger.info(f"get_loan_list_ids RequestException: {ex}")
        except Exception as ex:
            self.logger.info(f"get_loan_list_ids exception: {ex} result: {result}", exc_info=True)

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

        # print(client.get_loan_list_ids(["B", "C"], [3, 6]))

        print(client.get_bid_list(datetime.now() + timedelta(days=-30)))

    except Exception as ex:
        print(ex)
    pass


if __name__ == "__main__":
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=10, format=logging_format)
    logger = logging.getLogger(__name__)

    try:
        main()
    except Exception as ex:
        print(ex)