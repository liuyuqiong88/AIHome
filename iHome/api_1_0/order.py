# -*- coding: utf-8 -*-
# 订单

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
import datetime

# 新建订单视图
@api.route('/orders',methods=["POST"])
@login_requeired
def create_order():
    """创建，提交订单
    0.判断是否登陆
    １．获取house_id,start_time,end_time等参数
    2.效验参数不能为空
    ３．效验日期的合法性，
    ４。判断订购时间已否与已有订单冲突
    ５．新建订单
    ６．响应结果

    """

    json_dict = request.json
    house_id = json_dict.get('house_id')
    start_time = json_dict.get('start_time')
    end_time = json_dict.get('end_time')
    user_id = g.user_id

    # 2.判断参数是否缺少,并校验参数
    if not all([house_id,start_time,end_time]):
        return jsonify(error_no=RET.PARAMERR,error_msg=u'缺少参数')

    try:
        print start_time ,end_time
        start_time = datetime.datetime.strptime(start_time,'%Y-%m-%d')
        end_time = datetime.datetime.strptime(end_time,'%Y-%m-%d')
        print start_time, end_time
        if start_time and end_time:
            assert end_time > start_time ,Exception('入住时间有误')

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.PARAMERR,error_msg=u'入住时间有误')


    try:
        house = House.query.filter(House.id==house_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR, error_msg=u'查询数据库失败')

    if not house:
        return jsonify(error_no=RET.NODATA,error_msg=u'房屋不存在！')
    # 3.判断当前房屋在该时间段内是否被预定
    try:
        conflict_orders = Order.query.filter(Order.house_id==house_id,start_time<Order.end_date,end_time>Order.begin_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'查询订单冲突数据失败')

    if conflict_orders:
        return jsonify(error_no=RET.DATAERR,error_msg=u'该时间段此房屋已经被预定')

    # 4.创建订单模型对象,并给属性复制

    order = Order()
    order.user_id = user_id
    order.house_id = house_id
    order.begin_date = start_time
    order.end_date = end_time
    order.days = (end_time - start_time).days
    order.house_price = house.price
    order.amount = order.house_price * order.days



    # 5.保存订单数据到数据库

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_no=RET.DBERR,error_msg=u'提交数据失败')

    # 6.响应结果

    return jsonify(error_no=RET.OK,error_msg=u'保存订单成功')


# 获取订单视图
@api.route('/orders')
@login_requeired
def get_order():
    """获取订单
    ０.验证登陆用户
    1.获取user_id 参数
    ２．查询该用户的所有订单信息
    3.构造返回数据
    4.返回结果
    """
    # 获取查询订单的房东还是租客
    role = request.args.get('role')

    if role not in ["landlord","custom"]:
        return jsonify(error_no=RET.PARAMERR,error_msg=u'用户身份错误！')

    user_id = g.user_id

    try:
        if role == "custom":
            # 当请求订单为我的订单时返回的订单
            orders = Order.query.filter(Order.user_id==user_id).all()
        else:
            # 当请求订单为房东订单时返回的订单
            # 先查询该用户有多少个房子
            houses = House.query.filter(House.user_id==user_id).all()
            #再根据用户所拥有的房子去查订单表
            house_ids = [house.id for house in houses]
            orders = Order.query.filter(Order.house_id.in_(house_ids)).all()

    except Exception as e :
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'查询数据库失败')

    if not orders :
        return jsonify(error_no=RET.DATAERR, error_msg=u'查不到订单')

    orders_list = []

    for order in orders:
        orders_list.append(order.to_dict())



    return jsonify(error_no=RET.OK,error_msg=u'查询成功',data=orders_list)

# 修改订单状态视图
@api.route('/orders/<int:order_id>',methods=["PUT","POST"])
@login_requeired
def status_orders(order_id):
    """修改订单状态视图
    0.判断用用户是否登录
    1.获取order_id,并查询订单,状态要是"待接单"
    2.判断登录用用户是否是该订单的房东
    3.修改订单状态并保存到数据库
    4.响应结果

    """

    action = request.args.get('action')

    if action not in ['accept', 'reject']:
        return jsonify(error_no=RET.PARAMERR,error_msg=u'参数错误')

    # 1.获取order_id,并查询订单,状态要是"待接单"
    try:
        order = Order.query.filter(Order.id==order_id,Order.status=="WAIT_ACCEPT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'查询订单数据失败')
    if not order:
        return jsonify(error_no=RET.NODATA,error_msg=u'订单不存在！')

    user_id = g.user_id

    try:
        house = House.query.filter(House.id==order.house_id).first()
        oreder_landlord_id = house.user_id
    except Exception as e :
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'查询订单房东失败')

    print user_id,oreder_landlord_id

    if user_id != oreder_landlord_id:
        return jsonify(error_no=RET.ROLEERR,error_msg=u'用户身份错误')

    try:
        if action == 'accept':
            order.status = "WAIT_COMMENT"
        else:
            reason = request.json.get('reason')
            order.status = 'REJECTED'
            if not reason:
                return jsonify(error_no=RET.PARAMERR,error_msg=u'拒单理由为空')
            order.comment = reason


        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DATAERR,error_msg=u'修改订单状态失败')

    return jsonify(error_no=RET.OK,error_msg=u'OK')

# 评论
@api.route('/orders/comment/<int:order_id>',methods=["POST"])
@login_requeired
def set_order_com(order_id):
    """修改评论视图"""

    comment = request.json.get('comment')

    if not comment:
        return jsonify(error_no=RET.PARAMERR, error_msg='缺少必传参数')

    try:

        order = Order.query.filter(Order.id == order_id, Order.status == 'WAIT_COMMENT', Order.user_id == g.user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR, error_msg='查询订单数据失败')

    if not order:
        return jsonify(error_no=RET.NODATA, error_msg='订单不不存在')

    order.status = 'COMPLETE'
    order.comment = comment

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(error_no=RET.DBERR, error_msg='保存评论信息失败')

    return jsonify(error_no=RET.OK, error_msg='OK')