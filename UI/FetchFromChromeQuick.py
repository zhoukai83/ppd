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

    def check_bid_number(self, listing_item):
        # self.wait_until_css(".filter-total")
        # self.wait_until_text_present(".filter-total span", "1")
        self.wait_until_css(".el-table__body tr")
        # self.wait_loading_success()

        table_body_html = self.driver.find_element_by_css_selector(".el-table__body").get_attribute("innerHTML")
        soup = BeautifulSoup(table_body_html, "lxml")

        tr_list = soup.find_all("tr")
        if len(tr_list) != 1:
            self.logger.warn("check_bid_number %s len %s", listing_item["listingId"], len(tr_list))
            return False

        link_element = tr_list[0].find_all("td")[1].find("a")
        link_href = link_element.get('href')
        if str(listing_item["listingId"]) not in link_href:
            self.logger.warn("listing id changed:%s %s", listing_item["listingId"], link_href)
            return False

        return True

    def click_not_bid_button(self):
        self.logger.log(15, "start quick_click_not_bid_button")

        self.wait_loading_success()
        self.wait_until_css("#loan-listNew > section.order-container > label")
        checkbox_element = self.driver.find_element_by_css_selector("#loan-listNew > section.order-container > label")
        checkbox_class = checkbox_element.get_attribute("class")
        if "is-checked" not in checkbox_class:
            self.logger.info("click 未投")
            self.driver.execute_script("arguments[0].click();", checkbox_element)
            self.wait_loading_success()

        self.logger.log(15, "end")

    def fetch_detail_info(self, should_back=True):
        result = {}
        detail_info = []
        self.logger.info("wait finish")
        url = self.driver.current_url
        if not url.startswith("https://invest.ppdai.com/loan/info/"):
            self.logger.warning("not in detail info page: %s", url)
            # self.back()
            return None

        url_numbers = re.findall(r"\d+", url)
        if len(url_numbers) == 1:
            result["listingId"] = int(url_numbers[0])

        # if not self.wait_until_css("#baseInfo", 5):
        #     self.back()
        #     return None

        if not self.wait_until_css("#borrowerInfo") and should_back:
            self.back()
            return None

        base_info_html = self.driver.find_element_by_id("baseInfo").get_attribute("innerHTML")
        soup = BeautifulSoup(base_info_html, "lxml")

        result["title"] = soup.find("header").text.strip().split(" ")[0].strip()

        level = soup.select_one("section > div.area-info > div.first-line > a").text
        detail_info.append("级别：" + level)

        # self.logger.info("get user")
        loan_user_name = soup.find("span", class_="user-name").text
        detail_info.append("User：" + loan_user_name)

        # self.logger.info("get bid num")
        secondary_items = soup.find("div", class_="secondary-item").find_all("p")
        for secondary in secondary_items:
            if "投标人数" in secondary.text:
                detail_info.append(secondary.text)
                break

        # self.logger.info("get progress")
        progress = soup.find("div", class_="el-progress__text").text
        detail_info.append("进度：" + progress)

        # self.logger.info("finish get progress")
        main_element = soup.find("div", class_="main-item")
        for item in main_element.find_all("p"):
            detail_info.append(item.text)

        if not self.wait_until_css("#borrowerInfo") and should_back:
            self.back()
            return None

        borrower_info_html = self.driver.find_element_by_id("borrowerInfo").get_attribute("innerHTML")
        soup = BeautifulSoup(borrower_info_html, "lxml")
        for borrower_info_item_element in soup.find_all("div"):
            detail_info.append(borrower_info_item_element.text)

        if not self.wait_until_css("#loanRecord") and should_back:
            self.back()
            return None

        staticstic_info_html = self.driver.find_element_by_id("statisticInfo").get_attribute('innerHTML')
        soup = BeautifulSoup(staticstic_info_html, "lxml")

        record_element = soup.find(id="loanRecord")
        item_elements = record_element.find_all("div")
        for index in range(3):
            detail_info.append(item_elements[index].text.replace("\n", "").replace(" ", ""))

        record_element = soup.find(id="repayRecord")
        item_elements = record_element.find_all("div")
        for index in range(6):
            detail_info.append(item_elements[index].text)

        debt_element = soup.find(id="debtRecord")
        for item in debt_element.find_all("div", class_="item"):
            detail_info.append(item.getText())

        for item in detail_info:
            split_result = item.split("：")
            if len(split_result) != 2:
                self.logger.warn(f"item warn: {item}")
                continue
            result[split_result[0].strip()] = split_result[1].strip()

        json_string = json.dumps(result, indent=4, sort_keys=True, ensure_ascii=False).replace("\xa5", "")
        self.logger.info(json_string)

        if should_back:
            self.back()
        return json.loads(json_string)

    def bid_again(self):
        try:
            self.retry_call(self.driver.find_element_by_css_selector(".oneKey-success-btn").click)

            self.logger.info("click_not_bid_button")
            self.click_not_bid_button()

            self.logger.info("try bid again")
            self.quick_bid()
            self.logger.info("bid again success")
        except Exception as e:
            self.logger.error(e, exc_info=True)
