#开启进程，进程从mongo数据库中获取任务
import multiprocessing,os,time,sys
from multiprocessing import Process
from excutor_doc import db_oprate
import threading
db_obj = db_oprate.collection_db()  # 操作数据库对象
class processes:
    def __init__(self):
        #self.db_obj = db_oprate.collection_db()  # 操作数据库对象
        pass


    def load_module(self):
        curdir = os.path.abspath(os.path.dirname(__file__))
        curdir = os.path.join(curdir, 'script_main')
        sys.path.append(curdir)

    def process(self):  # 进程负责和中间层进行交互，开启线程
        self.load_module()  # 加载脚本所在目录到系统目录
        process_list = []
        for i in range(4): #开启执行队列任务的进程，该进程会开启线程
            process_list.append(multiprocessing.Process(target=self.process_demo, args=(),name='jm_process'))
        for process in process_list:
            process.start()  # 开启进程

    def process_demo(self):  # 开启线程的进程
        while True:
            for i in range(10):
                t = threading.Thread(target=self.threading_get,
                                     args=())  # 开启固定的线程，并将该进程所属的对象传递进去
                t.start()

            t.join()

    def threading_get(self):  # 进程开启的线程,该线程只是从队列获取任务，得到任务调用脚本
        # 线程负责调用相应的脚本,判断任务类型调用不同的脚本
        # 线程动态加载模块可能导致模块加载失败
        task = ''
        while True:
                topic = 'jd_task_kind'
                module_name = '.'.join(('script_main', topic))
                m1 = __import__(module_name)  # 找到了脚本所在的目录
                script = getattr(m1, topic)  # 根据类型找到脚本
                cls = getattr(script, topic)()  # 根据类型找到脚本中的类，实例话
                cls.run(task,db_obj)
                break






if __name__ == '__main__':
    cls = processes()
    cls.process()
