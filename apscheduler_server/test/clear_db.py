from pymongo import MongoClient

conn = MongoClient('localhost', 27017, connect=False)
db = conn['data_db']  # 存储任务队列，任务队列数据库
tb = db['data_tb']

ret = tb.update(
    {'upload_flag':1},
    {'$set':{'upload_flag':0}},
    multi=True
)