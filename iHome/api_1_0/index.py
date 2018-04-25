# -*- coding: utf-8 -*-
# 主页的视图函数

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

# 判断登陆的视图
@api.route('/sessions',)
def check_login():
    """判断是否登陆"""
    user_id = session.get("user_id")
    name = session.get("name")

    return jsonify(error_no=RET.OK,error_msg=u'OK',data={"user_id":user_id,"name":name})

# 搜索列表视图
@api.route('/houses/search')
def search():
    """搜索列表视图
    1.查询所有房屋信息
    2.构造响应数据
    3.响应结果
    """

    # 获取参数
    aid = request.args.get('aid')

    sk = request.args.get('sk','')
    current_app.logger.debug(sk)
    p = request.args.get('p','')
    sd = request.args.get('sd','')
    ed = request.args.get('ed','')

    start_date = None
    end_date =None



    # 校验参数
    try:
        p = int(p)
        if sd:
            start_date = datetime.datetime.strptime(sd, '%Y-%m-%d')
        if ed:
            end_date = datetime.datetime.strptime(ed, '%Y-%m-%d')
        if start_date and end_date: # 入住时间必须小于离开时间
            assert start_date < end_date, Exception('入住时间有误') # 主动抛出异常，让后面的代码可以捕获到
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.PARAMERR,error_msg=u'参数错误')

    houses_list = []

    try:

        house_query = House.query

        if aid:
            house_query = house_query.filter(House.area_id == aid)
        # houses = House.query.all()

        conflict_orders = []
        # 根据用户选中的入住和离开时间，筛选出对应的房屋信息（需要将已经在订单中的时间冲突的房屋过滤掉）
        if start_date and end_date:
            conflict_orders = Order.query.filter(start_date<Order.end_date , end_date >Order.begin_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(start_date < Order.end_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(end_date < Order.begin_date).all()
        # 当发现有时间冲突的房屋时，才需要筛选出来
        if conflict_orders:
            conflict_house_ids = [order.house_id for order in conflict_orders]
            house_query = house_query.filter(House.id.notin_(conflict_house_ids))


        # 排序
        if sk == 'booking':
            house_query = house_query.order_by(House.order_count.desc())
        elif sk == 'price-inc':
            house_query = house_query.order_by(House.price.asc())
        elif sk == 'price-des':
            house_query = house_query.order_by(House.price.desc())
        else:
            house_query = house_query.order_by(House.create_time.desc())

        paginate = house_query.paginate(p, constants.HOUSE_LIST_PAGE_CAPACITY,False)

        houses = paginate.items

        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'查询数据失败')
        # house_dict_list = []
    for house in houses:
        houses_list.append(house.to_basic_dict())

    response_dict = {
        'house': houses_list,
        'total_page': total_page,
    }

    return jsonify(error_no=RET.OK,error_msg=u'OK',data = response_dict)

@api.route('/houses/index')
def default_house_image():
    """主页房屋推荐:推荐最新发布的五个房屋
    1.直接查询最新发布的五个房屋：根据创建的时间倒叙，取最前面五个
    2.构造房屋推荐数据
    3.响应房屋推荐数据
    """
    try:
        houses = House.query.order_by(House.create_time.desc()).limit(constants.HOUSE_LIST_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error_no=RET.DBERR,error_msg=u'数据库错误')

    house_list = []

    for house in houses:
        house_list.append(house.to_basic_dict())

    return jsonify(error_no=RET.OK,error_msg=u'OK',data= house_list)


