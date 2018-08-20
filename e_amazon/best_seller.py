# -*- coding: utf-8 -*-
import datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv
from selenium.webdriver.support.wait import WebDriverWait
import logging
from logging.config import dictConfig

logging_config = dict(
	version=1,
	formatters={
		'f': {
			'format':
				'%(asctime)s %(name)-10s %(lineno)d %(process)d %(thread)d %(threadName)s %(levelname)-8s %('
		                'message)s'}
	},
	handlers={
		'h': {'class': 'logging.FileHandler',
		      'filename': 'logging.log',
		      'formatter': 'f',
		      'level': logging.INFO
		      },
		'console': {
			'class': 'logging.StreamHandler',
			'level': 'DEBUG',
			'formatter': 'f'
		}
	},
	loggers={
		'root': {
			'handlers': ['console'],
			'level': 'INFO',
			# 'propagate': True,
		},
		'simple': {
			'handlers': ['console', 'h'],
			'level': 'INFO',
		}
	}
)
dictConfig(logging_config)
logger = logging.getLogger('simple')

chrome_options = Options()
# define headless
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(chrome_options=chrome_options)

per_file_max_line = 20000
per_file_init_line = 0

class Catalog(object):
    def __init__(self, catalog_name='----', catalog_url='not found', parent_catalog_name='--'):
        self.catalog_name = catalog_name
        self.catalog_url = catalog_url
        self.parent_catalog_name = parent_catalog_name

    def __unicode__(self):
        return 'name={}, url={}, parent_name={}'.format(self.catalog_name, self.catalog_url, self.parent_catalog_name)


