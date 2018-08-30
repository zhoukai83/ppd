from Open.PpdTask import PpdTask

import logging
import json
import queue
import time
import os
import pandas as pd
from pandas import DataFrame

class SaveListingInfoTask(PpdTask):
    def __init__(self, queue, logger=None):
        logger = logger or logging.getLogger(__name__)
        PpdTask.__init__(self, logger)
        self.queue = queue

        if os.path.exists("listingInfo.csv"):
            self.df = pd.read_csv("listingInfo.csv", encoding="utf-8")
        else:
            self.df = None

    def save_list(self):
        if self.queue.empty():
            return False

        item = self.queue.get(timeout=2)
        if item is None:
            return True

        new_frame = item
        self.df = pd.concat([self.df, new_frame], sort=False).drop_duplicates("ListingId")
        self.df.to_csv("listingInfo.csv", encoding="utf-8", index=False)

        return True

    def task_body(self):
        if not self.save_list():
            time.sleep(5)
        pass