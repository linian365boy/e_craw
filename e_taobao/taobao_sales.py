# -*- coding: utf-8 -*-
import datetime
import random
import csv

import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

"""
查询淘宝销量前几的商品，不分品类
"""

chrome_options = Options()
# define headless
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)


class Esales(object):
    def __init__(self, catalogs_url, base_url, title, max_catalog_limit=1):
        self.catalogs_url = catalogs_url
        self.base_url = base_url
        self.catalogs = set()
        self.title_list = title
        self.csv_file_name = str(datetime.datetime.now()).replace(":", "_").strip().replace(" ", "_").split(".")[0]
        self.max_catalog_limit = max_catalog_limit

        try:
            with open("{}.csv".format(self.csv_file_name), 'w', encoding='utf-8', newline='') as f:
                f_csv = csv.DictWriter(f, self.title_list)
                f_csv.writeheader()
                print('create csv file and header success.')
        except Exception as e:
            print(e)

    def get_catalogs(self):
        """
        获取所有品类
        :param url url of the get all catalogs
        :return:
        """
        all_catalogs_eles = set()

        # get catalogs_url catalogs
        driver.get(self.catalogs_url)
        catalogs_eles = driver.find_elements_by_css_selector(
            'div.home-category-list li.category-list-item div.category-items a')

        catalogs_count = 0
        for ele in catalogs_eles:
            if self.filter_href(ele):
                catalogs_count += 1
                all_catalogs_eles.add(ele.get_attribute('href'))
                if catalogs_count >= self.max_catalog_limit:
                    break

        # get base_url catalogs
        if catalogs_count < self.max_catalog_limit:
            driver.get(self.base_url)
            catalogs_eles = driver.find_elements_by_css_selector('ul.service-bd li')
            for ele in catalogs_eles:
                ActionChains(driver).move_to_element(ele).perform()
                time.sleep(random.choice([1, 2]))
                small_catalogs_eles = driver.find_elements_by_css_selector('div.service-float div.service-panel p a')
                for small_ele in small_catalogs_eles:
                    if self.filter_href(small_ele):
                        all_catalogs_eles.add(small_ele.get_attribute('href'))
        self.catalogs = all_catalogs_eles

    def filter_href(self, ele):
        """
        过滤不符合要求的品类
        :param ele: the catalogs ele of wait to filter
        :return:
        """
        href = ele.get_attribute('href')
        if href and (href.find('list') > 0 or href.find('search') > 0):
            return True
        else:
            return False

    def sales(self):
        for catalog in self.catalogs:
            # order by sale desc
            href = catalog + '&sort=sale-desc'
            driver.get(href)
            # get the no.1 page products data
            for i in range(10):
                js = "window.scrollTo(0,{})".format(i * 500)
                driver.execute_script(js)
            products_divs = driver.find_elements_by_xpath('//*[@id="listsrp-itemlist"]/div/div/div[1]/div')
            row_dict = dict()
            for product_div in products_divs:
                nid = product_div.find_element_by_css_selector('div.item div.pic a').get_attribute('data-nid')
                row_dict['product_name'] = product_div.find_element_by_xpath('//*[@id="J_Itemlist_TLink_' + nid + '"]').text
                row_dict['product_url'] = product_div.find_element_by_xpath('//*[@id="J_Itemlist_TLink_' + nid + '"]').get_attribute('href')
                row_dict['sales_num'] = product_div.find_element_by_css_selector('div.item div.deal-cnt').text
                row_dict['sales_num'] = re.sub("\D", "", row_dict['sales_num'])
                row_dict['price'] = product_div.find_element_by_css_selector('div.item div.price').text
                row_dict['pic_url'] = product_div.find_element_by_xpath('//*[@id="J_Itemlist_Pic_' + nid + '"]').get_attribute('src')
                try:
                    with open("{}.csv".format(self.csv_file_name), 'a+', encoding='utf-8', newline='') as f:
                        f_csv = csv.DictWriter(f, self.title_list)
                        f_csv.writerow(row_dict)
                except Exception as e:
                    print(e)


if __name__ == '__main__':
    catalogs_url = 'https://www.taobao.com/tbhome/page/market-list'
    base_url = 'https://www.taobao.com'
    title = ['product_name', 'product_url', 'sales_num', 'price', 'pic_url']
    start = int(time.time() * 1000)
    esales = Esales(catalogs_url, base_url, title, max_catalog_limit=10)
    esales.get_catalogs()
    esales.sales()
    print('create esale file cost time => {} ms'.format(int(time.time()) * 1000 - start))
