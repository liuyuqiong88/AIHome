# -*- coding: utf-8 -*-
import redis
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
#
# from flask_wtf.csrf import CSRFProtect
# from flask_session import Session


class Config(object):
    """app 的实例化的配置参数类"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/iHome_01"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    SECRET_KEY = "ksc89Qq0Z61VJjA2fXXW0QpJQQA9FLRycS2tyIkHEijFgM3aYbQ3Z+c3DXgx2B3c"

    PERMANENT_SESSION_LIFETIME = 3600 * 24




class Develpment(Config):
    """开发模式下的配置"""

    pass

class Production(Config):
    """生产环境，线上，部署之后"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/iHome"


class UnitTest(Config):
    """测试环境"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/iHome_unittest"


# 运行模式的配置参数
configs = {
    "dev" : Develpment,
    "pro" : Production,
    "test": UnitTest,
}

