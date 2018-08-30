import sys
sys.path.insert(0,'..')

import json
import os
import pandas as pd
from  pandas import DataFrame
from Open.PpdOpenClient import PpdOpenClient
import Common.PandasUtils as PandasUtils

from collections import deque
import time


# {"timestamp": "2018-08-28 12:15:06", "status": 200, "error": "OK", "message": "您的操作太频繁啦，请喝杯茶后，再来试试吧", "path": "/gateway/openapi/buyList"}

def get_debt_info():
    df_debt_info = None
    debt_info_path = "DebtInfo.csv"

    debt_info_id_cache = deque(maxlen=100000)
    if os.path.exists(debt_info_path):
        df_debt_info = pd.read_csv(debt_info_path, encoding="utf-8")
        debt_info_id_cache = deque(df_debt_info["DebtId"].tolist(), maxlen=100000)

    client = PpdOpenClient()

    for page_index in range(1, 180):
        time.sleep(1)
        json_data = json.loads(client.get_buy_list(page_index, levels="B"))
        if "Count" not in json_data:
            print(json.dumps(json_data, ensure_ascii=False))

        print(json_data["Count"], json.dumps(json_data["DebtInfos"]))
        df_debt_list = DataFrame(json_data["DebtInfos"])
        debt_ids = df_debt_list["DebtdealId"].tolist()

        new_listing_id = list(set(debt_ids).difference(debt_info_id_cache))
        print(f"{page_index} {len(new_listing_id)} in {len(df_debt_list)}: {new_listing_id}")
        if not new_listing_id:
            print("sleep")
            time.sleep(0.3)
            continue

        for x in range(0, len(new_listing_id), 20):
            sub_listing_ids = new_listing_id[x: x + 20]
            json_data_debt = json.loads(client.get_debt_info(sub_listing_ids))
            if "Result" not in json_data_debt or json_data_debt["Result"] != 1:
                print(f"error get debt info: {sub_listing_ids}")
                continue

            df_debt_info = PandasUtils.save_to_csv(debt_info_path, df_debt_info, json_data_debt["DebtInfos"])
            debt_info_id_cache.extend(sub_listing_ids)
            time.sleep(0.3)

    # print(client.get_listing_info(df_debt_list["ListingId"].tolist()[:10]))


def get_debt_listing_info():
    client = PpdOpenClient()

    debt_info_path = "DebtInfo.csv"

    df_debt_info = pd.read_csv(debt_info_path, encoding="utf-8").drop_duplicates()
    # df_debt_over30 = df_debt_info[df_debt_info.Days > 30]
    df_debt_over30 = df_debt_info
    listing_ids = df_debt_over30["ListingId"].tolist()

    listing_info_path = "listinginfo.csv"
    df_listing_info = pd.read_csv(listing_info_path, encoding="utf-8")
    listing_id_cache = deque(df_listing_info["ListingId"].tolist())

    new_listing_id = list(set(listing_ids).difference(listing_id_cache))

    intersection = set(listing_ids).intersection(listing_id_cache)
    # new_listing_id = list(set(debt_info_id_cache).difference(listing_ids))
    print(f"{len(intersection)}, {intersection}")
    print(f"{len(new_listing_id)} in {len(listing_ids)}: {new_listing_id}")

    for x in range(0, len(new_listing_id), 10):
        sub_listing_ids = new_listing_id[x: x + 10]
        json_data = json.loads(client.get_listing_info(sub_listing_ids))
        df_listing_info = PandasUtils.save_to_csv(listing_info_path, df_listing_info, json_data["LoanInfos"])
        print(json_data)
        time.sleep(0.5)
    # print(json.dumps(json_data, ensure_ascii=False))


def main():
    # get_debt_info()
    get_debt_listing_info()
    pass


if __name__ == "__main__":
    main()