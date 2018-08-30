# task_master.py

import random, time, queue
from multiprocessing.managers import BaseManager
import json
from datetime import datetime

task_queue = queue.Queue(10)
result_queue = queue.Queue()


class QueueManager(BaseManager):
    pass


def task_q():
    return task_queue


def result_q():
    return result_queue


def main():
    print('master start.')
    QueueManager.register('get_task_queue', callable=task_q)
    QueueManager.register('get_result_queue', callable=result_q)
    config_file = json.load(open("config.json", "r"))
    server_addr = config_file["ServerAddr"]
    manager = QueueManager(address=(server_addr, 50083), authkey=b'abc')
    manager.start()
    task = manager.get_task_queue()
    result = manager.get_result_queue()

    count = 1
    max_sub_count = 5
    sub_count = 50

    while True:
        r = task.get()
        print(datetime.now().strftime("%H:%M:%S.%f"), len(r))
    # manager.join()

    count = 0
    while not task.empty():
        count += 1
        if count % 5 == 0:

            print('task queque is not empty', task.qsize())
            count = 0

        time.sleep(1)
    time.sleep(5)
    manager.shutdown()
    print('master exit.')

if __name__ == '__main__':
    main()
