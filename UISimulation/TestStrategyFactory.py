import logging
import logging.config

import pandas as pd
import time

from Common.OpenStrategy import OpenStrategy
from Common.StrategyBase import StrategyBase
from Common.StrategyFactory import StrategyFactory
from Common.UIStrategyFactory import UIStrategyFactory


file_path = "..\\UISimulation\\UISimMain.csv"

def test_last_item():
    sf = UIStrategyFactory(logger=logger)
    df = pd.read_csv(file_path, encoding="utf-8")
    df = df[df["期限"] != 12]

    df = df[df["listingId"] == 127171391]
    # print(sf.report(df.to_dict('records'), -100))
    records = df.to_dict("records")
    item = records[-1]
    sf.is_item_can_bid(item, True)


def test_ui():
    sf = UIStrategyFactory()
    df = pd.read_csv(file_path, encoding="utf-8")
    df = df[df["期限"] != 12]
    # print(sf.report(df.to_dict('records'), -100))
    sf.report_all(df)


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
    test_ui_today()

    test_last_item()
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
