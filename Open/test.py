import json
import logging
import logging.config
import os
from datetime import datetime
from datetime import timedelta

from PpdOpenClient import PpdOpenClient
import pandas as pd
from pandas import DataFrame, Series


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

def save_to_csv(df, item_list):
    data_file_path = "loanlist.csv"
    frame = DataFrame(item_list)
    frame.set_index("ListingId", inplace=True)

    if df is None:
        frame.to_csv(data_file_path, encoding="utf-8")
        df = frame
    else:
        df = pd.concat([df, frame], sort=False).drop_duplicates()
        df.to_csv(data_file_path, encoding="utf-8")

    return df


def main():
    df = pd.read_csv("loanlist.csv", encoding="utf-8")
    df.set_index("ListingId", inplace=True)
    url = "https://openapi.ppdai.com/listing/openapiNoAuth/loanList"
    start_date_time = datetime.utcnow()
    print(start_date_time.strftime('%Y-%m-%d %H:%M:%S'))

    data = {
        "PageIndex": "1",
        "StartDateTime": (start_date_time + timedelta(minutes=-10)).strftime('%Y-%m-%d %H:%M:%S')
    }

    client = PpdOpenClient()
    result = client.post(url, data=data)

    json_data = json.loads(result)
    if json_data["Result"] == 1:
        df = save_to_csv(df, json_data["LoanInfos"])

    pass


if __name__ == "__main__":
    logger = setup_logging()
    main()