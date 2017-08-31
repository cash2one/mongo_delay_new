#-*- coding utf-8 -*-
import json,time,uuid,base64
#from excutor_doc.jd_tools import *
#from excutor_doc.excutor_main import *
#from center_layer.center_interface._interface import *
import requests,itertools
import setting
class jd_task_shop:
    def __init__(self,obj_db):
        self.obj_db=obj_db
    
    def getolddata(self,task,obj_db):
        myshopinfo = None
        shopid = task.get('data').get('shopId')
        tb = obj_db.chocie_db_tb(setting.TMP_DB, 'jd_task_shop')  # 根据上传数据的任务类型进行分表
        arr = obj_db.find_data(tb, {'data.shopId':shopid})
        for myinfo in arr:
            myshopinfo = myinfo
        return myshopinfo
    def getzskulist(self,oldlist,newlist):
        nzlist = []
        zlist = oldlist + newlist
        zlist.sort(key=lambda temp: temp['time'])
        it = itertools.groupby(zlist)
        for k, g in it:
            nzlist.append(k)
        return nzlist
    def updateshopidinfo(self, mydata, obj_db):
        shopid = mydata.get('data').get('shopId')
        tb = obj_db.chocie_db_tb(setting.TMP_DB, 'jd_task_shop')  # 根据上传数据的任务类型进行分表
        obj_db.find_modify(tb,{'data.shopId':shopid},mydata)
    def run(self, newdata):
        olddata = self.getolddata(newdata, self.obj_db)
        ptb = self.obj_db.chocie_db_tb(setting.TMP_DB, 'jd_task_shop')
        pindex = list(ptb.index_information())
        if 'data.shopId_1' not in pindex:
            self.obj_db.create_union_index(ptb, [('data.shopId', 1)])
        if olddata is None:
            try:
                self.obj_db.insert(newdata)
            except Exception as e:
                print(e)
            finally:
                return 0
        try:
            #产品详情合并
            oldskulist=olddata.get('data').get('allSku')
            newskulist=newdata.get('data').get('allSku')
            zskulist= self.getzskulist(oldskulist,newskulist)
            #lastTime合并
            oldlasttime = olddata.get('data').get('lastTime')
            newlasttime = newdata.get('data').get('lastTime')
            if newlasttime and oldlasttime:
                if newlasttime > oldlasttime:
                    zlasttime = newlasttime
                else:
                    zlasttime = oldlasttime
            else:
                if newlasttime:
                    zlasttime = newlasttime
                else:
                    zlasttime = oldlasttime
            olddata['data']['allSku']=zskulist
            olddata['data']['lastTime']=zlasttime
            self.updateshopidinfo(olddata,self.obj_db)
        except Exception as e:
            print (e)

