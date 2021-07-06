# -*- coding: utf-8 -*-
# @Time : 2020/09/08 11:11
# @File : eastmoney_bond.py

import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver

logger = logging.getLogger()

PATH = r'/Users/liyungui/program/chromedriver'


# selenium获取可转债数据
class Bond():
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36')

        self.driver = webdriver.Chrome(executable_path=PATH, options=options)

    def get_bond(self, code):
        url = 'http://quote.eastmoney.com/bond/{}.html'.format(code)
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 5).until(EC.title_contains(code[2:]))
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "czjg")))
            text = self.driver.find_element_by_class_name("czjg").text
            print(text)
            return text
        except Exception as e:
            logging.error(e)
            logging.warning(url)
            return '0'


if __name__ == '__main__':
    bond = Bond()
    bond.get_bond('sh113581')
    bond.get_bond('sz123063')
    bond.get_bond('sh113575')
    bond.get_bond('sz123050')
    bond.get_bond('sz123051')
    bond.driver.quit()
