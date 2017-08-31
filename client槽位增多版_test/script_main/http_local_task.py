import gzip,requests,json,time,base64
from excutor_doc import system_info,db_oprate
from client_doc import setting

import copy
class http_local_task:
    def __init__(self,**arg):
        self.head = {
            "device": {"type": setting.DEVICE_TYPE, "id": setting.DEVICE_ID, "mac": '', "api_key": ''},
            "command": {"action": '', "version": ''},
            "body":
                {"taskstats": {"time": time.time(), "status": ''}, "get_tasks": '', "tasks": '',
                 "data": "", "client_status": '', "proxy_data": '', "cookie_data": ''
                 }

        }

        self.db_obj = db_oprate.collection_db()#操作数据库对象


    def update_task_list(self):# 更新任务列表
        task_tb = self.db_obj.choice_task_table()#切换到存储任务的数据表
        #print ('update_list')
        self.head[setting.ROW_BODY]['taskstats']['status'] = []
        self.head['command']['action'] =setting.UPDATE_TASK_LIST #'update_task_list'
        for item in setting.TOPIC:#循环遍历所有任务队列
            count =self.db_obj.find_data_count(task_tb,{'topic':item})#得到此类型的任务总个数
            complt =self.db_obj.find_data_count(task_tb,{setting.ROW_TOPIC:item,'status':setting.STATUS_FINISH})#记录完成该类型任务完成个数
            run = self.db_obj.find_data_count(task_tb,{setting.ROW_TOPIC:item,'status':setting.STATUS_EXCUTING})# 得到此类型正在运行的任务个数
            wait = self.db_obj.get_tb_count(self.db_obj.choice_table(item+"_ready_list"))# 得到该任务就绪队列的总任务个数
            effc =complt/(setting.UPDATE_TASK_LIST_TIME-setting.UPDATE_MUCH_TASKINFO_TIME)#得到运行速率,每秒的完成个数为运行速率  完成个数增加量／时间
            self.head[setting.ROW_BODY]['taskstats']['status'].append({setting.ROW_TOPIC:item,'count':count,'wait':wait,"run":run,'complete':complt,'effc':effc})
        recv_data  = self.send_data()
        if not recv_data:
            return

        try:
            for item in recv_data['content']:#遍历任务列表
                task = item['task']
                if item['action'] == 'add':
                    task['time'] = time.time() #将添加进来的任务的时间改为当前时间
                    print ('add:',task)
                    self.db_obj.update_data(task_tb,task)
                    #将任务插入总任务列表
                elif item['action'] == 'delete':
                    del_task = {setting.ROW_GUID :item['task'][setting.ROW_GUID]}
                    print('delete:',del_task)
                    self.db_obj.del_data(task_tb,del_task)
                    #将任务从总任务列表删除
                elif item['action'] == 'update':#update
                    print ('update')
                    task['time'] = time.time()  # 将添加进来的任务的时间改为当前时间
                    self.db_obj.update_data(task_tb, task)
                    #更新总任务列表中任务的属性
        except Exception as e:
            print (e)

    def update_much_taskinfo(self):#批量更新当前任务状态
        tmp_list = []
        task_tb = self.db_obj.choice_task_table()  # 切换到存储任务的数据表
        #有些任务执行一次就会删除，假如任务状态为4删除状态，是否需要将此任务上传服务器通知服务器删除
        self.head[setting.ROW_BODY]['tasks'] = []
        self.head['command']['action'] = setting.UPDATE_MUCH_TASKINFO
        data = self.db_obj.find_data(task_tb,{setting.ROW_STATUS:{'$in':[setting.STATUS_DELETED,setting.STATUS_FINISH]}},10)

       #状态是2和5代表任务正在执行和任务完成，正在执行状态的更新是防止超时服务器，
        # 将任务分配给其他客户端，而状态5表示任务执行完成，执行时间被改变上传服务器
        if data.count():
            for task in data:
                try:
                    task.pop('_id')
                    # 将任务状态改为0
                    self.head[setting.ROW_BODY]['tasks'].append(task) #将任务状态为4和5任务属性变化的数据添加进去
                    tmp_list.append(task)
                except:
                    pass
            recv_data  = self.send_data()
            if not recv_data:
                return
            for task in tmp_list:
                self.db_obj.update_clx_data(task_tb,{setting.ROW_GUID: task['guid'], setting.ROW_STATUS: {'$in': [setting.STATUS_DELETED,setting.STATUS_FINISH]}},
                                            {'$set': {setting.ROW_STATUS: 0,'time': (int(task[setting.ROW_TIME]) + int(task[setting.ROW_INTERVAL]))}})

            print('批量更新当前任务状态')


    def upload_client_data(self):  # 客户端回报数据
        try:
            data_tb =  self.db_obj.choice_data_table()#切换到存储数据表
            # 填充数据上传时间
            data_list = []
            tmp_list = []
            tmp_list1= []
            self.head['command']['action'] = setting.UPLOAD_CLIENT_DATA
            tmp_list = self.db_obj.find_data(data_tb, {'upload_flag': 0}, 5)
            if not tmp_list.count():#没有数据
                return
            for data in tmp_list:
                tmp_list1.append(copy.deepcopy(data))
                if data['data_lenth_flag']:# 数据大于16m标识
                    data.pop('_id')
                    obj_id = data['body'] #得到存储数据的id
                    body =self.db_obj.gridfs_get_data(obj_id)  # 从文档中读出body字段{'result':'',data:''}
                    body = eval(body)  # 还原body
                    data['result'] = body['result']
                    data['data'] = body['data']
                    data['upload_time'] = time.time()#上传时间
                    data_list.append(data)  # 将所有数据追加到列表
                else:#小于16m的数据
                    data.pop('_id')
                    data['upload_time'] = time.time()  # 上传时间
                    data_list.append(data)  # 将所有数据追加到列表
            tmp = bytes(json.dumps(data_list), encoding='utf-8')
            tmp = base64.b64encode(gzip.compress(tmp))
            tmp = str(tmp, encoding='utf-8').replace('\n', '')
            self.head['body']['data'] = tmp  # 将上传数据添加到该字段
            recv_data = self.send_data()  # 将数据发送
            if not recv_data:
                return
            for data1 in tmp_list1:
                #print (data1['_id'])
                # 确认上传成功才将上传状态改变
                # 如果客户端不留存上传记录的话，上传成功删除数据
                if setting.UPLOAD_DATA_MODO == setting.UPLOAD_SAVE_MODO:
                    # 更新upload_falg状态是要留存记录
                    self.db_obj.find_modify(data_tb, {'_id': data1['_id']}, {'$set': {'upload_flag': 1}})

                elif setting.UPLOAD_DATA_MODO == setting.UPLOAD_CLEAR_MODO:
                    # 不留存记录直接将上传成功的数据删除
                    self.db_obj.find_modify_remove(data_tb, {'_id':data1['_id']})
                    if data1['data_lenth_flag']:  # 数据大于16m标识
                        obj_id = data1['body']  # 得到存储数据的id
                        self.db_obj.gridfs_del_data(obj_id)  # 删除data_tb 中关联的gridfs
        except Exception as e:
            print ('upload_client_data!!!',e)


    def upload_client_status(self):  # 客户端上传状态 主要是cpu 等硬件信息的上传。
        #print ('upload_client_status')
        self.head['command']['action'] = setting.UPLOAD_CLIENT_STATUS
        sysinfo = system_info.system_info()  # 设备信息函数
        self.head[setting.ROW_BODY]['client_status'] = {'sysinfo': sysinfo, 'time': time.time()}  # 系统信息，和获取信息时间
        print("cpu*******", self.head[setting.ROW_BODY]['client_status'])
        try:
            recv_data = self.send_data()
            if not recv_data:
                return
            print("上传cpu信息的回复：",recv_data)  # 得到服务器的回复
        except Exception as e:
            print ('客户端上传状态',e)

    def update_proxy_data(self):  # 更新代理数据
        #print ('update_proxy_data')
        self.head['command']['action'] = setting.UPDATE_PROXY_DATA
        try:
            self.head['body']['proxy_data'] = [{'ip': '', 'port': '', 'type': '', 'url': ''},
                                               {}]  # 上报代理数据type代表http/https,url指用于的平台
            recv_data = self.send_data()
            if not recv_data:
                return
            proxy_list = recv_data['content']#代理列表
            proxy_tb = self.db_obj.choice_table('jame_proxy') #切换到存储代理表
            for proxy in proxy_list:
                self.db_obj.update_term_data(proxy_tb,{'ipInfo.ip':proxy['ipInfo']['ip'],'ipInfo.port':proxy['ipInfo']['port']},proxy)#将代理数据插入数据库

          # 将服务器返回的数据转换为字典
            #print(recv_data)  # 得到服务器的回复
        except Exception as e:
            print('更新代理数据',e)

    def update_cookie_data(self):  # 更新cookie数据
        #print ('update_cookie_data')
        self.head['command']['action'] = setting.UPDATE_COOKIE_DATA
        try:
            self.head['body']['cookie_data'] = {'jd': [{'sid': '', '_jdu': '', '_jdv': '', '_jda': '', }, {}],
                                                'tianmao': [{}, {}]}  # 上报的cookie数据，以平台为key以cookie列表为value
            recv_data = self.send_data()
            if not recv_data:
                return
             # 将服务器返回的数据转换为字典
            # print(recv_data)  # 得到服务器的回复
        except Exception as e:
            print ('更新cookie数据',e)

    def run(self, task):
        #print ('run',task['guid'])
        # task['guid'] = 函数名，task['topic'] = local_task
        obj = http_local_task()
        getattr(obj, task['guid'])()  # 调用对应的服务器交互函数

    def send_data(self):#发送数据接口，返回服务器的回复，通信正确返回的是一个字典
        try:
            text = requests.post("http://%s:%s/"%(setting.SERVER_IP,setting.SERVER_PORT), json=self.head,headers = {'content-type':
'application/json'},timeout = 60)
            #print (text.status_code,'*******服务器返回码')
            if text.status_code == 200:
                return json.loads(text.text)
            else:
                return
        except:
            print (self.head['command']['action'],'无法连接服务器或者数据异常')
            return




if __name__ == '__main__':
    obj = http_local_task()
    obj.upload_client_data()