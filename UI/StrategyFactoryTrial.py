#!/usr/bin/python
import logging
import Utils
import sys
import os
import json

from Common.StrategyBase import StrategyBase as Strategy
from Common.UIStrategyFactory import UIStrategyFactory

class StrategyFactoryTrial(UIStrategyFactory):
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.strategy_list = []

        base_strategy = Strategy("自动1", "女年龄")
        base_strategy.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["性别", "==", "女", "str"],
            ["年龄", ">", "28", "int"],
            ["年龄", "<", "45", "int"],
            ["待还金额", "<", "20000", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["成功还款次数", ">", "0", "int"],
            ["待还金额/历史最高负债", "<", "0.9", "rate"],
            ["借款金额/单笔最高借款金额", "<", "0.9", "rate"],
            ["网络借贷平台借款余额", "<", "20000", "int"]
        ])

        base_strategy1 = Strategy("零逾期  ", "零逾期")
        base_strategy1.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["逾期（0-15天）还清次数", "==", "0", "int"],
            ["成功还款次数", ">", "40", "int"],
        ])

        base_strategy4 = Strategy("低逾期 ", "逾期<0.02")
        base_strategy4.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.05", "rate"],
            ["成功还款次数", ">", "50", "int"],
        ])

        base_strategy2 = Strategy("女标", "学历认证0逾期")
        base_strategy2.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["性别", "==", "女", "str"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["成功还款次数", ">", "20", "int"],
            ["文化程度", "!=", "无", "str"],
            ["逾期（0-15天）还清次数", "<", "5", "int"],
        ])

        base_strategy3 = Strategy("211本", "211学历认证0逾期")
        base_strategy3.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["毕业院校", "in", "School211", "str"],
            ["成功借款次数", "!=", "0", "int"],
            ["成功还款次数", ">", "5", "int"],
            ["文化程度", "!=", "专科", "str"],
            ["学习形式", "==", "普通", "str"]
            # ["逾期（0-15天）还清次数", "<", "5", "int"],
        ])

        self.strategy_list.append(base_strategy)
        self.strategy_list.append(base_strategy1)
        self.strategy_list.append(base_strategy2)
        self.strategy_list.append(base_strategy3)
        self.strategy_list.append(base_strategy4)


        base_strategy3 = Strategy("12月中女", "12月女 中年 逾期<0.02")
        base_strategy3.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "==", "12", "int"],
            ["性别", "==", "女", "str"],
            ["年龄", ">", "28", "int"],
            ["年龄", "<", "45", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],
            ["成功还款次数", ">", "50", "int"],
        ])
        self.strategy_list.append(base_strategy3)

        pass


import pandas as pd

def main():
    sf = StrategyFactoryTrial()
    logger = logging.getLogger(__name__)
    df = pd.read_csv("UIMain.csv", encoding="utf-8")

    # total = 0
    # success = 0
    # for listing_item in df.to_dict('records'):
    #     can_bid, first_strategy = sf.is_item_can_bid(listing_item)
    #     if can_bid:
    #         success += 1
    #         # print(first_strategy.strategy_detail())
    #         # logger.log(21, "bid: %s: %s %s", listing_item["listingId"], first_strategy, first_strategy.strategy_detail())
    #
    #     total += 1
    #
    # print(total, success)

    records = df.to_dict("records")

    print(sf.report(records, -300))

    print(records[-1])


def test():
    school_list = Utils.get_211_school()
    if "清华大学1" in school_list:
        print("exist")

if __name__ == "__main__":
    logging_format = '%(message)s'
    logging.basicConfig(level=15, format=logging_format)
    # Utils.setup_logging()

    # test()
    main()