import sys
sys.path.insert(0,'..')

from datetime import datetime
from datetime import timedelta

import logging
import requests
from Open.RsaClient import RsaClient
import json
from collections import deque
import os

privatekey_1 = '''
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDDN2K33KPvgHUff4Ta29qvpgmvXvYUwSGoJoBznu7LMmdYZBx+YKUpN8ij7N+dbA1aewb2AG/QlQ6WLUifVw6RhJ6s5V6NoWewes8Pe4NGk6HW8bp4PcxkUVavIOU/YZQHxiNnmeN1Y/X0Dpiuytz7JPg8gq5jbfVX90NKag8VrwIDAQABAoGAXxYxPYF5UIVvh0Ijwj7ojDoB6awFjSJtdGwckTTO96a7c/B/eIc2q5cCYeZVHWauMm5Oe7DGxgB0tG2mPAa5jwlQSJUP19laCBjmc/pnzyY2c1OiGnaTo5AswUmGrO3sz4DoHj2o6WMKTWoZL8VkuCdlq4SNZ6qrKPCR02mnsFECQQDzGfqKhad20Y5R39a494jeoiJAaUm9cTA6SBVoxAixCs4EIZwE63YWPFgeO6uMDzvyD8iefFBT/0ORhjbh2k3VAkEAzZL9BakD3HYC9NXG084+IcNe1a6sOfW5FnYGXadL/BUPHLYMp4AtRaTRnlnB/l7ngRFkpwf4YTNFn6Ix5fIjcwJBALOaturOshnr2s0MphRD9aAeg1W5NBy9WldE2GRtqMo8ZFbTCfTsjXMCJEw545T30F8XYC4PRD26sw357eRRJ/0CQHwub8QMjjWN4ElQHhRygNvabh48rvMwOYeU8lF+rwrvGbrpSgmhBzgL0UiLxgFICSbRf/DagrMMyuEclHHobHsCQQCIxPQdcZ0iXTBN6iGuE6XwXfHFL9zjOVrWhfqTCCs/NMtZmC0uVLYcY1tRjabBJg543Zo9RO356GtWTaQkHgIK
-----END RSA PRIVATE KEY-----
'''

privatekey_2 = '''
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCBUDp6YFA76M1OiPGChrn42ti5l4iUvpO+SC2v+TXupZLmYPSPZbnEImbigTVGdDb6q4/AA3PNx+OOZnVKSJMz3PKW3ATx+wzhlCN+fZyIVJKvM5mFnauTGxkKlDcQqgxOX4bAaITA7gDJCuygUHg6qHE72Z2AJD1VTCl0lijI7QIDAQABAoGAVhT9SLfS0X7RJSWeeACNzm6I9Us9vZ78JSBRYaKpV1tbZgdG5iqWtk0cZk4TE/qLGuWYRP9HWMZm4kWscK3NZy0d1LAqcqk+/3XBDsem+38fP4s0qgoP9kee1NLKzjtzxstxkRgUE43Mlh2WpKEgDDQ9Z6lKh6Iu7jh9co1edYECQQD0c95eDNGbJQIPHFgE0IrKQZEHPWqIGneDmsen0Glwb38v/GsBFJE3YX3kfm5MWcdEPAC7Bo9aAVUFMSTJtM1hAkEAh2v/TOOc+1lfTRF/h/SAbfzuxP674naKqw5khoAyN5OJWykQT7IS2AoMmlXLlkFzdEzSEVs3n5a/Bf8SQcU7DQJAQePtf0pTQU9TY8FPFFUl4+iSb/IlAfSoXEffIyOxGAZlsQiHyy3BCr1zkqBlmJzmckT+KWtWPnt3cEPT166tYQJAUYga+A7dt5JyRzMuxgrVu+KZWq9HLSxThnMu4K+UDFPeUa0ibej3YWyDc/QNk5QqT63kl6CEl6epsJGGS2TUjQJBAO2/QnFx2eLSveUiGcwWeH48kDaJQHq2VHe7x0MEFdeU+HpCMaVlRLEDndLHowYRfU70OY4s60OTT8sr/oaHAts=
-----END RSA PRIVATE KEY-----
'''

