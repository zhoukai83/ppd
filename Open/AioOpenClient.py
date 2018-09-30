import sys
sys.path.insert(0, "..")

import asyncio
import logging
from datetime import datetime

import json
from pprint import pprint
from datetime import timedelta
from aiohttp import ClientSession, ClientTimeout
from Open.PpdOpenClient import PpdOpenClient


class AioOpenClient(PpdOpenClient):
    def __init__(self, logger=None, key_index=1):
        self.logger = logger or logging.getLogger(__name__)
        PpdOpenClient.__init__(self, self.logger, key_index=key_index)

    async def aio_post(self, url, data, access_token="", timeout_sec=None):
        start_date_time = datetime.utcnow()
        timestamp = start_date_time.strftime('%Y-%m-%d %H:%M:%S')

        REQUEST_HEADER = {'Connection': 'keep-alive',
                          'Cache-Control': 'max-age=0',
                          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36',
                          # 'Accept-Encoding': 'gzip, deflate, sdch',
                          'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
                          'Content-Type': 'application/json;charset=utf-8'
                          }

        sort_data = self.rsa_client.sort(data)
        sign = self.rsa_client.sign(sort_data).decode("utf-8")

        REQUEST_HEADER["X-PPD-APPID"] = self.appid
        REQUEST_HEADER["X-PPD-SIGN"] = sign
        REQUEST_HEADER["X-PPD-TIMESTAMP"] = timestamp
        REQUEST_HEADER["X-PPD-TIMESTAMP-SIGN"] = self.rsa_client.sign("%s%s" % (self.appid, timestamp)).decode("utf-8")
        REQUEST_HEADER["Accept"] = "application/json;charset=UTF-8"

        if access_token.strip():
            REQUEST_HEADER["X-PPD-ACCESSTOKEN"] = access_token

        result = await self.post_data(url, data, REQUEST_HEADER, timeout_sec=timeout_sec)
        # req = self.session.post(url, data=json.dumps(data), headers=REQUEST_HEADER, timeout=timeout)
        # return req.text
        return result
        pass

    async def post_data(self, url, data, headers, timeout_sec=0.6):
        post_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        timeout = ClientTimeout(total=timeout_sec)
        async with ClientSession(headers=headers, timeout=timeout) as session:
            self.logger.debug(f"{url}, post, {post_data}")
            async with session.post(url, data=post_data) as response:
                response = await response.read()
                return response

    async def aio_get_loan_list(self, page_index=1, time_delta_secs=None, timeout_sec=0.6):
        url = "https://openapi.ppdai.com/listing/openapiNoAuth/loanList"
        data = {
            "PageIndex": page_index
        }

        # start_date_time = datetime.utcnow()
        if time_delta_secs:
            start_date_time = datetime.now() + timedelta(seconds=time_delta_secs)
            data["StartDateTime"] = start_date_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        self.log_count += 1
        if self.log_count > 100:
            print(self.client_index, data, time_delta_secs)
            self.log_count = 0

        response = await self.aio_post(url, data=data)
        return response

    async def aio_get_listing_info(self, listing_ids: int):
        if len(listing_ids) > 10:
            raise ValueError(f"get_listing_info() parame listing_ids length > 10,  {len(listing_ids)}, {listing_ids}")

        url = "https://openapi.ppdai.com/listing/openapiNoAuth/batchListingInfo"
        data = {
            "ListingIds": listing_ids
        }

        response = await self.aio_post(url, data=data)

        listing_infos = []
        json_data = json.loads(response, encoding="utf-8")
        if json_data.get("Result", -999) != 1:
            self.logger.info(f"aio_batch_get_listing_info error: {json.dumps(json_data, ensure_ascii=False)}")
            return listing_infos

        listing_infos = json_data.get("LoanInfos", [])
        return listing_infos
        pass

    def aio_batch_get_listing_info(self, listing_ids):
        listing_infos = []
        loop = asyncio.get_event_loop()
        tasks = []
        for index in range(0, len(listing_ids), 10):
            sub_listing_ids = listing_ids[index:index + 10]
            self.logger.info(sub_listing_ids)

            task = asyncio.ensure_future(self.aio_get_listing_info(sub_listing_ids))
            tasks.append(task)

        json_datas = loop.run_until_complete(asyncio.gather(*tasks))
        for json_data in json_datas:
            listing_infos.extend(json_data)

        return listing_infos


def main():
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=20, format=logging_format)
    logger = logging.getLogger(__name__)

    client = AioOpenClient()
    list_ids = client.get_loan_list_ids(["B", "C"], [3, 6, 9])
    list_ids = list_ids[:19]
    logger.info(list_ids)

    # logger.info("start")
    # logger.info(json.dumps(client.batch_get_listing_info(list_ids), ensure_ascii=False))
    # logger.info("end")

    # logger.info("start")
    # logger.info(json.dumps(client.aio_batch_get_listing_info(list_ids), ensure_ascii=False))
    # logger.info("end")

    # logger.info("start")
    # logger.info(json.dumps(client.batch_get_listing_info(list_ids), ensure_ascii=False))
    # logger.info("end")
    pass


if __name__ == "__main__":
    main()
