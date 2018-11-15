import logging
import logging.config

import pandas as pd
import time

from Common.OpenStrategy import OpenStrategy
from Common.StrategyBase import StrategyBase
from Common.StrategyFactory import StrategyFactory


class UIStrategyFactory(StrategyFactory):
    # 网络借贷
    # 最高负债比
    # 还款次数 > 20
    # 借款金额/单笔最高借款金额

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.strategy_list = []

        # if strategy_class is None:
        strategy_class = StrategyBase
        self.column_name_create_date = "creationDate"

        # strategy_class = OpenStrategy
        # self.column_name_create_date = "PreAuditTime"
        # PreAuditTime

        # base_strategy = strategy_class("自动B", "女年龄")
        # base_strategy.add_filters([
        #     ["级别", "==", "B", "str"],
        #     ["期限", "<", "7", "int"],
        #     ["性别", "==", "女", "str"],
        #     ["年龄", ">", "28", "int"],
        #     ["年龄", "<", "45", "int"],
        #     ["待还金额", "<", "10000", "int"],                       # 12000 - 20000
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     # ["成功借款次数", "!=", "0", "int"],
        #     ["成功还款次数", ">", "30", "int"],
        #     ["本次借款后负债/历史最高负债", "<", "0.95", "rate"],              # 0.7 - 0.95
        #     # ["借款金额/单笔最高借款金额", "<", "0.98", "rate"],          # 0.7 - 0.95
        #     ["网络借贷平台借款余额", "<", "6000", "int"],              # 0  - 20000
        #     ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],    # 0.05
        # ])
        # self.strategy_list.append(base_strategy)

        # base_strategy1 = strategy_class("零逾B", "零逾期 40")
        # base_strategy1.add_filters([
        #     ["级别", "==", "B", "str"],
        #     ["期限", "<", "7", "int"],
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     ["逾期（0-15天）还清次数", "==", "0", "int"],
        #     ["成功还款次数", ">", "25", "int"],                     # 30 - 60
        #     ["本次借款后负债/历史最高负债", "<", "1", "rate"],  # 0.7 - 1
        #     # ["网络借贷平台借款余额", "<", "12000", "int"],            # 8000 - 10000
        #     ["借款金额/单笔最高借款金额", "<", "1", "rate"]
        # ])
        # self.strategy_list.append(base_strategy1)

        base_strategy2 = strategy_class("女学B", "逾期<5")
        base_strategy2.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["性别", "==", "女", "str"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["年龄", ">", "25", "int"],
            ["年龄", "<", "48", "int"],
            ["成功还款次数", ">", "35", "int"],             # 30 - 40
            ["文化程度", "!=", "无", "str"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.04", "rate"],  # 0.05
            ["本次借款后负债/历史最高负债", "<", "0.9", "rate"],  # 0.7 - 0.96
            ["借款金额/单笔最高借款金额", "<", "1", "rate"],
            ["网络借贷平台借款余额", "<", "10000", "int"]
        ])
        self.strategy_list.append(base_strategy2)

        # base_strategy_low_all = strategy_class("低逾", "<0.01")
        # base_strategy_low_all.add_filters([
        #     ["期限", "<", "7", "int"],
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     ["逾期（0-15天）还清次数/成功还款次数", "<", "0.03", "rate"],
        #     ["成功还款次数", ">", "40", "int"],
        #     ["本次借款后负债/历史最高负债", "<", "0.9", "rate"],  # 0.7 - 0.95
        #     ["借款金额/单笔最高借款金额", "<", "1", "rate"],
        #     # ["网络借贷平台借款余额", "<", "9000", "int"]
        # ])
        # self.strategy_list.append(base_strategy_low_all)

        base_strategy3 = strategy_class("低逾B", "<0.02")
        base_strategy3.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],
            ["成功还款次数", ">", "40", "int"],
            ["本次借款后负债/历史最高负债", "<", "0.88", "rate"],  # 0.7 - 0.95
            ["借款金额/单笔最高借款金额", "<", "0.95", "rate"],
            ["网络借贷平台借款余额", "<", "6000", "int"]
        ])
        self.strategy_list.append(base_strategy3)

        base_strategy_c1 = strategy_class("低逾C", ">60")
        base_strategy_c1.add_filters([
            ["级别", "==", "C", "str"],
            ["期限", "<", "7", "int"],
            ["成功还款次数", ">", "45", "int"],  # 40 - 60
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            # ["逾期（0-15天）还清次数", "==", "0", "int"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.01", "rate"],
            ["本次借款后负债/历史最高负债", "<", "0.88", "rate"],  # 0.7 - 0.96
            ["借款金额/单笔最高借款金额", "<", "0.95", "rate"],
            ["网络借贷平台借款余额", "<", "100", "int"]  # 8000 - 10000
        ])
        self.strategy_list.append(base_strategy_c1)
        #
        base_strategy_a1 = strategy_class("低逾A6", ">30")
        base_strategy_a1.add_filters([
            ["级别", "==", "A", "str"],
            ["期限", "==", "6", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.03", "rate"],
            ["成功还款次数", ">", "35", "int"],  # 20 - 60
            ["本次借款后负债/历史最高负债", "<", "0.94", "rate"],  # 0.7 - 1
            ["借款金额/单笔最高借款金额", "<", "0.97", "rate"],
            ["网络借贷平台借款余额", "<", "7000", "int"]  # 8000 - 10000
        ])
        self.strategy_list.append(base_strategy_a1)

        base_strategy_a_3 = strategy_class("低逾A3", ">30")
        base_strategy_a_3.add_filters([
            ["级别", "==", "A", "str"],
            ["期限", "==", "3", "int"],
            ["逾期（15天以上）还清次数/成功还款次数", "<", "0.01", "rate"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.1", "rate"],
            ["成功还款次数", ">", "25", "int"],  # 20 - 60
            ["本次借款后负债/历史最高负债", "<", "1", "rate"],  # 0.7 - 1
            ["借款金额/单笔最高借款金额", "<", "1", "rate"],
            ["网络借贷平台借款余额", "<", "8000", "int"]  # 8000 - 10000
        ])
        self.strategy_list.append(base_strategy_a_3)

        base_strategy_b_3 = strategy_class("低逾B3", "<0.08")
        base_strategy_b_3.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "4", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],
            ["成功还款次数", ">", "30", "int"],
            ["本次借款后负债/历史最高负债", "<", "0.98", "rate"],  # 0.7 - 0.95
            ["借款金额/单笔最高借款金额", "<", "0.98", "rate"],
            ["网络借贷平台借款余额", "<", "7000", "int"]
        ])
        self.strategy_list.append(base_strategy_b_3)

        # base_strategy_b_12 = strategy_class("低逾B12", ">60")
        # base_strategy_b_12.add_filters([
        #     ["级别", "==", "B", "str"],
        #     ["期限", "==", "12", "int"],
        #     ["成功还款次数", ">", "45", "int"],  # 40 - 60
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     ["逾期（0-15天）还清次数/成功还款次数", "<", "0.02", "rate"],
        #     ["本次借款后负债", "<", "8000", "int"],
        #     ["本次借款后负债/历史最高负债", "<", "0.95", "rate"],  # 0.7 - 0.96
        #     ["借款金额/单笔最高借款金额", "<", "0.99", "rate"],
        #     ["网络借贷平台借款余额", "<", "1", "int"]  # 8000 - 10000
        # ])
        # self.strategy_list.append(base_strategy_b_12)

        # base_strategy_low_all = strategy_class("低逾", ">100")
        # base_strategy_low_all.add_filters([
        #     ["成功还款次数", ">", "80", "int"],  # 40 - 60
        #     ["逾期（15天以上）还清次数", "==", "0", "int"],
        #     ["逾期（0-15天）还清次数/成功还款次数", "<", "0.01", "rate"],
        #     ["本次借款后负债/历史最高负债", "<", "1", "rate"],  # 0.7 - 0.96
        #     ["借款金额/单笔最高借款金额", "<", "1", "rate"],
        #     # ["网络借贷平台借款余额", "<", "5000", "int"]  # 8000 - 10000
        # ])
        # self.strategy_list.append(base_strategy_low_all)
        pass


