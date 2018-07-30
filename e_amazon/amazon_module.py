#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import random
import re
import os
import requests
import time
from bs4 import BeautifulSoup
import csv
from e_amazon.craw_constant import headers_list

URL = 'https://www.amazon.com/'

headers = random.choice(headers_list)


def open_url(url, try_max=5):
	response = requests.get(url, headers=headers)
	# try max 5
	status_count = try_max
	while status_count > 0 and response.status_code != 200:
		response = requests.get(url, headers=headers)
		if response.status_code == 200:
			break
		status_count -= 1
	return response.content


def soup_by_url(url, try_robot_check_max=9):
	res_content = open_url(url, 3)
	soup = BeautifulSoup(res_content, 'html.parser')

	count = try_robot_check_max
	while count > 0 and ("Robot Check" in soup.get_text()):
		print('Robot Check')
		time.sleep(random.choice([0.5, 1, 2, 3, 4]))
		headers = random.choice(headers_list)
		r = requests.get(URL, headers=headers)
		count -= 1
		soup = BeautifulSoup(r.content, 'html.parser')
	return soup


def url_to_asin(url):
    try:
        asin = re.search('/dp/(.*?)/ref', url)
        if asin:
            asin = asin.group()
            asin = asin.replace('/dp/', '')
            asin = asin.replace('/ref', '')
            return asin
    except:
        pass
    try:
        asin = re.search('/dp/(.*?)$', url)
        if asin:
            asin = asin.group()
            asin = asin.replace('/dp/', '')
            return asin
    except:
        pass
    return None


def asin_to_url(asin):
    url = "https://www.amazon.com/dp/" + asin
    return url


def url_to_full_url(url):
    if re.match("https://", url):
        return url
    if re.match("/dp", url):
        url = "https://www.amazon.com" + url
        return url
    if re.match("/gp", url):
        url = "https://www.amazon.com" + url
        return url


def asin_to_listing_info(asin):
    url = asin_to_url(asin)
    listing_info_dict = url_to_listing_info(url)
    return listing_info_dict


def url_to_listing_info(url):
    print("***********************************")
    print("start to get listing info...")
    print("url: ", url)

    asin = url_to_asin(url)
    print("asin: ", asin)

    soup = soup_by_url(url)

    brand = ""
    if soup.find(id="bylineInfo"):
        brand = soup.find(id="bylineInfo").get_text().strip()
    if soup.find(id="brand"):
        brand = soup.find(id="brand").get_text().strip()
    print("brand: ", brand)

    badge = ""
    if soup.find("a", class_="badge-link"):
       badge = " ".join(soup.find("a", class_="badge-link").get_text().strip().split())
    print("badge: ", badge)

    title = ""
    if soup.find(id="productTitle"):
        title = soup.find(id="productTitle").get_text().strip()
    print("title: ", title)

    variation_name = ""
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

    price = ""
    sale_price =""
    if soup.find(id="price"):
        price = soup.find(id="price").find("span").get_text().strip()
    if soup.find(id="priceblock_ourprice"):
        price = soup.find(id="priceblock_ourprice").get_text().strip()
    if soup.find(id="priceblock_saleprice"):
        sale_price = soup.find(id="priceblock_saleprice").get_text().strip()

    print("price: ", price)
    print("sale_price: ", sale_price)
    # print("soup: ", soup)

    sold_by = ""
    if soup.find(id="merchant-info"):
        # print("sold_by: ..................")
        # print("soup.find(id='merchant-info').get_text().strip(): ", soup.find(id="merchant-info").get_text().strip())
        sold_by = " ".join(soup.find(id="merchant-info").get_text().strip().split())
    print("sold_by: ", sold_by)

    how_many_sellers = ""
    if soup.find(id="olp_feature_div"):
        try:
            how_many_sellers = soup.find(id="olp_feature_div").find("a").get_text().strip()
        except:
            pass
    print("how_many_sellers: ", how_many_sellers )

    bullets_list = []
    if  soup.find("div", id="feature-bullets"):
        bullets_soup = soup.find("div", id="feature-bullets")
        bullets_contents = bullets_soup.find_all("span", class_="a-list-item")
        print("bullets: ")
        for bullets_content in bullets_contents:
            # this if is special for toys categary
            if bullets_content.span:
                continue
            bullets_content_text = bullets_content.get_text().strip()
            bullets_list.append(bullets_content_text)
            print(bullets_content_text)

    description = ""
    if soup.find(id="productDescription"):
        description = soup.find(id="productDescription").get_text()
    if soup.find(id="aplus"):
        description = soup.find(id="aplus").get_text()
    description = " ".join(description.split())
    print("description: ", description)

    salesrank = ""
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

    print("salesrank: ", salesrank)

    review_num = 0
    if soup.find(id="acrCustomerReviewText"):
        review_num = soup.find(id="acrCustomerReviewText").get_text().split()[0].strip()
    print("review_num: ", review_num)

    review_value = 0
    if soup.find(class_="arp-rating-out-of-text"):
        review_value = soup.find(class_="arp-rating-out-of-text").get_text().strip()
        review_value = re.search('(.*?)\s', review_value)
        review_value = review_value.group()
        review_value = review_value.strip()
    print("review_value: ", review_value)

    qa_num = ""
    if soup.find(id="askATFLink"):
        qa_num = soup.find(id="askATFLink").get_text().split()[0].strip()
        print("qa_num: ", qa_num)

    listing_info_dict = {
                         "asin": asin,
                         "url": url,
                         "brand": brand,
                         "badge": badge,
                         "title": title,
                         "variation_name": variation_name,
                         "price": price,
                         "sale_price": sale_price,
                         "sold_by": sold_by,
                         "how_many_sellers": how_many_sellers,
                         "bullets": bullets_list,
                         "description": description,
                         "salesrank": salesrank,
                         "review_num": review_num,
                         "review_value": review_value,
                         "qa_num": qa_num
                         }
    print(listing_info_dict)
    return listing_info_dict


