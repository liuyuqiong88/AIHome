# -*- coding: utf-8 -*-
#使用蓝图按照接口版本划分模块
from flask import Blueprint,current_app

api = Blueprint('api_1_0',__name__,url_prefix='/api_1_0')

from index import *