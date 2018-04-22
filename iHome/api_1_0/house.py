# -*- coding: utf-8 -*-
# 城区模块功能视图

from flask import current_app,request,make_response,json,jsonify
from flask import g
from flask import session
from iHome import db
from iHome.models import *
from iHome.utils.common import login_requeired
from . import api
from iHome.utils.response_code import RET
from iHome import redis_store
from iHome.utils.image_storage import upload_image

@api.route('/areas',methods=["GET"])
def get_areas():
    """提供城区信息
    1.直接查询所有城区信息
    2.构造城区信息响应数据
    3.响应城区信息
    """
    # 1.直接查询所有城区信息
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR, error_msg=u'查询地区数据失败')

    # 2.构造城区信息响应数据
    area_dict_list = []

    for area in areas:
        area_dict_list.append(area.to_dict())
    # 3.响应城区信息

    return jsonify(error_no=RET.OK,error_msg=u'成功',data = area_dict_list)
