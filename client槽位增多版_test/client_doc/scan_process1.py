#开启进程，进程从mongo数据库中获取任务
import multiprocessing,os,time,sys
from multiprocessing import Process
from client_doc import setting
from excutor_doc import db_oprate
import threading
db_obj = db_oprate.collection_db()  # 操作数据库对象
class processes:
    def __init__(self):
        #self.db_obj = db_oprate.collection_db()  # 操作数据库对象
        pass

    def select_table(self, table):  # 查表，并删除第一个查询到的数据
        tb = db_obj.choice_table(table)#切换就绪表
        data = db_obj.find_modify_remove(tb,{})
        return data

    def load_module(self):
        curdir = os.path.abspath(os.path.dirname(__file__))
        curdir = os.path.join(curdir, setting.SCRIPT_DIR)
        sys.path.append(curdir)

    def process(self):#开启进程池
        self.load_module()  # 加载脚本所在目录到系统目录
        process_list = []
        process_list.append(multiprocessing.Process(target=self.scan_localtask, args=(), name='jm_process'))
        for i in range(50):  # 开启执行队列任务的进程，该进程会开启线程
            process_list.append(multiprocessing.Process(target=self.process_demo, args=(), name='jm_process'))
        for process in process_list:
            process.start()  # 开启进程
        process.join()


    def process_demo(self):#运行结束后杀掉进程重新启动进程
        while True:
            item = multiprocessing.Process(target=self.threading_get, args=(), name='jm_process')
            item.start()
            item.join()
            item.terminate()  # 杀死进程
            item.join()
            print('进程', item.is_alive())

    def threading_get(self):  # 进程开启的线程,该线程只是从队列获取任务，得到任务调用脚本
        # 线程负责调用相应的脚本,判断任务类型调用不同的脚本
        # 线程动态加载模块可能导致模块加载失败
        while True:
            task = self.pop_task()
            if task:
                # 调用脚本
                try:
                    try:
                        task.pop('_id')
                    except:
                        pass
                    print(task, 'get task********')
                    topic = task[setting.ROW_TOPIC]
                    module_name = '.'.join((setting.SCRIPT_DIR, topic))
                    m1 = __import__(module_name)  # 找到了脚本所在的目录
                    script = getattr(m1, topic)  # 根据类型找到脚本
                    cls = getattr(script, topic)()  # 根据类型找到脚本中的类，实例话
                    cls.run(task,db_obj)
                except:#run 脚本出错
                    pass
                break
            else:
                # print('***********')
                time.sleep(0.1)



    def pop_task(self):  # db数据库，topic任务类型
        result = ''
        for topic in setting.TOPIC:#轮询任务类型
            queued_name = topic + setting.READY_LIST # 表   根据类型拼接到自己类型所在的就绪任务队列
            data = self.select_table(queued_name)  # 得到任务，实际上的真实数据为任务id，并且将就绪列表的id删除
            if data:  # 得到就绪任务
                task_tb =db_obj.choice_task_table()
                result = db_obj.find_modify(task_tb,{setting.ROW_GUID:data[setting.ROW_GUID]},{'$set': {setting.ROW_STATUS: setting.STATUS_EXCUTING}})
                 # 进入总任务列表修改任务状态为正在执行
                break#得到一个任务就返回
        return result

    def scan_localtask(self):#负责扫描本地任务的进程
        topic = setting.LOCAL_TASK_TYPE
        queued_name = topic + '_ready_list'  # 表   根据类型拼接到自己类型所在的就绪任务队列
        while True:
            data = self.select_table(queued_name)  # 得到任务，实际上的真实数据为任务id，并且将就绪列表的id删除
            if data:
                try:
                    task_tb = db_obj.choice_task_table()
                    result = db_obj.find_one(task_tb,{setting.ROW_GUID: data[setting.ROW_GUID], setting.ROW_TOPIC: data[setting.ROW_TOPIC]})
                     #获取本地任务，调用本地任务脚本
                    module_name = '.'.join((setting.SCRIPT_DIR, topic))
                    try:
                        m1 = __import__(module_name)  # 找到了脚本所在的目录
                    except Exception as e:
                        print (e)
                    script = getattr(m1, topic)  # 根据类型找到脚本
                    try:
                        cls = getattr(script, topic)()  # 根据类型找到脚本中的类，实例话
                    except Exception as e:
                        print (e)
                    cls.run(result)#找到与服务器交互的脚本
                    db_obj.find_modify(task_tb,{setting.ROW_GUID: data[setting.ROW_GUID],setting.ROW_TOPIC: data[setting.ROW_TOPIC],},{
                                                                        '$set': {
                                                                            'status': 0,
                                                                            setting.ROW_TIME: int(time.time()) + int(
                                                                                result[setting.ROW_INTERVAL])}
                                                                    },)
                   # 获取本地任务，调用本地任务脚本
                except:
                    pass
            else:
                time.sleep(0.1)


    def run(self):#开启多进程
        obj = processes()
        obj.process()

def run():
    cls = processes()
    cls.run()

if __name__ == '__main__':
    cls = processes()
    cls.run()