def download_picture_by_asin(asin, folder):
    print("***********************************")
    print("start to download picture...")
    try:
        listing_url = "https://www.amazon.com/dp/" + str(asin)
        # print(listing_url)
        listing_soup = soup_by_url(listing_url)
        picture_urls = ""
        picture_urls_dict = dict()
        if listing_soup.find("img", id="landingImage"):
            picture_urls = listing_soup.find("img", id="landingImage")["data-a-dynamic-image"]
        try:
            picture_urls_dict = eval(picture_urls)
        except:
            print("picture_urls_dict fail to get! ")
        # print(picture_urls_dict.keys)
        picture_urls_list = []
        for key in picture_urls_dict.keys():
            picture_urls_list.append(key)
        picture_url = picture_urls_list[0]

        try:
            pic = requests.get(picture_url, timeout=10)
        except requests.exceptions.ConnectionError:
            print("download picture failed!")

        if not os.path.exists(folder):
            print("***********************************")
            print("picture folder not exist, create the folder now...")
            os.mkdir(folder)
            print("***********************************")
            print("success to create picture folder")

        string = folder + "/"+ str(asin) + '.jpg'
        with open(string, 'wb') as fp:
            fp.write(pic.content)
        print("success to download picture.")
    except:
        print("fail to download picture.")

def download_picture_by_url(url, picture_folder):
    print("***********************************")
    print("start to download picture...")
    try:
        listing_url = url
        # print(listing_url)
        listing_soup = soup_by_url(listing_url)
        picture_urls = ""
        picture_urls_dict = dict()
        if listing_soup.find("img", id="landingImage"):
            picture_urls = listing_soup.find("img", id="landingImage")["data-a-dynamic-image"]
        try:
            picture_urls_dict = eval(picture_urls)
        except:
            print("picture_urls_dict fail to get! ")
        # print(picture_urls_dict.keys)
        picture_urls_list = []
        for key in picture_urls_dict.keys():
            picture_urls_list.append(key)
        picture_url = picture_urls_list[0]

        try:
            pic = requests.get(picture_url, timeout=10)
        except requests.exceptions.ConnectionError:
            print("download picture failed!")

        if not os.path.exists(picture_folder):
            print("***********************************")
            print("picture folder not exist, create the folder now...")
            os.mkdir(picture_folder)
            print("***********************************")
            print("success to create picture folder")

        asin = url_to_asin(listing_url)
        string = picture_folder + "/"+ str(asin) + '.jpg'
        with open(string, 'wb') as fp:
            fp.write(pic.content)
        print("success to download picture.")
    except:
        print("fail to download picture.")



