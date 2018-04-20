# -*- coding: utf-8 -*-
from iHome.third_libs.yuntongxun.CCPRestSDK import REST

# 请求服务器地址
serverIP = 'app.cloopen.com'
# 请求端口
serverPort = '8883'
# REST版本号
softVersion = '2013-12-26'


# 单例模式的发信息对象
class CCP(object):

    _instanse = None

    def __new__(cls, *args, **kwargs):

        if not cls._instanse:
            cls._instanse = super(CCP,cls).__new__(cls,*args,**kwargs)

            cls._instanse.rest =  REST(serverIP,serverPort,softVersion)
            # 设置　AccountSid　以及　AccountToken　　参数
            cls._instanse.rest.setAccount('8a216da862dcd1050162dd2f7099007a', '4463f5369cef4efe8f63baa7828d52a3')
            # 设置　AppId　参数
            cls._instanse.rest.setAppId('8a216da862dcd1050162dd2f71070081')

        return cls._instanse


    def send_sms_code(self,to,datas,temId):

        # # 创建一个发送短信的对象
        # rest = REST(serverIP,serverPort,softVersion)
        #
        # # 设置　AccountSid　以及　AccountToken　　参数
        # rest.setAccount('8a216da862dcd1050162dd2f7099007a','4463f5369cef4efe8f63baa7828d52a3')
        # # 设置　AppId　参数
        # rest.setAppId('8a216da862dcd1050162dd2f71070081')

        # 发送短信
        result = self._instanse.rest.sendTemplateSMS(to,datas,temId)

        if result.get('statusCode') == "000000":
            return 0
        else:
            return 1

if __name__ == '__main__':




    rest = CCP()

    # 调用发送短信的函数，第一个参数为要发送的手机号码，第二个参数为验证号码以及过期时间（时间单位为分钟）,第三个参数为ｉｄ号
    result = rest.send_sms_code('13798076559',['665544',5],'1')