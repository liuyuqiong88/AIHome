# -*- coding: utf-8 -*-


from flask import Blueprint,current_app
from utils.common import RegenConverter


# 创建静态html蓝图
html_blue = Blueprint('html',__name__)


# 处理静态文件的视图
@html_blue.route('/<re(".*"):filename>')
def get_static_file(filename):
    """提供静态html文件"""

    if not filename:
        filename = "html/index.html"

    if filename != 'favicon.ico':
        filename = "html/%s" %filename



    # current_app 是上下文应用，返回的是当前的这个app，
    # send_static_file 是Ｆｌａｓｋ内置的静态文件处理函数
    return  current_app.send_static_file(filename)