#keyword to all listing info
def page_url_to_asin_list(url):
    # print("************************* page url to asins ****************************")
    # print("url: ", url)
    soup = soup_by_url(url)
    # print(soup)
    # lis = soup.find("ul", id="s-results-list-atf").find_all("li")
    # lis = soup.find("ul", id="s-results-list-atf").find_all("li", class_="s-result-item")
    lis = soup.find_all("li", class_="s-result-item")
    # print(lis)
    page_asins_list = []
    for li in lis:
        # print(li)
        try:
            asin = li["data-asin"]
            page_asins_list.append(asin)
        except:
            pass
    return page_asins_list


def page_url_to_asin_url_dict_list(url):
    # print("************************* page url to asins ****************************")
    soup = soup_by_url(url)
    # print(soup)
    # lis = soup.find("ul", id="s-results-list-atf").find_all("li")
    # lis = soup.find("ul", id="s-results-list-atf").find_all("li", class_="s-result-item")
    lis = soup.find_all("li", class_="s-result-item")
    # print(lis)
    asin_url_dict_list = []
    for li in lis:
        # print(li)
        try:
            asin = li["data-asin"]
            url = li.a["href"]
            url = url_to_full_url(url)
            asin_url_dict = {
                            "asin": asin,
                            "url": url
                            }
            asin_url_dict_list.append(asin_url_dict)
        except:
            pass
    return asin_url_dict_list


def first_page_url_to_all_page_urls(first_page_url, pages=1):
    pages_urls_list = []
    pages_urls_list.append(first_page_url)
    if pages == 1:
        return pages_urls_list
    while pages > 1:
        soup = soup_by_url(pages_urls_list[-1])
        try:
            if soup.find(id="pagnNextLink")["href"]:
                next_page_url_part2 = soup.find(id="pagnNextLink")["href"]
                next_page_url = "https://www.amazon.com" + next_page_url_part2
                pages_urls_list.append(next_page_url)
            pages = pages - 1
        except:
            return pages_urls_list

    return pages_urls_list


def keyword_to_first_page_url(keyword):
    base_url = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="
    # keyword = "dog+training+collar"
    url = base_url + keyword
    return url


def keyword_to_all_listing_asin_list(keyword, how_many_pages):
    first_page_url = keyword_to_first_page_url(keyword)
    all_page_urls = first_page_url_to_all_page_urls(first_page_url, how_many_pages)
    # print("pages_urls", pages_urls)
    all_listing_asin_list = []
    page_num_and_asin_dict_list = []
    for page_index, page_url in enumerate(all_page_urls):
        if page_url:
            page_asin_list = page_url_to_asin_list(page_url)
            for asin_index, asin in enumerate(page_asin_list):
                page_num = "page" + str(page_index + 1) + "-" + str(asin_index + 1)
                print(page_num, asin)
                all_listing_asin_list.append(asin)

                page_num_and_asin_dict = {
                                         "page_num": page_num,
                                         "asin": asin
                                         }
                page_num_and_asin_dict_list.append(page_num_and_asin_dict)

    picture_folder = keyword

    if not os.path.exists(picture_folder):
        print("***********************************")
        print("picture folder not exist, create the folder now...")
        os.mkdir(picture_folder)
        print("success to create picture folder")
    dict_list_to_csv_file(page_num_and_asin_dict_list, "page_num_and_asin.csv", picture_folder)
    return all_listing_asin_list


def keyword_to_all_listing_url_list(keyword, how_many_pages):
    first_page_url = keyword_to_first_page_url(keyword)
    all_page_urls = first_page_url_to_all_page_urls(first_page_url, how_many_pages)
    # print("pages_urls", pages_urls)
    all_listing_url_list = []
    page_num_and_asin_dict_list = []
    for page_index, page_url in enumerate(all_page_urls):
        if page_url:
            asin_url_dict_list = page_url_to_asin_url_dict_list(page_url)
            for url_index, asin_url_dict in enumerate(asin_url_dict_list):
                asin = asin_url_dict["asin"]
                url = asin_url_dict["url"]
                page_num = "page" + str(page_index + 1) + "-" + str(url_index + 1)
                print(page_num, asin)
                all_listing_url_list.append(url)

                page_num_and_asin_dict = {
                                         "page_num": page_num,
                                         "asin": asin,
                                         "url": url
                                         }
                page_num_and_asin_dict_list.append(page_num_and_asin_dict)

    picture_folder = keyword

    if not os.path.exists(picture_folder):
        print("***********************************")
        print("picture folder not exist, create the folder now...")
        os.mkdir(picture_folder)
        print("success to create picture folder")
    print("page_num_and_asin_dict_list: ", page_num_and_asin_dict_list)
    dict_list_to_csv_file(page_num_and_asin_dict_list, "page_num_and_asin.csv", picture_folder)
    return all_listing_url_list


