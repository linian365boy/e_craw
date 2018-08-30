import json

import requests
# from bs4 import BeautifulSoup
import random
from e_amazon.craw_constant import headers_list

data = {
    'dataType': 2,
    'status': 1,
    'dataId': '3F9FBC5B87C64CA1A3569B31B00F612A'
}
url = 'http://www.szhrzhgc.com/appointmentime/web/gridAll.do?r=0.7311469071604546'
headers = random.choice(headers_list)
result = requests.post(url=url, data=data, headers=headers)
if result.status_code != 200:
    headers = random.choice(headers_list)
    result = requests.get(url, headers=headers)
# soup = BeautifulSoup(result.content, 'html.parser')

result_dict = json.loads(result.content)
all_day_data = result_dict.get('data').get('listDateWeek')

i = 0
for day in all_day_data:
    i += 1
    if i == 1:
        continue
    # print(day.get('date'), day.get('isApprointment'), day.get('listTime'))
    for time_segment in day.get('listTime'):
        print(day.get('date'), day.get('isApprointment'), time_segment.get('startTimeFrame'), time_segment.get('endTimeFrame'), time_segment.get('appNum'))
        if int(day.get('isApprointment')) != 1 \
                and int(day.get('isApprointment')) != 2 \
                and int(time_segment.get('appNum')) > 0:
            print('gogogo send me email')




