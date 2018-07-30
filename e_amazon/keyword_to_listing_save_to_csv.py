# coding: utf-8

import re
import requests
import os
import csv

from e_amazon import amazon_module


class Keyword_to_listing():

    def __init__(self):

        self.keyword_list = [
            "dog shock collar",
        ]
        self.max_page = 1
        self.csv_folder = ""
        self.csv_file_name = ""
        self.picture_folder = ""
        self.picture_url = ""
        self.keyword = ""
        self.asin = ""
        self.listing_info_dict = dict()

    def listing_info_dict_to_csv_file(self):
        try:
            headers = []
            for i in self.listing_info_dict:
                headers.append(i)
        except:
            print("fail to find csv header tags")

        csv_file_path = self.csv_folder + self.csv_file_name

        if not os.path.exists(self.csv_folder):
            os.mkdir(self.csv_folder)
            print("success to create folder")

        if not os.path.isfile(csv_file_path):
            try:
                with open(csv_file_path, 'w', encoding='utf8', newline='') as f:
                    f_csv = csv.DictWriter(f, headers)
                    f_csv.writeheader()
                    print("success to write csv header!")
            except:
                print("fail to write csv header!")

        try:
            with open(csv_file_path, 'a+', encoding='utf8', newline='') as f:
                f_csv = csv.DictWriter(f, headers)
                f_csv.writerow(self.listing_info_dict)
                print("success to write csv content!")
        except:
            print("fail to write csv content!")

    def download_picture_by_url(self):
        try:
            if not os.path.exists(self.picture_folder):
                os.makedirs(self.picture_folder)
                print("success to create picture folder")
        except:
            print("fail to create picture folder")

        try:
            pic = requests.get(self.picture_url, timeout=10)
            picture_name = self.picture_folder + str(self.asin) + '.jpg'
            with open(picture_name, 'wb') as fp:
                fp.write(pic.content)
            print("success to download picture!")
        except requests.exceptions.ConnectionError:
            print("fail to download picture!")

    def asin_to_listing_info(self):
            print("asin: ", self.asin)
            url = "https://www.amazon.com/dp/" + self.asin
            soup = amazon_module.soup_by_url(url)

            brand = " "
            try:
                if soup.find(id="bylineInfo"):
                    brand = soup.find(id="bylineInfo").get_text().strip()
                if soup.find(id="brand"):
                    brand = soup.find(id="brand").get_text().strip()
            except:
                pass
            print("brand:", brand)

            badge = ""
            try:
                if soup.find("a", class_="badge-link"):
                   badge = " ".join(soup.find("a", class_="badge-link").get_text().strip().split())
            except:
                pass
            print("badge:", badge)

            title = ""
            try:
                if soup.find(id="productTitle"):
                    title = soup.find(id="productTitle").get_text().strip()
            except:
                pass
            print("title:", title)

            variation_name = " "
            try:
                if soup.find(id="variation_pattern_name"):
                    variation_name = soup.find(id="variation_pattern_name").find("span").get_text().strip()
                    print("variation_pattern_name: ", variation_name)
                elif soup.find(id="variation_color_name"):
                    variation_name = soup.find(id="variation_color_name").find("span").get_text().strip()
                    print("variation_color_name: ", variation_name)
                elif soup.find(id="variation_size_name"):
                    variation_name = soup.find(id="variation_size_name").find("span").get_text().strip()
                    print("variation_size_name: ", variation_name)
                else:
                    print("variation_name: ", variation_name)
                variation_name = " ".join(variation_name.split())
            except:
                pass

            price = " "
            try:
                if soup.find(id="price"):
                    price = soup.find(id="price").find("span").get_text().strip()
                if soup.find(id="priceblock_ourprice"):
                    price = soup.find(id="priceblock_ourprice").get_text().strip()
            except:
                pass
            print("price:", price)

            sold_by = " "
            try:
                if soup.find(id="merchant-info"):
                    sold_by = " ".join(soup.find(id="merchant-info").get_text().strip().split())
            except:
                pass
            print("sold_by:", sold_by)

            how_many_sellers = " "
            try:
                if soup.find(id="olp_feature_div"):
                    how_many_sellers = soup.find(id="olp_feature_div").find("a").get_text().strip()
            except:
                pass
            print("how_many_sellers:", how_many_sellers )

            bullets_list = []
            try:
                if  soup.find("div", id="feature-bullets"):
                    bullets_contents = soup.find("div", id="feature-bullets").find_all("span", class_="a-list-item")
                    for bullets_content in bullets_contents:
                        print(bullets_content.get_text().strip())
                        #toys
                        if bullets_content.span:
                            continue
                        bullets_list.append(bullets_content.get_text().strip())
                        bullets = bullets_list

                        bullet_1 = " "
                        bullet_2 = " "
                        bullet_3 = " "
                        bullet_4 = " "
                        bullet_5 = " "
                        bullet_6 = " "
                        bullet_7 = " "
                        bullet_8 = " "
                        bullet_9 = " "
                        bullet_10 = " "
                        if bullets:
                            try:
                                bullet_1 = bullets[0]
                            except:
                                pass
                            try:
                                bullet_2 = bullets[1]
                            except:
                                pass
                            try:
                                bullet_3 = bullets[2]
                            except:
                                pass
                            try:
                                bullet_4 = bullets[3]
                            except:
                                pass
                            try:
                                bullet_5 = bullets[4]
                            except:
                                pass
                            try:
                                bullet_6 = bullets[5]
                            except:
                                pass
                            try:
                                bullet_7 = bullets[6]
                            except:
                                pass
                            try:
                                bullet_8 = bullets[7]
                            except:
                                pass
                            try:
                                bullet_9 = bullets[8]
                            except:
                                pass
                            try:
                                bullet_10 = bullets[9]
                            except:
                                pass
            except:
                pass
            print("bullets_list:", bullets_list)

            description = " "
            try:
                if soup.find(id="productDescription"):
                    description = soup.find(id="productDescription").get_text()
            except:
                pass
            description = re.sub(r"(Product Description.*; } )", "", description)
            description = description.replace("Read more", "")
            description = " ".join(description.split())
            print("description:", description)

            aplus = " "
            try:
                if soup.find(id="aplus"):
                    aplus = soup.find(id="aplus").get_text()
                aplus = " ".join(aplus.split())
            except:
                pass
            aplus = re.sub(r"(From the manufacturer .aplus-v2 .*; } )", "", aplus)
            aplus = re.sub(r"(Product Description .aplus-v2 .*; } )", "", aplus)
            aplus = aplus.replace("Read more", "")
            aplus = " ".join(aplus.split())
            print("aplus:", aplus)

            salesrank = " "
            try:
                if soup.find(id="SalesRank"):
                    salesrank = soup.find(id="SalesRank")
                    salesrank = salesrank.get_text().strip()
                    salesrank = re.search('#(\d|,)+', salesrank)
                    salesrank = salesrank.group()
                    salesrank = salesrank.replace(',', '')
                    salesrank = salesrank.replace('#', '')
                #toys
                if soup.find(id="productDetails_detailBullets_sections1"):
                    trs = soup.find(id="productDetails_detailBullets_sections1").find_all("tr")
                    for tr in trs:
                        if tr.find("th").get_text().strip():
                            if tr.find("th").get_text().strip() == "Best Sellers Rank":
                                salesrank = tr.find("td").get_text().strip()
                                salesrank = re.search('#(\d|,)+', salesrank)
                                salesrank = salesrank.group()
                                salesrank = salesrank.replace(',', '')
                                salesrank = salesrank.replace('#', '')
            except:
                pass
            print("salesrank:", salesrank)

            review_num = " "
            try:
                if soup.find(id="acrCustomerReviewText"):
                    review_num = soup.find(id="acrCustomerReviewText").get_text().split()[0].strip()
            except:
                pass
            print("review_num:", review_num)

            review_value = " "
            try:
                if soup.find(class_="arp-rating-out-of-text"):
                    review_value = soup.find(class_="arp-rating-out-of-text").get_text().strip()
                    review_value = re.search('(.*?)\s', review_value)
                    review_value = review_value.group()
                    review_value = review_value.strip()
            except:
                pass
            print("review_value:", review_value)

            qa_num = " "
            try:
                if soup.find(id="askATFLink"):
                    qa_num = soup.find(id="askATFLink").get_text().split()[0].strip()
            except:
                pass
            print("qa_num:", qa_num)

            picture_url = " "
            try:
                picture_urls_dict = dict()
                if soup.find("img", id="landingImage"):
                    picture_urls = soup.find("img", id="landingImage")["data-a-dynamic-image"]
                    picture_urls_dict = eval(picture_urls)
                picture_urls_list = []
                for key in picture_urls_dict.keys():
                    picture_urls_list.append(key)
                picture_url = picture_urls_list[0]
            except:
                pass
            print("picture_url:", picture_url)

            self.listing_info_dict = {
                "asin": self.asin,
                "url": url,
                "brand": brand,
                "badge": badge,
                "title": title,
                "variation_name": variation_name,
                "price": price,
                "sold_by": sold_by,
                "how_many_sellers": how_many_sellers,
                "bullet_1": bullet_1,
                "bullet_2": bullet_2,
                "bullet_3": bullet_3,
                "bullet_4": bullet_4,
                "bullet_5": bullet_5,
                "bullet_6": bullet_6,
                "bullet_7": bullet_7,
                "bullet_8": bullet_8,
                "bullet_9": bullet_9,
                "bullet_10": bullet_10,
                "description": description,
                "aplus": aplus,
                "salesrank": salesrank,
                "review_num": review_num,
                "review_value": review_value,
                "qa_num": qa_num,
                "picture_url": picture_url
                                 }

            return self.listing_info_dict

    def keyword_to_asin_list(self):
        print("keyword_to_asin_list is running...")
        base_url = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="
        keyword_with_underline = "_".join(self.keyword.split())
        keyword_with_plus = "+".join(self.keyword.split())
        first_page_url = base_url + keyword_with_plus

        pages_urls_list = []
        pages_urls_list.append(first_page_url)
        page = 1
        while page <= self.max_page:
            soup = amazon_module.soup_by_url(pages_urls_list[-1])
            try:
                if soup.find(id="pagnNextLink")["href"]:
                    next_page_url_part2 = soup.find(id="pagnNextLink")["href"]
                    next_page_url = "https://www.amazon.com" + next_page_url_part2
                    pages_urls_list.append(next_page_url)
                page = page + 1
            except:
                pass

            try:
                lis = soup.find_all("li", class_="s-result-item")
                for index, li in enumerate(lis):
                    try:
                        self.asin = li["data-asin"]

                        page_rank = "page" + str(page - 1) + "-" + str(index + 1)
                        print("page_rank:", page_rank)

                        sponsored_or_natural_rank = "natural_rank"
                        try:
                            if li.find("h5").get_text().strip().split()[0]:
                                if li.find("h5").get_text().strip().split()[0] == "Sponsored":
                                    sponsored_or_natural_rank = "sponsored"
                                else:
                                    sponsored_or_natural_rank = "natural_rank"
                        except:
                            pass
                        print("sponsored_or_natural_rank:", sponsored_or_natural_rank)

                        is_prime = ""
                        try:
                            if li.find("i", class_="a-icon-prime"):
                                is_prime  = "prime"
                        except:
                            pass
                        print("is_prime:", is_prime)

                        listing_info_dict = self.asin_to_listing_info()
                        listing_info_dict["page_rank"] = page_rank
                        listing_info_dict["sponsored_or_natural_rank"] = sponsored_or_natural_rank
                        listing_info_dict["is_prime"] = is_prime

                        try:
                            self.listing_info_dict_to_csv_file()
                        except:
                            pass

                        try:
                            self.picture_url = listing_info_dict['picture_url']
                            self.download_picture_by_url()
                        except:
                            pass
                    except:
                        pass
            except:
                pass

    def start(self):
        try:
            for keyword_temp in self.keyword_list:
                try:
                    self.keyword = keyword_temp
                    keyword_with_underline = "_".join(self.keyword.split())
                    self.csv_folder = "listing/" + keyword_with_underline + "/"
                    self.csv_file_name = keyword_with_underline + ".csv"
                    self.picture_folder = self.csv_folder + "pictures/"

                    # create csv folder
                    try:
                        if not os.path.exists(self.csv_folder):
                            os.makedirs(self.csv_folder)
                            print("success to create csv_folder folder")
                    except:
                        print("fail to create csv_folder folder")

                     # create picture folder
                    try:
                        if not os.path.exists(self.picture_folder):
                            os.makedirs(self.picture_folder)
                            print("success to create picture folder")
                    except:
                        print("fail to create picture folder")

                    self.keyword_to_asin_list()
                except:
                    print("fail")
        except:
            print("fail")

#main function
keyword_to_listing = Keyword_to_listing()
keyword_to_listing.start()