#store to all listing info
def first_store_url_to_store_urls(store_frontpage_url, pages=1):
    pages_urls_list = []
    pages_urls_list.append(store_frontpage_url)
    if pages == 1:
        return pages_urls_list
    while pages > 1:
        # seed_url = pages_urls_list[-1]
        soup = soup_by_url(pages_urls_list[-1])
        try:
            if soup.find(id="pagnNextLink")["href"]:
                next_page_url_part2 = soup.find(id="pagnNextLink")["href"]
                next_page_url = "https://www.amazon.com" + next_page_url_part2
                print(next_page_url_part2)
                pages_urls_list.append(next_page_url)
        except:
            return pages_urls_list

        pages = pages - 1

    return pages_urls_list


def store_url_to_asins(store_url):
    soup = soup_by_url(store_url)

    # lis = soup.find(id="s-results-list-atf").find_all("li")
    # for li in lis:
    #     print(li.find("a")["href"])

    lis = soup.find_all("li", class_="s-result-item")

    # for index, li in enumerate(lis):
    #     print(index + 1, li.find("a")["href"])

    asin_list = []
    for index, li in enumerate(lis):
        url = li.find("a", class_="a-link-normal a-text-normal")["href"]
        asin = url_to_asin(url)
        asin_list.append(asin)
    return asin_list


def store_frontpage_url_to_asins(store_frontpage_url, pages=1):
    # store_url = "https://www.amazon.com/s?marketplaceID=ATVPDKIKX0DER&me=A294P4X9EWVXLJ&merchant=A294P4X9EWVXLJ&redirect=true"
    # pages = 6
    asins_list = []
    store_urls = first_store_url_to_store_urls(store_frontpage_url, pages)
    for page_index, store_url in enumerate(store_urls):
        asin_list = store_url_to_asins(store_url)
        for asin_index, asin in enumerate(asin_list):
            asins_list.append(asin)
            num = "page" + str(page_index + 1) + "-" + str(asin_index + 1)
            # print(num, asin)

            # try:
            #     download_picture_by_asin(asin)
            #     print("download picture successfully!")
            # except:
            #     print("fail to download picture......")

    return asins_list


#asin to all review info
def review_url_to_review_dict_list(url):
    soup = soup_by_url(url)

    review_list = soup.find(id="cm_cr-review_list").find_all("div", {"data-hook":"review"})
    review_dict_list = []

    for review in review_list:
        review_title = review.find("a", {"data-hook":"review-title"}).get_text()
        # print(review_title.get_text())

        review_star_rating = review.find("i", {"data-hook": "review-star-rating"}).get_text()
        # print(review_star_rating.get_text())
        # print(review_star_rating.get_text().split()[0])

        review_author = review.find("a", {"data-hook": "review-author"}).get_text()
        # print(review_author.get_text())

        review_date = review.find("span", {"data-hook": "review-date"}).get_text()
        # print(review_date.get_text())

        review_body = review.find("span", {"data-hook": "review-body"}).get_text()
        # print(review_body.get_text())

        review_dict = dict({"review_title": review_title,
                            "review_star_rating": review_star_rating,
                            "review_author": review_author,
                            "review_date": review_date,
                            "review_body": review_body})
        review_dict_list.append(review_dict)

    return review_dict_list


def first_review_url_to_review_info_list(url, max_page, top_or_recently="recently", all_or_positive_or_critical="all"):
    location = re.search("ref=", url)
    span = location.span()[0]
    first_review_url_part1 = url[:span]

    review_base_url = first_review_url_part1 + "ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=" + all_or_positive_or_critical + "&reviewerType=avp_only_reviews&sortBy=" + top_or_recently + "&pageNumber="

    first_review_url = review_base_url + str(1)
    first_review_url_soup = soup_by_url(first_review_url)
    last_page = first_review_url_soup.find(id="cm_cr-pagination_bar").find_all("li", class_="page-button")[-1].get_text()
    last_page = int(last_page)
    min_page = min(last_page, max_page)

    review_info_list = []

    for page_index, page in enumerate(range(1, min_page+1)):
        review_url = review_base_url + str(page)
        try:
            review_infos = review_url_to_review_dict_list(review_url)
            for review_info_index, review_info in enumerate(review_infos):
                review_info_list.append(review_info)
                print("page" + str(page_index + 1) + "-" + str(review_info_index + 1))
                print(review_info)
        except:
            print("break")
            return review_info_list
    return review_info_list


