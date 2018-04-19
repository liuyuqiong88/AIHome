# -*- coding: utf-8 -*-
from distutils.command.config import config

from flask import abort, jsonify
from flask import make_response
from flask import request
from iHome import constants
from . import api
from iHome import redis_store
from iHome.utils.captcha.captcha import captcha
from iHome.utils.response_code import *

last_uuid = ""

@api.route('/api')
def index():
    redis_store.set('name','qiong')
    return "api"

@api.route("/image_code",methods=["GET","POST"])
def get_image_code():
    """提供图片验证码"""

    # 取得uuid号码
    uuid = request.args.get('uuid')
    global last_uuid

    # 判定uuid是否为空
    if not uuid:
        abort(403)


    # 生成图片验证码的名字，文字信息，图片
    name,text,image =captcha.generate_captcha()
    try:
        if redis_store.get('ImageCode:' + last_uuid):
            redis_store.delete('ImageCode:' + last_uuid)
        redis_store.set('ImageCode:' + uuid, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        print e
        return jsonify(error_no=RET.DBERR,error_msg=u'存储图片验证码失败')
    #响应图片验证码
    response = make_response(image)


    last_uuid = uuid
    # 响应头的文件类型改为图片类型
    response.headers['Content-Type'] = 'image/jpg'

    return response