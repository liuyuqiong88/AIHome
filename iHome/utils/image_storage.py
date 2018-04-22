# -*- coding: utf-8 -*-
# 上传保存图片到七牛云
import qiniu


access_key = "yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW"
secret_key = "bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW"
bucket_name = "ihome"

def upload_image(image_data):
    """保存图片到七牛云的函数"""

    # 创建七牛云的对象
    q = qiniu.Auth(access_key, secret_key)
    # 获取上传的ｔｏｋｅｎ
    token = q.upload_token(bucket_name)
    # 调用上传的方法，实现生产并响应结果给我们
    # 说明：参数2传入None,表示让七牛云给我们生成数据的唯一标识key
    ret, info = qiniu.put_data(token, None, image_data)
    if info.status_code == 200:
    # 如果上传成功就返回key
        print u"上传成功"
        return ret.get('key')
    else:
    # 如果上传失败就抛出异常
        raise Exception('上传图片片失败')


if __name__ == '__main__':

    with open('/home/python/Desktop/flask_project/aijia/iHome/static/images/home03.jpg',"rb") as f:
        image_data = f.read()

    key = upload_image(image_data)
    print key