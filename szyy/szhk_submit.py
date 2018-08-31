import json

import requests
# from bs4 import BeautifulSoup
import random
from e_amazon.craw_constant import headers_list

data = {
    'appointmenDate': '2018-09-07',
    'appTypeId': '3F9FBC5B87C64CA1A3569B31B00F612A',
    'appTimeId': 'RDFG65E168E54D02AA5F6B855CDCV68K'
}
cookies = {
    'JSESSIONID': '13912F23CD61CDF76051D70A1ABBF056',
    'DWRSESSIONID': 'RF1GB2ybYQpqYEh!87xBEbdcG6QizhuJdmm'
}

url = 'http://www.szhrzhgc.com/appointmenrecord/addAppointSave.do?r=0.7321439071604546'
headers = random.choice(headers_list)
result = requests.post(url=url, data=data, headers=headers, cookies=cookies)
if result.status_code != 200:
    headers = random.choice(headers_list)
    result = requests.get(url, headers=headers)
# soup = BeautifulSoup(result.content, 'html.parser')

result_dict = json.loads(result.content)
if int(result_dict.get('system_result_key')) == 0 and int(result_dict.get('app_result_key')) == 0:
    print('success!')
elif int(result_dict.get('app_result_key')) == 1:
    print(result_dict.get('app_result_message_key'))
elif int(result_dict.get('system_result_key')) == 7:
    print('no login')




