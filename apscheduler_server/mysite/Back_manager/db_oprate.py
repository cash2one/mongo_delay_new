#封装数据库操作

from pymongo import MongoClient
from gridfs import *
from bson import ObjectId
from apscheduler_server import setting#将平台服务的seeting文件导入
class collection_db:
    def __init__(self):
        self.conn = MongoClient(setting.DATABASES_IP, 27017, connect=False)
        self.db = self.conn[setting.DATABASES]  # 存储任务队列，任务队列，超时队列数据库
        self.save_data = self.conn[setting.TMP_DB]  # 保存数据的数据库
        self.fs = GridFS(self.save_data, 'body')  # 存储任务body的大文档，无空间限制


    def chocie_db_tb(self,db,tb):#切换到指定数据库中的指定表
        return self.conn[db][tb]#切换到表


    def choice_main_table(self,tb):#切换总任务库下
        return self.db[tb]

    def get_tb_count(self,tb):#得到数据表的数据个数
        return tb.count()
    def get_data_count(self,tb,query):
        return tb.find(query).count()
    def del_data(self, tb, data): # 删除数据
        tb.remove(data)

    def choice_data_table(self,tb):#切换到存储上传数据的数据库
        return self.save_data[tb]

    def find_modify(self,tb,query,update,upsert=False):#原子性操作
        return tb.find_and_modify(
                query=query, update=update,upsert=upsert)

    def update_clx_data(self, tb, query, update):  # 提供条件更新数据
        ret = tb.update(
            query,
            update,

        )
        return ret

    def update_term_data(self, tb, query, update):  # 更改数据，根据条件，有则更新，没有则插入
        ret = tb.update(
            query,
            update,
            True
        )
        return ret

    def much_update_data(self,tb,query,update):#批量更新
        ret = tb.update(
            query,
            update,
            multi=True
        )
        return ret
    def find_modify_remove(self, tb, query={}):  # 原子性操作，得到并删除
        return tb.find_and_modify(
            query=query, remove=True)

    def find_data(self, tb, data, limit=0):  # 查找数据,可以指定得到前几行
        return tb.find(data).limit(limit)

    def obj_distinct(self,obj,query):#查找的数据对象去重
        return obj.distinct(query)
    def find_one(self,tb,query={}):
        return tb.find_one(query)
    def skip_data_limit(self,tb,query={},skip=0,limit=0):#跳过几行，取几条数据，用于分页
        return tb.find(query).skip(skip).limit(limit)
    def insert_data(self, tb, data):  # 插入数据库
        tb.insert(data)


    def create_com_index(self,tb,filed):#表建立普通索引
        tb.create_index(filed,unique=False)

    def create_union_index(self,tb,list):#表建立联合唯一索引
        tb.create_index(list,unique=True)

    def gridfs_put_data(self, data):  # 添加grdfis部分
        return self.fs.put(bytes(str(data), encoding='utf-8'))

    def gridfs_get_data(self, obj_id):  # 得到上传数据的gridfs部分
        return self.fs.get(ObjectId(obj_id)).read()