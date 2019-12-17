# 创建数据库脚本
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# 连接数据库
engine = create_engine('sqlite:///smzdm.db', echo=True)

# 基本类
Base = declarative_base()

# 表要继承基本类
class Item(Base):
    # 定义各字段
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    item_id = Column(Integer)
    zhi = Column(String)
    buzhi = Column(String)
    price = Column(String)
    url = Column(String)
    img = Column(String)
    update_time = Column(String)

    def __repr__(self):
        return(self.name)

# 创建表
Base.metadata.create_all(engine)

# ### 测试
# # 连接数据库
# engine = create_engine('sqlite:///smzdm.db')
# # 基本类
# Base = declarative_base()
# Session = sessionmaker(bind=engine)
# session = Session()
# id = session.query(Item).filter(Item.item_id==18144407).one()
# if id:
#     print(id.url)
# else:
#     print("no id")