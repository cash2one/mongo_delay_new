#使用多进程
#使生产者和消费者同步进行
#task_time 负责扫描就绪队列
#task_cute负责执行就绪队列的任务
import multiprocessing,os,time

import pull_script#自动从服务器获取脚本




#开启抓取器进程个数,默认并发100，默认抓取超时3s,重试5次，最坏的情况是15s抓取100url
#如果追求最大效率 开启的调用脚本的进程数 = 抓取器的进程个数  ，这样的话可以保证每个进程的任务都可以同一时间得到执行。
#每个任务的运行时间：最大运行时间 task*url/100*15


class check_connect_status:
    def __init__(self):
        self.connect_server_process = ''
        self.db_obj = db_oprate.collection_db()  # 操作数据库对象

    def select_table(self, table):  # 查表，并删除第一个查询到的数据
        tb = self.db_obj.choice_table(table)  # 切换就绪表
        data = self.db_obj.find_modify_remove(tb, {})
        return data


    def get_check_task(self):#如果有检查任务代表需要检查客户端与服务器的交互就绪任务列表，如果就绪列表在个数大于某个数不减少，则认为断链
        topic = 'local_check_task'
        queued_name = topic + '_ready_list'  # 表   根据类型拼接到自己类型所在的就绪任务队列
        while True:
            try:
                data = self.select_table(queued_name)  # 得到任务，实际上的真实数据为任务id，并且将就绪列表的id删除
                if data:
                    try:
                        task_tb = self.db_obj.choice_task_table()
                        result = self.db_obj.find_one(task_tb,{'guid': data['guid']})#查找到任务
                        print (result)
                        self.db_obj.find_modify(task_tb,{'guid': data['guid']},{'$set': {'status': 0,
                                                                                     'time': int(time.time()) + int(
                                                                                         result['interval'])}})

                    except Exception as e:
                        print (e,'main_fun 41line')
                    local_tb = self.db_obj.choice_table(setting.LOCAL_TASK_TYPE+'_ready_list')#切换到本地就绪表
                    return self.db_obj.find_data_count(local_tb)#得到本地与服务器交互的本地任务列表数
                else:
                    time.sleep(1)
            except:
                pass


    def kill_process_by_name(self,name):#杀死进程的方法
        cmd = "ps -e | grep %s" % name
        f = os.popen(cmd)
        txt = f.readlines()
        print (txt)
        if len(txt) == 0:
            print ("no process \"%s\"!!" % name)
            return
        else:
           for line in txt:
               colum = line.split()
               pid = colum[0]
               cmd = "kill -9 %d" % int(pid)
               rc = os.system(cmd)
               if rc == 0 :
                   print ("exec \"%s\" success!!" % cmd)
               else:
                   print ("exec \"%s\" failed!!" % cmd)
        return


    def process(self):# 开启客户端的必要进程
        self.process_list = []
        self.connect_server_process =multiprocessing.Process(target=scan_process.run)
        self.process_list.append(self.connect_server_process)  # 得到就绪任务然后调用相应的脚本

        if setting.CRAWL_EXCUTOR_MODE == setting.PYTHON_CRAWL_EXCUTOR:#选用本地python抓取器
            for _ in range(setting.CATCHER_COUNT):
                self.process_list.append(multiprocessing.Process(target=excutor_main.catcher))  #调用本地python执行器
        elif setting.CRAWL_EXCUTOR_MODE == setting.GO_CRAWL_EXCUTOR:#选用本地go抓取器
            self.process_list.append(multiprocessing.Process(target=get_crawltask_inter.run)) #调用go执行器相关的webserver

        for process in self.process_list:
            process.start()


    def scan_process(self):
        doc = os.getcwd()
        doc = os.path.join(doc, 'client_doc')
        delay_path = os.path.join(doc, 'delay_queue.py')
        os.system('nohup %s %s jm_process >/dev/null 2>&1 &' % ('python3.5', delay_path))  # 扫描进程

    def update_local_task(self):#更新本地与服务器交互的任务状态
        for item, topic in enumerate(setting.REQUEST_SERVER_LIST):
            print('insert', topic)
            task = {"device": {'type': "", 'version': '127.22', 'id': ''},
                    'guid': topic, 'time': time.time(), 'timeout': 0, 'topic':setting.LOCAL_TASK_TYPE,
                    'interval': setting.REQUEST_SERVER_TIME[item],  # 从配置文件读出本地任务周期时间
                    'suspend': 0,  # 暂停标识
                    'status': 0,
                    'body': ''
                    }
            task_tb = self.db_obj.choice_task_table()
            self.db_obj.update_data(task_tb,task)

    def zmq_run(self):
        self.process()#开启必要进程
        self.scan_process()
        time.sleep(30)#防止客户端没有清空保存与服务器通信的就绪列表，本地检查任务误判重启，等待一段时间消费掉就绪列表的任务
        while True:
            task_count = self.get_check_task() #获取与服务器交互的任务个数
            if task_count >=2:
                print ('和服务器失去连接')
                for item in self.process_list:
                    item.terminate()#杀死进程
                    item.join()
                    print (item,len(self.process_list))
                    print ('进程',item.is_alive())
                self.update_local_task()
                self.process()#重新启动客户端
            else:
                time.sleep(1)

    def http_run(self):
        self.scan_process()
        self.process()  # 开启必要进程
        time.sleep(30)
        while True:
            task_count = self.get_check_task() #获取与服务器交互的任务个数
            if task_count >=2:
                print ('和服务器失去连接')
                for item in self.process_list:
                    item.terminate()#杀死进程
                    item.join()
                    print (item,len(self.process_list))
                    print ('进程',item.is_alive())
                self.update_local_task()
                self.process()#重新启动客户端
            else:
                time.sleep(1)

    def run(self):
        type=  setting.LOCAL_TASK_TYPE.split('_')[0]
        print (''.join(['您选择了',type,':与服务器交互']))
        if type == 'zmq':
            self.zmq_run()
        elif type == 'http':
            self.http_run()

if __name__ == '__main__':
#目前下拉脚本只在linux系统上测试通过，下拉脚本依赖ssh客户端与sshpass

#注：下拉脚本必须要在加载主程序之前进行，因为setting文件中会读取脚本文件的类型
#关于使用，如果需要自动拉取，只需要执行 pull_script.pull_script()即可
#如果不需要自动拉取将 pull_script.pull_script()注释掉即可
    result = pull_script.pull_script()#从服务器下拉脚本
    if result:#检查客户端依赖模块是否安装完成，如果存在安装失败的模块，程序无法启动
        print ('程序依赖检查通过，启动程序')
        from client_doc import setting
        from client_doc import scan_process
        from excutor import excutor_main
        from excutor_doc import db_oprate
        from client_doc import get_crawltask_inter  # go抓取器获得抓取任务和上传解析任务的接口
        obj = check_connect_status()
        obj.run()
    else:#存在安装失败的模块
        print ('安装必要模块失败,无法启动程序')


