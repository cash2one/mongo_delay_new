from pymongo import  MongoClient
import time
time_list = []
conn = MongoClient('192.168.0.210', 27017)
db = conn['jd_comment']
def choice_table(tb):
    return db[tb]

tb = choice_table('comment')
tb1 = choice_table('comment1')
data = tb.find().limit(1000000)
i = 0
for item in data:
    i+=1
    print (i)
    item.pop('_id')
    tb1.insert(item)
