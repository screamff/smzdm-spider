# coding:utf-8
import requests
import time
from bs4 import BeautifulSoup
import threading
import queue
import datetime
import re
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 连接数据库
engine = create_engine('sqlite:///search_results.db')
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
    def __init__(self, target_address, keyword=None, cookies=None):
        threading.Thread.__init__(self)
        self.target_address = target_address
        self.keyword = keyword
        self.cookies = cookies
        

    def run(self):
        r = requests.get(self.target_address, params=self.keyword, cookies=cookies_dict, headers={"User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36"})
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
            temp_name = content.select_one('div h5').a.get_text().strip()
            # 商品地址
            temp_url = content.select_one('div h5').a['href']
            # 商品id
            item_id = re.match(r".*/(\d+)/", temp_url).group(1)
            old_item = session.query(Item).filter(Item.item_id==item_id).scalar()
            # 商品图片url
            temp_img = line.select_one('.z-feed-img').select_one('img')['src']
            # 商品值不值得买
            zhi = int(content.select_one('.z-icon-zhi').next_element.next_element.string)
            buzhi = int(content.select_one('.z-icon-buzhi').next_element.next_element.string)
            # 更新老商品的评价
            if old_item:
                old_item.zhi = zhi
                old_item.buzhi = buzhi
                continue
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
    __tablename__ = 'results'
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
    Base.metadata.create_all(engine)
    item_name = input('输入商品名字:')
    keyword = {'s': item_name.encode("utf-8")}
    cookies = "__ckguid=pRU6fG7bupaAEht67p4Fh; smzdm_user_source=8D338CF9A6C99A9FC011DEBC6E14DEB9; device_id=1018093322154779854027573666f25827dd1b6f4c216adbdc1351292a; _ga=GA1.2.2123467025.1547798543; __jsluid_s=e9792b89a391fc442b9235a5bb10c69f; __jsluid_h=b72740262a292c254d89193c99c6c468; homepage_sug=h; r_sort_type=score; PHPSESSID=4dfe9e3da6ca90e20d74c3a0fb09ee19; Hm_lvt_9b7ac3d38f30fe89ff0b8a0546904e58=1575438314,1576461068; zdm_qd=%7B%7D; smzdm_user_view=5D987DBC83676D6A3A321AF556265172; wt3_sid=%3B999768690672041; ss_ab=ss8; _gid=GA1.2.53837185.1576723716; wt3_eid=%3B999768690672041%7C2155935802700580408%232157673430500459891; _zdmA.uid=ZDMA.yzxrIJZ9I.1576735639.2419200; s_his=%E9%A3%9E%E5%88%A9%E6%B5%A6%E7%94%B5%E5%8A%A8%E7%89%99%E5%88%B7%2C%E9%A3%9E%E5%88%A9%E6%B5%A66511%2C%E8%82%A5%E7%9A%82%2C%E5%8D%A1%E7%89%87%E6%9C%BA%2C%E7%94%B5%E5%8A%A8%E7%89%99%E5%88%B7%2C%E5%93%87%E5%93%88%E5%93%88%2Cyashua%2C%E7%89%99%E5%88%B7; Hm_lpvt_9b7ac3d38f30fe89ff0b8a0546904e58=1576735792"
    cookies = cookies.split(';')
    cookies_dict = {}
    for i in cookies:
        a, b = i.split('=')
        cookies_dict[a]=b
    
    # 爬取-处理线程
    thread = threading.Thread(target=start_analyze)
    thread.start()

    for i in range(1, 5):
            target_address = "https://search.smzdm.com/?c=faxian&p=" + str(i)
            thread = ItemSpider(target_address, keyword, cookies=cookies_dict)
            thread.start()
            time.sleep(0.5)