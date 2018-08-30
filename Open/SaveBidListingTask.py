from Open.PpdTask import PpdTask

import logging
import json
import queue
import time
import os
import pandas as pd
from pandas import DataFrame

class SaveBidListingTask(PpdTask):
    def __init__(self, input_queue, logger=None):
        logger = logger or logging.getLogger(__name__)
        PpdTask.__init__(self, logger)
        self.input_queue = input_queue

        if os.path.exists("BidListing.csv"):
            self.df = pd.read_csv("BidListing.csv", encoding="utf-8")
        else:
            self.df = None

    def save_list(self):
        if self.input_queue.empty():
            return False

        item = self.input_queue.get(timeout=2)
        if item is None:
            return True


        if self.df is not None:
            self.df = pd.concat([self.df, DataFrame([item])], sort=False).drop_duplicates("ListingId")
        else:
            self.df = DataFrame([item])

        self.df.to_csv("BidListing.csv", encoding="utf-8", index=False)
        return True

    def task_body(self):
        if not self.save_list():
            time.sleep(5)
        pass