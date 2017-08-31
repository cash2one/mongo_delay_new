from pymongo import MongoClient
import time
conn = MongoClient('127.0.0.1', 27017, connect=False)
db = conn['jame_bd']  # 存储任务队列，任务队列，超时队列数据库
db1 = conn['tmp_db']
ctb = db1['jm_task_proxyverificate']
stb =db['jame_proxy']

proxyip = stb.find_and_modify(query={'ipInfo.status': 1, 'usetime': {'$lte': (time.time() - 5 * 60)}},
                                        update={'$set': {'usetime': time.time()}, '$inc': {'ipInfo.count': 1}},
                                        )  # 'ipInfo.status':1,'usetime':{'$lte':(time.time()-5*60)}

tmp = proxyip['ipInfo']
# 'ipInfo.ip' 'ipInfo.port' 'ipInfo.ptl'+
if tmp:
    if isinstance(tmp.get('ip'), bytes):
        tmp = tmp.get('ip').decode('utf-8')
    proxy = 'http://' + tmp.get('ip') + ':' + str(tmp.get('port'))
    print(proxy, 'run add proxy*****************')


"""
data = ctb.find()
for i in data:
    i.pop('_id')
    a = {'data':i,'time':time.time()}
    stb.insert(a)
"""