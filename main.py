# coding:utf-8
import time
import threading
import queue
import datetime
import re
import os
import logging
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# todo:
# 1.关键词搜索
# 2.使用flask构建看板页面
# 3.进行数据分析
# 常见问题:
# 多线程创建多个session（15个左右）引发的database locked, sqlite的性能限制,增加请求延迟或增加数据库的timeout时间,
# 减少线程数(使用线程池或异步),采取将请求线程与处理线程分开的方法(最开始的方法)。

# 连接数据库
engine = create_engine('sqlite:///smzdm.db')
# 基本类
Base = declarative_base()
Session = sessionmaker(bind=engine)

# 日志记录
logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'log.txt'),
                    format="%(levelname)s:%(name)s:%(asctime)s:%(message)s",
                    level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))


class ItemSpider(threading.Thread):
    """爬取smzdm精选好价页面物品信息
    参数--target_address  url地址
        --keyword  搜索物品的参数,暂未完成(页面解析方法不一样)
    示例--itemspider = ItemSpider("https://www.smzdm.com/jingxuan/p1")
          itemspider.start()"""
    divs = queue.Queue()
    def __init__(self, target_address, keyword=None):
        threading.Thread.__init__(self)
        self.target_address = target_address
        self.keyword = keyword
        

    def run(self):
        r = requests.get(self.target_address, params=self.keyword, headers={"User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"})
        soup = BeautifulSoup(r.content, "html.parser")
        # 保存网页测试用
        # with open(r".\saved.html", "wb") as f:
        #     f.write(r.content)
        div_row = soup.select('.feed-row-wide')
        if len(div_row)>0:
            self.divs.put(div_row)
            print('正在处理...数量:{},使用线程:{}'.format(len(div_row), threading.current_thread()))
        else:
            pass


    @staticmethod
    def analyze(div_row, session):
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
            temp_img = line.select_one('.z-feed-img').select_one('img')['src']
            # 商品值不值得买
            zhi = int(content.select_one('.icon-zhi-o-thin').next_sibling.string)
            buzhi = int(content.select_one('.icon-buzhi-o-thin').next_sibling.string)
            # 更新老商品的评价
            if old_item:
                old_item.zhi = zhi
                old_item.buzhi = buzhi
                continue
            # 商品更新日期
            temp_time = datetime.datetime.fromtimestamp(int(line['timesort']))
            # print('更新日期:', temp_time)
            # 商品价格
            temp_price = content.select_one('.z-highlight')    
            try:
                temp_price = temp_price.get_text().strip()
            except:
                logger.warning('item:{}price:{}'.format(temp_url, temp_price))
            item = Item(name=temp_name, item_id=item_id, url=temp_url, img=temp_img,
                        update_time=temp_time, price=temp_price, zhi=zhi, buzhi=buzhi)
            session.add(item)
            # print(item)
            # stdout输出延迟
            # time.sleep(1)
        session.commit()


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    item_id = Column(Integer)
    zhi = Column(Integer)
    buzhi = Column(Integer)
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


def start_analyze():
    session = Session()
    while True:
        try:
            div_row = ItemSpider.divs.get(timeout=3)
            print('解析中...')
            ItemSpider.analyze(div_row, session)
        except queue.Empty:
            logger.info('all pages finished')
            break
        except Exception as e:
            logger.warning('analyze_warning:{}'.format(e))
            continue
    session.close()


if __name__=="__main__":
    # 若没有数据库就创建
    Base.metadata.create_all(engine)

    # 初始化一些变量
    start_time = time.time()

    # 预设的一些可爬取页面
    urls = {'all':"https://www.smzdm.com/jingxuan/p",
            'inland':"https://www.smzdm.com/jingxuan/xuan/s0f0t0b0d1r0p",
            'haitao':"https://www.smzdm.com/jingxuan/xuan/s0f0t0b0d2r0p",
            'quanma':"https://www.smzdm.com/jingxuan/xuan/s0f0t0b0d0r2p",
            'huodong':"https://www.smzdm.com/jingxuan/xuan/s0f0t0b0d0r3p",
            'computer':"https://www.smzdm.com/jingxuan/xuan/s0f163t0b0d0r0p"}

    
    # 爬取-请求线程
    sem = threading.Semaphore(30)
    # 爬取-处理线程
    thread = threading.Thread(target=start_analyze)
    thread.start()
    with sem:
        for i in range(1, 5):
            target_address = urls['all'] + str(i)
            thread = ItemSpider(target_address)
            thread.start()
            time.sleep(0.1)

    # 计算耗时
    for spider_thread in threading.enumerate()[1:]:
        spider_thread.join()
    logger.info('use_time:{}'.format(time.time()-start_time))
    print('用时:', time.time()-start_time)
