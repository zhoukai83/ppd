import logging
import logging.config
from Common import Utils
import sys
import os
import json
from Common.StrategyBase import StrategyBase
from Common.OpenStrategy import OpenStrategy

import pandas as pd


class StrategyFactory:
    def __init__(self, strategy_class=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.strategy_list = []

        if strategy_class is None:
            strategy_class = StrategyBase
            self.column_name_create_date = "creationDate"
        else:
            self.column_name_create_date = "PreAuditTime"
        # PreAuditTime

        # base_strategy = strategy_class("自动1  ", "女年龄")
        # base_strategy.add_filters([
        #     ["级别", "==", "B", "str"],
        #     ["期限", "<", "7", "int"],
        #     ["性别", "==", "女", "str"],
        #     ["年龄", ">", "28", "int"],
        #     ["年龄", "<", "45", "int"],
        #     ["待还金额", "<", "20000", "int"],
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     ["成功借款次数", "!=", "0", "int"],
        #     ["成功还款次数", ">", "20", "int"],
        #     ["待还金额/历史最高负债", "<", "0.9", "rate"],
        #     ["借款金额/单笔最高借款金额", "<", "0.9", "rate"],
        #     ["逾期（0-15天）还清次数/成功还款次数", "<", "0.03", "rate"],
        #     # ["网络借贷平台借款余额", "<", "20000", "int"]
        # ])
        # self.strategy_list.append(base_strategy)
        #
        # base_strategy1 = strategy_class("零逾期  ", "零逾期 40")
        # base_strategy1.add_filters([
        #     ["级别", "==", "B", "str"],
        #     ["期限", "<", "7", "int"],
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     ["成功借款次数", "!=", "0", "int"],
        #     ["逾期（0-15天）还清次数", "==", "0", "int"],
        #     ["成功还款次数", ">", "70", "int"],
        #     # ["网络借贷平台借款余额", "<", "30000", "int"]
        # ])
        # self.strategy_list.append(base_strategy1)
        #
        # base_strategy2 = strategy_class("女标   ", "女学历 逾期<5")
        # base_strategy2.add_filters([
        #     ["级别", "==", "B", "str"],
        #     ["期限", "<", "7", "int"],
        #     ["性别", "==", "女", "str"],
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     ["成功借款次数", "!=", "0", "int"],
        #     ["成功还款次数", ">", "30", "int"],
        #     ["文化程度", "!=", "无", "str"],
        #     ["逾期（0-15天）还清次数", "<", "3", "int"],
        #     ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],
        #     # ["网络借贷平台借款余额", "<", "20000", "int"]
        # ])
        # self.strategy_list.append(base_strategy2)
        #
        # base_strategy3 = strategy_class("低逾期 ", "逾期<0.02")
        # base_strategy3.add_filters([
        #     ["级别", "==", "B", "str"],
        #     ["期限", "<", "7", "int"],
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     ["成功借款次数", "!=", "0", "int"],
        #     ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],
        #     ["成功还款次数", ">", "80", "int"],
        #     # ["网络借贷平台借款余额", "<", "20000", "int"]
        # ])
        # self.strategy_list.append(base_strategy3)


        pass

    def is_item_can_bid(self, item, use_log=True):
        can_bid = False
        first_strategy = None

        if "listingId" in item:
            listing_id = item["listingId"]
        else:
            print(item)
            listing_id = item["ListingId"]

        for strategy_item in self.strategy_list:
            try:
                if strategy_item.is_item_can_bid(item):
                    if use_log:
                        self.logger.info("%s %s %s", "success", listing_id, strategy_item)
                    can_bid = True

                    if first_strategy is None and can_bid:
                        first_strategy = strategy_item
            except Exception as e:
                self.logger.error(f"{listing_id}:  {strategy_item}, {item}", exc_info=True)

        if not can_bid and use_log:
            self.logger.log(15, "%s %s", "failed ", listing_id)
        return can_bid, first_strategy

    def report(self, list_items, test_num=-100, use_log=True):
        success = 0
        total = 0
        total_succss = 0
        obj = {}
        for strategy_item in self.strategy_list:
            success = 0
            if use_log:
                self.logger.debug(f"\nuse strategy: {strategy_item}")
            for listing_item in list_items[test_num:]:
                if use_log:
                    self.logger.debug(f"\n {listing_item}")

                if strategy_item.is_item_can_bid(listing_item, use_log):
                    success += 1

            obj[str(strategy_item)] = success
            total_succss += success


            if use_log:
                self.logger.log(15, "%s %s \t %s", len(list_items), success, strategy_item)

        success = 0
        for listing_item in list_items[test_num:]:
            can_bid, first_strategy = self.is_item_can_bid(listing_item, use_log)
            if can_bid:
                success += 1
            total += 1

        obj["total"] = total
        obj["success"] = success
        obj["overlap"] = total_succss - obj["success"]
        return obj

    def report_all(self, list_items):
        result_list = []
        series_creation_date = pd.to_datetime(list_items[self.column_name_create_date])
        for date_item in pd.to_datetime(list_items[self.column_name_create_date]).dt.date.unique():
            next_day = pd.Timestamp(date_item) + pd.DateOffset(1)
            df = list_items[(series_creation_date > pd.Timestamp(date_item)) & (series_creation_date < next_day)]
            result = self.report(df.to_dict('records'), -3000, False)
            result["date"] = date_item
            result_list.append(result)

        df = pd.DataFrame.from_dict(result_list)
        column_names = list(df.columns.values)
        new_columns = ['date', 'total', 'success', 'overlap'] + column_names[4:]
        print(df[new_columns])


def test_ui():
    sf = StrategyFactory()
    df = pd.read_csv("..\\UI\\UIMain.csv", encoding="utf-8")
    df = df[df["期限"] != "12个月"]
    # print(sf.report(df.to_dict('records'), -100))
    sf.report_all(df)


def test_open():
    sf = StrategyFactory(OpenStrategy)
    df_listinginfo = pd.read_csv("..\\Open\\listingInfo.csv", encoding="utf-8")
    df_loanlist = pd.read_csv("..\\Open\\loanlist.csv", encoding="utf-8")
    df = pd.merge(df_loanlist, df_listinginfo, on="ListingId", suffixes=['', '_y'])
    # df = df[(df["Months"] < 12) & (df["CreditCode"] == "B")]
    df = df[(df["Months"] < 12) & (df["CreditCode"] == "B")]
    # df = df[df["ListingId"] == 126113392]

    # print(sf.is_item_can_bid(df.to_dict('records')[0]))
    # print(sf.report(df.to_dict('records'), -10000))
    sf.report_all(df)

def main():
    # test_ui()
    test_open()

if __name__ == "__main__":
    # logger = Utils.setup_logging()
    # logger.log(21, "bid: %s", "sss")
    # logger.info("test")
    logging_format = '%(message)s'
    logging.basicConfig(level=10, format=logging_format)

    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    main()
