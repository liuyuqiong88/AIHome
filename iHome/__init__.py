# -*- coding: utf-8 -*-
from logging.handlers import RotatingFileHandler

import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import *
from utils.common import RegenConverter

# 创建mysql数据库链接到app
db = SQLAlchemy()

# redis链接的实例对象
redis_store = None

def setUpLogging(level):
    """根据开发环境设置入职等级"""

    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def get_app(config_name):

    # 取得对应模式的配置类

    setUpLogging(configs[config_name].LOGGING_LEVEL)
    # 实例化Ｆｌａｓｋ（）对象
    app = Flask(__name__)

    # 从Config读取配置参数
    app.config.from_object(configs[config_name])

    db.init_app(app)


    # 配置redis数据库参数
    global redis_store
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

    # 设置ａｐｐ的session 为redis
    Session(app)

    # 设置app的csrf_token
    # CSRFProtect(app)

    # 注册自定义转换器RegenConverter到app的转换器converters中
    app.url_map.converters['re'] = RegenConverter
    # 注册蓝图到app
    from api_1_0 import api
    app.register_blueprint(api)

    # 注册静态视图蓝图到app
    from web_html import html_blue
    app.register_blueprint(html_blue)

    return app