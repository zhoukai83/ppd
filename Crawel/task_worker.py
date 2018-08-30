# task_worker.py

import sys, time, queue
from multiprocessing.managers import BaseManager
import json


class QueueManager(BaseManager):
    pass


def main():
    QueueManager.register('get_task_queue')
    QueueManager.register('get_result_queue')

    server_addr = '10.164.120.164'
    config_file = json.load(open("config.json", "r"))
    server_addr = config_file["ServerAddr"]

    print('Connect to server %s...' % server_addr)

    m = QueueManager(address=(server_addr, 50083), authkey=b'abc')
    m.connect()

    task = m.get_task_queue()
    result = m.get_result_queue()

    start_time = time.clock()
    for i in range(10):
        try:
            if task.empty():
                return

            n = task.get(timeout=1)
            print('run task %d * %d' % (n, n))
            r = '%d * %d = %d' % (n, n, n * n)
            result.put(r)
        except queue.Queue.Empty:
            print('task queque is empty')

    print(time.clock() - start_time)
    print('worker exit')

if __name__ == "__main__":
    main()
