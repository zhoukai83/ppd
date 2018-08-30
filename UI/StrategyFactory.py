import logging
import logging.config
import Utils
import sys
import os
import json
from Strategy import Strategy
import pandas as pd


class StrategyFactory:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.strategy_list = []

        base_strategy = Strategy("自动1  ", "女年龄")
        base_strategy.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["性别", "==", "女", "str"],
            ["年龄", ">", "28", "int"],
            ["年龄", "<", "45", "int"],
            ["待还金额", "<", "20000", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["成功还款次数", ">", "10", "int"],
            ["待还金额/历史最高负债", "<", "0.9", "rate"],
            ["借款金额/单笔最高借款金额", "<", "0.9", "rate"],
            ["网络借贷平台借款余额", "<", "20000", "int"]
        ])
        self.strategy_list.append(base_strategy)

        base_strategy1 = Strategy("零逾期  ", "零逾期 40")
        base_strategy1.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["逾期（0-15天）还清次数", "==", "0", "int"],
            ["成功还款次数", ">", "40", "int"],
            ["网络借贷平台借款余额", "<", "30000", "int"]
        ])
        self.strategy_list.append(base_strategy1)

        base_strategy2 = Strategy("女标   ", "女学历 逾期<5")
        base_strategy2.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["性别", "==", "女", "str"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["成功还款次数", ">", "20", "int"],
            ["文化程度", "!=", "无", "str"],
            ["逾期（0-15天）还清次数", "<", "4", "int"],
            ["网络借贷平台借款余额", "<", "20000", "int"]
        ])
        self.strategy_list.append(base_strategy2)

        base_strategy3 = Strategy("低逾期 ", "逾期<0.02")
        base_strategy3.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],
            ["成功还款次数", ">", "50", "int"],
            ["网络借贷平台借款余额", "<", "20000", "int"]
        ])
        self.strategy_list.append(base_strategy3)


        pass

    def is_item_can_bid(self, item, use_log=True):
        can_bid = False
        first_strategy = None
        for strategy_item in self.strategy_list:
            try:
                if strategy_item.is_item_can_bid(item):
                    if use_log:
                        self.logger.info("%s %s %s", "success", item["listingId"], strategy_item)
                    can_bid = True

                    if first_strategy is None and can_bid:
                        first_strategy = strategy_item
            except Exception as e:
                self.logger.error(e, exc_info=True)

        if not can_bid and use_log:
            self.logger.log(15, "%s %s", "failed ", item["listingId"])
        return can_bid, first_strategy

    def report(self, list_items, test_num=-100, use_log=True):
        success = 0
        total = 0

        obj = {}
        for listing_item in list_items[test_num:]:
            can_bid, first_strategy = self.is_item_can_bid(listing_item, use_log)
            if can_bid:
                success += 1
                # print(first_strategy.strategy_detail())
                # logger.log(21, "bid: %s: %s %s", listing_item["listingId"], first_strategy, first_strategy.strategy_detail())

            total += 1

        obj = {"total": total, "success": success}
        total_succss = 0
        for strategy_item in self.strategy_list:
            success = 0
            for listing_item in list_items[test_num:]:
                if strategy_item.is_item_can_bid(listing_item):
                    success += 1

            obj[str(strategy_item)] = success

            total_succss += success

            if use_log:
                self.logger.log(15, "%s %s \t %s", len(list_items), success, strategy_item)

        obj["overlap"] = total_succss - obj["success"]
        # print(obj)
        return obj

    def report_all(self, list_items):
        result_list = []
        series_creation_date = pd.to_datetime(list_items["creationDate"])
        for date_item in pd.to_datetime(list_items["creationDate"]).dt.date.unique():
            next_day = pd.Timestamp(date_item) + pd.DateOffset(1)
            df = list_items[(series_creation_date > pd.Timestamp(date_item)) & (series_creation_date < next_day)]
            result = self.report(df.to_dict('records'), -3000, False)
            result["date"] = date_item
            result_list.append(result)

        df = pd.DataFrame.from_dict(result_list)
        column_names = list(df.columns.values)
        new_columns = ['date', 'total', 'success', 'overlap'] + column_names[4:]
        print(df[new_columns])


def main():
    sf = StrategyFactory()

    df = pd.read_csv("UIMain.csv", encoding="utf-8")
    df = df[df["期限"] != "12个月"]
    total = 0
    success = 0
    # df = df[pd.to_datetime(df["creationDate"]) > pd.Timestamp(pd.datetime.now().date())]
    # for listing_item in df.to_dict('records'):
    #     can_bid, first_strategy = sf.is_item_can_bid(listing_item)
    #     if can_bid:
    #         success += 1
    #         # print(first_strategy.strategy_detail())
    #     total += 1

    sf.report_all(df)
    # print(sf.report(df.to_dict('records'), -3000))
    # print(total, success)

if __name__ == "__main__":
    # logger = Utils.setup_logging()
    # logger.log(21, "bid: %s", "sss")
    # logger.info("test")
    logging_format = '%(message)s'
    logging.basicConfig(level=15, format=logging_format)
    main()
