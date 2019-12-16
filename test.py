import re
import requests
import time
from bs4 import BeautifulSoup


def analyze(div_feed, timesleep=1):
    for i in div_feed:
        # 商品名字
        temp_name = i.select_one('div h5')
        print('商品名字:', temp_name.a.string.strip())
        # 商品地址
        temp_url = temp_name.a['href']
        print('详细描述:', temp_url)
        # 商品图片url
        temp_img = i.parent.select_one('.z-feed-img').select_one('img')['src']
        print('缩略图地址:', temp_img)
        # 商品值不值得买
        zhi = i.select_one('.icon-zhi-o-thin')
        buzhi = i.select_one('.icon-buzhi-o-thin')
        print("值↑",zhi.next_sibling.string,"不值↑",buzhi.next_sibling.string)
        # 商品更新日期
        temp = i.select_one('.feed-block-extras').contents
        temp_time = temp[0].strip()
        if temp_time is '':
            temp_time = temp[1].string
        print('更新日期:', temp_time)
        # 商品价格
        temp_price = i.select_one('.z-highlight')    
        try:
            print('价格:', temp_price.string.strip())
        except TypeError:
            print('价格:', temp_price.select('a').string.strip())
        except AttributeError:
            r = requests.get(temp_url, headers={"User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"})
            soup = BeautifulSoup(r.content, "html5lib")
            price = soup.select_one('.price')
            if price:
                print("另类价格:", price.span.string)
            else:
                old_price = soup.select_one('.old-price').select('span')[1]
                print("过期价格:", old_price.string)
            break
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
div_feed = soup.select('.z-feed-content')
analyze(div_feed)