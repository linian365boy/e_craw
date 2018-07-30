import requests
from bs4 import BeautifulSoup
import random
import os
import csv
import time
from datetime import datetime

from e_amazon.craw_constant import headers_list


class Keyword_placement():

    def __init__(self):
        # 这里填你要查排名的ASIN，注意英文引号，英文逗号，每行必须左对齐！
        self.asin_list = [
            "B01E9TJMAQ",
            "B074MM3CST",
        ]
        # 这里填你要查排名的关键词，注意英文引号，英文逗号，每行必须左对齐！
        self.keyword_list = [
            "dog ropes",
            "dog toy ropes",
        ]
        # 选填，不填也可以的，这里填ASIN和SKU对应关系，注意英文引号，英文冒号，英文逗号，每行必须左对齐！
        self.asin_sku_dict = {
            #"B01E9TJMAQ": "产品1",
            #"B074MM3CST": "产品2",
        }
        # 这里填每个关键词搜索的最大页数
        self.max_page = 5
        # 防止爬取太频繁导致亚马逊买家页面不能访问，每爬取一个页面，休息的时间秒数
        self.sleep_time = 1
        # 下面的不用更改
        self.rank_dict_list = []
        self.csv_file_name = ""

    def download_soup_by_url(self, url):
        headers = random.choice(headers_list)
        # r = requests.get(url, headers=headers)
        r = requests.get(url, headers=headers)
        # print("Downloading: r.status_code=", r.status_code)
        # print("url: ", url)
        if r.status_code != 200:
            headers = random.choice(headers_list)
            r = requests.get(url, headers=headers)

        soup = BeautifulSoup(r.content, 'html.parser')
        # soup = BeautifulSoup(r.read(), 'html.parser')
        # soup = BeautifulSoup(r.content.decode('utf-8'), 'html.parser')
        # soup = BeautifulSoup(r.content, 'html5lib')
        time.sleep(self.sleep_time)
        return soup

    def find_the_rank(self, soup, page, keyword):
        if soup:
            lis = soup.find_all("li", class_="s-result-item")
            for li_index, li in enumerate(lis):
                try:
                    asin = li["data-asin"].strip()
                    for given_asin in self.asin_list:
                        if given_asin.strip() == asin:
                            rank = li_index + 1
                            page_rank = "page" + str(page) + "-" + str(rank)
                            sponsored_or_natural_rank = "natural rank"
                            try:
                                if li.find("h5").get_text().strip().split()[0]:
                                    if li.find("h5").get_text().strip().split()[0] == "Sponsored":
                                        sponsored_or_natural_rank = "AD"
                            except:
                                pass
                            sku = "no sku"
                            try:
                                if self.asin_sku_dict[asin]:
                                    sku = self.asin_sku_dict[asin]
                            except:
                                pass
                            print(keyword + ": " + page_rank + ": " + asin + ": " + sku + ": " + sponsored_or_natural_rank)
                            rank_dict = {
                                "keyword": keyword,
                                "page_rank": page_rank,
                                "asin": asin,
                                "sku": sku,
                                "sponsored_or_natural_rank": sponsored_or_natural_rank,
                            }
                            self.rank_dict_list.append(rank_dict)
                except:
                    pass

    def dict_list_to_csv_file(self):
        print("***********************************")
        print("start to write csv file...")
        headers = []
        for i in self.rank_dict_list[0]:
            headers.append(i)

        csv_folder = "page rank"
        csv_file_path = csv_folder + "/" + str(self.csv_file_name) + ".csv"

        if not os.path.exists(csv_folder):
            print("***********************************")
            print("picture folder not exist, create the folder now...")
            os.mkdir(csv_folder)
            print("success to create picture folder")

        try:
            with open(csv_file_path, 'w', encoding='utf8', newline='') as f:
                f_csv = csv.DictWriter(f, headers)
                f_csv.writeheader()
                f_csv.writerows(self.rank_dict_list)
                print("success to write csv file...")
        except:
            print("fail to write csv!")

    def keyword_to_something(self, keyword):
        how_many_pages = self.max_page
        base_url = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="
        first_page_url = base_url + keyword

        page = 1
        # print(page)
        soup = self.download_soup_by_url(first_page_url)
        self.find_the_rank(soup, page, keyword)

        while how_many_pages > 1:
            try:
                if soup.find(id="pagnNextLink")["href"]:
                    next_page_url_part2 = soup.find(id="pagnNextLink")["href"]
                    next_page_url = "https://www.amazon.com" + next_page_url_part2
                    page = page + 1

                    soup = self.download_soup_by_url(next_page_url)
                    self.find_the_rank(soup, page, keyword)
            except:
                pass

            how_many_pages = how_many_pages - 1

    def get_keyword_placement(self):
        self.csv_file_name = str(datetime.now()).replace(":", "_").strip().replace(" ", "_").split(".")[0]
        start_time = datetime.now()
        for keyword in self.keyword_list:
            self.keyword_to_something(keyword)
        self.dict_list_to_csv_file()

        end_time = datetime.now()
        how_many_seconds = end_time - start_time
        print(start_time)
        print(end_time)
        print(str(how_many_seconds.total_seconds()) + "seconds")

#main function
keyword_placement = Keyword_placement()
keyword_placement.get_keyword_placement()