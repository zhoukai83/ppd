
import logging
import json
import time


class PpdItemConvertor:
    def __init(self, logger):
        self.logger = logger or logging.getLogger(__name__)

    def convert_open_to_ui(self, item):
        ui_item = {}
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
                    "StudyStyle": "学习形式",
                    "CurrentRate": "协议利率",
                    "FirstSuccessBorrowTime": "第一次成功借款时间",
                    "RegisterTime": "注册时间",
                    "TotalPrincipal": "累计借款金额",
                    "BorrowName": "User",
                    "ListingId": "listingId",
                    # "": "creationDate"
                    }

        for key, value in key_dict.items():
            if key not in item:
                continue

            ui_item[value] = item[key]

            if key == "Gender":
                if ui_item[value] == 2:
                    ui_item[value] = "女"
                elif ui_item[value] == 1:
                    ui_item[value] = "男"
                else:
                    raise ValueError(f"does not know geder value {item}")
            elif key == "EducationDegree":
                if ui_item[value] is None:
                    ui_item[value] = "无"
            # except Exception as ex:
            #     self.logger.warning(f"{ex}, {key}, {value}", exc_info=True)

        ui_item["成功还款次数"] = ui_item["正常还清次数"] + ui_item["逾期（0-15天）还清次数"] + ui_item["逾期（15天以上）还清次数"]
        ui_item["本次借款后负债"] = item["Amount"] + item["OwingAmount"]

        current_time = time.localtime()
        ui_item["creationDate"] = time.strftime('%Y-%m-%dT%H:%M:%S', current_time)
        return ui_item

    def convert_open_borrower_statistics_to_flat(self, item):
        overdueDayMap = item.get("overdueDayMap")
        if overdueDayMap:
            index = 0
            for key, value in overdueDayMap.items():
                # logging.info(f"{key} {value}")
                item[f"overdueDayMap_{index}_month"] = key
                item[f"overdueDayMap_{index}_value"] = value
                index += 1
            del item["overdueDayMap"]

        previous_listings = item.get("previousListings", [])
        if previous_listings:
            index = 0
            for previous_list in previous_listings:
                item[f"previous_listing_{index}_date"] = previous_list.get("creationDate")
                item[f"previous_listing_{index}_status"] = previous_list.get("statusId")
                index += 1
                # logging.info(f"{previous_list}")
            del item["previousListings"]

        if "loanAmountMax" in item:
            del item["loanAmountMax"]

        if "debtAmountMap" in item:
            del item["debtAmountMap"]

        if "listingStatics" in item:
            del item["listingStatics"]

        if "owingAmountMap" in item:
            del item["owingAmountMap"]

        return item


def main():
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=20, format=logging_format)
    logger = logging.getLogger(__name__)

    open_item = {
        "Age": 22,
        "Amount": 500.0,
        "AmountToReceive": 0,
        "AuditingTime": "2000-01-01T00:00:00.000",
        "BorrowName": "pdu4163126017",
        "CancelCount": 0,  # 历史记录：  2次撤标
        "CertificateValidate": 1,  # 身份证认证 ??
        "CreditCode": "B",
        "CreditValidate": 0,  #
        "CurrentRate": 20.0,
        "DeadLineTimeOrRemindTimeStr": "19天23时52分",
        "EducationDegree": "专科",  # 文化程度
        "FailedCount": 0,  # 历史记录： 0次失败
        "FirstSuccessBorrowTime": "2017-11-17T19:26:22.000",
        "FistBidTime": None,
        "Gender": 1,
        "GraduateSchool": "华北科技学院",  # 毕业院校
        "HighestDebt": 6832.48,  # 历史最高负债
        "HighestPrincipal": 5740.0,  # 单笔最高借款金额
        "LastBidTime": None,
        "LastSuccessBorrowTime": "2018-07-09T18:05:05.000",
        "LenderCount": 0,
        "ListingId": 128080987,
        "Months": 6,
        "NciicIdentityCheck": 0,
        "NormalCount": 10,  # 正常还清次数
        "OverdueLessCount": 0,  # 逾期少于15天
        "OverdueMoreCount": 0,
        "OwingAmount": 6085.88,  # 待还金额
        "OwingPrincipal": 5432.95,
        "PhoneValidate": 1,
        "RegisterTime": "2017-11-17T17:59:41.000",
        "RemainFunding": 500.0,
        "StudyStyle": "成人",  # 学习形式
        "SuccessCount": 3,  # 成功借款次数
        "TotalPrincipal": 12340.0,  # 累计借款金额
        "WasteCount": 0
    }

    import pandas as pd
    from Open.PpdOpenClient import PpdOpenClient

    client = PpdOpenClient()
    listing_ids = client.get_loan_list_ids(["B", "C"], [3, 6, 9])
    listing_id = listing_ids[-1]
    result = client.get_listing_info([listing_id])

    json_data = json.loads(result)

    if json_data.get("Result", -999) != 1:
        logger.warning(f"fetch loan list info result error: {json_data}")

    loan_infos = json_data.get("LoanInfos")
    open_item = loan_infos[0]

    file_path = "..\\UISimulation\\UISimMain.csv"
    df = pd.read_csv(file_path, encoding="utf-8")
    records = df.to_dict("records")
    ui_item_template = records[-1]
    print(json.dumps(ui_item_template, ensure_ascii=False))

    convertor = PpdItemConvertor()
    ui_item = convertor.convert_open_to_ui(open_item)
    print(json.dumps(ui_item, ensure_ascii=False, indent=4))

    print(set(ui_item_template.keys()).symmetric_difference(set(ui_item.keys())))
    print(set(ui_item.keys()).symmetric_difference(set(ui_item_template.keys())))
    pass


if __name__ == "__main__":
    main()