import logging
import json
import queue
from Common import Utils
from Open.PpdTask import PpdTask
from Common.StrategyFactory import StrategyFactory
from Common.OpenStrategy import OpenStrategy


class BidStrategyTask(PpdTask):
    def __init__(self, input_queue, logger=None):
        logger = logger or logging.getLogger(__name__)
        PpdTask.__init__(self, logger)
        self.input_queue = input_queue
        self.sf = StrategyFactory(OpenStrategy)

        self.save_to_csv_queue = queue.Queue(1000)

    def task_body(self):
        if self.input_queue.empty():
            return

        item = self.input_queue.get(timeout=2)
        if item is None:
            return

        for listing in item:
            # self.logger.info(listing)
            can_bid, first_strategy = self.sf.is_item_can_bid(listing)
            if can_bid:
                json_string = json.dumps(listing, indent=4, sort_keys=True, ensure_ascii=False)
                self.logger.log(21, f"bid: {listing['ListingId']}: {first_strategy} \n{first_strategy.strategy_detail()} \n {json_string}")
                self.output_queue.put(listing)
                self.save_to_csv_queue.put({"ListingId": listing['ListingId'], "Strategy": first_strategy.name})

def main():

    pass

if __name__ == "__main__":
    main()
