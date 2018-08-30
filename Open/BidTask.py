import logging
import json
import queue

from Open.PpdTask import PpdTask
from Open import Utils as OpenUtils

from Open.PpdOpenClient import PpdOpenClient

class BidTask(PpdTask):
    def __init__(self, queue, logger=None):
        logger = logger or logging.getLogger(__name__)
        PpdTask.__init__(self, logger)
        self.queue = queue

        self.client = PpdOpenClient()
        self.should_bid = False

    # {"Amount": 50, "ListingId": 126194065, "OrderId": null, "Result": 4001, "ResultCode": null,"ResultMessage": "账户余额不足，请先充值"}
    # {"Amount": 50, "ListingId": 126198456, "OrderId": null, "Result": 6001, "ResultCode": null, "ResultMessage": "标的额度已投满"}
    # {"Amount": 50, "ListingId": 126198698, "OrderId": "5b82104880b4415f0cbaa4eb", "Result": 9999, "ResultCode": null,"ResultMessage": "投标处理中"}
    def task_body(self):
        if self.queue.empty():
            return

        item = self.queue.get(timeout=2)
        if item is None:
            return

        if self.should_bid:
            result = self.client.bid(item["ListingId"])
            json_data = json.loads(result)
            if "Result" in json_data and "ResultMessage" in json_data and json_data["ResultMessage"] == "账户余额不足，请先充值" and json_data["Result"] == 4001:
                self.logger.info("no more money")
                self.should_bid = False
                OpenUtils.trigger_terminate_signal()

            self.logger.info(result)

        json_string = json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False)
        self.logger.log(21, f"bid: {item['ListingId']}")

        # OpenUtils.trigger_terminate_signal()
        pass