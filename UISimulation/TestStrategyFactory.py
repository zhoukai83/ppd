import logging
import logging.config

import pandas as pd
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 10000)
pd.set_option('max_colwidth', 400)
pd.set_option("display.width", 100)

from Common.OpenStrategy import OpenStrategy
from Common.StrategyBase import StrategyBase
from Common.StrategyFactory import StrategyFactory
from Common.UIStrategyFactory import UIStrategyFactory


file_path = "..\\UISimulation\\UISimMain.csv"


class NewStrategyFactory(StrategyFactory):
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.strategy_list = []

        # if strategy_class is None:
        strategy_class = StrategyBase
        self.column_name_create_date = "creationDate"

        # strategy_class = OpenStrategy
        # self.column_name_create_date = "PreAuditTime"
        # PreAuditTime

        # base_strategy_c1 = strategy_class("C零逾期 ", "C零逾期60")
        # base_strategy_c1.add_filters([
        #     ["级别", "==", "C", "str"],
        #     ["期限", "<", "7", "int"],
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     ["成功借款次数", "!=", "0", "int"],
        #     ["逾期（0-15天）还清次数", "==", "0", "int"],
        #     ["成功还款次数", ">", "60", "int"],  # 40 - 60
        #     ["本次借款后负债/历史最高负债", "<", "0.93", "rate"],  # 0.7 - 0.96
        #     ["借款金额/单笔最高借款金额", "<", "0.93", "rate"],
        #     ["网络借贷平台借款余额", "<", "1", "int"]  # 8000 - 10000
        # ])
        # self.strategy_list.append(base_strategy_c1)

        base_strategy_a1 = strategy_class("低逾期A ", "")
        base_strategy_a1.add_filters([
            ["级别", "==", "A", "str"],
            ["期限", "<", "7", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功还款次数", ">", "24", "int"],  # 40 - 60
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.04", "rate"],
            ["本次借款后负债/历史最高负债", "<", "0.98", "rate"],  # 0.7 - 0.96
            ["网络借贷平台借款余额", "<", "8000", "int"]  # 8000 - 10000
        ])
        self.strategy_list.append(base_strategy_a1)

        # base_strategy3 = strategy_class("低逾期 ", "逾期<0.02")
        # base_strategy3.add_filters([
        #     ["级别", "==", "C", "str"],
        #     ["期限", "<", "7", "int"],
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     ["成功借款次数", "!=", "0", "int"],
        #     ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],
        #     ["成功还款次数", ">", "50", "int"],
        #     ["本次借款后负债/历史最高负债", "<", "0.93", "rate"],  # 0.7 - 0.95
        #     ["借款金额/单笔最高借款金额", "<", "0.98", "rate"],
        #     ["网络借贷平台借款余额", "<", "6000", "int"]
        # ])
        # self.strategy_list.append(base_strategy3)
        pass


def test_last_item():
    sf = UIStrategyFactory(logger=logger)
    df = pd.read_csv(file_path, encoding="utf-8")
    df = df[df["期限"] != 12]

    df = df[df["listingId"] == 127817865]
    # print(sf.report(df.to_dict('records'), -100))
    records = df.to_dict("records")
    item = records[-1]
    sf.is_item_can_bid(item, True, True)


def test_ui():
    sf = UIStrategyFactory()
    df = pd.read_csv(file_path, encoding="utf-8")
    df = df[df["期限"] != 12]
    # print(sf.report(df.to_dict('records'), -100))
    sf.report_all(df)


def test_c():
    sf = NewStrategyFactory()
    df = pd.read_csv(file_path, encoding="utf-8")
    df = df[(df["期限"] != 12) & (df["级别"] == "C")]
    # print(sf.report(df.to_dict('records'), -100))
    # sf.report_all(df)
    # sf.report(df.to_dict("records"))
    sf.report_passed(df.to_dict("records"))

def test_a():
    sf = NewStrategyFactory()
    df = pd.read_csv(file_path, encoding="utf-8")
    df = df[(df["期限"] != 12) & (df["级别"] == "A")]
    # print(sf.report(df.to_dict('records'), -100))
    # sf.report_all(df)
    # sf.report(df.to_dict("records"))
    sf.report_passed(df.to_dict("records"))

def test_ui_today():
    sf = UIStrategyFactory()
    df = pd.read_csv(file_path, encoding="utf-8")
    df = df[df["期限"] != 12]

    series_creation_date = pd.to_datetime(df["creationDate"])
    current_day = pd.to_datetime('today').strftime("%m/%d/%Y")
    print(current_day)

    next_day = pd.Timestamp(current_day) + pd.DateOffset(1)
    # df = df[(series_creation_date > pd.Timestamp(current_day)) & (series_creation_date < next_day)]
    print(df.shape)
    result = sf.report(df.to_dict('records'), -3000, False, True)

    # print(sf.report(df.to_dict('records'), -100))
    # sf.report_all(df)


def test_ui_base_strategy_factory():
    sf = UIStrategyFactory(OpenStrategy)
    df_listinginfo = pd.read_csv("..\\Open\\listingInfo.csv", encoding="utf-8")
    df_loanlist = pd.read_csv("..\\Open\\loanlist.csv", encoding="utf-8")
    df = pd.merge(df_loanlist, df_listinginfo, on="ListingId", suffixes=['', '_y'])
    # df = df[(df["Months"] < 12) & (df["CreditCode"] == "B")]
    df = df[(df["Months"] < 12) & (df["CreditCode"] == "B")]
    # df = df[df["ListingId"] == 126113392]

    # print(sf.is_item_can_bid(df.to_dict('records')[0]))
    # print(sf.report(df.to_dict('records'), -10000))
    sf.report_all(df)


def test_overdue():
    import json
    sf = UIStrategyFactory()
    df = pd.read_csv("..\\UI\\UIOverDue.csv", encoding="utf-8")
    df['期限'] = df['期限'].str.extract('(\d+)').astype(int)
    df = df[df["期限"] < 12]
    df["逾期（15天以上）还清次数"] = df["逾期(15天以上)还清次数"]
    df["逾期（0-15天）还清次数"] = df["逾期(0-15天)还清次数"]
    df["级别"] = "B"
    # sf.report_all(df)
    obj = sf.report(df.to_dict("records"))


    print(json.dumps(obj, indent=4, ensure_ascii=False))


def main():
    test_ui()

    # test_a()
    # test_ui_today()

    # test_last_item()
    # test_overdue()
    # test_ui_base_strategy_factory()

if __name__ == "__main__":
    # logger = Utils.setup_logging()
    # logger.log(21, "bid: %s", "sss")
    # logger.info("test")
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logger = logging.basicConfig(level=10, format=logging_format)

    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    start = time.time()
    main()
    print(f"End: {time.time() - start}")
