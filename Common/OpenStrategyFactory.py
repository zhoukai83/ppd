import logging
import logging.config
from Common import Utils
import sys
import os
import json
from Common.StrategyBase import StrategyBase
from Common.OpenStrategy import OpenStrategy
from Common.StrategyFactory import StrategyFactory

import pandas as pd


class OpenStrategyFactory(StrategyFactory):
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.strategy_list = []

        # if strategy_class is None:
        #     strategy_class = StrategyBase
        #     self.column_name_create_date = "creationDate"
        # else:
        strategy_class = OpenStrategy
        self.column_name_create_date = "PreAuditTime"
        # PreAuditTime

        base_strategy = strategy_class("自动1  ", "女年龄")
        base_strategy.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["性别", "==", "女", "str"],
            ["年龄", ">", "28", "int"],
            ["年龄", "<", "45", "int"],
            ["待还金额", "<", "20000", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["成功还款次数", ">", "20", "int"],
            ["待还金额/历史最高负债", "<", "0.9", "rate"],
            ["借款金额/单笔最高借款金额", "<", "0.9", "rate"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.03", "rate"],
            # ["网络借贷平台借款余额", "<", "20000", "int"]
        ])
        self.strategy_list.append(base_strategy)

        base_strategy1 = strategy_class("零逾期  ", "零逾期 40")
        base_strategy1.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["逾期（0-15天）还清次数", "==", "0", "int"],
            ["成功还款次数", ">", "70", "int"],
            # ["网络借贷平台借款余额", "<", "30000", "int"]
        ])
        self.strategy_list.append(base_strategy1)

        base_strategy2 = strategy_class("女标   ", "女学历 逾期<5")
        base_strategy2.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["性别", "==", "女", "str"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["成功还款次数", ">", "30", "int"],
            ["文化程度", "!=", "无", "str"],
            ["逾期（0-15天）还清次数", "<", "3", "int"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],
            # ["网络借贷平台借款余额", "<", "20000", "int"]
        ])
        self.strategy_list.append(base_strategy2)

        base_strategy3 = strategy_class("低逾期 ", "逾期<0.02")
        base_strategy3.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],
            ["成功还款次数", ">", "80", "int"],
            # ["网络借贷平台借款余额", "<", "20000", "int"]
        ])
        self.strategy_list.append(base_strategy3)
        pass


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
    logging.basicConfig(level=15, format=logging_format)

    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    main()
