import logging
import logging.config
import Utils
import sys
import os
import json

item = {"listingId": 124795277, "借款用途": "日常消费", "借款金额": "¥18,925", "其他事项": "暂无", "协议利率": "20%",
        "单笔最高借款金额": "¥11,900.00", "历史最高负债": "¥13,151.10", "历史记录": "0次流标， 0次撤标， 0次失败", "学习形式": "无", "工作信息": "私营业主",
        "年龄": "27", "征信记录": "暂未提供", "待还金额": "¥2,112.52", "性别": "女", "成功借款次数": "5次", "成功还款次数": "21次", "收入情况": "暂未提供",
        "文化程度": "无", "期限": "6个月", "正常还清次数": "21次", "毕业院校": "无", "注册时间": "2017/03/14", "第一次成功借款时间": "2017/03/14",
        "累计借款金额": "¥35,708.00", "级别": "B", "网络借贷平台借款余额": "暂未提供", "资金运用情况": "日常消费", "还款来源": "个人存款",
        "逾期（0-15天）还清次数": "0次", "逾期（15天以上）还清次数": "0次"}

def setup_logging(default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    logger = logging.getLogger(__name__)
    logger.info("start")
    return logger


class FilterItem():
    def __init__(self, key, compare, value, type):
        self.key = key
        self.compare = compare
        self.value = value
        self.type = type

    def __str__(self):
        return "{0} \t {1} {2} {3}".format(self.type, self.key, self.compare, self.value)


class BaseStrategy():
    def __init__(self, name, description, logger=None):
        self.name = name
        self.description = description
        self.logger = logger or logging.getLogger(__name__)
        self.filters = []

    def __str__(self):
        return "{0}:{1}".format(self.name, self.description)

    def add_filter(self, key, compare, value, type=None):
        self.filters.append(FilterItem(key, compare, value, type))
        return self

    def add_filters(self, filter_list):
        for filter_item in filter_list:
            self.add_filter(filter_item[0], filter_item[1], filter_item[2], filter_item[3])

    def is_item_can_bid(self, item):
        can_bid = True
        for filter_item in self.filters:
            key = filter_item.key
            compare = filter_item.compare
            value_type = filter_item.type
            value = filter_item.value

            filter_item_result = False
            if key not in item and value_type != "rate":
                self.logger.info(key + "not exist")
                can_bid = False
                continue

            should_convert_to_number = compare == ">" or compare == "<"
            if value_type == "int":
                actual_value = Utils.convert_to_int(item[key])
                expected_value = Utils.convert_to_int(value)
            elif value_type == "rate":
                key_pair = key.split("/")
                denominator = Utils.convert_to_float(item[key_pair[1]])
                if denominator == 0:
                    actual_value = 0
                else:
                    actual_value = round(Utils.convert_to_float(item[key_pair[0]]) / denominator, 3)
                expected_value = Utils.convert_to_float(value)
            elif should_convert_to_number:
                actual_value = Utils.convert_to_float(item[key])
                expected_value = Utils.convert_to_float(value)
            else:
                actual_value = item[key]
                expected_value = value

            if compare == "!=":
                filter_item_result = expected_value != actual_value
            elif compare == "==":
                filter_item_result = expected_value == actual_value
            elif compare == ">":
                filter_item_result = actual_value > expected_value
            elif compare == "<":
                filter_item_result = actual_value < expected_value
            else:
                self.logger.error("not support")
                filter_item_result = False

            self.logger.debug("{0: <5} {1: <7} {2: <7} {3}".format(str(filter_item_result), actual_value, expected_value, filter_item))
            # print(filter_item_result, "\t", actual_value, expected_value, "\t", filter_item)
            if not filter_item_result:
                self.logger.debug(
                    "{0: <5} {1: <7} {2: <7} {3}".format(str(filter_item_result), actual_value, expected_value,
                                                         filter_item))
                can_bid = False

        return can_bid


class StrategyFactory():
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.strategy_list = []

        base_strategy = BaseStrategy("自动1", "女年龄")
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
            ["借款金额/单笔最高借款金额", "<", "0.9", "rate"]
        ])

        base_strategy1 = BaseStrategy("低息飞首", "0逾期非首届，16%投标利率")
        base_strategy1.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["逾期（0-15天）还清次数", "==", "0", "int"],
            ["成功还款次数", ">", "0", "int"]
        ])

        base_strategy2 = BaseStrategy("女标", "学历认证0逾期")
        base_strategy2.add_filters([
            ["级别", "==", "B", "str"],
            ["期限", "<", "7", "int"],
            ["性别", "==", "女", "str"],
            ["逾期（15天以上）还清次数", "==", "0", "int"],
            ["成功借款次数", "!=", "0", "int"],
            ["成功还款次数", ">", "0", "int"],
            ["文化程度", "!=", "无", "str"]
        ])



        self.strategy_list.append(base_strategy)
        # self.strategy_list.append(base_strategy1)

        self.strategy_list.append(base_strategy2)
        pass

    def is_item_can_bid(self, item):
        can_bid = False
        for strategy_item in self.strategy_list:
            if strategy_item.is_item_can_bid(item):
                self.logger.info("%s %s %s", item["listingId"], "success", strategy_item)
                can_bid = True

        if not can_bid:
            self.logger.info("%s %s", item["listingId"], "failed")
        return can_bid