class Esales(object):
    def __init__(self, url, title, max_limit):
        self.url = url
        self.csv_file_name = str(datetime.datetime.now()).replace(":", "_").strip().replace(" ", "_").split(".")[0]
        self.title_list = title
        self.max_limit = max_limit
        self.per_file_init_line = per_file_init_line

        try:
            with open("{}.csv".format(self.csv_file_name), 'w', encoding='utf-8', newline='') as f:
                f_csv = csv.DictWriter(f, self.title_list)
                f_csv.writeheader()
                logger.info('create csv file and header success.')
        except Exception as e:
            logger.info(e)

    def children_catalog(self, parent_url):
        logger.info('parent_url=>{}'.format(parent_url))
        driver.get(parent_url)
        for i in range(8):
            js = "window.scrollTo(0,{})".format(i * 1000)
            try:
                driver.execute_script(js)
            except:
                pass
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'zg_browseRoot'))
            )
            try:
                eles = element.find_elements_by_class_name("zg_browseUp")
                loop_count = len(eles)
            except:
                loop_count = 0
            parent_css_ul = '/ul'*loop_count
            css_ul = '/ul'*(loop_count+1)
            logger.info('parent_css_ul=>{}, css_ul=>{}'.format(parent_css_ul, css_ul))
            # https://www.amazon.com/Best-Sellers-Fire-TV/zgbs/amazon-devices/8521791011/ref=zg_bs_nav_2_2102313011
            # 非叶子节点，当前选中节点的页面，span.zg_selected
            # //*[@id="zg_browseRoot"]/ul/ul/ul/li/span
            # 其子节点：
            # //*[@id="zg_browseRoot"]/ul/ul/ul/ul/li
            # 父节点：
            # //*[@id="zg_browseRoot"]/ul/ul/li/a

            # 叶子
            # //*[@id="zg_browseRoot"]/ul/ul/ul/li[4]/span
            # 父节点：
            # //*[@id="zg_browseRoot"]/ul/ul/li/a
            try:
                parent_catalog_name = element.find_element_by_xpath('//*[@id="zg_browseRoot"]'+parent_css_ul+'/li/span').text.strip()
                children_catalogs_eles = element.find_elements_by_xpath('//*[@id="zg_browseRoot"]'+css_ul+'/li')
            except:
                children_catalogs_eles = []
            logger.info('{} has {} children catalog, loop_count=>{}'.format(parent_catalog_name, len(children_catalogs_eles), loop_count))
            children_list = []
            if len(children_catalogs_eles):
                for ele in children_catalogs_eles:
                    catalog_name = ele.text
                    href = ele.find_element_by_tag_name('a').get_attribute('href')
                    catalog = Catalog(catalog_name, href, parent_catalog_name)
                    children_list.append(catalog)
            return children_list
        except Exception as e:
            logger.info('error => {}'.format(e))
            return None

    def all_catalog(self, url):
        children_list = self.children_catalog(url)
        if children_list and len(children_list):
            for cata in children_list:
                self.sales(cata)
                self.all_catalog(cata.catalog_url)
        else:
            return


    def sales(self, catalog):
        # order by sale desc
        href = catalog.catalog_url
        driver.get(href)
        # get the no.1 page products data
        for i in range(10):
            js = "window.scrollTo(0,{})".format(i * 800)
            try:
                driver.execute_script(js)
            except:
                pass
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'zg-ordered-list'))
            )
            products_divs = element.find_elements_by_xpath('//*[@id="zg-ordered-list"]/li')
            length = len(products_divs)
            logger.info('find page one products number {}'.format(length))
            if length > self.max_limit:
                products_divs = products_divs[0:self.max_limit]
            for index, product_div in enumerate(products_divs):
                row_dict = {}.fromkeys(['parent_catalog_name', 'catalog_name', 'product_name', 'product_url',
                                        'product_stars', 'product_reviews', 'price', 'pic_url'], '----')
                row_dict['parent_catalog_name'] = catalog.parent_catalog_name
                row_dict['catalog_name'] = catalog.catalog_name

                try:
                    row_dict['product_name'] = product_div.find_element_by_xpath('//*[@id="zg-ordered-list"]/li[' + str(index+1) + ']/span/div/span/a/div').get_attribute('textContent')
                except:
                    pass
                try:
                    row_dict['product_url'] = product_div.find_element_by_xpath('//*[@id="zg-ordered-list"]/li[' + str(index+1) + ']/span/div/span/a').get_attribute('href')
                except:
                    pass
                try:
                    row_dict['product_stars'] = product_div.find_element_by_xpath('//*[@id="zg-ordered-list"]/li[' + str(index+1) + ']/span/div/span/div[1]/a[1]/i/span').get_attribute('textContent')
                except:
                    pass
                try:
                    row_dict['product_reviews'] = product_div.find_element_by_xpath('//*[@id="zg-ordered-list"]/li[' + str(index+1) + ']/span/div/span/div[1]/a[2]').get_attribute('textContent')
                except:
                    row_dict['product_reviews'] = 0
                try:
                    row_dict['price'] = product_div.find_element_by_xpath('//*[@id="zg-ordered-list"]/li[' + str(index+1) + ']/span/div/span/div[2]/a/span/span').get_attribute('textContent')
                except:
                    pass
                try:
                    row_dict['pic_url'] = product_div.find_element_by_xpath('//*[@id="zg-ordered-list"]/li[' + str(index+1) + ']/span/div/span/a/span/div/img').get_attribute('src')
                except:
                    pass
                try:
                    if self.per_file_init_line <= per_file_max_line:
                        with open("{}.csv".format(self.csv_file_name), 'a+', encoding='utf-8', newline='') as f:
                            f_csv = csv.DictWriter(f, self.title_list)
                            f_csv.writerow(row_dict)
                            self.per_file_init_line += 1
                    else:
                        try:
                            self.csv_file_name = str(datetime.datetime.now()).replace(":", "_").strip().replace(" ", "_").split(".")[0]
                            with open("{}.csv".format(self.csv_file_name), 'w', encoding='utf-8', newline='') as f:
                                f_csv = csv.DictWriter(f, self.title_list)
                                f_csv.writeheader()
                                f_csv.writerow(row_dict)
                                self.per_file_init_line = 1
                                logger.info('create another csv file and header success.')
                        except Exception as e:
                            logger.info(e)
                except Exception as e:
                    logger.info(e)
        except Exception as e:
            logger.info(e)


    def filter_href(self, ele):
        if ele:
            return True
        else:
            return False


if __name__ == '__main__':
    url = 'https://www.amazon.com/Best-Sellers/zgbs'
    start = int(time.time()) * 1000
    title = ['parent_catalog_name', 'catalog_name', 'product_name', 'product_url', 'product_reviews', 'product_stars', 'price', 'pic_url']
    esales = Esales(url, title, 20)
    esales.all_catalog(url)
    logger.info('cost time => {}ms'.format((int(time.time()) * 1000) - start))
