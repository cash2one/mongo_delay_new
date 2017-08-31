#-*- coding:utf-8 -*-
import json,uuid
from excutor_doc.jd_tools import *
from pyquery import PyQuery as pq
import requests
import re,base64
import time
from excutor_doc import excutor_main
class jd_task_kind:
    @classmethod
    def generateTask(cls):
        tasks=[]
        kinds=[]
        allKindId = {"portablePower": "9987,830,13658", "dataLine": "9987,830,13661", "phoneCase": "9987,830,866",
                      "flatAccessories": "670,671,5146", "padPasting": "9987,830,867", "mobilePhone": "9987,653,655",
                      "carAccessories": "9987,830,864", "charger": "9987,830,13660",
                      "mobilephoneBattery": "9987,830,13657", "accessoriesOfAppleProducts": "9987,830,13659",
                      "smartBracelet": "652,12345,12347", "healthMonitoring": "652,12345,12351",
                      "mobileMemoryCard": "9987,830,1099", "mobilePhoneEarphone": "9987,830,862",
                      "creativeAccessories": "9987,830,868", "mobileAccessories": "9987,830,11302",
                      "bluetoothHeadset": "9987,830,863", "mobileBracket": "9987,830,12811",
                      "cameraAccessories": "9987,830,12809", "smartWatch": "652,12345,12348",
                      "smartGlasses": "652,12345,12349", "intelligentRobot": "652,12345,12806",
                      "motionTracker": "652,12345,12350", "intelligentAccessories": "652,12345,12352",
                      "smartHome": "652,12345,12353", "inmotion": "652,12345,12354",
                      "unmannedAerialVehicle": "652,12345,12807",
                      "otherEquipmentOfIntelligentDevice": "652,12345,12355"}
        for index, item in enumerate(allKindId):
            kinds.append(allKindId[item])
        basic_task = {'device':{'type': '', 'version': '127.22', 'id': ''},
                    'guid': '',
                    'time': '',#time.time(),
                    'timeout': 1200,
                    'topic': 'jd_task_kind',
                    'interval': 86400,  # 任务执行周期间隔时间
                    'suspend': 0,  # 暂停标识
                    'status': 0,
                    'body': {
                          'kind': '', 'platform': '', 'sort': '',
                        }
        }
        sortlist = ['sort_totalsales15_desc','sort_rank_asc']
        platformlist = ['jd_app','jd_web']
        for i in range(len(kinds)):
            for index1, item1 in enumerate(sortlist):
                for index2, item2 in enumerate(platformlist):
                    guid = str(uuid.uuid1())  # 根据时间戳生成随机的uuid
                    dictUpdate={'guid':guid,'time':time.time(),'body':{'kind':kinds[i],'platform':item1,'sort':item2}}
                    basic_task.update(dictUpdate)
                    tasks.append(basic_task)
        return tasks

    @classmethod
    def getMaxPage(cls, task):
        platform = task['body']['platform']
        kind = task['body']['kind']
        sort = task['body']['sort']
        totalPage = 0
        if platform == 'jd_web':
            url = 'https://list.jd.com/list.html?cat='+ kind + '&page=1&stock=0&sort=' + sort + '&trans=1&JL=4_7_0#J_main'
            myheader = {
                'accept': '*/*',
                'accept-encoding': 'gzip, deflate, sdch',
                'accept-language': 'zh-CN,zh;q=0.8',
                'connection': 'keep-alive',
                #   'origin': '',
                #     'host': '',
                'referer': '',
                'user-agent': '',
                #   'cookie': ''
            }
            myheader['referer'] = 'https://list.jd.com/list.html?cat=' + kind
            myheader['user-agent'] = jd_tools.get_web_useragent()
         #   myheader['cookie'] = jd_tools.get_jd_web_cookie()
            r = requests.get(url, headers = myheader)
            urldata = r.text
            rst = re.search(r'class=\"fp-text\"', urldata)
            if rst is not None:
                strEndPos = rst.end()
                rst1 = re.findall(r'\d+', urldata[strEndPos:strEndPos + 50])
                if rst1 is not None and len(rst1)>=2:
                    totalPageS = rst1[1]
                    totalPage = int(totalPageS)
        elif platform == 'jd_app':
            kind = kind.replace(',','-')
            url = 'https://so.m.jd.com/products/'+ kind +'.html'
            myheader = {
              #  'origin': '',
                #  'host': '',
              #  'referer': '',
                'user-agent': '',
                #   'cookie': '',
            }
           # myheader['origin'] = 'https://so.m.jd.com'
          #  myheader['referer'] = 'https://so.m.jd.com/category/all.html'
            myheader['user_agent'] = jd_tools.get_app_useragent()
           # myheader['cookie'] = jd_tools.get_jd_app_cookie()
            r = requests.get(url, headers = myheader)
            urldata = r.text
            rst = re.search(r'wareCount', urldata)
            if rst is not None:
                strEndPos = rst.end()
                rst1 = re.findall(r'\d+', urldata[strEndPos:strEndPos + 15])
                if rst1 is not None and len(rst1)>=1:
                    totalPageS = rst1[0]
                    totalPage = int(totalPageS)/10
                    totalPage = int(totalPage)
        print ('totalPage=',totalPage)
        return totalPage


    @classmethod
    def get_urls(cls,task):
        platform = task['body']['platform']
        kind = task['body']['kind']
        sort = task['body']['sort']
        urlList=[]
        maxpage = 100
        page = 1
        if platform == 'jd_web':
            url = 'https://list.jd.com/list.html?'
            method = 'GET'
            myheader = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, sdch',
            'accept-language': 'zh-CN,zh;q=0.8',
            'connection': 'keep-alive',
         #   'origin': '',
       #     'host': '',
            'referer': '',
            'user-agent': '',
         #   'cookie': ''
            }
            myheader['referer'] = 'https://list.jd.com/list.html?cat='+kind
            myheader['user-agent'] = jd_tools.get_web_useragent()
            useproxy = True
        elif platform == 'jd_app':
            url = 'https://so.m.jd.com/ware/searchList.action'
            method = 'POST'
            myheader = {
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate, sdch',
            'accept-language': 'zh-CN,zh;q=0.8',
            'content-length':'59',
            'connection': 'keep-alive',
            'content-type':'application/x-www-form-urlencoded',
            'x-requested-with':'XMLHttpRequest',
            'origin': '',
          #  'host': '',
            'referer': '',
            'user-agent': '',
         #   'cookie': '',
            }
            myheader['origin'] = 'https://so.m.jd.com'
            nkind = kind.replace(',', '-')
            myheader['referer'] = 'https://so.m.jd.com/products/'+ nkind +'.html'
            myheader['user-agent'] = jd_tools.get_app_useragent()
            useproxy = True
        while(page<=maxpage):
            if platform == 'jd_web':
                useproxy = True
                data = {'cat':kind,'page':str(page), 'stock':'0','sort':sort,'trans':'1','JL':'6_0_0'}
            elif platform == 'jd_app':
                kindstrlist = kind.split(",")
                data = {'_format_':'json','stock':0,'sort':sort,'page':page,'categoryId':kindstrlist[0],'c1':kindstrlist[1],'c2':kindstrlist[2]}
            useproxy  =False
            myurl={'url':url,'method':method,'data':data,'header':myheader,'useproxy':useproxy,'platform':platform,'other':{'sort':sort,'kind':kind,'page':page}}
            urlList.append(myurl)
            page=page+1
        return urlList

    @classmethod
    def getstr(cls, str, left, right):
        str = str[str.find(left) + left.__len__():]
        str = str[:str.find(right)]
        return str
    """
    @classmethod
    def parser(cls, html, task):
        html = str(base64.b64decode(html), encoding='utf8')
        platform = task['platform']
        sort = task['other']['sort']
        kind = task['other']['kind']
        ppage = task['other']['page']
        data = []
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S BJT", time.localtime(time.time()))
        if platform == 'jd_web':
            page = html
            data = cls.getstr(page, "pay_after = [", "];").split(",")
            return {'time': timeStr, 'key_search': 0, 'key_word': None, 'platform': platform, 'sort': sort,
                    'kind': kind, 'page': page, 'order': data}
        elif platform == 'jd_app':
            try:
                page = json.loads(html)
                page = page['value']
                page = json.loads(page)
                mydatalist = page['wareList']['wareList']
                for index, item in enumerate(mydatalist):
                    data.append(item['wareId'])
            except Exception as e:

                print(e, '**************')

            finally:
                return {'time': timeStr, 'key_search': 0, 'key_word': None, 'platform': platform, 'sort': sort,
                        'kind': kind, 'page': ppage, 'order': data}

    """
    @classmethod
    def parser(cls,html,task):
        html = base64.b64decode(html).decode(encoding='utf8')
        #print (html,'html+++++')
        platform = task['platform']
        sort = task['other']['sort']
        kind = task['other']['kind']
        ppage = task['other']['page']
        data = []
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S BJT", time.localtime(time.time()))
        if platform == 'jd_web':
            try:
                page = html#去掉
                doc = pq(page)
                goods = doc('li[class="gl-item"] div[class="gl-i-wrap j-sku-item"]').items()
                for mygood in goods:
                    mysku = mygood.attr('data-sku')
                    data.append(mysku)
            except Exception as e:
                print (e)
            return {'time': timeStr, 'key_search': 0, 'key_word': None, 'platform': platform, 'sort': sort,
                'kind': kind, 'page': ppage, 'order': data}
        elif platform == 'jd_app':
            try:
                page = json.loads(html) #去掉
                page = page['value']
                page = json.loads(page)
                mydatalist = page['wareList']['wareList']
                for index, item in enumerate(mydatalist):
                    data.append(item['wareId'])
            except Exception as e:
                print(e)
            finally:
                return {'time': timeStr, 'key_search': 0, 'key_word': None, 'platform': platform, 'sort': sort,
                        'kind': kind, 'page': ppage, 'order': data}


    @classmethod
    def isAntiSpider(cls, html,task):
        html = str(base64.b64decode(html), encoding='utf8')
        isAntiSpier = False
        platform = task['platform']
        if platform == 'jd_app':
            constStr1 = '{"areaName":"","value":"{\\"searchFilter\\":{\\"filterItemPromotion\\":{},\\"filterItemAttrs\\":[],\\"filter\\":[]},\\"wareList\\":{\\"adEventId\\":\\"\\",\\"errorCorrection\\":\\"\\",\\"gaiaContent\\":false,\\"hasTerm\\":true,\\"isFoot\\":false,\\"isSpecialStock\\":\\"0\\",\\"showStyleRule\\":\\"\\",\\"wareCount\\":0}}'
            constStr2 = '{"areaName":"","value":"{\\"searchFilter\\":{\\"filterItemPromotion\\":\\"{\\\\\\"imgUrl\\\\\\":\\\\\\"http:\\/\\/m.360buyimg.com\\/mobilecms\\/jfs\\/t5491\\/219\\/1639317102\\/1775\\/467927d7\\/5912bc85Nfe97ec68.png\\\\\\",\\\\\\"promotionId\\\\\\":\\\\\\"423909\\\\\\",\\\\\\"name\\\\\\":\\\\\\"618\\\\\\",\\\\\\"promType\\\\\\":\\\\\\"icon\\\\\\"}\\",\\"filter\\":[{\\"classfly\\":\\"\\",\\"itemArray\\":[{\\"itemName\\":\\"\\",\\"termList\\":[{\\"otherAttr\\":{},\\"text\\":\\"京东配送\\",\\"value\\":{\\"bodyValues\\":\\"1\\",\\"bodyKey\\":\\"self\\"}},{\\"otherAttr\\":{},\\"text\\":\\"货到付款\\",\\"value\\":{\\"bodyValues\\":\\"1\\",\\"bodyKey\\":\\"cod\\"}},{\\"otherAttr\\":{},\\"text\\":\\"仅看有货\\",\\"value\\":{\\"bodyValues\\":\\"1\\",\\"bodyKey\\":\\"stock\\"}},{\\"otherAttr\\":{},\\"text\\":\\"促销\\",\\"value\\":{\\"bodyValues\\":\\"1\\",\\"bodyKey\\":\\"promotion\\"}},{\\"otherAttr\\":{},\\"text\\":\\"全球购\\",\\"value\\":{\\"bodyValues\\":\\"1\\",\\"bodyKey\\":\\"globalPurchaseFilter\\"}},{\\"otherAttr\\":{},\\"text\\":\\"PLUS尊享\\",\\"value\\":{\\"bodyValues\\":\\"1\\",\\"bodyKey\\":\\"plusWareFilter\\"}}]}],\\"itemKey\\":\\"\\",\\"key\\":\\"configuredFilters\\",\\"otherAttr\\":{}}]},\\"wareList\\":{\\"adEventId\\":\\"\\",\\"errorCorrection\\":\\"\\",\\"gaiaContent\\":false,\\"hasTerm\\":true,\\"isFoot\\":false,\\"isSpecialStock\\":\\"0\\",\\"showStyleRule\\":\\"\\",\\"wareCount\\":0}}"}'
            charStr1 = '\\"wareCount\\":0'
            charStr2 = '京东下载页'
            charStr3 = '专业网上购物平台品质保障'
            if html == constStr1:
                isAntiSpier = True
            if html == constStr2:
                isAntiSpier = True
            if html.find(charStr1) is not -1:
                isAntiSpier = True
            if html.find(charStr2) is not -1:
                isAntiSpier = True
            if html.find(charStr3) is not -1:
                isAntiSpier = True
        return isAntiSpier


    @classmethod
    def run(cls,task,obj_db):#dbcon 数据库连接
        tb = obj_db.choice_crawl_table()  # 进入抓取任务表
        task_data = obj_db.find_one(tb,{})
        if task_data:
            obj_id = task_data['body']
            body = obj_db.gridfs_get_crawldata(obj_id)  # 读出gridfs
            #obj_db.gridfs_del_crawldata(obj_id)  # 将body从文档中删除
            body = eval(body)  # 还原body
            task_data['body'] = body
            print (body)
            print ('get_data')
        """
        #返回的抓取结果中的html文件base64,所以在解析的时候需要反解
        print ('run')
        obj = excutor_main.excutor_cls(obj_db)
        urls = cls.get_urls(task)#url['useproxy']字段为true,interface内部如果有代理会分配代理
        arg = {'urls': urls, 'guid': task['guid'], 'topic': task['topic']}
        ptask = obj.yield_interface(arg,timeout=30000)# 第二个参数为超时时间的设定
        result={'guid':task['guid'],'result':[],'data':[],'topic':task['topic']}
        #生成的存储任务字段，增加data_lenth_flag字段代表数据长度是否（1，0）大于16M，upload_type 字段代表存储的数据类型，无法解析的html/解析数据／其他
        if ptask:
            results = ptask['body']['result']
            for index, _result in enumerate(results):
                if cls.isAntiSpider(_result['html'], _result):
                    result['result'].append({'platform':_result['platform'],'sort':_result['other']['sort'],'kind':_result['other']['kind'],'page':_result['other']['page'],'html':'isAntiSpider'})
                    continue
                data = cls.parser(_result['html'],_result)
                if data and len(data.get('order'))>=1:
                    result['result'].append({'platform': _result['platform'],'sort': _result['other']['sort'],'kind': _result['other']['kind'], 'page': _result['other']['page'],'html': 'has parsed'})
                else:
                    result['result'].append({'platform': _result['platform'], 'sort': _result['other']['sort'],'kind': _result['other']['kind'], 'page': _result['other']['page'],'html':'error'})
                result['data'].append(data)
            #得到解析数据插入数据库，根据不同的数据调用不同的接口，并且为特定的字段标识，接口内部负责填充
            #obj.data_save(result)#大于16m的存储数据接口
            obj.data_lt16M_save(result)#小于16m的存储数据接口
            #obj.html_sava()#无法解析的html文件存储接口，只包含一个html文件，所以数据不大于16m
        """

    """
    @classmethod
    def print(cls):
        print ("ok")
    """
    """
    @classmethod
    def pre_run(cls):
        tObj = getSock_topic()
        req = {'topic':'kind','count':1}
        task = tObj.send_and_get_json(req)
        print (task)
        urllist = self.get_urls(task)
        uObj = getSock_url()
        for index, item in enumerate(urllist):
            urlTask = {'topic':task,'url':item}
            ret = uObj.send_and_get_json(urlTask)
            if ret['ret'] is not 'ok':
                uObj.send_and_get_json(urlTask)
            print (index+1)
    """
    @classmethod
    def parser_run(cls):
        pass



if __name__ == '__main__':
    task = {'device':{'type': '', 'version': '127.22', 'id': ''},
        'guid': '9a4e4a10-45d6-11e7-9169-a860b60c7382',
        'time': time.time(),
        'timeout': 1200,
        'topic': 'jd_task_kind',
        'interval': 86400,  # 任务执行周期间隔时间
        'suspend': 0,  # 暂停标识
        'status': 0,
        'body': {
             'kind': '9987,830,866', 'platform': 'jd_app', 'sort': None,
                }
    }

    obj = oprate_task_job(9995)
    ret = obj.add_task(task)
    print (ret)
    obj = jd_task_kind()
    obj.run(task)
