
import uuid,time
from pymongo import MongoClient
class create_task:
    def __init__(self):
        conn = MongoClient('localhost', 27017, connect=False)
        db = conn['jame_bd']  # 存储任务队列，任务队列，超时队列数据库
        self.tb = db['task_main']


    def jd_task_ad_product(self,sku=13860081643,platform='jd_app'):#生成广告位任务
        guid = str(uuid.uuid1())
        task = {
                'device': {'type': '', 'version': '127.22', 'id': ''},
                'guid': guid,
                'time': time.time(),  # time.time(),
                'timeout': 60,#任务执行超时时间，从执行到完成的时间，超时则退出执行
                'topic': 'jd_task_ad_product',
                'interval': 86400,  # 任务执行周期间隔时间
                'suspend': 0,  # 暂停标识
                'status': 0,
                'body': {
                    'sku':sku, 'platform': platform,
                }
                }

        return task

    def jd_task_ad_kind(self,kind='9987,830,13658',platform='jd_app',position='center'):  #
        guid = str(uuid.uuid1())
        task = {
            'device': {'type': '', 'version': '127.22', 'id': ''},
            'guid': guid,
            'time': time.time(),  # ,
            'timeout': 60,  # 任务执行超时时间，从执行到完成的时间，超时则退出执行
            'topic': 'jd_task_ad_kind',
            'interval': 86400,  # 任务执行周期间隔时间
            'suspend': 0,  # 暂停标识
            'status': 0,
            'body': {
                'kind': kind, 'platform': platform,'url':{'position':position}
            }

        }

        return task

    def jd_task_ad_keyword(self,sort='',platform= 'jd_app', keyword ='防摔手机壳'):
        guid = str(uuid.uuid1())
        task = {
            'device': {'type': '', 'version': '127.22', 'id': ''},
            'guid': guid,
            'time': time.time(),  # time.time(),
            'timeout': 60,  # 任务执行超时时间，从执行到完成的时间，超时则退出执行
            'topic': 'jd_task_ad_keyword',
            'interval': 86400,  # 任务执行周期间隔时间
            'suspend': 0,  # 暂停标识
            'status': 0,
            'body': {
               'platform': platform, 'keyword':{'urlCoding':keyword,},'sort':sort
            }

        }
        return task
    def insert_db(self,task):
        self.tb.insert(task)



if __name__ =='__main__':
    obj = create_task()
    task = obj.jd_task_ad_product()
    obj.insert_db(task)
