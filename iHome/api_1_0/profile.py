# -*- coding: utf-8 -*-

#　个人中心

import re
from flask import current_app,request,make_response,json,jsonify
from flask import g
from flask import session
from iHome import db
from iHome.models import User
from iHome.utils.common import login_requeired
from . import api, RET, redis_store
from iHome.utils.image_storage import upload_image

# 上传图片视图
@api.route('/users/avatar',methods=["POST"])
@login_requeired
def upload_avatar():
    """上传图片到七牛云"""

    # 0.TODO 判断当前用户是否登录

    # 1.获取用用户上传的头像数据
    user_id = session['user_id']
    try:
        image_data = request.files.get('avatar')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.PARAMERR,error_msg=u'获取文件数据失败')
    # 2.调用用上传图片片的方方法,上传头像到七牛牛云
    try:
        key = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DATAERR,error_msg=u'上传图片错误！')
    # 3.如果上传成功,存储图片片唯一一标识到数据库
    try:
        user = User.query.filter(User.id == user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'查询用户失败')

    if not user:
        return jsonify(error_no=RET.NODATA,error_msg=u'用户不存在！')
    user.avatar_url = key

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR, error_msg=u'图片提交数据库失败')

    # 4.如果上传成功响应结果
    response_data = user.to_dict()

    return jsonify(error_no=RET.OK,error_msg=u'图片上传成功!',data=response_data)

# 修改用户名字视图
@api.route('/users/name',methods=["PUT"])
@login_requeired
def set_user_name():
    """修改用户名
    0.TODO 判断用户是否登录
    1.获取新的用户名，并判断是否为空
    2.查询当前的登录用户
    3.将新的用户名赋值给当前的登录用户的user模型
    4.将数据保存到数据库
    5.响应修改用户名的结果
    """
    # 1.获取新的用户名，并判断是否为空
    new_name = request.json.get('name')
    print new_name
    if not all([new_name]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少必传参数')
    # 2.查询当前的登录用户
    user_id =session['user_id']
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.PARAMERR, errmsg='用户不存在')

    #     3.将新的用户名赋值给当前的登录用户的user模型
    user.name = new_name

    # 4.将数据保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存新的用户名失败')
    # 5.响应修改用户名的结果
    response_data = user.to_dict()
    return jsonify(errno=RET.OK, errmsg='修改用户名成功',data = response_data)

# 显示个人信息视图
@api.route('/userinfo')
@login_requeired
def get_user_info():
    """提供个人信息
    0.TODO 判断用户是否登录
    1.从session中获取当前登录用户的user_id
    2.查询当前登录用户的user信息
    3.构造个人信息的响应数据
    4.响应个人信息的结果
    """
    # 1.从session中获取当前登录用户的user_id

    user_id = g.user_id

    #  2.查询当前登录用户的user信息
    try:
        user = User.query.filter(User.id==user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR, error_msg='查询用户数据失败')

    response_data = user.to_dict()

    return jsonify(error_no=RET.OK,error_msg=u'OK',data = response_data)


# 修改身份证视图
@api.route('/users/auth',methods=["POST"])
def set_auth():
    pass