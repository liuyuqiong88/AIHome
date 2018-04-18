# -*- coding: utf-8 -*-

# 从werkzeug.routing引入基转换器BaseConverter
from werkzeug.routing import BaseConverter

class RegenConverter(BaseConverter):
    """自定义正则转换器"""

    def __init__(self,url_map,*args):

        super(RegenConverter,self).__init__(url_map)
        self.regex = args[0]