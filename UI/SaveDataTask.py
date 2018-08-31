
from PpdCommon.PpdTask import PpdTask

import logging
import json
import queue
import time
import os
import pandas as pd
from pandas import DataFrame


class SaveDataTask(PpdTask):
    def __init__(self, input_queue, logger=None):
        logger = logger or logging.getLogger(__name__)
        PpdTask.__init__(self, logger=logger)
        self.input_queue = input_queue

        self.data_file_path = "UIMain.csv"
        if os.path.exists(self.data_file_path):
            self.df = pd.read_csv(self.data_file_path, encoding="utf-8")
        else:
            self.df = None

    def save_list(self):
        try:
            # if self.input_queue.empty():
            #     return False

            item = self.input_queue.get(timeout=5)
            if item is None:
                return True

            new_frame = DataFrame([item])
            self.df = pd.concat([self.df, new_frame], ignore_index=True, sort=False).drop_duplicates("listingId")
            self.df.to_csv(self.data_file_path, encoding="utf-8", index=False)

            return True
        except:
            return False

    def task_body(self):
        if not self.save_list():
            time.sleep(2)
        pass