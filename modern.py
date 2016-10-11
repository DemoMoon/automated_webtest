# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from Util import parse_config
__author__ = 'yingxue'
# 解析配置文件
config = parse_config()
# 与数据库建立链接
engine = create_engine('mysql://%s:%s@%s/%s?charset=%s' % (
    config.get('common', 'user'),
    config.get('common', 'pwd'),
    config.get('common', 'host'),
    config.get('common', 'database'),
    config.get('common', 'charset')), echo=True)
# 数据库表结构
Base = declarative_base()


class Users(Base):
    __tablename__ = 'wb_users'
    id = Column(Integer, primary_key=True)
    mobile = Column(String)

    # def __init__(self, id, mobile):
    #     self.id = id
    #     self.mobile = mobile
    #
    # def __repr__(self):
    #     return super(Users, self).__repr__()

class UsersInfo(Base):
    __tablename__ = 'wb_users_info'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

# 创建所有的表
Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