def asin_to_first_review_url(asin):
    listing_url = asin_to_url(asin)
    soup = soup_by_url(listing_url)
    first_review_url_part2 = soup.find(id="dp-summary-see-all-reviews")["href"]
    first_review_url = "https://www.amazon.com" + first_review_url_part2
    # print(first_review_url)
    return first_review_url


## price
# asin = "B00EV6FU7C"
# listing_info = asin_to_listing_info(asin)
# print(listing_info)
# print(listing_info["title"])
# for info in listing_info:
#     print(info)
# test best seller top 100


def node_url_to_node_url_list(node_url):
    node_list = []
    soup = soup_by_url(node_url)
    try:
        # lis = soup.find("span", class_="zg_selected").find_next("ul").find_all("li")    #wrong
        # print(soup.find("span", class_="zg_selected").parent.parent.find("ul").find_all("li"))
        lis = soup.find("span", class_="zg_selected").parent.parent.find("ul").find_all("li")

        for li in lis:
            if li.find("a")["href"]:
                node = li.find("a").get_text()
                print(node)
                li_node_url = li.find("a")["href"]
                node_url_to_node_url_list(li_node_url)
                node_list.append(node)
    except:
        print("error")

    return node_list


def keyword_to_merchantwords_search_rank(keyword):
    try:
        keyword = keyword.replace(" ", "%20")
        url = "https://www.merchantwords.com/search/us/" + keyword + "/sort-highest"
        soup = soup_by_url(url)

        trs = soup.find("table").find("tbody").find_all("tr")

        node_list = []
        for tr in trs:
            # print(tr.get_text())
            try:
                blurry_words = tr.find("span").get_text()
                # print(blurry_words)

                num = tr.find_all("td")[1].get_text()
                num = num.replace(",", "")
                # print(num)

                node = tr.find("small")
                node = str(node)
                node = node.replace("<br/>", "; ")
                node = node.replace("<small>", "")
                node = node.replace("</small>", "")
                node = node.replace("&amp;", "&")
                # print(node)

                node_tuple = (blurry_words, num, node)
                node_list.append(node_tuple)
            except:
                pass

        # print(node_list[0][1])
        return(node_list[0][1])
    except:
        print("fail to get merchantwords rank!")


def keyword_to_long_tail_keyword_list(keyword):
    try:
        print("keyword:", keyword)
        print("-" * (len("keyword: ") + len(keyword)))
        if keyword[0] == "*":
            # start with "*"
            url_head = "https://completion.amazon.com/search/complete?method=completion&mkt=1&r=Y5KKREBZPVVDRZT19HX9&s=133-8959284-8300960&c=&p=Gateway&l=en_US&b2b=0&fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q=*&qs="
            url_tail = "&cf=1&fb=1&sc=1&"
        else:
            # start without "*"
            url_head = "https://completion.amazon.com/search/complete?method=completion&mkt=1&r=Y5KKREBZPVVDRZT19HX9&s=133-8959284-8300960&c=&p=Gateway&l=en_US&b2b=0&fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q="
            url_tail = "&qs=&cf=1&fb=1&sc=1&"
        try:
            keyword = keyword.replace(" ", "%20")
            keyword = keyword.replace("'", "%27")
            url = url_head + keyword + url_tail

            soup = soup_by_url(url)

            soup_string = soup.get_text()
            soup_string = soup_string[13:-11]
            soup_list = eval(soup_string)

            long_tail_keyword_list = []
            for long_tail_keyword in soup_list[1]:
                print(long_tail_keyword)
                long_tail_keyword_list.append(long_tail_keyword)

            print("")
            return(long_tail_keyword_list)
        except:
            print("can't find long tail words")
    except:
        print("can't find long tail words")


