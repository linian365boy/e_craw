# -*- coding: utf-8 -*-
import datetime
import random

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
    def __init__(self, url, title):
        self.url = url


    def get_products(self):
        driver.get(self.url)
        for i in range(10):
            js = "window.scrollTo(0,{})".format(i * 500)
            driver.execute_script(js)
        products_divs = driver.find_elements_by_xpath('//*[@id="listsrp-itemlist"]/div/div/div[1]/div')
        for product_div in products_divs:
            nid = product_div.find_element_by_css_selector('div.item div.pic a').get_attribute('data-nid')
            print(nid)
            product_name = product_div.find_element_by_xpath('//*[@id="J_Itemlist_TLink_' + nid + '"]').text
            product_url = product_div.find_element_by_xpath('//*[@id="J_Itemlist_TLink_' + nid + '"]').get_attribute('href')
            sales_num = product_div.find_element_by_css_selector('div.item div.deal-cnt').text
            price = product_div.find_element_by_css_selector('div.item div.price').text
            pic_url = product_div.find_element_by_xpath('//*[@id="J_Itemlist_Pic_' + nid + '"]').get_attribute('src')

            print(product_name, product_url, sales_num, price, pic_url)




if __name__ == '__main__':
    url = 'https://s.taobao.com/list?spm=a21bo.2017.201867-links-1.6.5af911d9IcEzX5&q=%E5%B8%86%E5%B8%83+-%E4%BF%9D%E6%9A%96+-%E5%8A%A0%E7%BB%92+-%E6%A3%89&style=grid&seller_type=taobao&cps=yes&cat=50342020&sort=sale-desc'
    title = ['产品名称', '产品链接', '收货人数量', '产品价格', '产品图片']
    esales = Esales(url, title)
    esales.get_products()

