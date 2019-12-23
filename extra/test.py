# 本地页面解析测试
# 需要在main.py中去掉保存文件的注释
import re
import requests
import time
import datetime
from bs4 import BeautifulSoup
import os
import logging


def analyze(div_row, timesleep=1):
    for line in div_row:
        content = line.select_one('.z-feed-content')
        # errorlog.html使用
        # content = line
        # 商品名字
        temp_name = content.select_one('div h5')
        print('商品名字:', temp_name.a.get_text().strip())
        # 商品地址
        temp_url = temp_name.a['href']
        print('详细描述:', temp_url)
        # 商品图片url
        temp_img = line.select_one('.z-feed-img').select_one('img')['src']
        print('缩略图地址:', temp_img)
        # 商品id
        item_id = re.match(r".*/(\d+)/", temp_url).group(1)
        print('商品id:', item_id)
        # 商品值不值得买
        # zhi = int(content.select_one('.icon-zhi-o-thin').next_sibling.string)
        # buzhi = int(content.select_one('.icon-buzhi-o-thin').next_sibling.string)
        zhi = int(content.select_one('.z-icon-zhi').next_element.next_element.string)
        buzhi = int(content.select_one('.z-icon-buzhi').next_element.next_element.string)
        print("值↑",zhi,"不值↑",buzhi)
        # 商品更新日期
        temp_time = content.select_one('.feed-block-extras').next_element.strip()
        try:
            temp_time = time.strptime(temp_time,'%H:%M')
            now = datetime.datetime.now()
            temp_time = datetime.datetime(now.year, now.month, now.day,
                                          temp_time.tm_hour, temp_time.tm_min)
        except:
            temp_time = time.strptime(temp_time,'%m-%d %H:%M')
            now = datetime.datetime.now()
            temp_time = datetime.datetime(now.year, temp_time.tm_mon,
                                          temp_time.tm_mday, temp_time.tm_hour,
                                          temp_time.tm_min)
        # temp_time = datetime.datetime.fromtimestamp(int(line['timesort']))
        print('更新日期:', temp_time)
        # 商品价格
        temp_price = content.select_one('.z-highlight')    
        try:
            print('价格:', temp_price.get_text().strip())
        except:
            print('本段出现错误:', temp_price)
        print("-"*40)

# with open('saved.html', 'rb') as f:
#     soup = BeautifulSoup(f, "html5lib")
# div_row = soup.select('.feed-row-wide')
# analyze(div_row)

# with open('errorlog.html', 'rb') as f:
#     soup = BeautifulSoup(f, "html5lib")
# div_content = soup.select('.z-feed-content')
# analyze(div_content)

logger = logging.getLogger(os.path.basename(__file__))
print(logger)
path = os.path.join(os.path.dirname(__file__), 'log.txt')
with open(path, 'r') as f:
    print(f.read())