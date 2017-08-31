
from pymongo import  MongoClient
import setting
import time
conn = MongoClient('localhost', 27017, connect=False)
db = conn[setting.DATABASES]
tb = db[setting.TASKS_LIST]

def insert_localtask():# 添加与服务器交互的本地任务，guid是函数名，topic是local_task
    for item,topic in enumerate(setting.REQUEST_SERVER_LIST):
        print('insert',topic)
        task = {"device":{'type': "", 'version': '127.22', 'id': ''},
                'guid':topic, 'time': time.time(), 'timeout':0, 'topic':'local_task',
                'interval':setting.REQUEST_SERVER_TIME[item],  # 从配置文件读出本地任务周期时间
                'suspend': 0,  # 暂停标识
                'status': 0,
                'body': ''

                }
        tb.update(
            {'guid':topic,'topic':'local_task'},
            task,
            True
        )


insert_localtask()