import logging
import queue
import threading


class PpdTask(threading.Thread):
    def __init__(self, input_queue=None, logger=None):
        threading.Thread.__init__(self)
        self.terminate = False
        self.logger = logger or logging.getLogger(__name__)
        if input_queue is not None:
            self.input_queue = input_queue
        self.output_queue = queue.Queue(maxsize=100)

    def get_output_queue(self):
        return self.output_queue

    def run(self):
        try:
            while not self.terminate:
                self.task_body()
        except Exception as ex:
            self.logger.error(ex, exc_info=True)

    def task_body(self):
        self.logger.info("task_body")
        pass


def main():
    pass


if __name__ == "__main__":
    main()
