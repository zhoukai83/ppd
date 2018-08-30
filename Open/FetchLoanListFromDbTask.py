import pymongo
import logging
import time
import datetime
from PpdTask import PpdTask


class FetchLoanListFromDbTask(PpdTask):
    def __init__(self, queue, logger=None):
        logger = logger or logging.getLogger(__name__)
        PpdTask.__init__(self, logger)
        self.queue = queue
        conn = pymongo.MongoClient('10.164.120.164', 27017)
        db_ppd = conn.ppd
        self.collection_listing = db_ppd.Listing

    def task_body(self):
        item = self.__fetch_latest_from_db()
        if len(item) > 0:
            self.output_queue.put(item)
        time.sleep(1)

    def __fetch_latest_from_db(self):
        MAX_RETRY = 5
        retry = 0
        while retry < MAX_RETRY:
            try:
                d = datetime.datetime.now()
                d = datetime.datetime(2009, 11, 12, 12)
                return list(self.collection_listing.find({"fetchTime": {"$gt": d}}).sort('_id', pymongo.DESCENDING).limit(1000))
            except Exception as e:
                print(e)
            retry += 1
            time.sleep(1)

        return []