# coding:utf-8
import asyncio
import time

# from pymongo import MongoClient, DESCENDING
import motor.motor_asyncio

import setting

ASCENDING = 1
"""Ascending sort order."""
DESCENDING = -1

# connection = MongoClient('127.0.0.1', 27017)
#connection = motor.motor_asyncio.AsyncIOMotorClient('192.168.0.210', 27017)
connection = motor.motor_asyncio.AsyncIOMotorClient(setting.DATABASES_IP, 27017)

'''
ready 可执行
delay 不可执行，等待消费
reserved  已被读取，但还未回应
delete 已完成或已删除
'''


class Motor_Queue:
    def __init__(self):
        dbname = setting.DATABASES#总任务数据库
        self.db = connection[dbname]

    async def gettable(self, table):#返回表对象
        return self.db[table]

    async def put_task(self,task):#将任务添加到总任务列表
        table = await self.gettable(setting.TASKS_LIST)#得到存储总任务列表的表对象

        await table.update(
            {
                setting.ROW_TOPIC: task[setting.ROW_TOPIC],
                setting.ROW_GUID: task[setting.ROW_GUID],
            },
            task,
            True
        )

    async def add_readylist(self,task):#将就绪任务添加到就绪队列
        queue_name = task['topic'] + setting.READY_LIST  # 根据任务的topic标识+ready_list 拼接成各个任务属性的就绪队列名称
        table = await self.gettable(queue_name)  # 得到存储总任务列表的表对象
        try:
            await table.update(
                {
                    setting.ROW_TOPIC: task[setting.ROW_TOPIC],
                    setting.ROW_GUID: task[setting.ROW_GUID]
                },
                {
                    setting.ROW_TOPIC: task[setting.ROW_TOPIC],
                    setting.ROW_GUID: task[setting.ROW_GUID],
                },
                True
            )
        except Exception as e:
            print ('add_readylist******',e)
        #将topic 和id 插入就绪表中
    async def clear_readylist(self,topic):#清空某种类型的就绪列表
        queue_name = topic + setting.READY_LIST  # 根据任务的topic标识+ready_list 拼接成各个任务属性的就绪队列名称
        table = await self.gettable(queue_name)  # 得到存储总任务列表的表对象
        try:
            await table.remove()
        except Exception as e:
            print('clear_readylist****', e)

    async def clear_task(self,topic):#清空某种类型的任务
        table = await self.gettable(setting.TASKS_LIST)  # 得到存储总任务列表的表对象
        try:
            await table.remove({'topic':topic})
        except Exception as e:
            print('clear_readylist****', e)


    # 增加一个任务到等待队列,如果存在相同的topic和id的任务，则强制覆盖
    # delaytime表示在当前时间延迟时间，单位秒
    # 如果timeout大于0，则覆盖task中的设置
    # 如果任务处于已取走状态，则先设置一次完成，触发操作
    async def update_exetime(self,task):#更新执行时间只适用于周期性任务

        if task[setting.ROW_STATUS] == setting.STATUS_DELETED:#如果是一次性任务则不进行更新
            return
        #print('update time')
        try:
            table = await self.gettable(setting.TASKS_LIST)  # 得到存储总任务列表的表对象
            task[setting.ROW_TIME] = task[setting.ROW_TIME]+task[setting.ROW_INTERVAL]#更新下次的执行时间 上次执行时间+周期时间

            await table.update(
                {
                    setting.ROW_TOPIC: task[setting.ROW_TOPIC],
                    setting.ROW_GUID: task[setting.ROW_GUID]
                },
                task,
                True
            )
        except Exception as e:
            print('rrrrrr',e)
        #print ('update time end')
    # 增加一个任务到等待队列,如果存在相同的topic和id的任务，则强制覆盖
    # delaytime表示在当前时间延迟时间，单位秒
    # 如果timeout大于0，则覆盖task中的设置
    # 如果任务处于已取走状态，则先设置一次完成，触发操作
    async def add(self, task, delaytime=0, timeout=0):
        try:
            table = await self.gettable(task[setting.ROW_TOPIC])
            task[setting.ROW_TIME] = time.time() + delaytime
            task[setting.ROW_STATUS] = setting.STATUS_DELAY
            task[setting.ROW_TIMEOUT] = setting.get_task_timeout(task[setting.ROW_TOPIC]) if timeout <= 0 else timeout

            await table.update(
                {
                    setting.ROW_TOPIC: task[setting.ROW_TOPIC],
                    setting.ROW_GUID: task[setting.ROWROW_GUID]
                },
                task,
                True
            )
        except Exception as e:
            print('ffff',e)


    # 得到一个时间到了的任务，放入就绪队列，只返回任务topic和id
    async def get_timeup_task(self):
        # Todo，入口需校验任务类别命名是否符合要求
        table = await self.gettable(setting.TASKS_LIST)#总任务列表
        try:
            while True:
                result = await table.find_and_modify(
                    query={
                        setting.ROW_STATUS: setting.STATUS_DELAY,
                        setting.ROW_TIME: {'$lte': setting.NOW()},
                    },
                    update={
                        '$set': {setting.ROW_STATUS: setting.STATUS_READY}
                    },
                    sort={
                        setting.ROW_TIME: DESCENDING
                    }
                )

                if result:
                    return result
                # 没有任务，休息1秒
                await asyncio.sleep(1)

        except Exception as e:
            print('yyyy',e)


    async def get_complete_task(self):# 得到一个完成任务并将状态改变为可扫描状态
        # Todo，入口需校验任务类别命名是否符合要求
        table = await self.gettable(setting.TASKS_LIST)
        while True:
            try:
                result = await table.find_and_modify(
                    query={
                        setting.ROW_STATUS: {'$in': [4, 5]}, setting.ROW_TIME: {'$lte': time.time()}
                    },
                    update={
                        '$set': {setting.ROW_STATUS: 0}
                    },
                    sort={
                        setting.ROW_TIME: DESCENDING
                    }
                )
                if result:
                    print (result)
                    result[setting.ROW_STATUS] = 0
                    await self.update_exetime(result)
                else:
                    await asyncio.sleep(1)

            except Exception as e:
                print('kkk',e)

    async def set_delete(self, task):
        # Todo，入口需校验任务类别命名是否符合要求
        table = await self.gettable(task[setting.ROW_TOPIC])
        try:
            result = await table.find_and_modify(
                {
                    task[setting.ROW_GUID],
                    # task[config.ROW_TOPIC]
                },
                update={
                    '$set': {
                        setting.ROW_STATUS: setting.STATUS_DELETED,
                        setting.ROW_BODY: task[setting.ROW_BODY]
                    },


                }
            )
            return result

        except Exception as e:
            print(e)
            return None

    async def set_finish(self, task):
        # Todo，入口需校验任务类别命名是否符合要求
        table = await self.gettable(task[setting.ROW_TOPIC])
        try:
            result = await table.find_and_modify(
                query={
                    setting.ROW_TOPIC: task[setting.ROW_TOPIC],
                    setting.ROW_GUID: task.config[setting.ROW_GUID]
                },
                update={
                    '$set': {
                        setting.ROW_STATUS: setting.STATUS_FINISH,
                        setting.ROW_BODY: task[setting.ROW_BODY]
                    }
                }
            )
            return result
        except Exception as e:
            print(e)
            return None

    # 获得一个就绪任务,准备去执行
    async def get_ready_task(self, topic):
        table = await self.gettable(topic)

        try:
            result = await table.find_and_modify(
                query={
                    setting.ROW_STATUS: setting.STATUS_READY,
                },
                update={
                    '$set': {
                        setting.ROW_STATUS: setting.STATUS_RESERVED,
                        setting.ROW_TIME: setting.NOW() + timeout
                    }
                },
                sort={
                    setting.ROW_TIME: DESCENDING
                }
            )
            if result:
                # 更新超时时间，这样可以保证每个任务有自己的超时设置，不过这样有必要吗？
                if result[setting.ROW_TIMEOUT] < 1:
                    result[setting.ROW_TIMEOUT] = setting.get_task_timeout(topic)

                await table.update(
                    {
                        setting.ROW_GUID: result[setting.ROW_GUID],
                        # config.ROW_TOPIC:topic
                    },
                    {
                        '$set': {
                            setting.ROW_TIME: setting.NOW() + result[setting.ROW_TIMEOUT]
                        }
                    },
                )
                return result
            else:
                return None

        except Exception as e:
            print(e)
            return None

    # 获得一个任务
    async def get_task(self, topic, id):
        table = await self.gettable(topic)
        try:
            result = await table.find_one(
                {
                    setting.ROW_GUID: id,
                    # config.ROW_TOPIC:topic
                }
            )
            if result:
                return result
            else:
                return None

        except Exception as e:
            print(e)
            return None

    async def update_task_body(self, task):
        table = await self.gettable(task[setting.ROW_TOPIC])
        try:
            result = await table.update(
                {
                    setting.ROW_GUID: task[setting.ROW_GUID],
                    # config.ROW_TOPIC:task[config.ROW_TOPIC],
                },
                {
                    '$set': {
                        setting.ROW_BODY: task[setting.ROW_BODY]
                    }
                },
                True
            )
            if result:
                return result
            else:
                return None

        except Exception as e:
            print(e)
            return None

    async def get_task_status(self, topic, id):
        table = await self.gettable(topic)
        try:
            result = await table.find_one(
                {
                    # config.ROW_TOPIC:topic,
                    setting.ROW_GUID: id,
                },
                {
                    setting.ROW_STATUS: 1,
                    '_id': 0,
                }
            )
            return result

        except Exception as e:
            print(e)
            return None

    async def show_tables(self):
        return await self.db.collection_names()




if __name__ == "__main__":
    pass