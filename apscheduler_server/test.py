from pymongo import  MongoClient
from gridfs import *
from bson import ObjectId
import json,time
import setting

conn = MongoClient('192.168.0.210', 27017)
db = conn['tmp_db']
fs = GridFS(db, 'body')  # 存储任务body的大文档，无空间限制

def choice_table(tb):
    return db[tb]

j = 0
tb = choice_table('jm_task_proxyverificate')
data_sum = tb.find_one()
id = data_sum['_id']
print (id,type(id))
str_r = ObjectId(id)
print (str_r,type(str_r))


