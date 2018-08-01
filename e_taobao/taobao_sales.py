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
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)


class Esales(object):

	def __init__(self, catalogs_url, base_url):
		self.catalogs_url = catalogs_url
		self.base_url = base_url
		self.time = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")
		self.catalogs = set()


	def get_catalogs(self):
		"""
		获取所有品类
		:param url url of the get all catalogs
		:return:
		"""
		all_catalogs_eles = set()

		# get catalogs_url catalogs
		driver.get(self.catalogs_url)
		catalogs_eles = driver.find_elements_by_css_selector('div.home-category-list li.category-list-item div.category-items a')
		for ele in catalogs_eles:
			if self.filter_href(ele):
				all_catalogs_eles.add({'title': ele.text, 'href': ele.get_attribute('href')})

		# get base_url catalogs
		driver.get(self.base_url)
		catalogs_eles = driver.find_elements_by_css_selector('ul.service-bd li')
		for ele in catalogs_eles:
			ActionChains(driver).move_to_element(ele).perform()
			time.sleep(random.choice([1, 2]))
			small_catalogs_eles = driver.find_elements_by_css_selector('div.service-float div.service-panel p a')
			for small_ele in small_catalogs_eles:
				if self.filter_href(small_ele):
					all_catalogs_eles.add({'title': small_ele.text, 'href': small_ele.get_attribute('href')})
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
			href = catalog.get('href') + '&sort=sale-desc'
			driver.get(href)
			# get the no.1 page products data
			for i in range(10):
				js = "window.scrollTo(0,{})".format(i * 500)
				self.driver.execute_script(js)
				time.sleep(random.choice([0.5, 0.3]))
			# TODO get products data



if __name__ == '__main__':
	catalogs_url = 'https://www.taobao.com/tbhome/page/market-list'
	base_url = 'https://www.taobao.com'
	esales = Esales(catalogs_url, base_url)
	catalogs = esales.catalogs
	print(catalogs)
	print(len(catalogs))