def test_ui():
    sf = UIStrategyFactory()
    file_path = "..\\UI\\UIMain.csv"
    # file_path = "..\\UISimulation\\UISimulationMain.csv"
    df = pd.read_csv(file_path, encoding="utf-8")
    df = df[df["期限"] != "12个月"]
    # print(sf.report(df.to_dict('records'), -100))
    sf.report_all(df)


def test_ui_today():
    sf = UIStrategyFactory()
    df = pd.read_csv("..\\UI\\UIMain.csv", encoding="utf-8")
    df = df[df["期限"] != "12个月"]

    series_creation_date = pd.to_datetime(df["creationDate"])
    current_day = pd.to_datetime('today').strftime("%m/%d/%Y")
    print(current_day)

    next_day = pd.Timestamp(current_day) + pd.DateOffset(1)
    df = df[(series_creation_date > pd.Timestamp(current_day)) & (series_creation_date < next_day)]
    # print(df.shape)
    result = sf.report(df.to_dict('records'), -3000, True)

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


def test_open():
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


def test_ui_sim_main():
    sf = UIStrategyFactory()
    df = pd.read_csv("..\\UISimulation\\UISimMain.csv", encoding="utf-8")
    series_creation_date = pd.to_datetime(df["creationDate"])
    current_day = pd.to_datetime('today').strftime("%m/%d/%Y")
    print(current_day)

    next_day = pd.Timestamp(current_day) + pd.DateOffset(1)
    df = df[(series_creation_date > pd.Timestamp(current_day)) & (series_creation_date < next_day)]
    # print(df.shape)
    result = sf.report(df.to_dict('records'), -3000, True)

