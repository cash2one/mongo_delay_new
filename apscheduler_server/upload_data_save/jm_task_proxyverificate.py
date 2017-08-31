#-*- utf8 -*-
#根据类型对应相应的存储接口

import setting
import itertools

class jm_task_proxyverificate:
    def __init__(self,obj_db):
        self.obj_db=obj_db

    def getolddata(self, task, obj_db):
        proxyip = None
        ip = task.get('data').get('ipInfo').get('ip')
        port = task.get('data').get('ipInfo').get('port')
        ptl = task.get('data').get('ipInfo').get('ptl')
        tb = obj_db.chocie_db_tb(setting.TMP_DB, 'jm_task_proxyverificate') #根据上传数据的任务类型进行分表
        arr = obj_db.find_data(tb,{'data.ipInfo.ip': ip, 'data.ipInfo.port': port, 'data.ipInfo.ptl': ptl})
        for myip in arr:
            proxyip = myip
        return proxyip

    def getzuselist(self, oldlist, newlist):
        nzlist = []
        zlist = oldlist + newlist
        zlist.sort(key=lambda temp: temp['time'])
        it = itertools.groupby(zlist)
        for k, g in it:
            nzlist.append(k)
        listlen = len(nzlist)
        if listlen > 100:
            for _ in range(listlen - 100):
                del nzlist[0]
        return nzlist

    def getzscorecords(self,olddata,newdata):
        tempdata = olddata
        zret = olddata
        for k,v in newdata.items():
            tempdict = {}
            if k in olddata.keys():
                tmp = tempdata.get(k)
                tempdict['useInterval'] = tmp.get('useInterval',300)
                tempdict['transV']=tmp.get('transV',0)
                tempdict['score']=tmp.get('score',0)+v.get('score',0)
                tempdict['suscount']=tmp.get('suscount',0)+v.get('suscount',0)
                tempdict['usecount']=tmp.get('usecount',0)+v.get('usecount',0)
                if v.get('lastTime') and tmp.get('lastTime'):
                    if v.get('lastTime') > tmp.get('lastTime'):
                        tempdict['lastTime'] = v.get('lastTime')
                        tempdict['resTime'] = v.get('resTime')
                    else:
                        tempdict['lastTime'] = tmp.get('lastTime')
                        tempdict['resTime'] = tmp.get('resTime')
                else:
                    tempdict['lastTime'] = v.get('lastTime')
                    tempdict['resTime'] = v.get('resTime')
                zret[k]=tempdict
        return zret

    def getzverifitasks(self,olddata,newdata):
        tempdata = olddata
        zret = olddata
        for k, v in newdata.items():
            tempdict = {}
            if k in olddata.keys():
                tmp = tempdata.get(k)
                tempdict['interval']=tmp.get('interval',60*60*24)
                tempdict['timeout']=tmp.get('timeout',300)
                tempdict['status'] = tmp.get('status',0)
                if v.get('lastTime') and tmp.get('lastTime'):
                    if v.get('lastTime')>tmp.get('lastTime'):
                        tempdict['lastTime'] = v.get('lastTime')
                    else:
                        tempdict['lastTime'] = tmp.get('lastTime')
                else:
                    if v.get('lastTime'):
                        tempdict['lastTime']= v.get('lastTime')
                    else:
                        tempdict['lastTime'] =tmp.get('lastTime')
                tempdict['passcount'] = tmp.get('passcount',0)+v.get('passcount',0)
                tempdict['taskcount'] = tmp.get('taskcount',0)+v.get('taskcount',0)
                zret[k]=tempdict
        return zret

    def run(self, newdata):  # 运行在server端#obj_db为代理的表的对象
        olddata = self.getolddata(newdata, self.obj_db)
        ptb = self.obj_db.chocie_db_tb(setting.TMP_DB, 'jm_task_proxyverificate')
        pindex = list(ptb.index_information())
        if 'data.ipInfo.ip_1_data.ipInfo.port_1_data.ipInfo.ptl_1' not in pindex:
            self.obj_db.create_union_index(ptb,[('data.ipInfo.ip', 1), ('data.ipInfo.port', 1),('data.ipInfo.ptl', 1)])
        if olddata is None:
            try:
                self.obj_db.insert_data(ptb,newdata)
            except Exception as e:
                print (e)
            finally:
                return 0
        try:
            # 使用记录合并
            olduselist = olddata.get('data').get('ipInfo').get('use')
            newuselist = newdata.get('data').get('ipInfo').get('use')
            zuselist = self.getzuselist(olduselist, newuselist)
            # 打分记录合并
            oldscorerecords = olddata.get('data').get('ipInfo').get('score')
            newscorerecords = newdata.get('data').get('ipInfo').get('score')
            zscorerecords = self.getzscorecords(oldscorerecords, newscorerecords)
            # 验证任务记录合并
            oldverifitasks = olddata.get('data').get('ipInfo').get('task').get('verifi')
            newverifitasks = newdata.get('data').get('ipInfo').get('task').get('verifi')
            zverifitasks = self.getzverifitasks(oldverifitasks, newverifitasks)
            olddata['data']['ipInfo']['use'] = zuselist
            olddata['data']['ipInfo']['score'] = zscorerecords
            olddata['data']['ipInfo']['task']['verifi'] = zverifitasks
            olddata['data']['ipInfo']['status']=newdata.get('data').get('ipInfo').get('status')
            self.updateproxy(olddata, self.obj_db)
        except Exception as e:
            print (e)

    def updateproxy(self, mydata, obj_db):
        ip = mydata.get('data').get('ipInfo').get('ip')
        port = mydata.get('data').get('ipInfo').get('port')
        ptl = mydata.get('data').get('ipInfo').get('ptl')
        tb = obj_db.chocie_db_tb(setting.TMP_DB, 'jm_task_proxyverificate')  # 根据上传数据的任务类型进行分表
        obj_db.find_modify(tb,{'data.ipInfo.ip': ip, 'data.ipInfo.port': port, 'data.ipInfo.ptl': ptl},mydata)