def keyword_to_search_results_num(keyword):
    try:
        # print("keyword:", keyword)
        url_head = "https://www.amazon.com/s/ref=nb_sb_noss/147-7192934-0083761?url=search-alias%3Daps&field-keywords="
        url = url_head + keyword

        soup = soup_by_url(url)

        results = soup.find(id="s-result-count").get_text()
        results_text = results.split(":")[0]
        # print(results_text)

        m = re.search(r"of (.*?) results", results)
        results = m.group()
        results = results.replace("of ", "").replace(" results", "").replace(",", "")
        # print(results)
        return(results)
    except:
        print("fail to find results")


def keyword_to_bing_search_results_num(keyword):
    try:
        # print("keyword:", keyword)
        url_head = "https://www.bing.com/search?q="
        url_tail = "qs=n&form=QBRE"

        keyword = keyword.replace(" ", "%20")
        keyword = keyword.replace("'", "%27")
        url = url_head + keyword + url_tail

        soup = soup_by_url(url)
        # print(soup)

        results = soup.find("div", id="b_tween").get_text()
        results = results.replace(" 条结果时间不限 ", "")
        # results = results.replace(",", "")
        # results = results.spilt()[0]
        # print(results)
        return(results)
    except:
        print("fail to find results")


def dict_list_to_csv_file(dict_list, csv_file_name, csv_file_folder):
    try:
        if not os.path.exists(csv_file_folder):
            print("Folder does not exist, creating the folder...")
            os.mkdir(csv_file_folder)
            print("success to create folder")
            print("***********************************")

        print("***********************************")
        print("start to write csv file...")
        headers = []
        for i in dict_list[0]:
            headers.append(i)

        csv_file_path = csv_file_folder + "/" + csv_file_name
        try:
            with open(csv_file_path, 'w+', encoding='utf8', newline='') as f:
                f_csv = csv.DictWriter(f, headers)
                f_csv.writeheader()
                f_csv.writerows(dict_list)
                print("success to write csv file:", csv_file_name)
        except:
            print("fail to write csv file:", csv_file_name)
    except:
        print("fail to write csv file:", csv_file_name)


def asin_to_size_weight(asin):
    try:
        url_head = "https://sellercentral.amazon.com/fba/profitabilitycalculator/productmatches?searchKey="
        url_tail = "&language=en_US&profitcalcToken=p9FcdMuSse7SGDBTzP9EgOn9nuQj3D"
        url = url_head + asin + url_tail

        soup = soup_by_url(url)
        soup_text = soup.get_text()
        soup_dict = json.loads(soup_text)
        item_info_dict = soup_dict['data'][0]
        if item_info_dict['length'] == 0:
            return None
        return item_info_dict
    except:
        print("fail to get size and weight!")


def top100_node_url_to_asin_list(url):
    asin_list = []

    for page_index in range(5):
        try:
            page_url = re.sub(r"ref=zg(.*)", "ref=zg_bs_pg_" + str(page_index+1) + "?_encoding=UTF8&pg=" + str(page_index+1), url)
            print(page_url)
            page_soup = soup_by_url(page_url)
            page_lis = page_soup.find(id="zg_centerListWrapper").find_all("div", class_="zg_itemImmersion")
            for index, page_li in enumerate(page_lis):
                try:
                    link = page_li.find("a")['href']
                    asin = re.findall(r"dp/(.*?)/ref", link)[0]
                    print(str(page_index + 1) + "P" + str(index + 1) + ": " + asin)
                    asin_list.append(asin)
                except:
                    pass
        except:
            pass
    return asin_list

# url = "https://www.amazon.com/Best-Sellers-Pet-Supplies-Dog-Toys/zgbs/pet-supplies/2975413011/ref=zg_bs_unv_petsupplies_3_2975415011_1"
# url = "https://www.amazon.com/Best-Sellers-Pet-Supplies-Dog-Squeak-Toys/zgbs/pet-supplies/2975419011/ref=zg_bs_nav_petsupplies_3_2975413011"
# asin_list = top100_node_url_to_asin_list(url)
#
# print(asin_list)


def index(asin, keyword):
    try:
        search_term = asin + " %2B " + keyword
        search_term = search_term.replace("'", "%27").replace("/", "%2F").replace(",", "%2C").replace(" ", "+")

        url_head = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords="
        url = url_head + search_term

        soup = soup_by_url(url)
        result_txt = soup.find(id="s-result-count").get_text().strip().split()[0]
        if result_txt:
            # print("index")
            return 1
        else:
            # print("not index")
            return None
    except:
        # print("not index")
        return None
