#该脚本是对数据操作的封装

from pymongo import MongoClient
from gridfs import *
from bson import ObjectId
from client_doc import setting


#为客户端的任务表和就绪表添加必要的索引
conn = MongoClient(setting.DATABASES_IP, 27017, connect=False)
db = conn[setting.DATABASES]  # 存储任务队列，任务队列数据库
tb = db[setting.TASKS_LIST]
#为总任务列表建立guid的索引，和guid,topic的联合索引
tb.create_index(setting.ROW_GUID, unique=False)
tb.create_index([(setting.ROW_GUID, DESCENDING), (setting.ROW_TOPIC, DESCENDING)])#

#为就绪任务列表建立guid的索引，和guid,topic的联合索引
for topic in setting.TOPIC:
    db[topic + setting.READY_LIST].create_index(setting.ROW_GUID, unique=False)
    db[topic + setting.READY_LIST].create_index([(setting.ROW_GUID, DESCENDING), (setting.ROW_TOPIC, DESCENDING)])#为就绪链表创建联合唯一索引


class collection_db:
    def __init__(self):
        conn = MongoClient(setting.DATABASES_IP, 27017, connect=False)
        self.db = conn[setting.DATABASES]  # 存储任务队列，任务队列，超时队列数据库
        self.save_data = conn[setting.DATA_DB]  # 保存数据的数据库
        self.fs = GridFS(self.save_data, 'body')  # 存储任务body的大文档，无空间限制

        db = conn[setting.CRAWL_TASK_DATA]
        self.crawl_tb = db[setting.CRAWL_TASK_TABLE]#存储
        self.fs_crawl = GridFS(db, setting.CRAWL_TASK_BODY)  # 存储抓取后结果任务body的大文档，无空间限制，起中转作用

    def choice_table(self,tb):#切换到就绪列表
        return self.db[tb]

    def get_tb_count(self,tb):#得到数据表的数据个数
        return tb.count()


    def choice_crawl_table(self):#切换到抓取表中
        return self.crawl_tb


    def choice_data_table(self):#切换到存储上传数据的数据库
        return self.save_data[setting.DATA_TB]

    def choice_task_table(self):#切换存储任务的数据库
        return self.db[setting.TASKS_LIST]

    def get_ready_count(self,ready_name):#得到就绪任务个数
        return self.db[ready_name].count()

    def insert_data(self,tb,data):#插入数据库
        tb.insert(data)

    def del_data(self,tb,data):#删除数据
        tb.remove(data)
    def update_data(self,tb,data):#更改数据，有则更新没有则添加
        ret = tb.update(
            {
                setting.ROW_TOPIC: data[setting.ROW_TOPIC],
                setting.ROW_GUID: data[setting.ROW_GUID],
            },
            data,
            True
        )
        return ret
    def update_clx_data(self,tb,query,update):#提供条件更新数据
        ret = tb.update(
            query,
            update,
        )
        return ret

    def much_update_data(self,tb,query,update):#批量更新
        ret = tb.update(
            query,
            update,
            multi=True
        )
        return ret

    def update_term_data(self, tb,query,update): # 更改数据，根据条件，有则更新，没有则插入
        ret = tb.update(
            query,
            update,
            True
        )
        return ret


    def find_one(self,tb,query):
        return tb.find_one(query)

    def find_data(self,tb,data,limit=0):#查找数据,可以指定得到前几行
        return tb.find(data).limit(limit)

    def find_modify(self,tb,query,update,upsert=False):#原子性操作
        return tb.find_and_modify(
                query=query, update=update,upsert=upsert)

    def find_modify_remove(self,tb,query):#原子性操作，得到并删除
        return tb.find_and_modify(
                query=query, remove = True)

    def find_data_count(self,tb,data={}):#得到查找数据的个数
        return  tb.find(data).count()

    def gridfs_put_data(self,data):#添加grdfis部分
        return self.fs.put(bytes(str(data), encoding='utf-8'))

    def gridfs_get_data(self,obj_id):#得到上传数据的gridfs部分
        return self.fs.get(ObjectId(obj_id)).read()

    def gridfs_del_data(self,obj_id):#gridfs删除数据
        self.fs.delete(ObjectId(obj_id))

    def gridfs_get_crawldata(self,obj_id):#得到抓取任务
        return self.fs_crawl.get(ObjectId(obj_id)).read()

    def gridfs_del_crawldata(self,obj_id):#得到抓取任务
        self.fs_crawl.delete(ObjectId(obj_id))

    def gridfs_put_crawldata(self,data):  # 得到上传数据的gridfs部分
        return self.fs_crawl.put(bytes(str(data), encoding='utf-8'))

if __name__ == '__main__':
    obj = collection_db()
    a = obj.choice_data_table()