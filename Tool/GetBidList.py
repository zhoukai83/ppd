import sys
sys.path.insert(0, "..")

import pandas as pd
from pandas import DataFrame
import json
from datetime import datetime, timedelta
from Open.PpdOpenClient import PpdOpenClient

def main():
    data_file_path = "BidList.csv"
    client = PpdOpenClient()

    df = pd.read_csv(data_file_path, encoding="utf-8")

    data_string = client.get_bid_list(datetime.now() + timedelta(days=-30))
    json_data = json.loads(data_string, encoding="utf-8")
    if json_data.get("TotalRecord", 10000) > 5000:
        print(data_string)

    new_df = DataFrame(json_data.get("BidList"))

    df = pd.concat([df, new_df]).drop_duplicates("ListingId").sort_values("ListingId")
    df.to_csv(data_file_path, encoding="utf-8", index=False)
    pass


if __name__ == "__main__":
    main()