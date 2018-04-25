# -*- coding: utf-8 -*-

# 从werkzeug.routing引入基转换器BaseConverter
import functools

from flask import g
from flask import session, jsonify
from werkzeug.routing import BaseConverter

from iHome.utils.response_code import RET


class RegenConverter(BaseConverter):
    """自定义正则转换器"""

    def __init__(self,url_map,*args):

        super(RegenConverter,self).__init__(url_map)
        self.regex = args[0]


def login_requeired(func):
    """判断登陆状态"""

    @functools.wraps(func)
    def wraaper(*args,**kwargs):
        user_id = session.get("user_id")

        if not user_id:
            return jsonify(error_no=RET.SESSIONERR,error_msg=u'用户未登陆!')
        else:
            g.user_id = user_id
            return func(*args,**kwargs)

    return wraaper

