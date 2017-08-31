
#此脚本将从中间层获取任务，执行器，抓取器，解析器，发送器的功能方法都封装,本地一个任务封装了一组相同类型的任务
#可进行业务拆分

"""
topic名称定义：
抓取任务：jm_crawl
解析任务：parsing
发送任务：send

"""

import time,queue,base64,socket
import motor.motor_asyncio
import asyncio,aiohttp
from gridfs import *
from pymongo import MongoClient
from client_doc import setting

class excutor_cls:

    async def db_findandupdate(self,table,query,update,sort=''):#查找数据并且更新数据,表，条件，更新内容,默认获取最大值
        #return await self.tb.find_one({'topic': topic})
        return await self.tb.find_and_modify(query=query, update=update,sort=sort)  # 获取解析任务并从数据表中删除


    async def db_findandremov(self, topic='JM_Crawl'): #只返回查找的第一条数据
        #return await self.tb.find_one({'topic': topic})
        return await self.tb.find_and_modify(query={'topic': topic}, remove=True)  # 获取解析任务并从数据表中删除

    async def db_delete(self, arg):  # 删除数据
        await self.tb.remove(arg)

    async def db_insert(self, task):  # 插入数据
        try:
            body = task['body']
            obj_id =self.fs.put(bytes(str(body), encoding='utf-8'))
            task['body'] = str(obj_id)  # 将文档的id存储进去
            a = await self.tb.update(
                {

                    'topic': task['topic'],
                },
                task,
                True
            )
        except Exception as e:
            print('Inser Error:',e)

    def __init__(self):
        self.count = 0
        #lib requests/aiohttp
        #本地生成的任务格式统一如下，服务器生成的多个本地任务将全部集成到一个任务中
        self.local_task = {

                            'topic':'jm_crawl',
                             'guid':'',#沿用服务器下发的任务id
                             'body':
                                    {
                                     'crawl':{'name':'','version':''},
                                     'urls':'',
                                     'abstime':'',
                                    #异步字段（是否使用异步）
                                    #使用平台
                                    #content主要是一组任务共有的关键信息
                                     'content':{

                                                'proxymode':'auto','encode':'utf-8',
                                                'lib':'aiohttp','max_retry':0,'bulk':False,
                                                'cookie':'','debug':False,'usephantomjs':False,

                                               },
                                    'result':[],#{'url': '', 'time': '', 'html': '', 'error': '', 'proxy': '', 'retry': 0, 'headers': '', 'other': '', 'sucess': False, 'platform': ''}
                                    'parsing_data':[],
                                    'callback':{"topic":'parsing',},
                                    }

                             }#excutor_interface的输出，catcher_interface的输入


        self.semaphore = asyncio.Semaphore(100)
        self.url_q = asyncio.Queue()
        self.result_q = asyncio.Queue()


        #存放抓取任务的数据库
        conn = motor.motor_asyncio.AsyncIOMotorClient(setting.DATABASES_IP, 27017,connect=False)
        db = conn[setting.CRAWL_TASK_DATA]
        self.tb = db[setting.CRAWL_TASK_TABLE]

        pdb = conn['jame_bd']
        self.ptable1 = pdb['jame_proxy1']
        self.ptable = pdb['jame_proxy']


        #存放解析任务的数据库
        #存储result的文档,大文件的文档
        conn1 = MongoClient(setting.DATABASES_IP, 27017, connect=False)
        dat = conn1[setting.CRAWL_TASK_DATA]
        self.fs = GridFS(dat,setting.CRAWL_TASK_BODY)



    def run(self):
        tasks = []
        for _ in range(0, setting.AIOHTTP_CONCURRENCY_SUM):
            tasks.append(self.work())#抓取任务
        tasks.append(self.create_parstask())  # 将同一任务分解的单个抓取任务得到的数据拼接为一个解析任务
        tasks.append(self.get_crawltask())  # 将任务分解为单个抓取任务
        f = asyncio.wait(tasks)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(f)
        self.url_q.join()
        self.result_q.join()

    async def work(self):
        while True:
            await asyncio.sleep(0)
            url = await self.get_url()
            if url:
                await self.parseUrl(url)

    async def get_crawltask(self):#将任务分解为单个抓取任务
        while True:
           # print ('url_q:',self.url_q.qsize(),"result_q",self.result_q.qsize())
            if self.url_q.qsize() < 500:#存储抓取url的队列小于500时才会重新获取一个抓取任务，但是存储url的队列有可能大于500，如队列长度为499时，一个抓取任务分解1000个url就为1499个
                task = await self.db_findandremov('JM_Crawl') #从数据库查找一个抓取任务
                if task:
                    print('分解抓取任务***************')
                    urls = task['body']['urls']
                    guid = task['guid']
                    callback = task['body']['callback']
                    task_count= len(urls)
                    for url in urls:
                        url['guid'] = guid#将服务器下发的任务id添加进去
                        url['task_count'] = task_count#将任务总数加到url中
                        url['callback'] = callback#
                        await self.url_q.put(url)  # 将url添加到队列

                else:
                    await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(0.1)


    async def get_url(self):
        try:
            url = await self.url_q.get()
        except:
            pass
        return url


    async def create_parstask(self):#拼接解析任务
        i = 0
        j = 0
        while True:
            result = await self.result_q.get()#取到url解析相关的内容
            j += 1
            print('task *************************',j)
            if result:
                collection = str(result['url']['guid']) + '_queue'  # 拼接到解析任务自己队列
                try:
                    queue_name = getattr(self, collection)
                except:
                    setattr(self, collection, queue.Queue(0))  # 没ut有队列就创建
                    queue_name = getattr(self, collection)
                finally:
                    queue_name.put(result)  # 添加数据
                if queue_name.qsize() >= result['url']['task_count']:  # 队列长度大等于任务的总url个数
                    print('reday插入数据库1***********')
                    task = {

                            'topic':'jm_crawl',
                             'guid':'',#沿用服务器下发的任务id
                             'body':
                                    {
                                     'crawl':{'name':'','version':''},
                                     'urls':'',
                                     'abstime':'',
                                    #异步字段（是否使用异步）
                                    #使用平台
                                    #content主要是一组任务共有的关键信息
                                     'content':{
                                                'proxymode':'auto','encode':'utf-8',
                                                'lib':'aiohttp','max_retry':0,'bulk':False,
                                                'cookie':'','debug':False,'usephantomjs':False,
                                               },
                                    'result':[],#{'url': '', 'time': '', 'html': '', 'error': '', 'proxy': '', 'retry': 0, 'headers': '', 'other': '', 'sucess': False, 'platform': ''}
                                    'parsing_data':[],
                                    'callback':{"topic":'parsing',},
                                    }

                             }#excutor_interface的输出，catcher_interface的输入

                    task['topic'] = result['url']['callback']['topic']
                    for _ in range(result['url']['task_count']):
                        tmp = queue_name.get()
                        tmp['url'] = tmp['url']['url']
                        task['body']['result'].append(tmp)
                        #print (queue_name.qsize(),"**************",result['url']['task_count'])
                    #将解析任务写到数据库
                    i += 1
                    try:
                        task.pop('_id')
                    except:
                        pass
                    await self.db_insert(task)  # 插入数据库
                    print(' 生成解析********',i)
                self.result_q.task_done()
            else:
                await asyncio.sleep(0.1)



    async def parseUrl(self,url):
        try:
            await self.aiohttp_lib(url)
        except Exception as e:
            print('Failed....', e, url['url'])
            # return page

    async def aiohttp_lib(self,url):  #可用
        #result中除了time,html,sucess,status,其他都为url中获取
        result = {'url': '', 'time': '','html': '', 'retry': 0, 'sucess': False,'status':0,'error':'','headers':{},'platform':'', "proxy_info":{
                                    "is_use_proxy":False, #bool 是否使用代理
                                    "use_succ":False ,# bool 代理是否使用成功
                                    "proxy_type": 'default',#string 使用蓝灯时填入landeng 使用其他代理时填入default
                                    "proxy_url": "", #string 使用的代理的完整的url
                                    "exec_time_ms":0, #int64 使用代理访问一共多长时间 毫秒
                                    "proxy_detail":"127.0.0.1:3000" ,#string  代理详情
                                    },'other':'',

                                  "content_judge": {  # 字典 检查内容
                                      "is_judge": False,  # bool 是否执行检查内容
                                      "should_exist": [  # 数组  应该存在的
                                          {  # 字典
                                              "context": "",  # string 需要检查的内容
                                              "judge_result": False, # bool 该内容是否存在
                                          },
                                      ],
                                      "no_should_exist": [  # 数组  不应该存在的
                                          {  # 字典
                                              "context": "",  # string 需要检查的内容
                                              "judge_result": False,  # bool 该内容是否存在
                                          },
                                      ]
                                  },

                    }  # url字段对应了的内容包含所有内容

        headers = {}
        headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36 vulners.com/bot'})
        # guid代表父任务id,count代表该任务总共有多少页
        method = 'GET'
        data = None
        html = None
        proxy = None
        restime = None
        try:
            if url['useproxy']:#true用代理
                try:
                    proxy = url['proxy']#得到具体代理
                except:#没有携带代理，抓取器分配代理
                    #获取代理
                    try:
                        proxy_res = await self.get_proxy(self.ptable)#获取代理信息
                        tmp =  proxy_res['ipInfo']
                        #'ipInfo.ip' 'ipInfo.port' 'ipInfo.ptl'+
                        if tmp:
                                if isinstance(tmp.get('ip'), bytes):
                                    tmp = tmp.get('ip').decode('utf-8')
                                proxy = 'http://' + tmp.get('ip') + ':' + str(tmp.get('port'))

                    except:
                        pass
        except:
            pass
        list = url.keys()
        all_list = ['data', 'header', 'method']
        for item in all_list:
            if item in list:
                if item == 'method':
                    method = url['method']
                elif item == 'data':
                    data = url['data']
                elif item == 'header':
                    headers = url['header']

        conn = aiohttp.TCPConnector(verify_ssl=False,
                                    limit=100,  #连接池在windows下不能太大, <500
                                    use_dns_cache=True)
        try:
            myhost = url['other'].get('host', 'https://www.jd.com')
        except:
            pass
        with (await self.semaphore):
            async with aiohttp.ClientSession(connector=conn, headers=headers) as session:
                while True:

                    try:
                        starttime=time.time()
                        if method == 'POST':
                            #with aiohttp.Timeout(0.1):设置请求的超时时间
                            async with session.post(url['url'],data=url['data'], headers=url['header'],proxy=proxy,timeout=3) as resp:
                                if resp.status == 200:
                                    restime = time.time()-starttime
                                    html =await resp.text()
                        elif method == 'GET':
                            async with session.get(url['url'],params=url['data'], headers=url['header'],proxy=proxy,timeout=3) as resp:
                                if resp.status == 200:
                                    restime = time.time()-starttime
                                    html =await resp.text()


                    except Exception as e:
                        if result['retry'] >= 5:
                            print('抓取的url超时', e)
                            break
                    if html:
                        print('得到数据的代理：', proxy)
                        result['sucess'] = True
                        result['html'] = base64.b64encode(bytes(html,encoding='utf8')).decode(encoding='utf8')
                        #代理有效，代理提升分数
                        if url['useproxy']:  # true用代理
                            try:
                                url['proxy']  #得到具体代理
                            except:  # 用代理却没有携带代理，代理打分
                                if proxy_res:#如果获取到了代理
                                    await self.backproxy(self.ptable,proxy_res, {'result': True, 'host': myhost,
                                                                  'resTime':restime,
                                                                  'deviceInfo': {'id': setting.DEVICE_ID,
                                                                                 'type': setting.DEVICE_TYPE}})

                        break
                    else:
                        if result['retry'] >= 5:
                            try:
                                if proxy_res:  # 如果获取到代理，打分
                                    await self.backproxy(self.ptable, proxy_res, {'result': False, 'host': myhost,
                                                                                  'resTime': restime,
                                                                                  'deviceInfo': {
                                                                                      'id': setting.DEVICE_ID,
                                                                                      'type': setting.DEVICE_TYPE}})
                            except:
                                pass
                            break
                        try:
                            if url['useproxy']:  # true用代理
                                try:
                                    proxy = url['proxy'] #得到具体代理
                                except:  # 用代理却没有携带代理，代理打分
                                    # 为抓取失败的代理减分 ,tmp 为代理数据库返回的真实数据，tmp['_id']
                                    if  proxy_res:#如果获取到代理，打分
                                        await self.backproxy(self.ptable, proxy_res, {'result': False, 'host': myhost,
                                                                                'resTime': restime,
                                                                                'deviceInfo': {'id': setting.DEVICE_ID,
                                                                                               'type': setting.DEVICE_TYPE}})
                                    try:
                                        proxy_res = await self.get_proxy(self.ptable)  # 抓取失败更换代理
                                        tmp =  proxy_res['ipInfo']
                                        if tmp:

                                                if isinstance(tmp.get('ip'), bytes):
                                                    tmp = tmp.get('ip').decode('utf-8')
                                                proxy = 'http://' + tmp.get('ip') + ':' + str(tmp.get('port'))

                                        else:#没有代理
                                            break
                                    except:
                                        pass

                        except:
                            pass
                        result['retry'] += 1  # 重试次数加1

                resp.release()
                session.close()
                conn.close()
                self.url_q.task_done()
                result['url'] = url
                result['headers'] = url['header']
                result['time'] = time.time()
                result['platform'] = url['platform']
                result['data'] = url['data']
                result['other'] = url['other']#{'sort','page','kind'}
                await self.result_q.put(result)#将单个url的抓取结果放入队列
                self.count  += 1
                #print ('抓取*********',result,self.result_q.qsize())
                #print ( url['task_count'],'****',self.count,'---------',self.result_q.qsize())

    async def get_proxy(self,tbobj): #获取代理

        proxyip =await tbobj.find_and_modify(query={'ipInfo.status': 1, 'usetime': {'$lte': (time.time() - 5 * 60)}},
                                        update={'$set': {'usetime': time.time()}, '$inc': {'ipInfo.count': 1}},
                                        )  # 'ipInfo.status':1,'usetime':{'$lte':(time.time()-5*60)}

        if proxyip:#得到代理
            return proxyip
        else:
            await tbobj.update({'ipInfo.status': 4},{'$set': {'ipInfo.count': 0, 'ipInfo.status': 1}})#将状态4的代理更新
            proxyip = await tbobj.find_and_modify(
                query={'ipInfo.status': 1, 'usetime': {'$lte': (time.time() - 5 * 60)}},
                update={'$set': {'usetime': time.time()}, '$inc': {'ipInfo.count': 1}},
                )  # 'ipInfo.status':1,'usetime':{'$lte':(time.time()-5*60)}

        return proxyip

    async def backproxy(self, tbobj, proxyip,
                  retdict):  # retdict字典要求有三个字段:'host','result','resTime','deviceInfo'('id','type')
        if (proxyip is None) or (proxyip.get('_id') is None):
            return
        host = retdict.get('host', 'https://www.jd.com')
        if isinstance(host, str):
            hoststr = host[host.find(':') + 3:].replace('.', '_').replace('/', '__')
        else:
            print(host, "不是字符串类型")
            return
        ret = retdict.get('result', False)
        resTime = retdict.get('resTime')
        if ret == False:
            tscore = -10
        elif (resTime is None) or (isinstance(resTime, float) == False):
            tscore = 1
        elif resTime <= 1.0:
            tscore = 10
        elif resTime <= 2.0:
            tscore = 9
        elif resTime <= 3.0:
            tscore = 8
        elif resTime <= 4.0:
            tscore = 7
        elif resTime <= 5.0:
            tscore = 6
        elif resTime <= 6.0:
            tscore = 5
        elif resTime <= 7.0:
            tscore = 4
        elif resTime <= 8.0:
            tscore = 3
        elif resTime <= 9.0:
            tscore = 2
        elif resTime <= 10.0:
            tscore = 1
        else:
            tscore = 0
        if ret == True:  # 访问成功
            susscore = 1
        else:  # 访问不成功
            susscore = 0

        tempstr1 = 'ipInfo.score.' + hoststr + '.' + 'score'
        tempstr2 = 'ipInfo.score.' + hoststr + '.' + 'usecount'
        tempstr3 = 'ipInfo.score.' + hoststr + '.' + 'suscount'

        await tbobj.find_and_modify(query={'_id': proxyip.get('_id')},
                              update={'$inc': {'ipInfo.count': -1, tempstr1: tscore, tempstr2: 1, tempstr3: susscore}},
                              new=True)

        if proxyip and proxyip.get('ipInfo') and proxyip.get('ipInfo').get('count') < 5 and proxyip.get('ipInfo').get(
                'count') > -5 and proxyip.get('ipInfo').get('status') == 4:
            await tbobj.find_and_modify(query={'_id': proxyip.get('_id')}, update={'$set': {'ipInfo.status': 1}})
        if proxyip and proxyip.get('ipInfo') and (
                        proxyip.get('ipInfo').get('count') < -5 or proxyip.get('ipInfo').get(
                    'count') > 5) and proxyip.get(
            'ipInfo').get('status') == 1:
            await tbobj.find_and_modify(query={'_id': proxyip.get('_id')}, update={'$set': {'ipInfo.status': 4}})
        # 记录使用记录
        mydvInfo = retdict.get('deviceInfo')
        if mydvInfo:
            devdata = {'device':  # 使用情况#设备
                           {'id': mydvInfo.get('id', socket.getfqdn(socket.gethostname())),  # 设备名
                            'info': {  # 待定,辅助id确定使用机器的唯一性,若为已知机器可通过id确定唯一性,则此字段可为空
                                'type': mydvInfo.get('type', 'pc'),  # 设备类型(pc/moble)
                            }},
                       'time': time.localtime(time.time()),  #使用记录时间
                       'interval': 5 * 60,  # 使用间隔
                       }
            await tbobj.find_and_modify(query={'_id': proxyip.get('_id')}, update={'$push': {'ipInfo.use': devdata}})



def catcher():
    print ('catcher')
    t = excutor_cls()
    t.run()

if __name__ =='__main__':
    t = excutor_cls()
    #t.test()
    t.run()
    #task = t.Access_to_task('get_task','',count=1)[0]
    #print (task)
    #t.catcher_interface(task)#抓取任务接口，因为本地任务是相同类型任务的集合，所以此接口内部一次只取一个任务，然后分解并发
    #t.parsing_interface(task)

    """
    for i in task_list:
        t.excutor_interface(i)
    """