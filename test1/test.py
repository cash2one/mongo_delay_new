from pymongo import  MongoClient
import copy
conn = MongoClient('localhost', 27017)
db = conn['jame_bd']

def choice_table(tb):
    return db[tb]

tb = choice_table('task_main')
tmp = []
data_sum = tb.find()
for i in data_sum:
    tmp.append(i)

print (tmp)
