import logging
import redis
import time
import json


class PpdRedisClient:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.redis_client = redis.StrictRedis(host='10.164.120.164', port=6379, db=0, charset="utf-8", decode_responses=True)
        self.key_add_time = "LoanListAddTime"
        self.key_item = "LoanListItem"
        pass

    def add_loan_list_items(self, loan_list_items):
        find_new = []
        for item in loan_list_items:
            if self.redis_client.sismember("LoanListId", item["ListingId"]):
                continue

            self.logger.info(f"sadd: {item}")
            self.redis_client.sadd("LoanListId", item["ListingId"])
            self.redis_client.hset(self.key_item, item["ListingId"], json.dumps(item, ensure_ascii=False))
            self.redis_client.zadd(self.key_add_time, time.time(), item["ListingId"])
            find_new.append(item)

        if find_new:
            id_count = self.redis_client.scard("LoanListId")
            if id_count > 1000:
                remove_ids = self.redis_client.zrange(self.key_add_time, 0, id_count - 1000)
                for id in remove_ids:
                    self.redis_client.srem("LoanListId", id)
                    self.redis_client.hdel(self.key_item, id)
                self.redis_client.zremrangebyrank(self.key_add_time, 0, id_count - 1000)

        return find_new

    def add_loan_list_items_pipeline(self, loan_list_items):
        find_new = False
        pipe = self.redis_client.pipeline(True)
        for item in loan_list_items:
            print(item)
            if not pipe.sismember("LoanListId", item["ListingId"]):
                self.logger.info(f"sadd: {item}")
                print(item)
                pipe.sadd("LoanListId", item["ListingId"])
                pipe.hset(self.key_item, item["ListingId"], item)
                pipe.zadd(self.key_add_time, time.time(), item["ListingId"])
                find_new = True

        if not find_new:
            pipe.execute()
            return find_new

        id_count = pipe.scard("LoanListId")
        if id_count > 1000:
            remove_ids = pipe.zrange(self.key_add_time, 0, id_count - 1000)
            for id in remove_ids:
                pipe.srem("LoanListId", id)
                pipe.hdel(self.key_item, id)
            pipe.zremrangebyrank(self.key_add_time, 0, id_count - 1000)

        pipe.execute()
        return find_new

    def get_loan_list_ids_by_count(self, count):
        total_count = self.redis_client.zcard(self.key_add_time)
        print(total_count)
        return self.redis_client.zrange(self.key_add_time, total_count - count, total_count)
        pass

    def get_loan_list_ids_by_time(self, start_time):
        now = time.time()
        return self.redis_client.zrevrangebyscore(self.key_add_time, now, start_time)

    def get_loan_list_items(self, ids):

        result = self.redis_client.hmget(self.key_item, ids)

        return json.loads("[" + ",".join(result) + "]", encoding="utf-8")
        pass


def main():
    client = PpdRedisClient()

    now = time.time()

    loan_list_ids = client.get_loan_list_ids_by_time(now - 60 * 60 * 2)
    print(len(loan_list_ids))
    print(loan_list_ids)

    loan_list_items = client.get_loan_list_items(loan_list_ids)
    for item in loan_list_items:
        print(item.decode("utf-8"))
    pass


if __name__ == "__main__":
    main()