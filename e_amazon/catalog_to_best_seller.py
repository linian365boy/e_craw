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


class Catalog(object):
    def __init__(self, catalog_name, catalog_url):
        self.catalog_name = catalog_name
        self.catalog_url = catalog_url


class Esales(object):
    def __init__(self, catalogs_url, base_url, title, max_catalog_limit=1, limit_per_catalog=20):
        """
        :param catalogs_url: get catalog url
        :param base_url:  get base url
        :param title: csv header row
        :param max_catalog_limit: max the catalog to craw
        :param limit_per_catalog: max the product of the catalog to craw
        """
        self.catalogs_url = catalogs_url
        self.base_url = base_url
        self.catalogs = set()
        self.title_list = title
        self.csv_file_name = str(datetime.datetime.now()).replace(":", "_").strip().replace(" ", "_").split(".")[0]
        self.max_catalog_limit = max_catalog_limit
        self.limit_per_catalog = limit_per_catalog

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
            '#zg_browseRoot > ul > li')

        catalogs_count = 0
        for ele in catalogs_eles:
            if self.filter_href(ele):
                catalogs_count += 1
                all_catalogs_eles.add(Catalog(ele.text, ele.find_element_by_tag_name('a').get_attribute('href')))
                if (self.max_catalog_limit > 0) and (catalogs_count >= self.max_catalog_limit):
                    break
        self.catalogs = all_catalogs_eles

    def sales(self):
        for catalog in self.catalogs:
            # order by sale desc
            href = catalog.catalog_url
            driver.get(href)
            # get the no.1 page products data
            for i in range(10):
                js = "window.scrollTo(0,{})".format(i * 500)
                try:
                    driver.execute_script(js)
                except:
                    pass
            products_divs = driver.find_elements_by_xpath('//*[@id="zg-ordered-list"]/li')
            row_dict = dict()
            product_count = 0
            for product_div in products_divs:
                row_dict['catalog_name'] = catalog.catalog_name
                row_dict['product_name'] = product_div.find_element_by_css_selector('div.p13n-sc-truncated').text
                row_dict['product_url'] = product_div.find_element_by_css_selector('span.aok-inline-block > a.a-link-normal').get_attribute('href')
                row_dict['product_stars'] = product_div.find_element_by_css_selector('div.a-icon-row a.a-link-normal').text
                row_dict['product_reviews'] = product_div.find_element_by_css_selector('div.a-icon-row a.a-size-small').text
                row_dict['price'] = product_div.find_element_by_css_selector('span.p13n-sc-price').text
                row_dict['pic_url'] = product_div.find_element_by_css_selector('div.a-spacing-small').get_attribute('src')
                try:
                    with open("{}.csv".format(self.csv_file_name), 'a+', encoding='utf-8', newline='') as f:
                        f_csv = csv.DictWriter(f, self.title_list)
                        f_csv.writerow(row_dict)
                        product_count += 1
                        if product_count >= self.limit_per_catalog:
                            break
                except Exception as e:
                    print(e)

    def filter_href(self, ele):
        """
        过滤不符合要求的品类
        :return:
        """
        if ele:
            return True
        else:
            return False


if __name__ == '__main__':
    catalogs_url = 'https://www.amazon.com/Best-Sellers/zgbs'
    base_url = 'https://www.amazon.com'
    title = ['catalog_name', 'product_name', 'product_url', 'product_reviews', 'product_stars', 'price', 'pic_url']
    start = int(time.time() * 1000)
    esales = Esales(catalogs_url, base_url, title, 3, 20)
    esales.get_catalogs()
    esales.sales()
    print('create esale file cost time => {} ms'.format(int(time.time()) * 1000 - start))
