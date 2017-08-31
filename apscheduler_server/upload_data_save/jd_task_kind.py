#-*- coding utf-8 -*-
import json,time,uuid
import re,itertools
from pymongo import MongoClient

class jd_task_product:

    def __init__(self):
        conn = MongoClient('192.168.0.210',27017)
        datadb = conn['tmp_db']
        self.datatb = datadb['jd_task_kind']
        taskdb = conn['jame_server']
        self.tasktb = taskdb['task_main']


    def updateSkuDict(self,args):
        basic_task={
            'sku':args['sku'],
            'spu':'',
            'firstTime':args['firstTime'],
            'shopId':'',
            'venderId':'',
            'kind':args['kind'],
            'childSku':None,
            'photoPath':'',
            'detailProductDes':'',
            'detailProductPhotoPaths':'',
            'displayPhotoPaths':'',
            'isPostByJd':'',
            'goodRate':None,
            'jdzy':False,
            'pcDetailScreenshot':'',
            'isAD':'',
            'history':{
                'order':{
                    'pc_order':[args['pc_order'],],
                    'mobile_order':[args['mobile_order'],],
                },
                'title':None,
                'ad_title':None,
                'price':{
                    'pc_price':None,
                    'mobile_price':None,
                    'qq_price':None,
                    'weChat_price':None
                },
                'lastTime':[{'time':args['firstTime'],'status':'on'},],
                'isHot':None,
                'isNew':None,
                'promType':None
            },
            'task':{
                'title':{'taskStatus':0,'taskTime':None,'intervalTime':8640,'taskId':None},
                'ad_title':{'taskStatus':0,'taskTime':None,'intervalTime':8640,'taskId':None},
                'price':{'taskStatus':0,'taskTime':None,'intervalTime':8640,'taskId':None},
                'comment':{'taskStatus':0,'taskTime':None,'intervalTime':8640,'taskId':None,'errorCount':None},
                'searchShop':{'taskStatus':0,'taskTime':None,'intervalTime':8640,'taskId':None},
                'photoDownload':{'taskStatus':0,'taskTime':None,'taskId':None},
                'detailProductPhotoDownload':{'taskStatus':0,'taskTime':None,'taskId':None},
                'displayPhotoDownload':{'taskStatus':0,'taskTime':None,'taskId':None},
                'jdzy':{'taskStatus':0,'taskTime':None,'taskId':None},
                'promType':{'taskStatus':0,'taskTime':None,'intervalTime':8640,'taskId':None},
                'pcDetailScreenshot':{'taskStatus':0,'taskTime':None,'taskId':None},
            }
        }
        return basic_task

    def updateDict(self, args):
        basic_task = {'device': {'type': '', 'version': '127.22', 'id': ''},
                      'guid': args['guid'],
                      'time': args['time'],  # time.time(),
                      'timeout': 1200,
                      'topic': 'jd_task_product',
                      'interval': 86400,  # 任务执行周期间隔时间
                      'suspend': 0,  # 暂停标识
                      'status': 0,
                      'body': {
                          'sku': args['body']['sku'], 'platform': args['body']['platform']
                      }
                      }
        return basic_task

    def generateTask(self):
        #1.从数据库中挑选出所有的sku
        dataarray = self.datatb.find({'upload_time':{'$gte':(time.time()-24*60*60*5)}},{'data':1})
        totalnum=0
        skulist=[]
        for index,mydata in enumerate(dataarray):
            datalist = mydata.get('data')
            for mydata in datalist:
                if len(mydata.get('order'))<=0 or (len(mydata.get('order'))==1 and mydata.get('order')[0]==''):
                    continue
                else:
                    skulist += mydata.get('order')
                    totalnum+=len(mydata.get('order'))
        skulist.sort()
        nskulist=itertools.groupby(skulist)
        datalist=[]
        for k,g in nskulist:
            datalist.append(k)
      #  print (datalist)
      #  print (totalnum)
        #2.用挑选出来的sku组成任务
        tasks=[]
        count = 0
        addN =0
        for i in range(len(datalist)):
            guid = str(uuid.uuid1())
            dictUpdate = {'guid': guid, 'time': time.time() + count,
                          'body': {'sku':datalist[i],'platform':'jd_app'}}
            basic_task = self.updateDict(dictUpdate)
            self.tasktb.insert(basic_task)
            tasks.append(basic_task)
            count += addN
        return tasks

    def generateSkuTask(self,onedata):
        nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        #1.挑选出sku
        totalnum=0
        skulist=[]
        orderlist=[]
        datalist = onedata.get('data')
        for mydata in datalist:
            if len(mydata.get('order'))<=0 or (len(mydata.get('order'))==1 and mydata.get('order')[0]==''):
                continue
            else:
                orderlist += mydata
                totalnum+=len(mydata.get('order'))
        datalist=[]
        for myorder in orderlist:
            #查找是否在sku的数据库中有此数据
            for k in myorder:
                myret=None
                mylist=k.get('order')
                for index,m in enumerate(mylist):
                    ret = self.skutb.find({'sku':m})
                    for item in ret:
                        myret=item
                    if myret is None:
                        datalist.append(m)
                        if k.get('platform')=='jd_app':
                            pc_order=None
                            mobile_order={'page':k.get('page'),'orderInPage':index+1,'sort':k.get('sort'),'time':nowtime}
                        elif k.get('platform')=='jd_web':
                            mobile_order=None
                            pc_order={'page':k.get('page'),'orderInPage':index+1,'sort':k.get('sort'),'time':nowtime}
                        else:
                            print ("error")
                            pc_order=None
                            mobile_order=None
                        mysku = self.updateSkuDict({'sku':m,'firstTime':nowtime,'pc_order':pc_order,'mobile_order':mobile_order,'kind':k.get('kind')})
                        self.skutb.insert(mysku)
        print (datalist)
        #2.用挑选出来的sku组成任务
        tasks=[]
        count = 0
        addN =0
        for i in range(len(datalist)):
            guid = str(uuid.uuid1())
            dictUpdate = {'guid': guid, 'time': time.time() + count,
                          'body': {'sku':datalist[i],'platform':'jd_app'}}
            basic_task = self.updateDict(dictUpdate)
            self.tasktb.insert(basic_task)
            tasks.append(basic_task)
            count += addN
        return tasks

#保存二级页面的脚本
class jd_task_kind:
    def __init__(self,obj_db):
        self.obj_db=obj_db
        self.jp = jd_task_product()
    def run(self,data): #参数1临时表中的上传数据，参数二：封装的数据库操作对象
        db = 'tmp_db'
        tb = data['topic']
        try:
            save_tb = self.obj_db.chocie_db_tb(db, tb)  # 切换到该数据对应存储的数据库和数据表下
            self.obj_db.create_com_index(save_tb, 'guid')  # 为guid建立索引
            self.obj_db.insert_data(save_tb,data)#将数据插入对应的数据库中
            self.jp.generateSkuTask(data)

        except Exception as e:
            print (e)

