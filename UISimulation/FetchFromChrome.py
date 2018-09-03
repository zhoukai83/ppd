import json
import logging
import re
import time

import Utils
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup

from FetchFromChrome import FetchFromChrome


class FetchFromChromeQuick(FetchFromChrome):
    def __init__(self, session_id=None, logger=None):
        FetchFromChrome.__init__(self, session_id, logger)

    def get_all_listing_items(self):
        MAX_RETRY = 1
        retry = 0
        listing_ids = []
        total_page = 1
        current_page = 1

        if not self.wait_until_css(".list-container tr", 2):
            return listing_ids, current_page, total_page

        while retry < MAX_RETRY:
            try:
                html = self.driver.find_element_by_css_selector(".list-container").get_attribute("innerHTML")
                soup = BeautifulSoup(html, "lxml")

                for row in soup.find_all("tr"):
                    cell = row.find_all("td")[1]
                    link_element = cell.find("a")
                    link_href = link_element.get("href")

                    if self._is_loan_exist(link_href):
                        continue

                    self.history.append(link_href)
                    if len(self.history) > 1000:
                        self.history.pop(0)

                    listing_id = self.get_id(link_href)

                    td_list = row.find_all("td")
                    lilv = td_list[3]
                    amount = td_list[4].text.replace("\xa5", "")
                    period = td_list[5]
                    # progress_bar = td_list[6]
                    #
                    # progresses = progress_bar.find_all(class_="progress")
                    self.logger.info(f"{link_href}, {lilv.text}, {amount}, {period.text}")
                    listing_ids.append(listing_id)

                    # self.driver.execute_script("arguments[0].setAttribute('target','')", link_element)

                total_page = Utils.convert_to_int(soup.find(class_="el-pagination__total").text)
                current_page = Utils.convert_to_int(soup.select(".number.active")[0].text)
                return listing_ids, current_page, total_page
            # except StopIteration as e:
            #     raise e
            except Exception as e:
                self.logger.error(e, exc_info=True)
            retry += 1
            time.sleep(1)

        return listing_ids, current_page, total_page,

    def iter_listing_item_to_detail_page(self):
        MAX_RETRY = 1
        retry = 0

        if not self.wait_until_css(".list-container tr", 2):
            return None, None

        while retry < MAX_RETRY:
            try:
                html = self.driver.find_element_by_css_selector(".list-container").get_attribute("innerHTML")
                soup = BeautifulSoup(html, "lxml")

                for row in soup.find_all("tr"):
                    cell = row.find_all("td")[1]
                    link_element = cell.find("a")
                    link_href = link_element.get("href")

                    if self._is_loan_exist(link_href):
                        continue

                    self.history.append(link_href)
                    if len(self.history) > 1000:
                        self.history.pop(0)

                    listing_id = self.get_id(link_href)

                    td_list = row.find_all("td")
                    lilv = td_list[3]
                    amount = td_list[4].text.replace("\xa5", "")
                    period = td_list[5]

                    self.logger.info("%s %s %r %s", link_href, lilv.text, amount, period.text)

                    # self.driver.execute_script("arguments[0].setAttribute('target','')", link_element)
                    return listing_id, link_element
            # except StopIteration as e:
            #     raise e
            except Exception as e:
                self.logger.error(e, exc_info=True)
            retry += 1
            time.sleep(1)

        return None, None

    def click_listing_in_listpage(self, listing_id, link_element=None, in_current_tab=True):
        try:
            link_element = self.driver.find_element_by_css_selector("a[href*='" + str(listing_id) + "']")
            if not in_current_tab:
                self.driver.execute_script("arguments[0].click();", link_element)
            else:
                self.driver.execute_script("arguments[0].setAttribute('target',''); arguments[0].click();", link_element)
            return True
            # self.retry_call(link_element.click)
        except Exception as ex:
            return False

