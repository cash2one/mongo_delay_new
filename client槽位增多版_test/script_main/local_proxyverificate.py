import uuid,time
from excutor_doc.excutor_main import *
class local_proxyverificate:
    def __init__(self):
        pass

    def run(self,task,obj_db):# 操作数据库对象
        print ('in proxy******')
        self.generateTask(obj_db)
        obj = excutor_cls(obj_db)
        obj.update_task_delay(task)

    def generateTask(self,dbobj):
        ptb = dbobj.choice_table('jame_proxy')
        tasktb = dbobj.choice_task_table()
        proxylist = self.generatepvtask(ptb)#cls.getVerificateTask()
        count = 0
        addN = 0#3
        for i in range(len(proxylist)):
            guid = str(uuid.uuid1())  # 根据时间戳生成随机的uuid
            dictUpdate = {'guid': guid, 'time': time.time() + count,
                          'body': proxylist[i]}
            basic_task = self.updateDict(dictUpdate)
            dbobj.insert_data(tasktb,basic_task)
          #  tasks.append(basic_task)
            count += addN
      #  return tasks

    def generatepvtask(self,ptb):
        proxyiplist=[]
        arr = ptb.find({})
        for item in arr:
            item.pop('_id')
            proxyiplist.append(item)
        return proxyiplist

    def updateDict(self, args):
        basic_task = {'device': {'type': '', 'version': '127.22', 'id': ''},
                      'guid': args['guid'],
                      'time': args['time'],  # time.time(),
                      'timeout': 1200,
                      'topic': 'jm_task_proxyverificate',
                      'interval': 86400,  # 任务执行周期间隔时间
                      'suspend': 0,  # 暂停标识
                      'status': 0,
                      'body': args['body']
                      }
        return basic_task