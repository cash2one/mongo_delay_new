#-*- coding utf-8 -*-
import setting
import itertools,time
from pymongo import MongoClient
class jd_task_product:

    def __init__(self,obj_db):
        self.obj_db = obj_db
      #  conn = MongoClient('192.168.0.210', 27017)
      #  datadb = conn['tmp_db']
      #  self.shoptb = datadb['jd_shop']
      #  self.skutb = datadb['jd_sku']
      #  taskdb = conn['jame_server']
      #  self.tasktb = taskdb['task_main']

    def updateShopDict(self,args):
        basic_task={
            'shopId':args['shopId'],
            'firstTime':args['firstTime'],
            'lastTime':args['firstTime'],
            'shopName':args['shopName'],
            'category':'',
            'shopLogoPath':args['shopLogoPath'],
            'isAD':'',
            'shopBrief':args['shopBrief'],
            'allSku':None,
            'history':args['history'],
            'task':{
               'shopTask':{'taskStatus':0,'taskTime':None,'intervalTime':0,'taskId':None},
               'skuTask':{'taskStatus':0,'taskTime':None,'intervalTime':0,'taskId':None},
               'shopLogoDownloadTask':{'taskStatus':0,'taskTime':None,'taskId':None}
            }
        }
        return basic_task

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

    def run(self, newdata):  # 运行在server端#obj_db为代理的表的对象
        print ("1")
        oldskudata = self.getoldskudata(newdata, self.obj_db)
        oldshopdata = self.getoldshopdata(newdata, self.obj_db)
        print ("2")
        skutb = self.obj_db.chocie_db_tb(setting.TMP_DB, 'jd_sku')
        skuindex = list(skutb.index_information())
        print ("3")
        if 'sku_1' not in skuindex:
            self.obj_db.create_union_index(skutb,[('sku', 1)])
        print ("4")
        shoptb = self.obj_db.chocie_db_tb(setting.TMP_DB, 'jd_shop')
        shopindex = list(shoptb.index_information())
        if 'shopId_1' not in shopindex:
            self.obj_db.create_union_index(shoptb, [('shopId', 1)])
        if oldshopdata is None:
            try:
                self.addshopinfo(self.obj_db,newdata)
            except Exception as e:
                print (e)
        else:
            try:
                # shop信息合并
                oldshopinfo = oldshopdata
                newshopinfo = newdata.get('data').get('shopInfo')
                zshopinfo = self.getzshopinfo(newshopinfo, oldshopinfo)
                # shop历史信息合并
                oldshophistory = oldshopdata
                newshophistory = newdata.get('data').get('shopInfoHistory')
                zshophistory = self.getzshophistory(newshophistory, oldshophistory)
                # 更新数据
                self.updateshopinfo(zshopinfo, zshophistory, self.obj_db)
            except Exception as e:
                print ("1error",e)
        try:
            #sku信息合并
            oldskuinfo = oldskudata
            newskuinfo = newdata.get('data').get('skuInfo')
            zskuinfo = self.getzskulist(newskuinfo,oldskuinfo)
            #sku历史信息合并
            oldskuhistory = oldskudata
            newskuhistory = newdata.get('data').get('skuInfoHistory')
            zskuhistory = self.getzskuhistory(newskuhistory,oldskuhistory)
            #更新数据
            self.updateskuinfo(zskuinfo,zskuhistory, self.obj_db)
        except Exception as e:
            print ("2error",e)

    def addshopinfo(self,obj_db, newdata):
        shopId=newdata.get('shopInfo').get('shopId')
        nowtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        shopName=newdata.get('shopInfo').get('shopName')
        shopLogoPath=newdata.get('shopInfo').get('shopLogoPath')
        shopBrief=newdata.get('shopInfo').get('shopBrief')
        history = newdata.get('shopInfoHistory')
        myshopdata = self.updateShopDict({'shopId':shopId,'firstTime':nowtime,'shopName':shopName,'shopLogoPath':shopLogoPath,'shopBrief':shopBrief,'history':history})
        tb = obj_db.chocie_db_tb(setting.TMP_DB, 'jd_shop')
        obj_db.insert_data(tb, myshopdata)

    def updateskuinfo(self,zskudata,zskuhistorydata,obj_db):
        zskudata['history']['title']=zskuhistorydata.get('title')
        tb = obj_db.chocie_db_tb(setting.TMP_DB,'jd_sku')
        obj_db.find_modify(tb,{'sku':zskudata.get('sku')},zskudata)

    def updateshopinfo(self,zshopdata,zshophistorydata,obj_db):
        zshopdata['history']=zshophistorydata
        tb = obj_db.chocie_db_tb(setting.TMP_DB, 'jd_shop')
        obj_db.find_modify(tb,{'shopId':zshopdata.get('shopId')},zshopdata)

    def getzskulist(self,newdata,olddata):
        if olddata.get('sku')==newdata.get('sku'):
            olddata['spu']=newdata.get('spu')
            olddata['kind']=newdata.get('kind')
            olddata['shopId']=newdata.get('shopId')
            olddata['venderId']=newdata.get('venderId')
            olddata['isPostByJd']=newdata.get('isPostByJd')
            olddata['detailProductPhotoPaths']=newdata.get('detailProductPhotoPaths')
            olddata['detailProductDes']=newdata.get('detailProductDes')
            olddata['photoPath']=newdata.get('photoPath')
            olddata['displayPhotoPaths']=newdata.get('displayPhotoPaths')
            olddata['childSku']=newdata.get('childSku')
        return olddata

    def getzskuhistory(self,newdata,olddata):
        odata = olddata.get('history').get('title')
        ndata = newdata.get('title')
        odata.append(ndata)
        return {'title':odata}

    def getzshopinfo(self,newdata,olddata):
        if olddata.get('shopId')==newdata.get('shopId'):
            olddata['shopName']=newdata.get('shopName')
            olddata['shopLogoPath']=newdata.get('shopLogoPath')
            olddata['shopBrief']=newdata.get('shopBrief')
        return olddata

    def getzshophistory(self,newdata,olddata):
        fdata = olddata.get('history').get('followCount')
        nfdata = newdata.get('followCount')
        fdata.append(nfdata)
        pdata = olddata.get('history').get('productNum')
        npdata = newdata.get('productNum')
        pdata.append(npdata)
        ndata = olddata.get('history').get('newProductNum')
        nndata = newdata.get('newProductNum')
        ndata.append(nndata)
        sdata = olddata.get('history').get('shopActivityTotalNum')
        nsdata = newdata.get('shopActivityTotalNum')
        sdata.append(nsdata)
        return {'followCount':fdata,'productNum':pdata,'newProductNum':ndata,'shopActivityTotalNum':sdata}

    def getoldskudata(self, newdata, obj_db):
        skutb = obj_db.chocie_db_tb(setting.TMP_DB, 'jd_sku')
        myret = None
        if newdata and newdata.get('skuInfo'):
            mysku = newdata.get('skuInfo').get('sku')
            array = obj_db.find_data(skutb,{'sku':mysku})
            for item in array:
                myret = item
        return myret

    def getoldshopdata(self, newdata, obj_db):
        shoptb = obj_db.chocie_db_tb(setting.TMP_DB, 'jd_shop')
        myret = None
        if newdata and newdata.get('shopInfo'):
            mysku = newdata.get('shopInfo').get('shopId')
            array = obj_db.find_data(shoptb, {'shopId': mysku})
            for item in array:
                myret = item
        return myret