class BidStrategy():
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def is_item_can_bid(self, item):
        if item["级别"] != "B":
            self.logger.info("level not ok")
            return False

        if item["性别"] != "女":
            self.logger.info("sex not ok")
            return False

        month = Utils.convert_to_int(item["期限"])
        if month >= 12:
            self.logger.info("month not ok")
            return False

        if int(item["年龄"]) < 27:
            self.logger.info("age lower")
            return False

        if int(item["年龄"]) > 50:
            self.logger.info("age large")
            return False

        if Utils.convert_to_int(item["逾期（15天以上）还清次数"]) > 0:
            self.logger.info("15 days > 0")
            return False

        if Utils.convert_to_int(item["成功借款次数"]) < 2:
            self.logger.info("成功借款次数 not ok")
            return False

        if Utils.convert_to_int(item["成功还款次数"]) < 3:
            self.logger.info("成功还款次数 not ok")
            return False

        need_pay = Utils.convert_currency_to_float(item["待还金额"])
        max_pay = Utils.convert_currency_to_float(item["历史最高负债"])
        if need_pay / max_pay > 0.9:
            self.logger.info("need pay / max pay > 0.9")
            return False

        return True
        pass

def test_level():
    print(sys._getframe().f_code.co_name)
    base_strategy1 = BaseStrategy("低息飞首", "0逾期非首届，16%投标利率")
    base_strategy1.add_filter("级别", "==", "B", "str")
    can_bid = base_strategy1.is_item_can_bid(item)
    print(can_bid)

    item["级别"] = "B"
    can_bid = base_strategy1.is_item_can_bid(item)
    print(can_bid)

def test_month():
    print(sys._getframe().f_code.co_name)
    base_strategy1 = BaseStrategy("低息飞首", "0逾期非首届，16%投标利率")
    base_strategy1.add_filter("期限", "<", "12")
    can_bid = base_strategy1.is_item_can_bid(item)
    print(can_bid)

    item["期限"] = "12"
    can_bid = base_strategy1.is_item_can_bid(item)
    print(can_bid)

def test_strategy1():
    strategy_factory = StrategyFactory()
    base_strategy1 = BaseStrategy("低息飞首", "0逾期非首届，16%投标利率")
    base_strategy1.add_filters([
        ["级别", "==", "B", "str"],
        ["期限", "<", "12", "int"],
        ["逾期（15天以上）还清次数", "==", "0", "int"],
        ["成功借款次数", "!=", "0", "int"],
        ["逾期（0-15天）还清次数", "==", "0", "int"],
        ["成功还款次数", ">", "0", "int"]
    ])
    can_bid = base_strategy1.is_item_can_bid(item)
    print(can_bid, base_strategy1, "\r\n")
    print("stratery", strategy_factory.is_item_can_bid(item), "\r\n")

def test_strategy2():
    base_strategy2 = BaseStrategy("女标", "学历认证0逾期")
    base_strategy2.add_filters([
        ["级别", "==", "B", "str"],
        ["期限", "<", "12", "int"],
        ["性别", "==", "女", "str"],
        ["逾期（15天以上）还清次数", "==", "0", "int"],
        ["成功借款次数", "!=", "0", "int"],
        ["成功还款次数", ">", "0", "int"]
    ])
    can_bid = base_strategy2.is_item_can_bid(item)
    print(can_bid, base_strategy2, "\r\n")

    item["性别"] = "男"
    can_bid = base_strategy2.is_item_can_bid(item)
    print(can_bid, base_strategy2, "\r\n")

    del item["性别"]
    can_bid = base_strategy2.is_item_can_bid(item)
    print(can_bid, base_strategy2, "\r\n")


def test_strategy_auto():
    base_strategy2 = BaseStrategy("自动1", "女年龄")
    base_strategy2.add_filters([
        ["级别", "==", "B", "str"],
        ["期限", "<", "4", "int"],
        ["性别", "==", "女", "str"],
        ["年龄", ">", "28", "int"],
        ["年龄", "<", "45", "int"],
        ["待还金额", "<", "20000", "int"],
        ["逾期（15天以上）还清次数", "==", "0", "int"],
        ["成功借款次数", "!=", "0", "int"],
        ["成功还款次数", ">", "0", "int"],
        ["待还金额/历史最高负债", "<", "0.9", "rate"],
        ["借款金额/单笔最高借款金额", "<", "0.9", "rate"]
    ])
    item["性别"] = "女"
    item["年龄"] = "30"
    can_bid = base_strategy2.is_item_can_bid(item)
    print(can_bid, base_strategy2, "\r\n")

    item["性别"] = "男"
    can_bid = base_strategy2.is_item_can_bid(item)
    print(can_bid, base_strategy2, "\r\n")

    del item["性别"]
    can_bid = base_strategy2.is_item_can_bid(item)
    print(can_bid, base_strategy2, "\r\n")

def test():
    test_level()
    test_month()

    test_strategy1()
    test_strategy2()


import pandas as pd

def main():
    # test_strategy_auto()
    sf = StrategyFactory()

    df = pd.read_csv("UIMain.csv", encoding="utf-8")
    for listing_item in df.to_dict('records'):
        sf.is_item_can_bid(listing_item)


if __name__ == "__main__":
    setup_logging()
    # main()
    # test()

    main()