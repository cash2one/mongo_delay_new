import multiprocessing
import time,os
import signal


def kill_create_process(pid):  # 开启线程的进程,线程结束重新开启
    t = multiprocessing.Process(target=process_demo, args=(), name='jm_process')
    t.start()
    try:
        os.kill(pid, signal.SIGKILL)
    except:
        pass


def process_demo():  # 子进程运行结束后杀掉进程重新启动进程
    while True:
        try:
            pid = os.getpid()
            print ('pid:',pid)
            a = os.kill(pid, signal.SIGKILL)
        except Exception as e:
            print (e)
        pid = os.getpid()
        kill_create_process(pid)

process_list = []
for i in range(5):  # 开启子进程
    process_list.append(multiprocessing.Process(target=process_demo, args=(), name='jm_process'))
for process in process_list:
    process.start()  # 开启进程
process.join()



if __name__ == "__main__":
    pass