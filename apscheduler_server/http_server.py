#flask版本的webserver

import  setting
import db_oprate#数据库操作模块
import gzip,base64
import time
import json
from flask import Flask,request,Response


app = Flask(__name__)
class server:
    def __init__(self,**arg):
        self.obj_db = db_oprate.collection_db()#数据库操作对象
        self.result = {'success': True, 'error': "error reason", 'content': ''}

    def update_task_list(self,**message):# 更新任务列表
        self.result['content'] = []
        data = message['body']['taskstats']['status']#客户端回报的任务简报，
        # 查看记录超时任务id和任务设备的队列中是否有该设备的超时的任务然后删除
        while True:#最多每次从数据库查找20个删除任务
            recode_tb = self.obj_db.choice_main_table(setting.RECODE_LIST)
            task = self.obj_db.find_modify_remove(recode_tb,{'device_id': message['device']['id']})
            #得到任务的具体内容
            if task:
                task.pop('_id')
                self.result['content'].append({'action': 'delete',"task": task}) #用于通知客户端删除任务
            else:
                break
        #更新下发到该设备的任务状态，如从完成状态改变为可执行状态。如果任务属性变化，如上边的情况会添加到记录队列通知删除，生成新任务新任务
        for item in data:#得到每个类型的任务的简报
            if item['topic'] in setting.DOWN_LOGO['down']:#任务类型 ，类型为down任务
                queued_name = item['topic'] + '_ready_list'  # 表     根据类型拼接到自己类型所在的就绪任务队列
                queued_timeout = item['topic'] + '_timeout_list'#超时队列
                if setting.DOWN_COUNT['down'] > item['count']: #客户端的该类型任务个数.
                    q_out_tb = self.obj_db.choice_main_table(queued_timeout)
                    tmtask_ids = self.obj_db.find_data(q_out_tb,{},setting.DOWN_COUNT['down']- item['count'])
                    for i in tmtask_ids:
                        try:
                            self.obj_db.find_modify_remove(q_out_tb,{'guid': i['guid']})  # 从超时队列中删除该任务ID
                            task_tb = self.obj_db.choice_main_table(setting.TASKS_LIST)
                            task = self.obj_db.find_modify(task_tb,{'guid': i['guid']},{'$set': {'device.id': message['device']['id']}})
                            # 进入总任务列表修改任务所属设备
                            if task:
                                try:
                                    task.pop('_id')
                                    task['status'] = 0
                                    self.result['content'].append({'action': 'add', "task": task})  # 将任务添加到回报数据中
                                except:
                                    pass
                        except Exception as e:
                            print(e,'超时队列更新任务列表出错')
                    if tmtask_ids.count() < setting.DOWN_COUNT['down']- item['count']:
                        q_tb = self.obj_db.choice_main_table(queued_name)
                        task_ids =  self.obj_db.find_data(q_tb,{},setting.DOWN_COUNT['down']- item['count']-tmtask_ids.count())
                        for id in task_ids:
                            try:
                                self.obj_db.find_modify_remove(q_tb, {'guid': id['guid']})
                                task_tb = self.obj_db.choice_main_table(setting.TASKS_LIST)
                                task = self.obj_db.find_modify(task_tb, {'guid': id['guid']},
                                                               {'$set': {'device.id': message['device']['id']}})

                               # 得到任务的具体内容
                                if task:
                                    try:
                                        task.pop('_id')
                                        task['status'] = 0
                                        self.result['content'].append({'action': 'add', "task": task})  # 将任务添加到回报数据中
                                    except:
                                        pass
                            except Exception as e:
                                print(e, '就绪队列更新任务列表出错')

                        #如果服务器端的任务数足够下发任务
                        #下发的任务数为  DOWN_COUNT['down']-  item['count']
                        #下发的任务格式如下：
                        #self.result['content'] = [{"action":"add/delete/update","tasks":{"commmand":{'type':"",'version':'127.22','id':11},'guid':11,'delay':155555,'timeout':60,},'body':{'info':"dsadsdas",'format':'aaaaaaa'}}]
                         #不够的话全部下发
            else:#notdown
                #下发的任务个数应
                if setting.DOWN_COUNT['notdown'] > item['count']: #客户端的该类型任务个数
                    pass
                    #任务个数足够
                    #下发的任务应为 DOWN_COUNT['notdown']- item['count']+item['complete']#客户端至上次回报数据完成的个数
            #item['wait']#就绪队列的任务个数
            #item["run"]#客户端正在运行的个数
            #item['complete']#客户端至上次回报数据完成的个数
            #item['effc']#运行速率
    #制定服务器下发客户端任务的具体情况
    #1.服务器端任务数量满足客户端的某种类型的数量是否下发，如果下发，是达到客户端的要求，还是根据算法自行确定，如果不下发，具体情况
    #2.服务器端任务数量不满足客户端请求的任务量是否下发，若下发下发多少。
    def update_much_taskinfo(self,**message):#批量更新当前任务状态
        self.result = {'success': True, 'error': "error reason", 'content': ''}
        task_tb = self.obj_db.choice_main_table(setting.TASKS_LIST)
        try:
            tasks = message['body']['tasks']#格式为[task1，task2....] 值为任务链表#只更新状态为2和5的
            #print ("批量更新任务状态",tasks)
            for task in tasks:
                #如果上传的任务的设备与服务器所分配的任务设备id一致则接受数据或其他处理，
                tmp = self.obj_db.find_one(task_tb,{'guid':task['guid']})
                if tmp:
                    if message['device']['id'] == tmp['device']['id']:
                        self.obj_db.find_modify(task_tb,{'guid': task['guid'],'topic':task['topic']},{'$set':{'status':task['status']}})
                        #为了安全只支持更改服务器的任务状态
        except Exception as e:
            print(e, '批量更新当前任务状态列表出错')


    def upload_client_data(self, **message):  # 客户端回报数据,客户端的上传数据都为这个接口
        self.result = {'success': True, 'error': "error reason", 'content': ''}
        print ('upload')
        try:
            data = message['body']['data']
            data = base64.b64decode(data)#解码
            data = gzip.decompress(data)#解压
            data = data.decode(encoding='utf-8')
            data = json.loads(data,encoding='utf-8')
            tb = self.obj_db.chocie_db_tb(setting.TMP_DB, setting.TMP_TB)#数据同一插入临时表
            for item in data:
                if item['data_lenth_flag']:  # 数据大于16m
                    grif = {'result': '', 'data': ''}
                    try:
                        """得到的抓取数据中的result,data字段存放在gridfs中"""
                        grif['result'] = item['result']  # 抓取的url必要信息
                        grif['data'] = item['data']  # 解析数据的必要信息
                        obj_id = self.obj_db.gridfs_put_data(grif)
                        item['result'] = ''
                        item['data'] = ''
                        item['body'] = str(obj_id)  # 将文档的id存储到body中
                        self.obj_db.insert_data(tb,item)# 将数据插入数据库
                    except Exception as e:
                        print('保存大于16m上传数据出错', e)
                else:  # 数据小于16m
                    try:
                        self.obj_db.insert_data(tb, item)  # 将数据插入数据库
                    except Exception as e:
                        print('保存小于16m的上传数据出错', e)
        except Exception as e:
            print ('数据上传出错',e)
        #data = gzip.decompress(data)
        # 根据guid得到任务，根据任务属性确定任务的存储的具体数据库和数据表
        # 上传的数据格式{'gudi':{'format':'','data':''}}format 压缩格式。data数据，guid 任务ID
        # 判断上传数据的数据类型，存储到不同的数据库中
        # 得到客户端回报的数据，写入数据库
        #data = gzip.decompress(data)
        """
        db = self.conn[setting.TMP_DB]
        tb = db[setting.TMP_TB]
        tb.insert(data)
        # 如果上传的任务的设备与服务器所分配的任务设备id一致则接受数据或其他处理，
        # 考虑上传数据间隔的问题，上传设备与任务设备不同，也会考虑接受数据
        """

    def upload_client_status(self, **message):  # 客户端上传状态主要是cpu和硬件信息的上报
        self.result = {'success': True, 'error': "error reason", 'content': ''}
        try:
            system_data = message['body']['client_status']
            sys_info = system_data['sysinfo']  # 客户端的详细硬件信息
            time = system_data['time']  # 客户端获取硬件信息的时间
            device_id = message['device']['id']  # 设备id
            cpu_tb= self.obj_db.choice_main_table(setting.CLIENT_CPU_DATA)
            self.obj_db.insert_data(cpu_tb,{'time': time, 'system_info': sys_info, 'device_id': device_id})
            # 将数据存储，上传的数据格式{'sysinfo':{},'time':time.time()}id代表设备id,{}中携带的是客户端的硬件信息
            print("设备信息：", system_data)
        except:
            pass
    def update_proxy_data(self, **message):  # 更新代理数据
        self.result = {'success': True, 'error': "error reason", 'content': []}
        proxy_list = message['body']['proxy_data']#得到代理数据
        nowtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()-setting.CHECK_PROXY_TIME))
        #服务器获取最近一个小时的代理下发客户端
        try:
            tb = self.obj_db.chocie_db_tb(setting.TMP_DB, 'jm_task_proxyverificate')
            #进入存储代理的数据表
            proxy_list =self.obj_db.find_data(tb,{'data.ipInfo.status':1,'data.ipInfo.task.verifi.www_baidu_com.lastTime':{'$gte':nowtime}},1000)#第三个参数为获取个数,'$lte':time.time()
            #获取当前时间前几个小时验证过的代理
            for proxy in proxy_list:
                self.result['content'].append(proxy['data'])#将上传代理的data字段下发到客户端
        except Exception as e:
            print ('下发代理出现异常',e)

    def update_cookie_data(self, **message):  # 更新cookie数据
        self.result = {'success': True, 'error': "error reason", 'content': ''}
        # message['body']['cookie_data']
        pass

def run():
    app.run(host=setting.SERVER_IP, port=int(setting.SERVER_PORT))



@app.route('/',methods=['GET','POST'])
def index():
    if request.method =='POST':
        message = request.get_json()#客户端提交数据是以form表单的形式提交，{'content':对应客户端上传的数据}\
        obj = server()
        ret = getattr(obj, message['command']['action'])  # 获取的是个对象
        ret(**message)
        return Response(json.dumps(obj.result), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)


