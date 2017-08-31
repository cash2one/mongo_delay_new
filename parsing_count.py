#查看得到解析数据的个数
from pymongo import  MongoClient
from gridfs import *
from bson import ObjectId
import json

conn = MongoClient('localhost', 27017)
db = conn['data_db']
fs = GridFS(db, 'body')  # 存储任务body的大文档，无空间限制

def choice_table(tb):
    return db[tb]

j = 0
tb = choice_table('data_tb')
data_sum = tb.find({'topic':'jd_task_kind'})
for data in data_sum:
    for i in data['data']:
        if i['order']:
            if i['order'] == ['']:
                continue
            print ( i['order'])
            j +=1

print ('order:',j)

n =0
for data in data_sum:
    for i in data['result']:
        for m in i:
            if m['html'] != 'error':
                n +=1

print ('parsing sucess:',n)