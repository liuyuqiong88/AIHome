# -*- coding: utf-8 -*-

from flask import current_app,request,make_response,json,jsonify

from iHome import db
from iHome.models import User
from . import api, RET, redis_store


@api.route('/users',methods=["POST","GET"])
def register_new_user():
    """处理注册逻辑的视图"""

    # 0.获取请求报文
    datas_dict = request.json
    # 1.获取参数:手手机号,短信验证码,密码
    mobile = datas_dict.get('mobile')
    smscode = datas_dict.get('smscode')
    password = datas_dict.get('password')
    print datas_dict
    # 2.判断参数是否缺少
    if not all([mobile,smscode,password]):
        return jsonify(error_no=RET.PARAMERR,error_msg=u'缺少参数')
    # 3.获取服务器器端短信验证码
    try:
        print 'Mobile:' + mobile
        smscode_server = redis_store.get('Mobile:' + mobile)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'获取服务器短信验证码错误')
    # 4.对比比短信验证码
    if smscode != smscode_server :
        print smscode_server,smscode
        return jsonify(error_no=RET.PARAMERR,error_msg=u'短信验证码错误！')
    # 5.初始化User模型,保存相关数据
    user = User()
    user.name = mobile
    user.mobile = mobile
    # TODO: 保存加密后的密码暂缓实现
    user.password = password
    # 6.将User模型存储到数据库

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_no=RET.DBERR,error_msg=u'保存注册数据失败！')

    # 7.响应结果:状态码和错误信息或用用户数据

    print user
    return jsonify(error_no=RET.OK,error_msg=u'注册成功！')

