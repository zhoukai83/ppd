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

class FetchFromChrome:
    def __init__(self, session_id=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.driver = webdriver.Remote("http://127.0.0.1:9515", webdriver.DesiredCapabilities.CHROME)
        # self.driver.implicitly_wait(5)  # seconds
        # self.driver = webdriver.Chrome("E:\soft\chromedriver_win32\chromedriver.exe")
        self.history = []

        # self.login()
        self.backup_session_id = self.driver.session_id
        self.logger.info(self.driver.session_id)
        if session_id:
            self.driver.session_id = session_id

        # self.refresh_url = "https://invest.ppdai.com/loan/listpage/?risk=1&mirror=3&pageIndex=1&times=2,3&period=1,2"

        self.refresh_url = "https://invest.ppdai.com/loan/listpage/?risk=1&mirror=3&pageIndex=1&times=3&period=2&auth="
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.session_id = self.backup_session_id
        self.driver.quit()

    def get_id(self, link):
        url_numbers = re.findall(r"\d+", link)
        if len(url_numbers) == 1:
            return int(url_numbers[0])

        self.logger.warn("link %s can not get number corretly", link)
        return None

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

    def navigate_detail(self, listing_id):
        self.driver.get("https://invest.ppdai.com/loan/info/" + str(listing_id))

    def login(self):
        self.driver.get("https://ac.ppdai.com/User/Login?redirect=https://invest.ppdai.com/loan/listnew")
        self.driver.find_element_by_id("UserName").send_keys("13810528461")
        self.driver.find_element_by_id("Password").send_keys("vHh4OOuOjA7v")
        self.driver.find_element_by_id("rememberMe").click()
        self.driver.find_element_by_id("login_btn").click()
        time.sleep(5)
        self.driver.get("https://invest.ppdai.com/loan/listpage/?risk=1&mirror=3&pageIndex=1&period=1,2,3,4&times=3,2")

        self.click_not_bid_button()


    def click_not_bid_button(self):
        self.logger.log(15, "start click_not_bid_button")
        self.wait_loading_success()
        self.wait_until_css("#loan-listNew > section.order-container > label")
        checkbox_class = self.driver.find_element_by_css_selector("#loan-listNew > section.order-container > label").get_attribute("class")
        if "is-checked" not in checkbox_class:
            self.logger.info("click 未投")
            self.wait_until_css("#loan-listNew > section.order-container > label > span.el-checkbox__input > span")
            self.wait_until_clickable("#loan-listNew > section.order-container > label > span.el-checkbox__input > span", 3)
            self.wait_until_not_visible(".el-loading-text")
            self.wait_loading_success()
            self.driver.find_element_by_css_selector("#loan-listNew > section.order-container > label > span.el-checkbox__input > span").click()
            self.wait_loading_success()

        self.logger.log(15, "start")

    def wait_loading_success(self):
        self.wait_until_not_visible(".el-loading-text", 1)
        self.wait_until_not_visible(".el-loading-mask", 1)
        self.wait_until_not_visible(".el-loading-spinner")

    def _is_loan_exist(self, href):
        for item in self.history:
            if item == href:
                return True

        return False

    def refresh_loan_list_page(self):
        # self.driver.get("https://invest.ppdai.com/loan/listpage/?risk=1&mirror=3&pageIndex=1&period=1,2&times=3,2&rate=3,4&money=100,15000")
        self.driver.get(self.refresh_url)

    def set_attribute(self, element, name, value):
        self.driver.execute_script("arguments[0].setAttribute('" + name + "', '" + value + "')", element)

    def set_style(self, element, name, value):
        self.driver.execute_script("arguments[0].style." + name + "='" + value + "'", element)

    def filter_item(self, listing_item):
        if "借款金额" not in listing_item:
            self.logger.warn("借款金额 not in %s", listing_item)
            return False

        loan_amount = Utils.convert_currency_to_float(listing_item["借款金额"])
        self.logger.info("filter amount: %s", loan_amount)
        filter_url = "{0}&money={1},{2}".format(self.refresh_url, int(loan_amount - 1), int(loan_amount + 1))
        self.driver.get(filter_url)
        return True

    def check_bid_number(self, listing_item):
        # self.wait_until_css(".filter-total")

        if not self.wait_until_text_present(".filter-total span", "1"):
            return False

        tr_element = self.driver.find_element_by_css_selector(".list-container tr")
        cell = tr_element.find_elements_by_tag_name("td")[1]
        link_element = cell.find_element_by_tag_name("a")
        link_href = link_element.get_attribute('href')
        if str(listing_item["listingId"]) not in link_href:
            self.logger.warn("listing id changed:%s %s", listing_item["listingId"], link_href)
            return False

        return True

    def quick_bid(self):
        self.wait_loading_success()

        self.retry_call(self.driver.find_element_by_class_name("el-button__one-key-bid").click)
        # if not self.wait_until_css("#bid-one-key .el-button__bid-confirm"):
        #     self.logger.warn("can not find bid confirm button")
        #     return False
        self.retry_call(self.driver.find_element_by_class_name("el-checkbox__protocol").click)
        self.retry_call(self.driver.find_element_by_css_selector("#bid-one-key .el-button__bid-confirm").click)
        return True
        # self.driver.find_element_by_css_selector("#bid-one-key > section > button").click()

    def back(self):
        self.driver.execute_script("window.history.go(-1)")

    def switch_to_window(self, index):
        # self.logger.info(self.driver.window_handles)
        window_name = self.driver.window_handles[index]
        # self.logger.info("swith to window: %s", window_name)
        self.driver.switch_to.window(window_name)

    def close_window(self, index):
        self.driver.close()
        window_name = self.driver.window_handles[0]
        self.driver.switch_to.window(window_name)

    def wait_until_visibility(self, element, timeout=3):
        try:
            element_present = EC.visibility_of(element)
            WebDriverWait(self.driver, timeout).until(element_present)
            return True
        except TimeoutException:
            self.logger.info("Timed out waiting for visibility: %s", element)
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

    def wait_until_text_present(self, selector, value, timeout=3):
        try:
            element_present = EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), value)
            WebDriverWait(self.driver, timeout).until(element_present)
            return True
        except TimeoutException:
            self.logger.info("Timed out waiting for text present: %s %s", selector, value)
            return False

    def wait_until_clickable(self, selector, timeout=3):
        try:
            # element_present = EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            element_present = EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            WebDriverWait(self.driver, timeout).until(element_present)
            return True
        except TimeoutException:
            self.logger.info("Timed out waiting for clickable: %s", selector)
            return False

    def wait_until_not_visible(self, selector, timeout=3):
        try:
            element_present = EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
            WebDriverWait(self.driver, timeout).until(element_present)
            return True
        except TimeoutException:
            self.logger.info("Timed out waiting for invisibility_of_element_located: %s", selector)
            return False

    def is_account_money_low(self):
        self.wait_until_css(".router-link__balance", timeout=2, show_timeout_log=False)

        try:
            account_money = Utils.convert_to_float(self.driver.find_element_by_css_selector(".router-link__balance").text)
        except Exception:
            return False
        return account_money < 50

    def fetch_detail_info(self):
        # window_name = self.driver.window_handles[-1]
        # self.driver.switch_to.window(window_name)

        if not self.wait_until_css("#baseInfo", 5):
            self.back()
            return None

        if not self.wait_until_css("#borrowerInfo"):
            self.back()
            return None

        url = self.driver.current_url
        if not url.startswith("https://invest.ppdai.com/loan/info/"):
            self.logger.warn("not in detail info page: %s", url)
            self.back()
            return None

        result = {}
        detail_info = []

        url_numbers = re.findall(r"\d+", url)
        if len(url_numbers) == 1:
            result["listingId"] = int(url_numbers[0])

        level = self.driver.find_element_by_css_selector(
            "#baseInfo > section > div.area-info > div.first-line > a").text
        self.logger.debug(level)
        detail_info.append("级别：" + level)

        loan_user_name = self.driver.find_element_by_css_selector(".user-name").text
        detail_info.append("User：" + loan_user_name)

        main_element = self.driver.find_element_by_class_name("main-item")
        for item in main_element.find_elements_by_tag_name("p"):
            self.logger.debug(item.text)
            detail_info.append(item.text)

        self.logger.debug("")
        self.logger.debug("borrowerInfo")
        borrower_info_element = self.driver.find_element_by_id("borrowerInfo")
        for borrower_info_item_element in borrower_info_element.find_elements_by_tag_name("div"):
            self.logger.debug(borrower_info_item_element.text)
            detail_info.append(borrower_info_item_element.text)

        self.logger.debug("")
        self.logger.debug("loan record")

        if not self.wait_until_css("#loanRecord"):
            self.back()
            return None

        record_element = self.driver.find_element_by_id("loanRecord")
        item_elements = record_element.find_elements_by_tag_name("div")
        for index in range(3):
            self.logger.debug(item_elements[index].text)
            detail_info.append(item_elements[index].text)

        self.logger.debug("")
        self.logger.debug("Repay record")
        record_element = self.driver.find_element_by_id("repayRecord")
        item_elements = record_element.find_elements_by_tag_name("div")
        for index in range(6):
            self.logger.debug(item_elements[index].text)
            detail_info.append(item_elements[index].text)

        self.logger.debug("")
        self.logger.debug("debt record")
        record_element = self.driver.find_element_by_id("debtRecord")
        item_elements = record_element.find_elements_by_tag_name("div")
        for index in range(4):
            self.logger.debug(item_elements[index].text)
            detail_info.append(item_elements[index].text)

        for item in detail_info:
            split_result = item.split("：")
            result[split_result[0].strip()] = split_result[1].strip()

        json_string = json.dumps(result, indent=4, sort_keys=True, ensure_ascii=False).replace("\xa5", "")
        self.logger.info(json_string)
        self.back()
        return json.loads(json_string)

    def iter_listing_item_to_detail_page(self):
        MAX_RETRY = 1
        retry = 0

        self.wait_until_css(".list-container")
        if not self.wait_until_css(".list-container tr"):
            return None, None
        while retry < MAX_RETRY:
            try:
                self.logger.debug("iter_listing_item_to_detail_page")
                for row in self.driver.find_elements_by_css_selector(".list-container tr"):
                    cell = row.find_elements_by_tag_name("td")[1]
                    link_element = cell.find_element_by_tag_name("a")
                    link_href = link_element.get_attribute('href')
                    if self._is_loan_exist(link_href):
                        continue

                    self.wait_until_not_visible(".el-loading-mask")
                    self.history.append(link_href)
                    if len(self.history) > 1000:
                        self.history.pop(0)

                    listing_id = self.get_id(link_href)
                    lilv = row.find_elements_by_tag_name("td")[3]
                    amount = row.find_elements_by_tag_name("td")[4].text.replace("\xa5", "")
                    period = row.find_elements_by_tag_name("td")[5]

                    self.logger.info("%s %s %r %s", link_href, lilv.text, amount, period.text)
                    self.wait_loading_success()

                    # self.retry_call(link_element.click)
                    # link_element.click()
                    return listing_id, link_element
            # except StopIteration as e:
            #     raise e
            except Exception as e:
                self.logger.error(e, exc_info=True)
            retry += 1
            time.sleep(1)

        return None, None

    def click_listing_in_listpage(self, listing_id, link_element):
        self.driver.execute_script("arguments[0].setAttribute('target','')", link_element)
        self.retry_call(link_element.click)

    def click_to_next_page(self):
        self.retry_call(self.driver.find_element_by_css_selector(".btn-next").click)

    def back_until_listing_page(self, navigate_count=0):
        if navigate_count != 0:
            self.driver.execute_script(f"window.history.go(-{navigate_count})")

        for x in range(2):
            if self.driver.current_url.startswith("https://invest.ppdai.com/loan/listpage"):
                break

            self.back()
            time.sleep(1)

    def get_all_buy_listing_items(self):
        MAX_RETRY = 1
        retry = 0
        listing_ids = []

        if not self.wait_until_css(".wapBorrowDebtList", 2):
            return listing_ids

        while retry < MAX_RETRY:
            try:
                html = self.driver.find_element_by_css_selector(".wapBorrowDebtList").get_attribute("innerHTML")
                soup = BeautifulSoup(html, "lxml")

                list_li_element = soup.find_all("li")
                for index in range(0, len(list_li_element), 2):
                    row = list_li_element[index]
                    nextpaytime = Utils.convert_to_int(row.select(".nextpaytime")[0].text)

                    link = list_li_element[index+1].find("a")
                    listing_url = link.get("href")
                    listing_id = link.text

                    listing_ids.append([listing_id, nextpaytime, listing_url])
            except Exception as e:
                self.logger.error(e, exc_info=True)
            retry += 1
            time.sleep(1)

        return listing_ids

    def fetch_detail_buy_info(self):
        if not self.wait_until_css(".newLendDetailInfo", 5):
            return None

        detail_info = []
        base_info_html = self.driver.find_element_by_css_selector(".newLendDetailInfo").get_attribute("innerHTML")
        soup = BeautifulSoup(base_info_html, "lxml")

        for item in soup.find_all("dl"):
            self.logger.debug(item.text)
            detail_info.append(item.text)

        borrower_info_html = self.driver.find_element_by_css_selector(".lender-info").get_attribute("innerHTML")
        soup = BeautifulSoup(borrower_info_html, "lxml")
        for borrower_info_item_element in soup.find_all("p"):
            self.logger.debug(borrower_info_item_element.text)
            detail_info.append(borrower_info_item_element.text)

        if not self.wait_until_css(".lendDetailTab_tabContent"):
            return None

        tab_contains_elements = self.driver.find_elements_by_css_selector(".tab-contain")
        staticstic_info_html = tab_contains_elements[-1].get_attribute('innerHTML')
        soup = BeautifulSoup(staticstic_info_html, "lxml")

        for item in soup.select("p.ex"):
            detail_info.append(item.text)

        result = {}
        for item in detail_info:
            split_result = item.split("：")
            if len(split_result) != 2:
                self.logger.warn(f"item warn: {item}")

            key = split_result[0].strip()

            if key.find("\n") >= 0:
                key = key.split("\n")[0].strip()

            result[key] = split_result[1].strip()

        json_string = json.dumps(result, indent=4, sort_keys=True, ensure_ascii=False).replace("\xa5", "")
        return json.loads(json_string)


def main():
    import platform
    with open('UIMain.json') as f:
        data = json.load(f)
        config = data[platform.node()]

    with FetchFromChrome(config["Session"]) as fetch_from_chrome:
        fetch_from_chrome.fetch_detail_buy_info()
    pass


if __name__ == "__main__":
    logging_format = '%(message)s'
    logging.basicConfig(level=10, format=logging_format)

    main()