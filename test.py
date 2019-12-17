# 本地页面解析测试
# 需要在main.py中去掉保存文件的注释
import re
import requests
import time
import datetime
from bs4 import BeautifulSoup


def analyze(div_row, timesleep=1):
    for line in div_row:
        content = line.select_one('.z-feed-content')
        # 商品名字
        temp_name = content.select_one('div h5')
        print('商品名字:', temp_name.a.string.strip())
        # 商品地址
        temp_url = temp_name.a['href']
        print('详细描述:', temp_url)
        # 商品图片url
        temp_img = content.parent.select_one('.z-feed-img').select_one('img')['src']
        print('缩略图地址:', temp_img)
        # 商品id
        item_id = re.match(r".*/(\d+)/", temp_url).group(1)
        print('商品id:', item_id)
        # 商品值不值得买
        zhi = content.select_one('.icon-zhi-o-thin')
        buzhi = content.select_one('.icon-buzhi-o-thin')
        print("值↑",zhi.next_sibling.string,"不值↑",buzhi.next_sibling.string)
        # 商品更新日期
        temp_time = datetime.datetime.fromtimestamp(int(line['timesort']))
        print('更新日期:', temp_time)
        # 商品价格
        temp_price = content.select_one('.z-highlight')    
        try:
            print('价格:', temp_price.string.strip())
        except AttributeError:
            if temp_price.get_text().strip():
                print('gettext价格:', temp_price.get_text().strip())
            else:
                r = requests.get(temp_url, headers={"User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"})
                soup = BeautifulSoup(r.content, "html5lib")
                price = soup.select_one('.price')
                if price:
                    print("另类价格:", price.span.string)
                else:
                    old_price = soup.select_one('.old-price').select('span')[1]
                    print("过期价格:", old_price.string)
            # print(price.string)
            # for child in temp.contents:
            #     print(child)
            #     child = child.string.strip()
            #     price = re.match(r".*元.*", child)
            #     if price:
            #         print('价格:', child)
            #         break
            # print(price)
            # print(temp)
            # print(temp.contents[1].contents)
            # print('过期价格:', temp.contents[2].strip())
        print("-"*40)
        # 标准输出延迟
        # time.sleep(timesleep)

with open('saved.html', 'rb') as f:
    soup = BeautifulSoup(f, "html5lib")
div_row = soup.select('.feed-row-wide')
analyze(div_row)
