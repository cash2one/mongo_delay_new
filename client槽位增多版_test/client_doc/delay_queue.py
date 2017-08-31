# coding:utf-8

import asyncio

import setting
# from mongodb import MongoDB_Queue as BaseQueue
import queue_coprate

import time
class DelayQueue:
    def __init__(self):
        self._queue = queue_coprate.Motor_Queue()

    async def run_task_at_time(self, task, absTime, TimeOut=0):
        await self._queue.put_abstime(task, absTime, TimeOut)

    async def pop(self, topic):
        while True:
            task = await self._queue.get_ready_task(topic)
            if task:
                return task
            asyncio.sleep(1)

    async def pop_list(self, topic, count=1):
        tasks = []
        while len(tasks) < count:
            task = await self.pop(topic)
            if task: tasks.append(task)

        return tasks

    async def finish(self, task):
        await self._queue.set_finish(task[setting.ROW_TOPIC], task[setting.ROW_GUID])

    async def update_task_body(self, task):
        await self._queue.update_task_body(task)

    async def finish_and_update(self, task):
        await self.finish(task)
        await self.update_task_body(task)

    # 设置任务结束状态，删除状态
    async def delete(self, task):
        await self._queue.set_delete(task[setting.ROW_TOPIC], task[setting.ROW_ID])

    async def scan_ready_task(self):
        while True:
            ready_task= await self._queue.get_timeup_task()#得到一个就绪任务
            await self._queue.add_readylist(ready_task)#将就绪任务的id和topic记录到就绪表中

    async def scan_complete_task(self):# 扫描完成任务
        await self._queue.get_complete_task()#将完成的任务状态更改为可扫描状态

    async def add_local_task(self):#将与服务器交互的任务添加到总任务列表
        #找到本地任务的最大时间，到了最大时间重新更新本地任务，如果只添加一次可能有一次执行不到就不会再被执行
        #与服务器交互的本地任务
        for topic in setting.CONNECT_SERVER_TYPE:
            topic = topic+'_local_task'
            await self._queue.clear_readylist(topic)#清空所有的本地就绪队列，防止改变通信方式
            await self._queue.clear_task(topic)#清空本地任务
        for item, topic in enumerate(setting.REQUEST_SERVER_LIST):
            print('insert', topic)
            task = {"device": {'type': "", 'version': '127.22', 'id': ''},
                    'guid': topic, 'time': time.time(), 'timeout': 0, 'topic': setting.LOCAL_TASK_TYPE,
                    'interval': setting.REQUEST_SERVER_TIME[item],  # 从配置文件读出本地任务周期时间
                    'suspend': 0,  # 暂停标识
                    'status': 0,
                    'body': ''
                    }
            await self._queue.put_task(task)
        #检查是否与服务器断连的本地任务

        task['topic']= 'local_check_task'
        task['guid'] = 'local_check_task'
        task['time'] = time.time()+10#延时执行一会，防止启动误判
        task['interval'] = setting.LOCAL_CHECK_TASK_TIME
        await self._queue.put_task(task)
        if setting.ENNABLE_PROXYVERIFICATE:#开启本地代理验证任务
            task['topic'] = 'local_proxyverificate'
            task['guid'] = 'local_proxyverificate'
            task['time'] = time.time()
            task['interval'] = setting.PROXYVERIFICATE_TIME
            await self._queue.put_task(task)

    def run(self):
        loop = asyncio.get_event_loop()
        tasks = []

        tasks.append(self.add_local_task())
        tasks.append(self.scan_ready_task())
        #tasks.append(self._queue.get_complete_task())#完成任务状态到可悲扫描的状态。将任务状态上报完成后由本地任务进行更改

        f = asyncio.wait(tasks)
        try:
            loop.run_until_complete(f)
            loop.run_forever()
        except Exception as e:
            print('****', e)
        finally:
            loop.close()




def scan_task():
    q = DelayQueue()
    q.run()


if __name__ == "__main__":
    scan_task()

    """
    q = DelayQueue()
    loop = asyncio.get_event_loop()
    tasks = []
    tasks.append(q.scan_ready_task())
    tasks.append(q.scan_complete_task())
    f = asyncio.wait(tasks)
    # asyncio.ensure_future(test_mongodb_queue(), loop=loop)
    # loop.run_forever()
    try:
        loop.run_until_complete(f)
    finally:
        loop.close()
    """