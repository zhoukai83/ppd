# -*- coding: utf-8 -*-
import json
import logging
import os
import time

from datetime import datetime
from datetime import timedelta
import requests
import pandas as pd
from pandas import DataFrame, Series
from Open.PpdTask import PpdTask
from Open.PpdOpenClient import PpdOpenClient
import queue

class FetchListingInfoTask(PpdTask):
    def __init__(self, input_queue, logger=None):
        logger = logger or logging.getLogger(__name__)
        PpdTask.__init__(self, logger)
        self.config_file = json.load(open("../config.json", "r"))
        self.input_queue = input_queue

        if os.path.exists("listingInfo.csv"):
            self.df = pd.read_csv("listingInfo.csv", encoding="utf-8")
        else:
            self.df = None
        self.client = PpdOpenClient()

        self.save_to_file_queue = queue.Queue(maxsize=1000)

    def get_listing_info(self, listing_ids):
        for x in range(0, len(listing_ids), 10):
            sub_listing_ids = listing_ids[x: x + 10]
            result = self.client.get_listing_info(sub_listing_ids)
            json_data = json.loads(result)
            if "Result" not in json_data:
                self.logger.warn(f"fetch loan list info result not exist: {json_data}")
                continue

            if json_data["Result"] == 1:
                new_frame = DataFrame(json_data["LoanInfos"])
                new_listings_info = new_frame[~new_frame["ListingId"].isin(self.df["ListingId"])]
                self.output_queue.put(new_listings_info.to_dict('records'))

                self.save_to_file_queue.put(new_frame)
                # self.output_queue.put(json_data["LoanInfos"])
                # self.df = pd.concat([self.df, new_frame], sort=False).drop_duplicates("ListingId")
                # self.df.to_csv("listingInfo.csv", encoding="utf-8", index=False)
            else:
                self.logger.warn(f"fetch loan list info result != 1: {json_data}")

    def task_body(self):
        if self.input_queue.empty():
            return

        item = self.input_queue.get(timeout=2)
        if item is None:
            return

        start = time.time()
        self.get_listing_info(item)
        # self.logger.info(f"get_listing_info: {time.time() - start}")


def main():

    pass


if __name__ == "__main__":
    main()

