import redis
import logging
import json

if __name__ == "__main__":
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=20, format=logging_format)
    logger = logging.getLogger(__name__)

    logger.info("start")
    r = redis.StrictRedis(host='10.164.120.164', port=6379, db=0)
    # r.set('foo', list(range(100)))

    logger.info("start")
    # r.delete("loan_listing_ids")
    t = r.get('loan_listing_ids')
    logging.info(t)
    if t:
        logger.info(f"{t}, {json.loads(t)}")
