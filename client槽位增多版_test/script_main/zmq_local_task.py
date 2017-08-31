#此脚本负责向服务器请求数据和上报数据
#status 状态初始状态0，进入延时队列1，正在执行2，超时3，删除4，完成5
import time,zmq

from excutor_doc import system_info
from client_doc import setting
from pymongo import MongoClient
from gridfs import *
from bson import ObjectId
import copy
class zmq_local_task:


    def __init__(self):
        conn = MongoClient('localhost', 27017, connect=False)
        self.db = conn[setting.DATABASES]#存储任务队列，任务队列，超时队列数据库
        self.save_data = conn[setting.DATA_DB]#保存数据的数据库
        self.fs = GridFS(self.save_data, 'body')  # 存储任务body的大文档，无空间限制

        self.head = {
                     "device":{"type":setting.DEVICE_TYPE,"id":setting.DEVICE_ID,"mac":'',"api_key":''},
                     "command":{"action":'',"version":''},
                     "body":
                         {"taskstats":{"time":time.time(),"status":''},"get_tasks":'',"tasks":'',
                             "data":"","client_status":'',"proxy_data":'',"cookie_data":''
                        }

                     }
        context = zmq.Context()
        self.socket_server1 = context.socket(zmq.REQ)
        self.socket_server1.connect('tcp://%s:%s'%(setting.SERVER_IP,setting.SERVER_PORT))
        self.poll = zmq.Poller()
        self.poll.register(self.socket_server1, zmq.POLLIN)


    def send(self,msg):
        self.socket_server1.send_json(msg)
        while True:  # 服务器中断会一直尝试重连
            socks = dict(self.poll.poll(30000))
            if socks.get(self.socket_server1) == zmq.POLLIN:
                break
            else:
                time.sleep(0.1)
                #print ('重新连接服务器')
                self.socket_server1.setsockopt(zmq.LINGER, 0)
                self.socket_server1.close()
                self.poll.unregister(self.socket_server1)
                context = zmq.Context()
                self.socket_server1 = context.socket(zmq.REQ)
                self.socket_server1.connect('tcp://%s:%s'%(setting.SERVER_IP,setting.SERVER_PORT))
                self.poll.register(self.socket_server1, zmq.POLLIN)
                self.socket_server1.send_json(msg)


    def recv_data(self):
        return self.socket_server1.recv_json()

    def update_task_list(self):# 更新任务列表
        print ('update_list')
        self.head[setting.ROW_BODY]['taskstats']['status'] = []
        self.head['command']['action'] =setting.UPDATE_TASK_LIST #'update_task_list'
        for item in setting.TOPIC:#循环遍历所有任务队列
            count = self.db[setting.TASKS_LIST].find({'topic':item}).count()#得到此类型的任务总个数
            start = time.time()
            complt = self.db[setting.TASKS_LIST].find({setting.ROW_TOPIC:item,'status':5}).count()#记录完成该类型任务完成个数
            run = self.db[setting.TASKS_LIST].find({setting.ROW_TOPIC:item,'status':2}).count()# 得到此类型正在运行的任务个数
            wait = self.db[item+"_ready_list"].count()# 得到该任务就绪队列的总任务个数
            effc =(self.db[setting.TASKS_LIST].find({setting.ROW_TOPIC:item,'status':5}).count()-complt)/(time.time()-start)#得到运行速率,每秒的完成个数为运行速率  完成个数增加量／时间
            self.head[setting.ROW_BODY]['taskstats']['status'].append({setting.ROW_TOPIC:item,'count':count,'wait':wait,"run":run,'complete':complt,'effc':effc})

        self.send(self.head)
        data = self.recv_data() # 将服务器返回的数据转换为字典
        """
        收到服务器端的任务进行解析

        try:
            self.send(self.head)
            data = self.recv_data()#将服务器返回的数据转换为字典
        except:
            pass
        """
        #print ("服务器回复：",data)#得到服务器下发到content tasks 下的任务
        for item in data['content']:#遍历任务列表
            task = item['task']

            if item['action'] == 'add':
                task['time'] = time.time()  # 将添加进来的任务的时间改为当前时间
                print ('add:',task)
                self.db[setting.TASKS_LIST].update(
                    {
                        setting.ROW_TOPIC: task[setting.ROW_TOPIC],
                        setting.ROW_GUID: task[setting.ROW_GUID]
                    },
                   task,
                   True
                )
                #将任务插入总任务列表
            elif item['action'] == 'delete':
                del_task = {setting.ROW_GUID :item['task'][setting.ROW_GUID]}
                print('delete:',del_task)
                self.db[setting.TASKS_LIST].remove(del_task)
                #将任务从总任务列表删除

            elif item['action'] == 'update':#update
                print ('update')
                task['time'] = time.time()  # 将添加进来的任务的时间改为当前时间
                self.db[setting.TASKS_LIST].update({setting.ROW_GUID:item['task'][setting.ROW_GUID]},task, upsert=True)
                #更新总任务列表中任务的属性

    def update_much_taskinfo(self):#批量更新当前任务状态
        print ('update taskinfo')
        #有些任务执行一次就会删除，假如任务状态为4删除状态，是否需要将此任务上传服务器通知服务器删除
        self.head[setting.ROW_BODY]['tasks'] = []
        self.head['command']['action'] = setting.UPDATE_MUCH_TASKINFO
        data = self.db[setting.TASKS_LIST].find({setting.ROW_STATUS:{'$in':[2,4,5]}}).limit(20)#状态是2和5代表任务正在执行和任务完成，正在执行状态的更新是防止超时服务器，
        # 将任务分配给其他客户端，而状态5表示任务执行完成，执行时间被改变上传服务器
        if data.count():
            tmp = copy.copy(data)
            for task in data:
                try:
                    task.pop('_id')
                    # 将任务状态改为1
                    self.head[setting.ROW_BODY]['tasks'].append(task)  # 将任务状态为2和5任务属性变化的数据添加进去
                except:
                    pass
            self.send(self.head)
            data = self.recv_data()  # 将服务器返回的数据转换为字典
            for task in tmp:
                self.db[setting.TASKS_LIST].update(
                    {setting.ROW_GUID: task['guid'], setting.ROW_STATUS: {'$in': [4, 5]}},
                    {'$set': {setting.ROW_STATUS: 0, 'time': (int(task['time']) + int(task['interval']))}})

    def upload_client_data(self):#客户端回报数据
        print('upload_client_data++++')
        #填充数据上传时间
        data_list = []
        data = ''
        try:
            self.head['command']['action'] = setting.UPLOAD_CLIENT_DATA
            data = self.save_data[setting.DATA_TB].find_and_modify(
               query={'upload_flag': 0},update={'$set': {'upload_flag': 0}})

        except Exception as e:
            print ('upload data error',e)
        if data:
            if data['data_lenth_flag']:# 数据大于16m标识
                try:
                    data.pop('_id')
                    obj_id = data['body']  # 得到存储数据的id
                    body = self.fs.get(ObjectId(obj_id)).read()  # 从文档中读出body字段{'result':'',data:''}
                    body = eval(body)  # 还原body
                    data['result'] = body['result']
                    data['data'] = body['data']
                    data['upload_time'] = time.time()  # 上传时间
                    data_list.append(data)  # 将所有数据追加到列表
                    self.head['body']['data'] = data_list  # 将上传数据添加到该字段
                    self.send(self.head)
                    ret = self.recv_data()  # 将服务器返回的数据转换为字典
                    print(ret, 'upload*************')
                    data = self.save_data[setting.DATA_TB].find_and_modify(
                        query={'guid': data['guid'], 'topic': data['topic']}, update={'$set': {'upload_flag': 1}})
                    #发送到服务器只有收到回应以后才进行更改上传状态
                    obj_id = data['body']  # 得到存储数据的id
                    self.fs.delete(ObjectId(obj_id)) #将body从文档中删除
                except Exception as e:
                    data = self.save_data[setting.DATA_TB].find_and_modify(
                        query={'guid': data['guid'], 'topic': data['topic']}, update={'$set': {'upload_flag': 1}})
                    print('上传大于16M数据报错',e)

            else:#小于16m的数据
                try:
                    data.pop('_id')
                    data['upload_time'] = time.time()  # 上传时间
                    data_list.append(data)  # 将所有数据追加到列表
                    self.head['body']['data'] = data_list  # 将上传数据添加到该字段
                    self.send(self.head)
                    ret = self.recv_data()  # 将服务器返回的数据转换为字典
                    self.save_data[setting.DATA_TB].find_and_modify(
                        query={'guid': data['guid'], 'topic': data['topic']}, update={'$set': {'upload_flag': 1}})
                    print(ret, 'upload*************')
                except Exception as e:
                    print ('上传小于16M数据出错',e)

    def upload_client_status(self):#客户端上传状态 主要是cpu 等硬件信息的上传。
        self.head['command']['action'] = setting.UPLOAD_CLIENT_STATUS

        sysinfo = system_info.system_info()#设备信息函数

        self.head[setting.ROW_BODY]['client_status'] = {'sysinfo':sysinfo,'time':time.time()}#系统信息，和获取信息时间
        print ("cpu*******",self.head[setting.ROW_BODY]['client_status'])
        try:
            self.send(self.head)
            data = self.recv_data()  # 将服务器返回的数据转换为字典
            #print("上传cpu信息的回复：", data)  # 得到服务器的回复
        except:
            pass


    def update_proxy_data(self):#更新代理数据
        self.head['command']['action'] = setting.UPDATE_PROXY_DATA
        try:
            self.head['body']['proxy_data'] = [{'ip':'','port':'','type':'','url':''},{}] #上报代理数据type代表http/https,url指用于的平台
            self.send(self.head)
            data = self.recv_data()  # 将服务器返回的数据转换为字典
            #print(data)  # 得到服务器的回复
        except:
            pass
    def update_cookie_data(self):#更新cookie数据
        self.head['command']['action'] = setting.UPDATE_COOKIE_DATA
        try:
            self.head['body']['cookie_data'] = {'jd':[{'sid':'','_jdu':'','_jdv':'','_jda':'',},{}],'tianmao':[{},{}]} #上报的cookie数据，以平台为key以cookie列表为value
            self.send(self.head)
            data = self.recv_data()  # 将服务器返回的数据转换为字典
            #print(data)  # 得到服务器的回复
        except:
            pass


    def run(self,task):
        #task['guid'] = 函数名，task['topic'] = local_task
        obj = zmq_local_task()
        getattr(obj,task['guid'])()# 调用对应的服务器交互函数




if __name__ == "__main__":
    obj = zmq_local_task()

    #剔除get_tasks 字段，分配任务个数交由服务器端来决定
    #update_task_list()
    pass