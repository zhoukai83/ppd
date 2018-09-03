import sys
sys.path.insert(0,'..')

from Common.StrategyBase import StrategyBase
import logging


item = {
    "Age": 22,
    "Amount": 500.0,
    "AmountToReceive": 0,
    "AuditingTime": "2000-01-01T00:00:00.000",
    "BorrowName": "pdu4163126017",
    "CancelCount": 0,     # 历史记录：  2次撤标
    "CertificateValidate": 1,               #身份证认证 ??
    "CreditCode": "B",
    "CreditValidate": 0,                    #
    "CurrentRate": 20.0,
    "DeadLineTimeOrRemindTimeStr": "19天23时52分",
    "EducationDegree": "专科",         #文化程度
    "FailedCount": 0,           # 历史记录： 0次失败
    "FirstSuccessBorrowTime": "2017-11-17T19:26:22.000",
    "FistBidTime": None,
    "Gender": 1,
    "GraduateSchool": "华北科技学院",                #毕业院校
    "HighestDebt": 6832.48,                     #历史最高负债
    "HighestPrincipal": 5740.0,                  #单笔最高借款金额
    "LastBidTime": None,
    "LastSuccessBorrowTime": "2018-07-09T18:05:05.000",
    "LenderCount": 0,
    "ListingId": 126040981,
    "Months": 6,
    "NciicIdentityCheck": 0,
    "NormalCount": 10,         #正常还清次数
    "OverdueLessCount": 0,     #逾期少于15天
    "OverdueMoreCount": 0,
    "OwingAmount": 6085.88,      #待还金额
    "OwingPrincipal": 5432.95,
    "PhoneValidate": 1,
    "RegisterTime": "2017-11-17T17:59:41.000",
    "RemainFunding": 500.0,
    "StudyStyle": "成人",               #学习形式
    "SuccessCount": 3,              #成功借款次数
    "TotalPrincipal": 12340.0,      #累计借款金额
    "WasteCount": 0
}

class OpenStrategy(StrategyBase):
    def __init__(self, name, description, logger=None):
        logger = logger or logging.getLogger(__name__)
        StrategyBase.__init__(self, name, description, logger)

    # Gender:
    #   2: 女
    #   1: 男
    def change_key(self, item):
        key_dict = {"CreditCode": "级别",
                    "Gender": "性别",
                    "Months": "期限",
                    "Age": "年龄",
                    "OwingAmount": "待还金额",
                    "OverdueLessCount": "逾期（0-15天）还清次数",
                    "OverdueMoreCount": "逾期（15天以上）还清次数",
                    "SuccessCount": "成功借款次数",
                    "NormalCount": "正常还清次数",
                    "HighestDebt": "历史最高负债",
                    "Amount": "借款金额",
                    "HighestPrincipal": "单笔最高借款金额",
                    "EducationDegree": "文化程度",
                    "GraduateSchool": "毕业院校",
                    "StudyStyle": "学习形式"}

        for key, value in key_dict.items():
            if key not in item:
                continue

            item[value] = item[key]

            if key == "Gender":
                if item[value] == 2:
                    item[value] = "女"
                elif item[value] == 1:
                    item[value] = "男"
                else:
                    raise ValueError(f"does not know geder value {item}")
            elif key == "EducationDegree":
                if item[value] is None:
                    item[value] = "无"

        item["成功还款次数"] = item["正常还清次数"] + item["逾期（0-15天）还清次数"] + item["逾期（15天以上）还清次数"]
        return item

    def is_item_can_bid(self, item):
        item = self.change_key(item)
        return StrategyBase.is_item_can_bid(self, item)

# Gender:
#   2: 女
#   1: 男

def test():
    base_strategy = OpenStrategy("自动1  ", "女年龄")
    base_strategy.add_filters([
            # ["CreditCode", "==", "B", "str"],
            # ["Months", "<", "7", "int"],
            # ["Gender", "==", "2", "int"],
            # ["Age", ">", "28", "int"],
            # ["Age", "<", "45", "int"],
            # ["OwingAmount", "<", "20000", "int"],     #待还金额
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
            # ["网络借贷平台借款余额", "<", "20000", "int"]
        ])

    item = {'Age': 42, 'Amount': 5200.0, 'AmountToReceive': 0, 'AuditingTime': '2000-01-01T00:00:00.000', 'BorrowName': 'pdu3030472653', 'CancelCount': 0, 'CertificateValidate': 0, 'CreditCode': 'AA', 'CreditValidate': 0, 'CurrentRate': 10.5, 'DeadLineTimeOrRemindTimeStr': '14天23时55分', 'EducationDegree': None, 'FailedCount': 0, 'FirstSuccessBorrowTime': '2017-11-07T09:31:53.000', 'FistBidTime': None, 'Gender': 1, 'GraduateSchool': None, 'HighestDebt': 1241.82, 'HighestPrincipal': 1000.0, 'LastBidTime': None, 'LastSuccessBorrowTime': '2017-11-07T09:31:53.000', 'LenderCount': 0, 'ListingId': 126037765, 'Months': 6, 'NciicIdentityCheck': 0, 'NormalCount': 6, 'OverdueLessCount': 0, 'OverdueMoreCount': 0, 'OwingAmount': 0.0, 'OwingPrincipal': 0.0, 'PhoneValidate': 1, 'RegisterTime': '2017-08-23T18:59:22.000', 'RemainFunding': 5200.0, 'StudyStyle': None, 'SuccessCount': 1, 'TotalPrincipal': 1000.0, 'WasteCount': 1}
    # item["CreditCode"] = "B"
    logger.info(base_strategy.is_item_can_bid(item))


if __name__  == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    test()