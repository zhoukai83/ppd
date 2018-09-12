import sys
sys.path.insert(0, "..")
import pandas as pd
from pandas import DataFrame
import json
import time
import logging
from bsddb3 import db as bsddb3

from UISimulation.PpdUISimulationRequest import PpdUISimulationRequest
from UISimulation.FetchFromChrome import FetchFromChrome
from Common.UIStrategyFactory import UIStrategyFactory
from Common.StrategyFactory import StrategyFactory
from Common.StrategyBase import StrategyBase


class ShouldSendStrategyFactory(StrategyFactory):
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.strategy_list = []

        # if strategy_class is None:
        strategy_class = StrategyBase
        self.column_name_create_date = "creationDate"

        # strategy_class = OpenStrategy
        # self.column_name_create_date = "PreAuditTime"
        # PreAuditTime

        base_strategy1 = strategy_class("C零逾期 ", "C零逾期60")
        base_strategy1.add_filters([
            # ["逾期（15天以上）还清次数", ">", "0", "int"],
            # ["逾期（0-15天）还清次数", ">20", "0", "int"],
            # ["成功还款次数", "<", "10", "int"],  # 40 - 60
            # ["本次借款后负债/历史最高负债", ">", "1", "rate"],  # 0.7 - 0.96
            # ["借款金额/单笔最高借款金额", ">", "1", "rate"],
            ["网络借贷平台借款余额", ">", "20000", "int"]  # 8000 - 10000
        ])
        self.strategy_list.append(base_strategy1)


def get_no_listing_info_list():
    df_bid = pd.read_csv("BidList.csv", encoding="utf-8")
    print(df_bid.shape)
    df_bid = df_bid[df_bid["Rate"] > 13]
    print(df_bid.shape)

    df_listing_info = pd.read_csv("listing.csv", encoding="utf-8")
    no_listing_info_ids = []
    for listing_id in df_bid["ListingId"]:
        listing_info = df_listing_info[df_listing_info["listingId"] == listing_id]
        if not listing_info.empty:
            # print(listing_info.to_dict("records"))
            continue
        else:
            # print("no info", listing_id)
            no_listing_info_ids.append(listing_id)

    print(f"no listing info count: {len(no_listing_info_ids)}")
    return no_listing_info_ids


def get_listing_info():
    no_listing_info = get_no_listing_info_list()
    ppd_sim_client = PpdUISimulationRequest()

    df = pd.read_csv("listingInfo.csv", encoding="utf-8")

    with FetchFromChrome("17a175eaf36def04cfe4692791d51377") as fetch_from_chrome:
        cookies = fetch_from_chrome.get_cookie_string()
        ppd_sim_client.update_cookies(cookies)

        for listing_id in no_listing_info:
            item = ppd_sim_client.get_detail_info(listing_id)
            print(item)
            new_df = DataFrame([item])
            df = pd.concat([df, new_df])
            df.to_csv("listingInfo.csv", encoding="utf-8", index=False)
            time.sleep(3)


def find_should_send_listing():
    df_bid = pd.read_csv("BidList.csv", encoding="utf-8")
    print(df_bid.shape)
    df_bid = df_bid[df_bid["Rate"] > 13]
    print(df_bid.shape)

    # df_bid = df_bid[df_bid["ListingId"] == 120310821]

    sf = UIStrategyFactory()
    df_listing_info = pd.read_csv("listing.csv", encoding="utf-8")
    passed_count = 0
    failed_count = 0
    base_strategy1 = StrategyBase("C零逾期 ", "C零逾期60")
    base_strategy1.add_filters([
            # ["逾期（15天以上）还清次数", ">", "0", "int"],
            # ["逾期（0-15天）还清次数", ">", "20", "int"],
            # ["成功还款次数", "<", "10", "int"],  # 40 - 60
            # ["本次借款后负债/历史最高负债", ">", "1", "rate"],  # 0.7 - 0.96
            # ["借款金额/单笔最高借款金额", ">", "1", "rate"],
            ["网络借贷平台借款余额", ">", "100000", "int"]  # 8000 - 10000
        ])

    payoff_list = json.load(open("payoff.json"))
    print(payoff_list)

    for listing_id in df_bid["ListingId"]:
        if listing_id in payoff_list:
            continue

        listing_info = df_listing_info[df_listing_info["listingId"] == listing_id].to_dict("records")

        # print(json.dumps(item, indent=4, ensure_ascii=False))
        if listing_info:
            item = listing_info[0]
            can_bid = base_strategy1.is_item_can_bid(item)
            if can_bid:
                print(f"passed {listing_id}, {item}")
                passed_count += 1
            else:
                failed_count += 1
            # else:
            #     print(f"passed {listing_id}, {listing_info[0]}")
        # else:
        #     print("no listing info")

    # sf = ShouldSendStrategyFactory()
    # print(sf.report_passed(df_listing_info.to_dict("records")))
    print(passed_count, failed_count)



def main():
    find_should_send_listing()

    pass


if __name__ == "__main__":
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=20, format=logging_format)

    logger = logging.getLogger(__name__)
    main()