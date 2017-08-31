from pymongo import  MongoClient
from gridfs import *
from bson import ObjectId
import json

conn = MongoClient('localhost', 27017)
db = conn['tmp_db']
fs = GridFS(db, 'body')  # 存储任务body的大文档，无空间限制

def choice_table(tb):
    return db[tb]

j = 0
tb = choice_table('tmp_tb')
data_sum = tb.find({'topic':'jd_task_kind'})
for data in data_sum:
    for i in data['data']:
        if i['order']:
            print ( i['order'])
            j +=1
    if j > 1:
        f = open('jd_task.txt','w+')
        data.pop('_id')
        f.write(json.dumps(data))
        break
print (data)