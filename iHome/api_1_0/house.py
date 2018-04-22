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

# 查询area城区信息
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

# 发布房源视图接口
@api.route('/houses',methods=["POST"])
@login_requeired
def new_house():
    """发布新的房源
    0.判断用户是否登录
    1.接受参数：基本信息和设备信息
    2.判断参数是否为空，并对某些参数进行合法性的校验,比如金钱相关的
    3.创建房屋模型对象，并赋值
    4.保存房屋数据到数据库
    5.响应发布新的房源的结果
"""
    # 1.接受参数：基本信息和设备信息
    json_dict = request.json
    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')
    facility = json_dict.get('facility') # [2,4,6,8,10]

    #     2.判断参数是否为空，并对某些参数进行合法性的校验,比如金钱相关的
    if not all([title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days, facility]):
        return jsonify(error_no=RET.PARAMERR,error_msg=u'缺少参数')

    # # 校验价格和押金是否合法，不允许传入数字以外的数据
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.PARAMERR,error_msg=u'金额格式错误')

    # 3.创建房屋模型对象，并赋值
    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    # 给facilities属性赋值，实现多对多的关联关系 facility == [2,4,6,8,10]
    facilities = Facility.query.filter(Facility.id.in_(facility)).all()
    house.facilities = facilities

    # 4.保存房屋数据到数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'保存数据库失败！')

    # 5.响应发布新的房源的结果
    return jsonify(error_no=RET.OK,error_msg=u'保存房屋信息成功',data={"house_id":house.id})

# 添加房屋图片视图
@api.route('/houses/image',methods=["POST"])
@login_requeired
def set_house_image():
    # 0.判断用用户是否登录
    # 1.接受参数:房屋图片,house_id,并校验参数

    try:
        image_data = request.files.get('house_image')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.PARAMERR,error_msg=u'图片有误')

    try:
        house_id = request.form.get('house_id')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.PARAMERR,error_msg=u'缺少必传参数')

    # 2.获取房屋模型对象

    try:

        house = House.query.filter(House.id == house_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'查询房屋数据失败')

    if not house:
            return jsonify(error_no=RET.NODATA,error_msg=u'房屋不存在！')
    # 3.上传房屋图片片
    try:
        key = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.THIRDERR,error_msg=u'上传房屋图片失败')
    # 4.创建house_image模型对象,存储房屋图片片数据到数据库
    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url =  key
    # 设置房屋默认图片
    if not house.index_image_url:
        house.index_image_url = key


    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'提交数据失败')
# 5.响应结果
    house_image_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(error_no=RET.OK, error_msg='上传房屋图片片成功', data={'house_image_url': house_image_url})

# 房屋详情视图
@api.route('/houses/<int:house_id>')
@login_requeired
def house_detail(house_id):
    """房屋详情视图
    0.检查是否登陆
    1.接受house_id参数，
    ２．查询房屋模型数据
    ３．构建返回数据
    ４．返回结果

    """
    # 1.接受house_id参数

    # ２．查询房屋模型数据

    try:
        house = House.query.filter(House.id == house_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'查询数据失败')

    if not house:
            return jsonify(error_no=RET.NODATA,error_msg=u'房屋不存在！')

    # ３．构建返回数据
    house_dict = house.to_full_dict()

    # ４．返回结果
    return jsonify(error_no=RET.OK,error_msg=u'查询房屋成功',data=house_dict)