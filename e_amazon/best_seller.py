# -*- coding: utf-8 -*-
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import requests
from e_amazon.craw_constant import headers_list


chrome_options = Options()
# define headless
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)
header = random.choice(headers_list)


class Catalog(object):
    def __init__(self, catalog_name='----', catalog_url='not found', parent_catalog_name='--'):
        self.catalog_name = catalog_name
        self.catalog_url = catalog_url
        self.parent_catalog_name = parent_catalog_name

    def __unicode__(self):
        return 'name={}, url={}, parent_name={}'.format(self.catalog_name, self.catalog_url, self.parent_catalog_name)


class Esales(object):
    def __init__(self, url, send_tools):
        self.url = url
        self.send_tools = send_tools
        self.catalogs = set()
        self.count = 0

    def get_children_catas(self, parent_url):
        self.count += 1
        print('parent_url=>{}'.format(parent_url))
        driver.get(parent_url)
        # get the no.1 page products data
        for i in range(8):
            js = "window.scrollTo(0,{})".format(i * 1000)
            try:
                driver.execute_script(js)
            except:
                pass
        parent_css_ul = '/ul'*(self.count-1)
        css_ul = '/ul'*self.count
        # //*[@id="zg_browseRoot"]/li/span
        parent_catalog_name = driver.find_element_by_xpath('//*[@id="zg_browseRoot"]'+parent_css_ul+'/li/span').text.strip()
        # //*[@id="zg_browseRoot"]/ul/li[1]
        children_catalogs_eles = driver.find_elements_by_xpath('//*[@id="zg_browseRoot"]'+css_ul+'/li')
        print('{} has {} children catalog, self.count=>{}'.format(parent_catalog_name, len(children_catalogs_eles), self.count))
        if len(children_catalogs_eles):
            for i, ele in enumerate(children_catalogs_eles):
                print('css_ul=>{}'.format(css_ul))
                self.get_children_catas(
                    ele.find_element_by_xpath('//*[@id="zg_browseRoot"]'+css_ul+'/li/a').get_attribute('href'))
        else:
            print('{} has no children catalog, self.count=>{}'.format(parent_catalog_name, self.count))
            return

    def get_catalogs(self, url):
        """
        获取所有品类
        :param url url of the get all catalogs
        :return:
        """
        all_catalogs_eles = set()

        # get catalogs_url catalogs
        driver.get(url)
        time.sleep(random.choice([1, 2, 3]))
        catalogs_eles = driver.find_elements_by_css_selector(
            '#zg_browseRoot > ul > li')

        if len(catalogs_eles) == 1:
            catalog_ele = catalogs_eles[0]
            catalog = Catalog(parent_catalog_name=catalog_ele.text)
            child_catalogs_eles = catalog_ele.find_elements_by_xpath('//*[@id="zg_browseRoot"]/ul/ul/li')
            print('{} has {} children catalog'.format(catalog.parent_catalog_name, len(child_catalogs_eles)))
            for ele in child_catalogs_eles:
                if self.filter_href(ele):
                    catalog.catalog_name = ele.text
                    catalog.catalog_url = ele.find_element_by_tag_name('a').get_attribute('href')
                    all_catalogs_eles.add(catalog)
                    self.get_catalogs(catalog.catalog_url)
        elif len(catalogs_eles) > 1:
            print('all has {} children catalog'.format(len(catalogs_eles)))
            for ele in catalogs_eles:
                if self.filter_href(ele):
                    all_catalogs_eles.add(Catalog(catalog_name=ele.text, catalog_url=ele.find_element_by_tag_name('a').get_attribute('href')))
                    self.get_catalogs(ele.find_element_by_tag_name('a').get_attribute('href'))
        else:
            print('no children catalogs')
            return
        self.catalogs = all_catalogs_eles

    def get_content(self):
        if self.send_tools != 'selenium':
            print('use {} craw data'.format(self.send_tools))
            # use requests and beautifulSoup
            html = requests.get(self.url, headers=header)
            soup = BeautifulSoup(html.content, "html.parser")
            products_divs = soup.select("span.a-icon-alt")
            for product_div in products_divs:
                ele = product_div.string
                print(ele)
        else:
            # use selenium
            print('use {} craw data..'.format(self.send_tools))
            driver.get(url)
            for i in range(8):
                js = "window.scrollTo(0,{})".format(i * 1000)
                try:
                    driver.execute_script(js)
                except:
                    pass
            products_divs = driver.find_elements_by_xpath('//*[@id="zg-ordered-list"]/li')
            print('length=%s' % len(products_divs))
            for product_div in products_divs:
                print(product_div.text)
            driver.close()

    def filter_href(self, ele):
        if ele:
            return True
        else:
            return False


if __name__ == '__main__':
    url = 'https://www.amazon.com/Best-Sellers/zgbs'
    # url = 'https://www.amazon.com/Best-Sellers/zgbs/amazon-devices/ref=zg_bs_unv_1_17045325011_2'
    start = int(time.time()) * 1000
    esales = Esales(url, "selenium")
    esales.get_children_catas(url)
    print('cost time => {}ms'.format((int(time.time()) * 1000) - start))
