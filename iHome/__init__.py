# -*- coding: utf-8 -*-

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



def get_app(config_name):

    # 取得对应模式的配置类

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
    CSRFProtect(app)

    # 注册自定义转换器RegenConverter到app的转换器converters中
    app.url_map.converters['re'] = RegenConverter
    # 注册蓝图到app
    from api_1_0 import api
    app.register_blueprint(api)

    # 注册静态视图蓝图到app
    from web_html import html_blue
    app.register_blueprint(html_blue)

    return app