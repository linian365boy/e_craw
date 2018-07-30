#!/usr/bin/env python
# -*- coding:utf-8 -*-

import io
import re
import os
import csv
from datetime import datetime

from e_amazon.amazon_module import soup_by_url


class Asin_to_reviews():

	def __init__(self):
		# 这里填你要爬取得ASIN，注意英文引号，英文逗号，每行必须左对齐！
		self.asin_list = [
			"B01B0BSN0G",
		]
		# 这里填每个ASIN里review最大爬取页数
		self.max_page = 1
		# recent表示爬取最近时间的review，top表示爬取默认排名高的review
		self.top_or_recent = "recent"
		# all代表所有星级，positive代表好评，critical代表差评
		self.all_or_positive_or_critical = "all"
		# 防止爬取太频繁导致亚马逊买家页面不能访问，每爬取一个页面，休息的时间秒数
		self.sleep_time = 1
		# 下面的不用更改
		self.review_dict_list = []
		self.csv_file_name = ""

	def dict_list_to_csv_file(self):
		# print("***********************************")
		# print("start to write csv file...")
		headers = []
		for i in self.review_dict_list[0]:
			headers.append(i)

		csv_folder = "reviews"
		csv_file_path = csv_folder + "/" + str(self.csv_file_name) + ".csv"

		if not os.path.exists(csv_folder):
			print("***********************************")
			print("reviews folder not exist, create the folder now...")
			os.mkdir(csv_folder)
			print("success to create reviews folder")

		if not os.path.isfile(csv_file_path):
			try:
				with io.open(csv_file_path, 'w', encoding='utf-8', newline='') as f:
					f_csv = csv.writer(f)
					f_csv.writerow(headers)
			except Exception as e:
				# print("FAIL to write csv header!")
				print(e)
				pass

		try:
			with io.open(csv_file_path, 'a+', encoding='utf-8', newline='') as f:
				f_csv = csv.DictWriter(f, headers)
				# print("self.review_dict_list:", self.review_dict_list)
				f_csv.writerows(self.review_dict_list)
		# print("SUCCESS to write csv content...")
		except Exception as e:
			print(e)
			pass

	def first_review_url_to_review_info(self, url, asin):
		location = re.search("ref=", url)
		span = location.span()[0]
		first_review_url_part1 = url[:span]

		review_base_url = first_review_url_part1 + "ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=" + self.all_or_positive_or_critical + "&reviewerType=all_reviews&sortBy=" + self.top_or_recent + "&pageNumber="
		first_review_url = review_base_url + str(1)
		first_review_url_soup = soup_by_url(first_review_url)

		last_page = 1
		try:
			last_page = first_review_url_soup.find(id="cm_cr-pagination_bar").find_all("li", class_="page-button")[
				-1].get_text()
		except:
			pass
		last_page = int(last_page)
		min_page = min(last_page, self.max_page)

		for page in range(1, min_page + 1):
			review_url = review_base_url + str(page)
			try:
				soup = soup_by_url(review_url)
				review_list = soup.find(id="cm_cr-review_list").find_all("div", {"data-hook": "review"})

				self.review_dict_list = []
				for review_index, review in enumerate(review_list):
					review_title = review.find("a", {"data-hook": "review-title"}).get_text()
					review_star_rating = review.find("i", {"data-hook": "review-star-rating"}).get_text()
					review_author = review.find("a", {"data-hook": "review-author"}).get_text()
					review_date = review.find("span", {"data-hook": "review-date"}).get_text()
					review_body = review.find("span", {"data-hook": "review-body"}).get_text()
					page_rank = "page" + str(page) + "-" + str(review_index + 1)
					profile_url_part = review.find("a", {"data-hook": "review-author"})['href']
					profile_url = "https://www.amazon.com" + profile_url_part

					review_bage = ""
					try:
						review_bage = review.find("span", {"data-hook": "avp-badge"}).get_text()
					except:
						pass

					review_variation = ""
					try:
						review_variation = review.find("a", {"data-hook": "format-strip"}).get_text()
					except:
						pass

					review_dict = {"page_rank": page_rank,
								   "asin": asin,
								   "review_bage": review_bage,
								   "review_variation": review_variation,
								   "review_title": review_title,
								   "review_star_rating": review_star_rating,
								   "review_author": review_author,
								   "review_date": review_date,
								   "review_body": review_body,
								   "profile_url": profile_url,
								   }
					print(review_dict)
					self.review_dict_list.append(review_dict)
				self.dict_list_to_csv_file()
			except:
				pass

	def asin_to_first_review_url(self, asin):
		listing_url = "https://www.amazon.com/dp/" + asin
		soup = soup_by_url(listing_url)
		first_review_url_part2 = soup.find(id="dp-summary-see-all-reviews")["href"]
		first_review_url = "https://www.amazon.com" + first_review_url_part2
		return first_review_url

	def get_reviews_by_asin(self, asin):
		try:
			first_review_url = self.asin_to_first_review_url(asin)
			self.first_review_url_to_review_info(first_review_url, asin)
		except:
			pass

	def get_reviews(self):
		self.csv_file_name = str(datetime.now()).replace(":", "_").strip().replace(" ", "_").split(".")[0]
		start_time = datetime.now()

		for asin in self.asin_list:
			self.get_reviews_by_asin(asin)

		end_time = datetime.now()
		how_many_seconds = end_time - start_time
		print(start_time)
		print(end_time)
		how_many_seconds = str(how_many_seconds.total_seconds()).split(".")[0]
		print(how_many_seconds + " seconds")


# main function
asin_to_reviews = Asin_to_reviews()
asin_to_reviews.get_reviews()
