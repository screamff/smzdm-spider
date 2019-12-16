# coding:utf-8
import requests
import time
from bs4 import BeautifulSoup
import threading
import queue
# todo:1.改写模块为类
# 2.使用flask构建看板页面
# 3.数据存入数据库
# 4.对值不值得买进行数据分析


class ItemSpider(threading.Thread):
    def __init__(self):
        self.htmls = queue.Queue()
        

    def run(self):
        # 此处放线程
        pass




def main(page_range):
    """使用不同页码网址进行搜索
    page_range:浏览范围，为整数"""
    for i in range(page_range):
        index= "https://www.smzdm.com/jingxuan/p"
        target_address = index + str(i)
        request_thread = threading.Thread(target=put_soup, args=(target_address,))
        request_thread.start()
        time.sleep(0.5)
        # target_address = input("输入物品连接:")


def put_soup(target_address):
    r = requests.get(target_address, headers={"User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"})
    if r.status_code == 200:
        pass
    else:
        print("http错误代码", r.status_code)
        exit()
    soup = BeautifulSoup(r.content, "html5lib")
    # print("正在搜索以下页面...", target_address, soup.title.string)
    htmls.put(soup)

    
def get_soup():
    """测试时可以取消注释保存网页的功能"""
    while True:
        try:
            site = htmls.get(timeout=5)
        except Exception as e:
            print(e)
            break
        # 保存网页测试时开启
        # with open(r".\saved.html", "wb") as f:
        #         f.write(str(site).encode('utf-8'))
        # div_feed = site.find_all('div', class_="z-feed-foot-l")
        div_feed = site.select('.z-feed-content')
        print('本次商品数量', len(div_feed))
        analyze(div_feed, 1)
        

def analyze(div_feed, timesleep=1):
    for i in div_feed:
        # 商品名字
        temp_name = i.select_one('div h5').a.string.strip()
        # print('商品名字:', temp_name)
        # 商品地址
        temp_url = i.select_one('div h5').a['href']
        # print('详细描述:', temp_url)
        # 商品图片url
        temp_img = i.parent.select_one('.z-feed-img').select_one('img')['src']
        # print('缩略图地址:', temp_img)
        # 商品值不值得买
        zhi = i.select_one('.icon-zhi-o-thin').next_sibling.string
        buzhi = i.select_one('.icon-buzhi-o-thin').next_sibling.string
        # print("值↑",zhi,"不值↑",buzhi)
        # 商品更新日期
        temp = i.select_one('.feed-block-extras').contents
        temp_time = temp[0].strip()
        if temp_time is '':
            temp_time = temp[1].string
        # print('更新日期:', temp_time)
        # 商品价格
        temp_price = i.select_one('.z-highlight')    
        try:
            temp_price = temp_price.string.strip()
            # print('价格:', temp_price.string.strip())
        except TypeError:
            temp_price = temp_price.select('a').string.strip()
            # print('价格:', temp_price.select('a').string.strip())
        except AttributeError:
            r = requests.get(temp_url, headers={"User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"})
            soup = BeautifulSoup(r.content, "html5lib")
            price = soup.select_one('.price')
            if price:
                temp_price = price.span.string
                # print("海淘价格:", price.span.string)
            else:
                old_price = soup.select_one('.old-price').select('span')[1]
                temp_price = old_price.string
                # print("过期价格:", old_price.string)
        print("-"*40)
        item = Item(temp_name, temp_url, temp_img, temp_time, temp_price, zhi, buzhi)
        print(item)
        # 标准输出延迟
        time.sleep(0.4)
    

class Item():
    def __init__(self, name, url, img, update_time, price, zhi, buzhi):
        self.name = name
        self.url = url
        self.img = img
        self.update_time = update_time
        self.price =price
        self.zhi = zhi
        self.buzhi = buzhi

    def __repr__(self):
        return("商品名字:{}\n详细地址:{}\n价格:{}\n值↑:{} 不值↓:{}\n更新日期:{}\n缩略图:{}".format(self.name,
                                                                                               self.url,
                                                                                               self.price,
                                                                                               self.zhi,
                                                                                               self.buzhi,
                                                                                               self.update_time,
                                                                                               self.img))
if __name__=="__main__":
    htmls = queue.Queue()
    search_thread = threading.Thread(target=get_soup)
    search_thread.start()
    main(5)

