# -*- coding: utf-8 -*-
from distutils.command.config import config

import logging
from logging.handlers import RotatingFileHandler

import re
from flask import abort, jsonify
from flask import current_app
from flask import make_response
from flask import request
from iHome import constants
from iHome.utils.sms import CCP
from . import api
from iHome import redis_store
from iHome.utils.captcha.captcha import captcha
from iHome.utils.response_code import *
import random


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

    current_app.logger.debug(text)

    try:
        if redis_store.get('ImageCode:' + last_uuid):
            redis_store.delete('ImageCode:' + last_uuid)
        redis_store.set('ImageCode:' + uuid, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:

        current_app.logger.errer(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'存储图片验证码失败')
    #响应图片验证码
    response = make_response(image)



    last_uuid = uuid
    # 响应头的文件类型改为图片类型
    response.headers['Content-Type'] = 'image/jpg'

    return response

# 获取短信验证码视图
@api.route('/send_sms_code',methods=["POST"])
def send_sms_code():

    # 0.获取参数
    json_dict = request.json

    imagecode = json_dict.get('imageCode')
    mobile = json_dict.get('mobile')
    uuid = json_dict.get('uuid')
    # １.验证参数不能为空
    if not all([imagecode,mobile,uuid]):
        return jsonify(error_no=RET.PARAMERR,error_msg=u'参数不能为空')
    #２. 手机格式是否正确
    if not re.match(r'1[2345678][\d]{9}',mobile):
        return jsonify(error_no=RET.PARAMERR,error_msg=u'手机格式有误')

    # 3.获取服务器存储的验证码
    try:
        image_code_server = redis_store.get('ImageCode:' + uuid)
    except Exception as e:
        current_app.logger.errer(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'获取服务器图片验证码失败')
    # 4.跟客户端传入的验证码进行对比
    if image_code_server.lower() != imagecode.lower() :
        return jsonify(error_no=RET.DATAERR,error_msg=u'图片验证码错误')
    # 5.如果对比成功就生成短信验证码
    sms_code = "06%d" %random.randint(0,9999)
    # 6.调用单例类发送短信

    ccp = CCP()
    statusCode = ccp.send_sms_code(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],'1')

    if statusCode != 0:
        return jsonify(error_no=RET.THIRDERR,error_msg=u'发送短信验证码失败')
    # 7.如果发送短信成功，就保存短信验证码到redis数据库

    try:
        result = redis_store.set('Mobile:' + mobile,sms_code, constants.SMS_CODE_REDIS_EXPIRES )

        test = redis_store.get('Mobile:' + mobile)

        print "111111111111111111111111111111",test,result

    except Exception as e:
        current_app.logger.errer(e)
        return jsonify(error_no=RET.DATAERR,error_msg=u'短信验证码存储失败！')
    # 8.响应发送短信的结果

    return jsonify(error_no=RET.OK,error_msg=u'短信验证码发送成功')
