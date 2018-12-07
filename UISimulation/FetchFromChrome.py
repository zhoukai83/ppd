import json
import logging
import re
import time

from Common import Utils
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup


class FetchFromChrome():
    def __init__(self, session_id=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.driver = webdriver.Remote("http://127.0.0.1:9515", webdriver.DesiredCapabilities.CHROME)
        self.history = []

        self.backup_session_id = self.driver.session_id
        self.logger.info(self.driver.session_id)
        if session_id:
            self.driver.session_id = session_id

        self.refresh_url = "https://invest.ppdai.com/loan/listpage/?risk=1&mirror=&pageIndex=1&period=1,2&times=3,2"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.session_id = self.backup_session_id
        self.driver.quit()

    def retry_call(self, func_body, times=3, sleep_time=0.1):
        try_count = 0
        while try_count < times:
            try:
                try_count += 1
                return func_body()
            except Exception as e:
                if try_count == 0:
                    self.logger.error(e, exc_info=True)

                time.sleep(sleep_time)

        return None

    def click_to_next_page(self):
        self.retry_call(self.driver.find_element_by_css_selector(".btn-next").click)

    def get_id(self, link):
        url_numbers = re.findall(r"\d+", link)
        if len(url_numbers) == 1:
            return int(url_numbers[0])

        self.logger.warning("link %s can not get number corretly", link)
        return None

    def _is_loan_exist(self, href):
        for item in self.history:
            if item == href:
                return True

        return False

    def wait_until_css(self, selector, timeout=3, show_timeout_log=True):
        try:
            element_present = EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            WebDriverWait(self.driver, timeout).until(element_present)
            return True
        except TimeoutException:
            if show_timeout_log:
                self.logger.info("Timed out waiting for css: %s", selector)
            return False

    def refresh_loan_list_page(self):
        # self.driver.get("https://invest.ppdai.com/loan/listpage/?risk=1&mirror=3&pageIndex=1&period=1,2&times=3,2&rate=3,4&money=100,15000")
        self.driver.get(self.refresh_url)

    def get_cookie_string(self):
        driver_cookies = self.driver.get_cookies()
        cookie_list = [f"{cookie['name']}={cookie['value']}" for cookie in driver_cookies]
        cookies = "; ".join(cookie_list)
        return cookies

    def get_loan_list_items(self):
        MAX_RETRY = 1
        retry = 0
        list_items = []

        if not self.wait_until_css(".list-container tr", 1.5):
            return list_items

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
                    if len(self.history) > 300:
                        self.history.pop(0)

                    listing_id = self.get_id(link_href)

                    # td_list = row.find_all("td")
                    # lilv = td_list[3]
                    # amount = td_list[4].text.replace("\xa5", "")
                    # period = td_list[5]
                    # progress_bar = td_list[6]
                    # progresses = progress_bar.find_all(class_="progress")
                    # self.logger.info(f"{link_href}, {lilv.text}, {amount}, {period.text}")
                    # listing_ids.append(listing_id)

                # total_page = Utils.convert_to_int(soup.find(class_="el-pagination__total").text)
                # current_page = Utils.convert_to_int(soup.select(".number.active")[0].text)
                return list_items
            except Exception as e:
                self.logger.error(e, exc_info=True)
            retry += 1
            time.sleep(1)

        return list_items
        pass

    def get_all_listing_items(self):
        MAX_RETRY = 1
        retry = 0
        listing_ids = []
        total_page = 1
        current_page = 1

        if not self.wait_until_css(".list-container tr", 1.5):
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
                    if len(self.history) > 300:
                        self.history.pop(0)

                    listing_id = self.get_id(link_href)

                    # td_list = row.find_all("td")
                    # lilv = td_list[3]
                    # amount = td_list[4].text.replace("\xa5", "")
                    # period = td_list[5]
                    # progress_bar = td_list[6]
                    # progresses = progress_bar.find_all(class_="progress")
                    # self.logger.info(f"{link_href}, {lilv.text}, {amount}, {period.text}")
                    listing_ids.append(listing_id)

                total_page = Utils.convert_to_int(soup.find(class_="el-pagination__total").text)
                current_page = Utils.convert_to_int(soup.select(".number.active")[0].text)
                return listing_ids, current_page, total_page
            except Exception as e:
                self.logger.error(e, exc_info=True)
            retry += 1
            time.sleep(1)

        return listing_ids, current_page, total_page,

    def is_account_money_low(self):
        self.wait_until_css(".router-link__balance", timeout=2, show_timeout_log=False)

        try:
            account_money = Utils.convert_to_float(self.driver.find_element_by_css_selector(".router-link__balance").text)
        except Exception:
            return False
        return account_money < 50
