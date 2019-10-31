# coding:utf-8
# 截取商品名称等信息，方便批量操作等
import re
import requests
import time
from bs4 import BeautifulSoup


def main(page_range):
    """使用不同页码网址进行搜索
    page_range:浏览范围，为整数"""
    for i in range(page_range):
        target_address = "https://www.smzdm.com/jingxuan/p" + str(i)
        # target_address = input("输入物品连接:")
        r = requests.get(target_address, headers={"User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"})
        if r.status_code == 200:
            pass
        else:
            print("http错误代码", r.status_code)
            exit()
        soup = BeautifulSoup(r.content, "html5lib")

        # 保存网页
        # with open(".\saved.html", "wb") as f:
        #         f.write(r.content)
        print("正在搜索以下网站...", target_address, soup.title.string)
        print("-"*40)
        div_feed = soup.find_all('div', class_="z-feed-foot-l")
        search_func(div_feed, 0.1)
        

def search_func(div_feed, timesleep=0.8):
    for i in div_feed:
        for item in i.parent.previous_siblings:
            if item.name == 'h5':
                try:
                    print("商品名:", item.a.string.strip(),"\n""直达地址:",item.a['href'])
                    print("价格", item.next_sibling.next_sibling.string.strip())
                except Exception as e:
                    print("---获取失败---")
        zhi = i.find('i', class_="icon-zhi-o-thin")
        buzhi = i.find('i', class_="icon-buzhi-o-thin")
        if not zhi or not buzhi:
            continue
        print("值↑",zhi.next_sibling.string,"不值↑",buzhi.next_sibling.string)
        print("-"*40)
        time.sleep(timesleep)


if __name__=="__main__":
    main(10)