privatekey_3 = '''
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCfOK+XUw/CXEmg/xTXRLPVXiinbzYMKbd0vnkPetbAN+3mSBdST1d0cDssNdXm68M6fHbhrfVCCigkfnv6s16n7eY/AVm2MajuhFCy8nROEPhgZkFDLp8VZGwULDmeXk8EdTy5h3AEx9beDwn9i4jy/69vvfuOes4QOaIL+QB/PQIDAQAB
-----END PUBLIC KEY-----
'''

privatekey_4 = '''
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDfyx0dAG2LcoItKtj5lvIES9Uu7jrRZsIGNJlR63EbWnVEGLnW1p2s+rVcfp6Ei7qMysHBLUgTArdDr3/oPbX59Ga3N1YHF03hc/XvSZv+Za3F0DouS7zUHjHmsHKKxTQ5uaChyKHAMG1beFHKPACO2cnwHv2vAVJLCKeyVGEzxQIDAQAB
-----END PUBLIC KEY-----
'''


#  2018-11-14 10:22:24,910  {"AccessToken":"79dad333594dfea0e1aa6a7ef7093f57641e5b9a6e7db51cb3bb3408ba1d94e8cb83c427f014dc1e611e91f3770ff6a0b32ae0a4c19ced9158324934","ExpiresIn":604800,"RefreshToken":"2cdb8235594dfea0e1aa6a7ef7093f57dbdb96f607c79bcff16bf076"}
# {"AccessToken":"78d9d769594dfea0e1aa6a7ef7093f57b3e97dcfca2f75129f8f77f112909a473ba2d3be060259a59e2739c846b027aadf4c5e12dc4064cf83842a7c","ExpiresIn":604800,"OpenID":"a27effb5cc9f4d2fad1053642a155fe1","RefreshToken":"2cdb8235594dfea0e1aa6a7ef7093f57dbdb96f607c79bcff16bf076"}
#  {"AccessToken":"748ad369594dfea0e1aa6a7ef7093f572065cc02835959376e2c745e7af2ffd567df49d2191106df32ee26645216404e08ca5c434de837168428b0ca","ExpiresIn":604800,"RefreshToken":"2cdb8235594dfea0e1aa6a7ef7093f57dbdb96f607c79bcff16bf076"}
class PpdOpenClient:
    def __init__(self, logger=None, key_index=1):
        self.session = requests.Session()

        self.logger = logger or logging.getLogger(__name__)

        if key_index < 1 or key_index > 4:
            raise ValueError(f"Do not support key index: {key_index}")

        self.config = self.__get_config(key_index)
        # 507d1c7703144dc19ddfd17e8028740b & state =

        self.appid = self.config["appid"]
        # self.code = "507d1c7703144dc19ddfd17e8028740b"
        self.access_token = self.config["AccessToken"]

        self.private_key = "\r\n".join(["-----BEGIN RSA PRIVATE KEY-----", self.config["privatekey"], "-----END RSA PRIVATE KEY-----"])
        self.listing_id_cache = deque(maxlen=200)

        self.loan_list_time_delta_sec = -60 * 15
        self.client_index = key_index

        self.rsa_client = RsaClient(self.private_key)
        self.request_exceptin_count = 0

        self.log_count = 0
        self.loan_list_page_index = 1
        pass

    def __get_config(self, key_index):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PpdOpenClient.json')) as f:
            data = json.load(f)
            config = data[f"client{key_index}"]
            return config

    def set_access_token(self, access_token):
        self.access_token = access_token

    def get_loan_list(self, page_index=1, time_delta_secs=None, timeout=None):
        # {
        #     "Amount": 20000.0,
        #     "CreditCode": "C",
        #     "ListingId": 129967042,
        #     "Months": 12,
        #     "PayWay": 1,
        #     "PreAuditTime": "2018-09-28 14:34:14",
        #     "Rate": 24.0,
        #     "RemainFunding": 134.0,
        #     "Title": "手机app用户的借款"
        # }
        url = "https://openapi.ppdai.com/listing/openapiNoAuth/loanList"
        data = {
            "PageIndex": page_index
        }

        # start_date_time = datetime.utcnow()
        if time_delta_secs:
            start_date_time = datetime.now() + timedelta(seconds=time_delta_secs)
            data["StartDateTime"] = start_date_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        self.log_count += 1
        if self.log_count > 100:
            print(self.client_index, data, time_delta_secs)
            self.log_count = 0
        result = self.post(url, data=data, timeout=timeout)
        return result

    def get_listing_info(self, listing_ids: list):
        # {
        #     "Age": 28,
        #     "Amount": 20000.0,
        #     "AmountToReceive": 0,
        #     "AuditingTime": "2018-09-28T14:52:23.683",
        #     "BorrowName": "pdu0765557327",
        #     "CancelCount": 0,
        #     "CertificateValidate": 0,
        #     "CreditCode": "C",
        #     "CreditValidate": 0,
        #     "CurrentRate": 24.0,
        #     "DeadLineTimeOrRemindTimeStr": "2018/9/28",
        #     "EducationDegree": null,
        #     "FailedCount": 0,
        #     "FirstSuccessBorrowTime": "2015-12-27T17:40:52.933",
        #     "FistBidTime": "2018-09-28T14:34:20.000",
        #     "Gender": 2,
        #     "GraduateSchool": null,
        #     "HighestDebt": 24661.98,
        #     "HighestPrincipal": 8000.0,
        #     "LastBidTime": "2018-09-28T14:52:23.000",
        #     "LastSuccessBorrowTime": "2018-09-28T14:32:15.000",
        #     "LenderCount": 179,
        #     "ListingId": 129967042,
        #     "Months": 12,
        #     "NciicIdentityCheck": 0,
        #     "NormalCount": 90,
        #     "OverdueLessCount": 4,
        #     "OverdueMoreCount": 0,
        #     "OwingAmount": 0.0,
        #     "OwingPrincipal": 0.0,
        #     "PhoneValidate": 1,
        #     "RegisterTime": "2015-12-27T17:33:51.000",
        #     "RemainFunding": 0.0,
        #     "StudyStyle": null,
        #     "SuccessCount": 17,
        #     "TotalPrincipal": 90858.0,
        #     "WasteCount": 9
        # },
        if len(listing_ids) > 10:
            raise ValueError(f"get_listing_info() parame listing_ids length > 10,  {len(listing_ids)}, {listing_ids}")

        url = "https://openapi.ppdai.com/listing/openapiNoAuth/batchListingInfo"
        data = {
            "ListingIds": listing_ids
        }

        return self.post(url, data=data)

    # 50次/min	获取债权可购买列表
    def get_buy_list(self, page_index=1, levels=None):
        url = "https://openapi.ppdai.com/debt/openapiNoAuth/buyList"
        data = {
            "PageIndex": page_index,
        }

        if levels is not None:
            data["Levels"] = levels

        return self.post(url, data=data)

    def buy_debt(self, debt_id):
        access_url = "https://openapi.ppdai.com/debt/openapi/buy"
        data = {
            "DebtDealId": debt_id
        }

        return self.post(access_url, data=data, access_token=self.access_token)


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

    def bid(self, listing_id, bid_number=51):
        url = "https://openapi.ppdai.com/listing/openapi/bid"
        data = {
            "ListingId": listing_id,
            "Amount": bid_number,
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

    def get_loan_list_items(self):
        new_listing_items = None
        result = None
        try:
            result = self.get_loan_list(time_delta_secs=self.loan_list_time_delta_sec, timeout=0.5,
                                        page_index=self.loan_list_page_index)
            json_data = json.loads(result)
            if json_data.get("Result", -999) != 1:
                self.logger.error(f"get_loan_list: {json_data}")
                self.loan_list_page_index = 1
                return new_listing_items

            loan_infos = json_data["LoanInfos"]
            loan_infos_len = len(loan_infos)

            if loan_infos_len < 180:
                if not self.loan_list_time_delta_sec < -60 * 20:
                    self.loan_list_time_delta_sec *= 1.1
            elif loan_infos_len >= 200:
                self.loan_list_time_delta_sec *= 0.9

            return loan_infos
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

        return new_listing_items

    def get_loan_list_ids(self, credit_code_list: str, month_list: int):
        loan_infos = self.get_loan_list_items()

        if not loan_infos:
            return None

        listing_ids = [item["ListingId"] for item in loan_infos if item["Months"] in month_list and item["CreditCode"] in credit_code_list and item.get("RemainFunding", 0) > 50 and not (item["CreditCode"] in ["A", "C"] and item["Months"] == 12)]
        new_listing_id = list(set(listing_ids).difference(self.listing_id_cache))

        if new_listing_id:
            self.logger.info(f"find from O{self.client_index}: {len(new_listing_id)} in {len(listing_ids)}, {len(loan_infos)}  {new_listing_id},{self.loan_list_time_delta_sec}")
            self.listing_id_cache.extendleft(new_listing_id)

        return new_listing_id

    def get_loan_list_v2(self, credit_code_list, month_list):
        loan_infos = self.get_loan_list_items()

        if not loan_infos:
            return None

        listings = [item for item in loan_infos if
                       item["Months"] in month_list and item["CreditCode"] in credit_code_list and item.get(
                           "RemainFunding", 0) > 50 and not (item["CreditCode"] in ["A", "C"] and item["Months"] == 12) and item["ListingId"] not in self.listing_id_cache]
        # new_listing_id = list(set(listing_ids).difference(self.listing_id_cache))
        new_listing_id = [item["ListingId"] for item in listings]
        if new_listing_id:
            self.logger.info(
                f"find from O{self.client_index}: {len(listings)}, {new_listing_id},{self.loan_list_time_delta_sec}")
            self.listing_id_cache.extendleft(new_listing_id)

        return listings

    def get_loan_list_v3(self, filter_func):
        loan_infos = self.get_loan_list_items()

        if not loan_infos:
            return None

        listings = filter_func(loan_infos, self.listing_id_cache)
        # new_listing_id = list(set(listing_ids).difference(self.listing_id_cache))
        new_listing_id = [item["ListingId"] for item in listings]
        if new_listing_id:
            self.logger.info(
                f"find from O{self.client_index}: {len(listings)}, {new_listing_id},{self.loan_list_time_delta_sec}")
            self.listing_id_cache.extendleft(new_listing_id)

        return listings

    def batch_get_listing_info(self, listing_ids):
        listing_infos = []
        for index in range(0, len(listing_ids), 10):
            sub_listing_ids = listing_ids[index:index + 10]
            result = self.get_listing_info(sub_listing_ids)
            json_data = json.loads(result)

            if json_data.get("Result", -999) != 1:
                self.logger.warning(f"fetch loan list info result error: {json_data}")
                continue

            loan_infos = json_data.get("LoanInfos")
            if loan_infos:
                listing_infos.extend(loan_infos)

        return listing_infos


def auth():
    logger.info("start")
    client = PpdOpenClient(key_index=1)
    try:
        logger.info("Get access token")
        logger.info(client.get_access_token("97cbd7d978d542f59f767f63796494e4"))
    except Exception as ex:
        print("exception", ex)

def update_token():
    logger.info("start")

    # try:
    #     client = PpdOpenClient(key_index=1)
    #     logger.info("Get access token")
    #     openid = "a27effb5cc9f4d2fad1053642a155fe1"
    #     refresh_token = "2ed3d567594dfea0e1aa6a7ef7093f57e5683307b404fc326114ef5e"
    #     logger.info(client.refresh_token(openid, refresh_token))
    # except Exception as ex:
    #     print("exception", ex)

    try:
        client = PpdOpenClient(key_index=2)
        logger.info("Get access token")
        openid = "77e88d5ccb7d4ba6955c9e4a0e132dc6"
        refresh_token = "78ddd332594dfea0e1aa6a7ef7093f57d7d04bdbfaac9bf9956f11a2"
        logger.info(client.refresh_token(openid, refresh_token))
    except Exception as ex:
        print("exception", ex)



def main():
    # client = PpdOpenClient()

    client = PpdOpenClient(key_index=2)
    listing_ids = [129967042, 129967782]
    logger.info(client.private_key)

    try:
        # open_detail_infos = client.batch_get_listing_info(listing_ids)
        # print(json.dumps(open_detail_infos, indent=4, ensure_ascii=False))
        #
        # filtered_open_listing_ids = [item["ListingId"] for item in open_detail_infos if item.get("NormalCount", 0) > 20 and (item["NormalCount"] * 1.0 / (
        #             item["NormalCount"] + item["OverdueLessCount"] + item["OverdueMoreCount"])) > 0.9]
        # logger.info(f"filter listing id: {len(filtered_open_listing_ids)}, {len(open_detail_infos)} {filtered_open_listing_ids}")
        # logger.info(client.get_buy_list(levels="AA"))

        # print("")
        # print(client.get_debt_info([118691808, 118691802, 118691801]))

        # openid = "a27effb5cc9f4d2fad1053642a155fe1"
        # refresh_token = "2cdb8235594dfea0e1aa6a7ef7093f57dbdb96f607c79bcff16bf076"
        # print(client.refresh_token(openid, refresh_token))

        # openid = "77e88d5ccb7d4ba6955c9e4a0e132dc6"
        # refresh_token = "78ddd332594dfea0e1aa6a7ef7093f57d7d04bdbfaac9bf9956f11a2"
        # print(client.refresh_token(openid, refresh_token))

        logging.info(client.get_loan_list_ids(["B", "C"], [3, 6]))
        #
        # balance_result = client.get_query_balance()
        # balance_result = json.loads(balance_result, encoding="utf-8")
        # print(balance_result.get("Balance"))
        # if balance_result.get("Balance") and balance_result.get("Balance")[0].get("Balance") < 200:
        #     print("不足")
        # logger.info(balance_result)

        # logger.info(client.get_loan_list(time_delta_secs=-3000, page_index=1))

        # logger.info(client.get_bid_list(datetime.now() + timedelta(days=-30)))

        # loan_list = client.get_loan_list_v3(lambda loan_lists, listing_id_cache: [item for item in loan_lists if
        #                                                                        item["Months"] in [3, 6] and item[
        #                                                                            "CreditCode"] == "B" and item.get(
        #                                                                            "RemainFunding", 0) > 50 and item[
        #                                                                            "ListingId"] not in listing_id_cache])

        # filter_func = lambda loan_lists, listing_id_cache: [item for item in
        #                                                     loan_lists if item["Months"] in [3, 6, 12]
        #                                                       and item["CreditCode"] in ["AA", "A", "B", "C"]
        #                                                       and item.get("RemainFunding", 0) > 50
        #                                                       and item["ListingId"] not in listing_id_cache]
        # loan_list = client.get_loan_list_v3(filter_func)
        # logger.info(loan_list)

    except Exception as ex:
        print(ex)
    pass


if __name__ == "__main__":
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=10, format=logging_format)
    logger = logging.getLogger(__name__)

    try:
        # main()
        # auth()
        update_token()
    except Exception as ex:
        print(ex)