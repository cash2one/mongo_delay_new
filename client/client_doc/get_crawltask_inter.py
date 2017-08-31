#外部抓取器获得抓取任务和上传解析任务接口
import json,time
from flask import Flask,request,Response
from pymongo import  MongoClient
from gridfs import *
from client_doc import setting

app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class crawl_server:
    def __init__(self):
        conn = MongoClient(setting.DATABASES_IP, 27017, connect=False)
        db = conn[setting.CRAWL_TASK_DATA]
        self.tb = db[setting.CRAWL_TASK_TABLE]

        # 存放解析任务的数据库
        # 存储result的文档,大文件的文档
        conn1 = MongoClient(setting.DATABASES_IP, 27017, connect=False)
        dat = conn1[setting.CRAWL_TASK_DATA]
        self.fs = GridFS(dat, setting.CRAWL_TASK_BODY)

        pdb = conn['jame_bd']
        self.ptable = pdb['jame_proxy']


    def db_findandremov(self, topic='JM_Crawl'):  # 只返回查找的第一条数据
        #return await self.tb.find_one({'topic': topic})
        return self.tb.find_and_modify(query={'topic': topic}, remove=True)  # 获取解析任务并从数据表中删除

    def db_delete(self, arg):  # 删除数据
        self.tb.remove(arg)

    def db_insert(self, task):  # 插入数据
        try:
            body = task['body']
            obj_id =self.fs.put(bytes(str(body), encoding='utf-8'))
            task['body'] = str(obj_id)  # 将文档的id存储进去
            a = self.tb.update(
                {

                    'topic': task['topic'],
                },
                task,
                True
            )
        except Exception as e:
            print('Insert Error:',e)

    def get_crawltask(self):#得到抓取任务
        task_list = []
        for _ in range(4):
            task = self.db_findandremov('JM_Crawl')  # 从数据库查找一个抓取任务
            if task:
                task.pop('_id')
                task_list.append(task)
            else:
                time.sleep(0.1)
                break
        return task_list
    def post_parstask(self,task):#处理上传的解析任务
        for item in task:
            self.db_insert(item)#将解析任务插入数据库

    def get_proxy(self,tbobj,count=100):
        proxy_list = []
        for i in range(count):
            proxyip = tbobj.find_and_modify(
                query={'ipInfo.status': 1, 'usetime': {'$lte': (time.time() - 5 * 60)}},
                update={'$set': {'usetime': time.time()}, '$inc': {'ipInfo.count': 1}},
                )  # 'ipInfo.status':1,'usetime':{'$lte':(time.time()-5*60)}

            if proxyip:  # 得到代理
                pass
            else:
                tbobj.update({'ipInfo.status': 4}, {'$set': {'ipInfo.count': 0, 'ipInfo.status': 1}})  # 将状态4的代理更新
                proxyip = tbobj.find_and_modify(
                    query={'ipInfo.status': 1, 'usetime': {'$lte': (time.time() - 5 * 60)}},
                    update={'$set': {'usetime': time.time()}, '$inc': {'ipInfo.count': 1}},
                )  # 'ipInfo.status':1,'usetime':{'$lte':(time.time()-5*60)}

            if proxyip:
                try:
                    proxyip.pop('_id')
                    proxy_list.append(proxyip)
                except:
                    pass
            else:
                break
        return proxy_list

    def score_proxy(self):
        pass

obj = crawl_server()

@app.route('/get_crawl', methods=['GET', 'POST'])
def crawl():
    if request.method == 'POST':
        message = request.get_data()
        task_list = obj.get_crawltask()
        return Response(json.dumps(task_list), mimetype='application/json')

@app.route('/post_pars', methods=['GET', 'POST'])
def parsing():
    if request.method == 'POST':
        message = request.get_data()#{'type':'get/send','content':''} type代表抓取器的请求类型，get为得到抓取任务，post是上传解析任务。task为具体的上传任务
        message = json.loads(str(message,encoding='utf8'))
        obj.post_parstask(message)
        #print (message[0]['body']['result'][0]['other'],'*************************-******************-*********get task',)
        return Response('ok', mimetype='application/json')

@app.route('/get_proxy', methods=['GET', 'POST'])
def get_proxy():
    if request.method == 'GET':
        message = request.get_data()#{'type':'get/send','content':''} type代表抓取器的请求类型，get为得到抓取任务，post是上传解析任务。task为具体的上传任务
        proxy_list = obj.get_proxy(obj.ptable)
        return Response(json.dumps(proxy_list), mimetype='application/json')

@app.route('/score_proxy', methods=['GET', 'POST'])
def score_proxy():#为proxy打分
    if request.method == 'GET':
        message = request.get_data()#{'type':'get/send','content':''} type代表抓取器的请求类型，get为得到抓取任务，post是上传解析任务。task为具体的上传任务
        proxy_list = obj.get_proxy(obj.ptable)
        return Response(json.dumps(proxy_list), mimetype='application/json')

def run():
    print ('hello run ')
    app.run(host=setting.CRAWL_EXCUTOR_IP, port=int(setting.CRAWL_EXCUTOR_PORT))#抓取器访问的本地地址

if __name__ =='__main__':
    run()
