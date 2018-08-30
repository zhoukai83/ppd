from Common.StrategyBase import StrategyBase
import logging
from Common import Utils

item = {
    "Age": 22,
    "Amount": 500.0,
    "AmountToReceive": 0,
    "AuditingTime": "2000-01-01T00:00:00.000",
    "BorrowName": "pdu4163126017",
    "CancelCount": 0,
    "CertificateValidate": 1,
    "CreditCode": "B",
    "CreditValidate": 0,
    "CurrentRate": 20.0,
    "DeadLineTimeOrRemindTimeStr": "19天23时52分",
    "EducationDegree": "专科",
    "FailedCount": 0,
    "FirstSuccessBorrowTime": "2017-11-17T19:26:22.000",
    "FistBidTime": None,
    "Gender": 1,
    "GraduateSchool": "华北科技学院",
    "HighestDebt": 6832.48,                     #历史最高负债
    "HighestPrincipal": 5740.0,                  #单笔最高借款金额
    "LastBidTime": None,
    "LastSuccessBorrowTime": "2018-07-09T18:05:05.000",
    "LenderCount": 0,
    "ListingId": 126040981,
    "Months": 6,
    "NciicIdentityCheck": 0,
    "NormalCount": 10,         #成功还款次数
    "OverdueLessCount": 0,     #逾期少于15天
    "OverdueMoreCount": 0,
    "OwingAmount": 6085.88,      #待还金额
    "OwingPrincipal": 5432.95,   #
    "PhoneValidate": 1,
    "RegisterTime": "2017-11-17T17:59:41.000",
    "RemainFunding": 500.0,
    "StudyStyle": "成人",
    "SuccessCount": 3,              #成功借款次数
    "TotalPrincipal": 12340.0,      #累计借款金额
    "WasteCount": 0
}

class OpenStrategy(StrategyBase):
    def __init__(self, name, description, logger=None):
        logger = logger or logging.getLogger(__name__)
        StrategyBase.__init__(self, name, description, logger)

    def is_item_can_bid(self, item):
        can_bid = True
        for filter_item in self.filters:
            filter_item_key = filter_item.key
            filter_item_compare = filter_item.compare
            filter_item_value_type = filter_item.type
            filter_item_value = filter_item.value

            if filter_item_key not in item and filter_item_value_type != "rate":
                self.logger.info(filter_item_key + "not exist")
                can_bid = False
                continue

            actual_value = item[filter_item_key]
            should_convert_to_number = filter_item_compare == ">" or filter_item_compare == "<"
            if filter_item_value_type == "int":
                actual_value_str = item[filter_item_key]
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
                can_bid = False

        return can_bid


# Gender:
#   2: 女
#   1: 男

def test():
    base_strategy = OpenStrategy("自动1  ", "女年龄")
    base_strategy.add_filters([
            ["CreditCode", "==", "B", "str"],
            ["Months", "<", "7", "int"],
            ["Gender", "==", "2", "int"],
            ["Age", ">", "28", "int"],
            ["Age", "<", "45", "int"],
            ["OwingAmount", "<", "20000", "int"],     #待还金额
            # ["逾期（15天以上）还清次数", "==", "0", "int"],
            # ["成功借款次数", "!=", "0", "int"],
            # ["成功还款次数", ">", "10", "int"],
            # ["待还金额/历史最高负债", "<", "0.9", "rate"],
            # ["借款金额/单笔最高借款金额", "<", "0.9", "rate"],
            # ["网络借贷平台借款余额", "<", "20000", "int"]
        ])

    item = {'Age': 42, 'Amount': 5200.0, 'AmountToReceive': 0, 'AuditingTime': '2000-01-01T00:00:00.000', 'BorrowName': 'pdu3030472653', 'CancelCount': 0, 'CertificateValidate': 0, 'CreditCode': 'AA', 'CreditValidate': 0, 'CurrentRate': 10.5, 'DeadLineTimeOrRemindTimeStr': '14天23时55分', 'EducationDegree': None, 'FailedCount': 0, 'FirstSuccessBorrowTime': '2017-11-07T09:31:53.000', 'FistBidTime': None, 'Gender': 1, 'GraduateSchool': None, 'HighestDebt': 1241.82, 'HighestPrincipal': 1000.0, 'LastBidTime': None, 'LastSuccessBorrowTime': '2017-11-07T09:31:53.000', 'LenderCount': 0, 'ListingId': 126037765, 'Months': 6, 'NciicIdentityCheck': 0, 'NormalCount': 6, 'OverdueLessCount': 0, 'OverdueMoreCount': 0, 'OwingAmount': 0.0, 'OwingPrincipal': 0.0, 'PhoneValidate': 1, 'RegisterTime': '2017-08-23T18:59:22.000', 'RemainFunding': 5200.0, 'StudyStyle': None, 'SuccessCount': 1, 'TotalPrincipal': 1000.0, 'WasteCount': 1}
    # item["CreditCode"] = "B"
    print(base_strategy.is_item_can_bid(item))


if __name__  == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test()