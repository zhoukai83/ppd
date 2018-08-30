# -*- coding: utf-8 -*-
import json
import logging
import logging.config
import logging.config
import os
import queue
import time

import sys
sys.path.insert(0,'..')

from Open.BidStrategyTask import BidStrategyTask
from Open.BidTask import BidTask
from Open.FetchLoanListTask import FetchLoanListTask
from Open.FetchListingInfoTask import  FetchListingInfoTask
from Open.SaveLoanListTask import SaveLoanListTask
from Open.SaveListingInfoTask import SaveListingInfoTask
from Open.SaveBidListingTask import SaveBidListingTask


from Open import Utils as OpenUtils

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gbk')

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

def terminate_task(t):
    t.terminate = True


def main():
    q = queue.Queue(maxsize=20)
    t1 = FetchLoanListTask(q)
    t2 = FetchListingInfoTask(t1.get_output_queue())
    t_save_1 = SaveLoanListTask(t1.save_to_csv_queue)
    t_save_2 = SaveListingInfoTask(t2.save_to_file_queue)

    t3 = BidStrategyTask(t2.get_output_queue())

    t_save_3 = SaveBidListingTask(t3.save_to_csv_queue)
    t4 = BidTask(t3.get_output_queue())

    task_list = [t1, t_save_1, t2, t_save_2, t3, t_save_3, t4]
    logger.info("task start")
    [t.start() for t in task_list]

    q.put([126114288])
    while True:
        time.sleep(1)
        if OpenUtils.terminate_signal_triggered(logger):
            break

    [terminate_task(t) for t in task_list]

    OpenUtils.restore_terminate_signal()

    pass

if __name__ == "__main__":
    logger = setup_logging()
    main()
    # test()