def test_new_strategy():
    class NewStrategyFactory(StrategyFactory):
        def __init__(self, logger=None):
            self.logger = logger or logging.getLogger(__name__)
            self.strategy_list = []
            strategy_class = StrategyBase
            self.column_name_create_date = "creationDate"
            base_strategy_b_12 = strategy_class("低逾B12", ">60")
            base_strategy_b_12.add_filters([
                ["级别", "==", "B", "str"],
                ["期限", "==", "12", "int"],
                ["成功还款次数", ">", "50", "int"],  # 40 - 60
                ["逾期（15天以上）还清次数", "==", "0", "int"],
                ["逾期（0-15天）还清次数", "==", "0", "int"],
                ["逾期（0-15天）还清次数/成功还款次数", "<", "0.1", "rate"],
                ["本次借款后负债", "<", "10000", "int"],
                ["本次借款后负债/历史最高负债", "<", "0.90", "rate"],  # 0.7 - 0.96
                ["借款金额/单笔最高借款金额", "<", "0.95", "rate"],
                ["网络借贷平台借款余额", "<", "1", "int"]  # 8000 - 10000
            ])
            self.strategy_list.append(base_strategy_b_12)
            pass

    sf = NewStrategyFactory()
    df = pd.read_csv("..\\UISimulation\\UISimMain.csv", encoding="utf-8")
    series_creation_date = pd.to_datetime(df["creationDate"])
    current_day = pd.to_datetime('today').strftime("%m/%d/%Y")
    print(current_day)

    next_day = pd.Timestamp(current_day) + pd.DateOffset(1)
    df = df[(series_creation_date > pd.Timestamp(current_day)) & (series_creation_date < next_day)]
    # print(df.shape)
    result = sf.report(df.to_dict('records'), -3000, True)

def main():
    # test_ui()
    test_new_strategy()
    # test_ui_today()
    # test_overdue()
    # test_ui_base_strategy_factory()
    # test_open()

if __name__ == "__main__":
    # logger = Utils.setup_logging()
    # logger.log(21, "bid: %s", "sss")
    # logger.info("test")
    logging_format = '%(message)s'
    logging.basicConfig(level=20, format=logging_format)

    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    start = time.time()
    main()
    print(f"End: {time.time() - start}")
