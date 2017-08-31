#为客户端使用的关键数据表的关键字段建立索引，提升性能。第一次在设备上运行或者客户端增加任务类型时运行

from client_doc import setting
from pymongo import MongoClient,DESCENDING,ASCENDING
conn = MongoClient('localhost', 27017, connect=False)
db = conn['jame_bd']  # 存储任务队列，任务队列数据库
tb = db['task_main']
#为总任务列表建立guid的索引，和guid,topic的联合索引
tb.create_index('guid', unique=False)
tb.create_index([("guid", DESCENDING), ("topic", DESCENDING)])#

#为就绪任务列表建立guid的索引，和guid,topic的联合索引
for topic in setting.TOPIC:
    db[topic + '_ready_list'].create_index('guid', unique=False)
    db[topic + '_ready_list'].create_index([("guid", DESCENDING), ("topic", DESCENDING)])#为就绪链表创建联合唯一索引

