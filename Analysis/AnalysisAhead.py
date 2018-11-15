
import sys
sys.path.insert(0, "..")

import logging
import asyncio
import json
import re
from UISimulation.PpdUISimulationRequest import PpdUISimulationRequest
from PpdCommon.PpdItem import PpdItemConvertor
from os import listdir
from os.path import isfile, join

import pandas as pd
from pandas import DataFrame

def is_ahead(data):
    convertor = PpdItemConvertor()
    data = convertor.convert_open_borrower_statistics_to_flat(data)

    # if overdue_day_total < -80:
    logging.info(f"{data.get('listingId')}:  {data}")
        # return True

    return False


def deal_file_name(file_name):
    result = None
    try:
        loop = asyncio.get_event_loop()
        client = PpdUISimulationRequest()
        ids = re.findall("\d+", file_name)

        if not ids:
            logging.warning(f"can not get id: {file_name}")
            return result
        id = ids[0]

        task = asyncio.ensure_future(client.get_borrower_statistics(id, use_cache=True))
        task_results = loop.run_until_complete(asyncio.gather(task))
        # logging.info(json.dumps(result, ensure_ascii=False))
        convertor = PpdItemConvertor()
        for data in task_results:
            result = convertor.convert_open_borrower_statistics_to_flat(data)
            return result
    except Exception as ex:
        logging.warning(file_name, exc_info=True)
        return result

    return result

def main():

    id = 132621576
    files = listdir("..\\data\\showBorrowerStatistics")
    count = 0
    logging.info(files[:10])

    datas = []
    for file_name in files:
        data = deal_file_name(file_name)

        if data and "successNum" in data:
            # logging.info(data)
            datas.append(data)

        # listing_may_ahead = deal_file_name(file_name)
        # if listing_may_ahead:
        #     count += 1

    logging.info(json.dumps(datas, ensure_ascii=False))
    df = DataFrame(datas)
    df.to_csv("AnalysisAhead.csv", encoding="utf-8", index=False)

if __name__ == "__main__":
    logging_format = '"%(asctime)s %(levelname)s %(module)s %(lineno)d \t%(message)s'
    logging.basicConfig(level=20, format=logging_format)
    logger = logging.getLogger(__name__)


    main()