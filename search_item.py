# coding:utf-8
# 搜索物品
# todo: 待重写
import re
import requests
import time
from bs4 import BeautifulSoup
import threading
import queue


def main(page_range, item_name):
    """使用不同页码网址进行搜索
    page_range:浏览范围，为整数"""
    keyword = {'s': item_name.encode("utf-8")}
    for i in range(page_range):
        target_address = "https://search.smzdm.com/?c=home&v=b&p=" + str(i)
        request_thread = threading.Thread(target=get_site, args=(target_address, keyword))
        request_thread.start()
        time.sleep(0.5)
        # target_address = input("输入物品连接:")


def get_site(target_address, keyword):
    r = requests.get(target_address,
                     params = keyword,
                     headers={"User-Agent":
                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"})
    if r.status_code == 200:
        pass
    else:
        print("http错误代码", r.status_code)
        exit()
    soup = BeautifulSoup(r.content, "html5lib")
    # print("正在搜索以下页面...", target_address, soup.title.string)
    htmls.put(soup)

    
def search_site():
    while True:
        try:
            site = htmls.get(timeout=5)
        except  Exception as e:
            break
        # 保存网页
        # with open(".\saved.html", "wb") as f:
        #         f.write(r.content)
        div_feed = site.find_all('div', class_="z-feed-foot-l")
        analyze(div_feed, 1)
        

def analyze(div_feed, timesleep=0):
    for i in div_feed:
        for item in i.parent.previous_siblings:
            # print(item.name)
            if item.name == 'h5':
                try:
                    for word in item.a.stripped_strings:
                        print("商品名:", word,"\n""直达地址:",item.a['href'])
                    # print("商品名:", item.a.stripped_strings[0],"\n""直达地址:",item.a['href'])
                    for price in item.a.next_sibling.stripped_strings:
                        print("价格", price)
                except Exception as e:
                    print("---获取失败---")
        zhi = i.find('i', class_="z-icon-zhi")
        buzhi = i.find('i', class_="z-icon-buzhi")
        if not zhi or not buzhi:
            continue
        print("值↑",zhi.parent.span.string,"不值↑",buzhi.parent.span.string)
        print("-"*40)
        time.sleep(timesleep)


if __name__=="__main__":
    htmls = queue.Queue()
    item_name = input('输入你要搜索的商品关键词：')
    search_thread = threading.Thread(target=search_site)
    search_thread.start()
    main(10, item_name)

