# coding:utf-8
import requests
import time
from bs4 import BeautifulSoup
import threading
import queue
import datetime
import re
from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# todo:1.改写模块为类 # 已完成
# 2.使用flask构建看板页面
# 3.数据存入数据库 # 已完成
# 4.对值不值得买进行数据分析
# 5.可能采取对商品详情页进行数据解析(单页解析太麻烦了)

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
        with open(r".\saved.html", "wb") as f:
            f.write(r.content)
        div_row = soup.select('.feed-row-wide')
        print('本次商品数量', len(div_row))
        self.analyze(div_row, 1)

    @staticmethod
    def analyze(div_row, timesleep=1):
        # 为一个线程分配一个会话
        session = Session()
        for line in div_row:
            content = line.select_one('.z-feed-content')
            # 商品名字
            temp_name = content.select_one('div h5').a.string.strip()
            # 商品地址
            temp_url = content.select_one('div h5').a['href']
            # 商品id
            item_id = re.match(r".*/(\d+)/", temp_url).group(1)
            old_item = session.query(Item).filter(Item.item_id==item_id).scalar()
            # 商品图片url
            temp_img = content.parent.select_one('.z-feed-img').select_one('img')['src']
            # 商品值不值得买
            zhi = content.select_one('.icon-zhi-o-thin').next_sibling.string
            buzhi = content.select_one('.icon-buzhi-o-thin').next_sibling.string
            # 更新老商品的评价
            if old_item:
                old_item.zhi = zhi
                old_item.buzhi = buzhi
                continue
            # 商品更新日期
            temp_time = datetime.datetime.fromtimestamp(int(line['timesort']))
            # print('更新日期:', temp_time)
            # 商品价格, todo:之后尝试不要请求商品详情页
            temp_price = content.select_one('.z-highlight')    
            try:
                temp_price = temp_price.string.strip()
            except AttributeError:
                # 记录错误日志
                with open(r".\errorlog.html", "wb") as f:
                    f.write(str(content).encode('utf-8'))
                if temp_price.get_text():
                    temp_price = temp_price.get_text().strip()
                else:
                    r = requests.get(temp_url, headers={"User-Agent":
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"})
                    soup = BeautifulSoup(r.content, "html5lib")
                    price = soup.select_one('.price')
                    if price:
                        temp_price = price.span.string
                    else:
                        old_price = soup.select_one('.old-price').select('span')[1]
                        temp_price = old_price.string
            print("-"*40)
            item = Item(name=temp_name, item_id=item_id, url=temp_url, img=temp_img,
                        update_time=temp_time, price=temp_price, zhi=zhi, buzhi=buzhi)
            session.add(item)
            session.commit()
            print(item)
            # stdout输出延迟
            # time.sleep(timesleep)
        session.close()
    

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    item_id = Column(Integer)
    zhi = Column(String)
    buzhi = Column(String)
    price = Column(String)
    url = Column(String)
    img = Column(String)
    update_time = Column(DateTime)


    def __init__(self, name, item_id, url, img, update_time, price, zhi, buzhi):
        """定义实例属性，方便自定义数据"""
        self.name = name
        self.item_id = item_id
        self.url = url
        self.img = img
        self.update_time = update_time
        self.zhi = zhi
        self.buzhi = buzhi
        self.price =price

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
    for i in range(1, 5):
        # target_address = "https://www.smzdm.com/jingxuan/p" + str(i)
        target_address = "https://www.smzdm.com/jingxuan/xuan/s0f0t0b0d0r3p" + str(i)
        thread = ItemSpider(target_address)
        thread.start()
        time.sleep(0.5)

    # target_address = "https://www.smzdm.com/jingxuan/xuan/s0f0t0b0d2r0p1"
    # thread = ItemSpider(target_address)
    # thread.start()
