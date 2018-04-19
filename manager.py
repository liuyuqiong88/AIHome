# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from iHome import get_app,db
from iHome.models import *




app = get_app('dev')

manager = Manager(app)

# 迁移类，在迁移时使db数据库和app建立关联
Migrate(app,db)
# 将迁移脚本添加到脚本管理器
manager.add_command('db',MigrateCommand)



# @app.route('/',methods=["POST","GET"])
# def index():
#
#     return 'index'


if __name__ == '__main__':
    print app.url_map
    manager.run()

