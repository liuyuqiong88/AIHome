# -*- coding: utf-8 -*-
import re
from flask import current_app,request,make_response,json,jsonify
from flask import session
from iHome import db
from iHome.models import User
from . import api, RET, redis_store

# 注册和登陆视图

# 注册
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
    if re.match(r'^1[2345678][\d]{9}&',mobile):
        return jsonify(error_no=RET.PARAMERR, error_msg=u'手机号格式不正确！')
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

    # 判断该手机是否已经注册
    if User.query.filter(User.mobile==mobile).first():
        return jsonify(error_no=RET.DATAEXIST,error_msg=u'用户已注册！')

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

    # 7.把登陆状态写入session
    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile

    # 8.响应结果:状态码和错误信息或用用户数据

    print user
    return jsonify(error_no=RET.OK,error_msg=u'注册成功！')


# 登陆
@api.route('/session',methods=["POST"])
def login():
    """处理登陆逻辑视图"""

    # 0.接受参数手机号，密码
    json_dict = request.json
    mobile = json_dict.get('mobile')
    password = json_dict.get('password')
    # １效验参数不能为空和手机号格式是否正确
    if not all([mobile,mobile]):
        return jsonify(error_no=RET.PARAMERR, error_msg=u'缺少参数')
    if re.match(r'^1[2345678][\d]{9}&',mobile):
        return jsonify(error_no=RET.PARAMERR, error_msg=u'手机号格式不正确！')
    # ２．查询读取数据库用户信息
    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'数据库链接错误')
    # ３．对比查询的信息是否为空以及密码是否正确
    if not user:
        return jsonify(error_no=RET.USERERR,error_msg=u'用户名或密码不正确')
    if not user.checkpassword(password):
        return jsonify(error_no=RET.USERERR, error_msg=u'用户名或密码不正确')
    #　４． 保存ｓｅｓｓｉｏｎ用户状态
    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile

    # ５．返回结果ｎ
    return jsonify(error_no=RET.OK,error_msg=u'登陆成功！')

# 注销登陆
@api.route('/session',methods=['DELETE'])
def logout():
    """注销登陆的视图"""

    # 获取登陆的user_id
    # 删除session保存的本用户状态
    session.pop('user_id')
    session.pop('name')
    session.pop('mobile')

    # 响应请求
    return jsonify(error_no=RET.OK,error_msg=u'注销登陆成功!')
