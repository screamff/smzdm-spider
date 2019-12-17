# coding:utf-8
import requests
import time
from bs4 import BeautifulSoup
import threading
import queue
import datetime
import re
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# todo:1.改写模块为类 # 已完成
# 2.使用flask构建看板页面
# 3.数据存入数据库 # 已完成
# 4.对值不值得买进行数据分析
# 5.可能采取对商品详情页进行数据解析(列表页解析太麻烦了)

# 连接数据库
engine = create_engine('sqlite:///smzdm.db')
# 基本类
Base = declarative_base()
Session = sessionmaker(bind=engine)


class ItemSpider(threading.Thread):
    """爬取smzdm精选好价页面物品信息
    参数--target_address  url地址
        --keyword  搜索物品的参数,暂未完成(页面解析方法不一样)
    示例--itemspider = ItemSpider("https://www.smzdm.com/jingxuan/p1")
          itemspider.start()"""
    def __init__(self, target_address, keyword=None):
        threading.Thread.__init__(self)
        self.target_address = target_address
        self.keyword = keyword
        

    def run(self):
        r = requests.get(self.target_address, params=self.keyword, headers={"User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"})
        soup = BeautifulSoup(r.content, "html5lib")
        # 保存网页测试用
        # with open(r".\saved.html", "wb") as f:
        #     f.write(r.content)
        div_feed = soup.select('.z-feed-content')
        print('本次商品数量', len(div_feed))
        self.analyze(div_feed, 1)

    @staticmethod
    def analyze(div_feed, timesleep=1):
        # 为一个线程分配一个会话
        session = Session()
        for i in div_feed:
            # 商品名字
            temp_name = i.select_one('div h5').a.string.strip()
            # print('商品名字:', temp_name)
            # 商品地址
            temp_url = i.select_one('div h5').a['href']
            # print('详细描述:', temp_url)
            # 商品id
            item_id = re.match(r".*/(\d+)/", temp_url).group(1)
            id = session.query(Item.item_id).filter(Item.item_id==item_id).all()
            if id:
                # todo: update值不值
                continue
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
            # 商品价格, todo:之后尝试不要请求商品详情页
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
            item = Item(name=temp_name, item_id=item_id, url=temp_url, img=temp_img,
                        update_time=temp_time, price=temp_price, zhi=zhi, buzhi=buzhi)
            session.add(item)
            print(item)
            # stdout输出延迟
            # time.sleep(timesleep)
        session.commit()
        session.close()
    

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    item_id = Column(Integer)
    zhi = Column(String)
    buzhi = Column(String)
    url = Column(String)
    img = Column(String)
    update_time = Column(String)
    price = Column(String)


    def __init__(self, name, item_id, url, img, update_time, price, zhi, buzhi):
        """定义实例属性，方便自定义数据"""
        self.name = name
        self.item_id = item_id
        self.url = url
        self.img = img
        self.update_time = update_time + datetime.datetime.now().strftime(' %Y-%m-%d')
        self.price =price
        self.zhi = zhi
        self.buzhi = buzhi

    def __repr__(self):
        return("商品名字:{}\n详细地址:{}".format(self.name, self.url))
        # return("商品名字:{}\n详细地址:{}\n价格:{}\n值↑:{} 不值↓:{}\n更新日期:{}\n缩略图:{}".format(self.name,
        #                                                                                        self.url,
        #                                                                                        self.price,
        #                                                                                        self.zhi,
        #                                                                                        self.buzhi,
        #                                                                                        self.update_time,
        #                                                                                        self.img))


if __name__=="__main__":
    for i in range(5):
        target_address = "https://www.smzdm.com/jingxuan/p" + str(i)
        thread = ItemSpider(target_address)
        thread.start()
        time.sleep(1)
        