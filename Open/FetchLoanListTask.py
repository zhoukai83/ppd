# -*- coding: utf-8 -*-
import json
import logging
import os
import time
import queue
from collections import deque

import pandas as pd

from Open.PpdOpenClient import PpdOpenClient
from Open.PpdTask import PpdTask


class FetchLoanListTask(PpdTask):
    def __init__(self, input_queue, logger=None):
        logger = logger or logging.getLogger(__name__)
        PpdTask.__init__(self, logger)
        self.config_file = json.load(open("../config.json", "r"))
        self.terminate = False
        self.input_queue = input_queue

        if os.path.exists("loanlist.csv"):
            self.df = pd.read_csv("loanlist.csv", encoding="utf-8")

        self.client = PpdOpenClient()

        self.cache = deque(self.df["ListingId"].tolist(), 1000)

        self.save_to_csv_queue = queue.Queue(maxsize=1000)

    def get_loan_list(self):
        new_listing_id = None
        data_file_path = "loanlist.csv"

        result = self.client.get_loan_list()
        json_data = json.loads(result)
        if "Result" not in json_data:
            self.logger.error(f"get_loan_list: {json_data}")
            time.sleep(0.3)
            return new_listing_id

        if json_data["Result"] != 1:
            self.logger.warn(f"get loan list no reuslt: {json_data}")
            return new_listing_id

        listing_ids = [item["ListingId"] for item in json_data["LoanInfos"]]
        new_listing_id = list(set(listing_ids).difference(self.cache))
        if new_listing_id is not None and len(new_listing_id) != 0:
            self.output_queue.put(new_listing_id)
            self.logger.info(f"生产者生产了: {len(new_listing_id)} in {len(listing_ids)},  {new_listing_id}")
        else:
            # self.logger.info("No more data")
            return

        self.cache.extend(new_listing_id)
        self.save_to_csv_queue.put(json_data["LoanInfos"])
        # new_frame = DataFrame(json_data["LoanInfos"])
        # self.df = pd.concat([self.df, new_frame], sort=False).drop_duplicates("ListingId")
        # self.df.to_csv(data_file_path, encoding="utf-8", index=False)

    def task_body(self):
        # start = time.time()
        self.get_loan_list()
        # self.logger.info(f"FetchLoanList End: {time.time() - start}")


def main():

    pass

if __name__ == "__main__":
    main()
