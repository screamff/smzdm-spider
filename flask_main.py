# coding:utf-8
from flask import Flask, render_template
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# 连接数据库
engine = create_engine('sqlite:///smzdm.db')
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
Item = Table('items', metadata, autoload=True)


@app.route('/', methods=['GET'])
def index():
    items = get_30_items()
    return render_template('index.html', items=items)


def get_30_items():
    session = Session()
    items=session.query(Item).order_by(Item.c.update_time).limit(30).all()
    session.close()
    return items

if __name__ == "__main__":
    print(get_30_items()[0])
    app.run(port=8642, debug=True)