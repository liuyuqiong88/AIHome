from . import api
from iHome import redis_store


@api.route('/api')
def index():
    redis_store.set('name','qiong')
    return "api"