import logging
import Utils
import sys
import os

item = {"listingId": 124795277, "借款用途": "日常消费", "借款金额": "¥18,925", "其他事项": "暂无", "协议利率": "20%",
        "单笔最高借款金额": "¥11,900.00", "历史最高负债": "¥13,151.10", "历史记录": "0次流标， 0次撤标， 0次失败", "学习形式": "无", "工作信息": "私营业主",
        "年龄": "27", "征信记录": "暂未提供", "待还金额": "¥2,112.52", "性别": "女", "成功借款次数": "5次", "成功还款次数": "21次", "收入情况": "暂未提供",
        "文化程度": "无", "期限": "6个月", "正常还清次数": "21次", "毕业院校": "无", "注册时间": "2017/03/14", "第一次成功借款时间": "2017/03/14",
        "累计借款金额": "¥35,708.00", "级别": "B", "网络借贷平台借款余额": "暂未提供", "资金运用情况": "日常消费", "还款来源": "个人存款",
        "逾期（0-15天）还清次数": "0次", "逾期（15天以上）还清次数": "0次"}


class StrategyFilterItem:
    def __init__(self, key, compare, value, type):
        self.key = key
        self.compare = compare
        self.value = value
        self.type = type

    def __str__(self):
        return "{0} \t {1} {2} {3}".format(self.type, self.key, self.compare, self.value)


class Strategy:
    def __init__(self, name, description, logger=None):
        self.name = name
        self.description = description
        self.logger = logger or logging.getLogger(__name__)
        self.filters = []

    def __str__(self):
        return "{0}:{1}".format(self.name, self.description)

    def strategy_detail(self):
        detail = []
        for filter_item in self.filters:
            detail.append(str(filter_item).strip())

        # return os.linesep.join(detail)
        return "\n".join(detail)

    def add_filter(self, key, compare, value, type=None):
        self.filters.append(StrategyFilterItem(key, compare, value, type))
        return self

    def add_filters(self, filter_list):
        for filter_item in filter_list:
            self.add_filter(filter_item[0], filter_item[1], filter_item[2], filter_item[3])

    def is_item_can_bid(self, item):
        can_bid = True
        for filter_item in self.filters:
            filter_item_key = filter_item.key
            filter_item_compare = filter_item.compare
            filter_item_value_type = filter_item.type
            filter_item_value = filter_item.value

            filter_item_result = False
            if filter_item_key not in item and filter_item_value_type != "rate":
                self.logger.info(filter_item_key + "not exist")
                can_bid = False
                continue

            should_convert_to_number = filter_item_compare == ">" or filter_item_compare == "<"
            if filter_item_value_type == "int":
                actual_value_str = item[filter_item_key]
                if filter_item_key == "网络借贷平台借款余额" and actual_value_str == "暂未提供":
                    actual_value_str = "0"

                actual_value = Utils.convert_to_int(actual_value_str)
                expected_value = Utils.convert_to_int(filter_item_value)
            elif filter_item_value_type == "rate":
                key_pair = filter_item_key.split("/")
                denominator = Utils.convert_to_float(item[key_pair[1]])
                if denominator == 0:
                    actual_value = 0
                else:
                    actual_value = round(Utils.convert_to_float(item[key_pair[0]]) / denominator, 3)
                expected_value = Utils.convert_to_float(filter_item_value)
            elif should_convert_to_number:
                actual_value = Utils.convert_to_float(item[filter_item_key])
                expected_value = Utils.convert_to_float(filter_item_value)
            else:
                actual_value = item[filter_item_key]
                expected_value = filter_item_value

            if filter_item_compare == "!=":
                filter_item_result = expected_value != actual_value
            elif filter_item_compare == "==":
                filter_item_result = expected_value == actual_value
            elif filter_item_compare == ">":
                filter_item_result = actual_value > expected_value
            elif filter_item_compare == "<":
                filter_item_result = actual_value < expected_value
            elif filter_item_compare == "in":
                if expected_value == "School211":
                    school211_list = Utils.get_211_school()
                    filter_item_result = actual_value in school211_list
                else:
                    self.logger.error("not support")
                    filter_item_result = False
            else:
                self.logger.error("not support")
                filter_item_result = False

            self.logger.debug("{0: <5} {1: <7} {2: <7} {3}".format(str(filter_item_result), actual_value, expected_value, filter_item))
            if not filter_item_result:
                self.logger.debug(
                    "{0: <5} {1: <7} {2: <7} {3}".format(str(filter_item_result), actual_value, expected_value,
                                                         filter_item))
                can_bid = False

        return can_bid


def test_level():
    print(sys._getframe().f_code.co_name)
    base_strategy1 = Strategy("低息飞首", "0逾期非首届，16%投标利率")
    base_strategy1.add_filter("级别", "==", "B", "str")
    can_bid = base_strategy1.is_item_can_bid(item)
    print(can_bid)

    item["级别"] = "B"
    can_bid = base_strategy1.is_item_can_bid(item)
    print(can_bid)


def test_month():
    print(sys._getframe().f_code.co_name)
    base_strategy1 = Strategy("低息飞首", "0逾期非首届，16%投标利率")
    base_strategy1.add_filter("期限", "<", "12")
    can_bid = base_strategy1.is_item_can_bid(item)
    print(can_bid)

    item["期限"] = "12"
    can_bid = base_strategy1.is_item_can_bid(item)
    print(can_bid)


def test_strategy1():
    base_strategy1 = Strategy("低息飞首", "0逾期非首届，16%投标利率")
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


def test_strategy2():
    base_strategy2 = Strategy("女标", "学历认证0逾期")
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
    base_strategy2 = Strategy("自动1", "女年龄")
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test()

