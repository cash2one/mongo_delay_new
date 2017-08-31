#-*- utf-8 -*-
from io import StringIO
import uuid,time,pymongo,base64,gzip,codecs
from excutor_doc.jd_tools import *
from excutor_doc.excutor_main import *
#from center_layer.center_interface._interface import *

class jm_task_proxyverificate:
    @classmethod
    def updateDict(cls, args):
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
    @classmethod
    def generateTask(cls):#getVerificateTask(cls):
        # 检查数据库,将大于验证时间的代理挑出来
       # proxylist = []
        obj = excutor_cls()
        ptb = obj.db_obj.choice_table('jame_proxy1')
        arr = ptb.find({})
        for index, item in enumerate(arr):
            tempip = item.pop('_id')
            ptlstr = tempip.get('ipInfo').get('ptl').lower()
            ptllist = ptlstr.split('/')
            if len(ptllist) == 1:
                ptllist = ptllist[0].split(',')
            for i in range(len(ptllist)):
                tempip['ipInfo']['ptl'] = ptllist[i]
                task_proxyip = {'device': {'type': '', 'version': '127.22', 'id': ''},
                                'guid': str(uuid.uuid1()),
                                'time': time.time(),  # time.time(),
                                'timeout': 1200,
                                'topic': 'jm_task_proxyverificate',
                                'interval': 86400,  # 任务执行周期间隔时间
                                'suspend': 0,  # 暂停标识
                                'status': 0,
                                'body': tempip  # myip.get("ipInfo")
                                }
                #   print (task_proxyip)
                ttb = obj.db_obj.choice_table('task_main')
                obj.db_obj.insert_data(ttb, task_proxyip)
        """
        proxylist = [{"ip":"120.210.32.5","port":"80","ptl":"https","score":{"www_baidu_com":
                                                                                        {"responseTime":32,
                                                                                         "transfersVelocity":3,
                                                                                         "lastTime":"2017-06-09 11:02:30 GMT",
                                                                                         "score":10,
                                                                                         "usecount":100,
                                                                                         "suscesscount":50,
                                                                                         "useInterval":502
                                                                                        },
                                                                            "www_jd_com":{"responseTime":32,
                                                                                         "transfersVelocity":3,
                                                                                         "lastTime":"2017-06-09 11:02:30 GMT",
                                                                                         "score":10,
                                                                                         "usecount":100,
                                                                                         "suscesscount":50,
                                                                                         "useInterval":502
                                                                                        },
                                                                            "www_taobao_com":
                                                                                        {"responseTime":32,
                                                                                         "transfersVelocity":3,
                                                                                         "lastTime":"2017-06-09 11:02:30 GMT",
                                                                                         "score":10,
                                                                                         "usecount":100,
                                                                                         "suscesscount":50,
                                                                                         "useInterval":502
                                                                                        },
                                                                            "www_google_com":
                                                                                       {"responseTime":32,
                                                                                         "transfersVelocity":3,
                                                                                         "lastTime":"2017-06-09 11:02:30 GMT",
                                                                                         "score":10,
                                                                                         "usecount":100,
                                                                                         "suscesscount":50,
                                                                                         "useInterval":502
                                                                                        }},
                      "task": {"verificate": {"www_baidu_com":
                                                  {"interval": 86400,
                                                   "lastTime": "2017-06-09 09:03:30 GMT",
                                                   "status": 0,
                                                   "timeout": 300
                                                   },
                                              "www_jd_com":
                                                  {"interval": 86400,
                                                   "lastTime": "2017-06-09 09:03:30 GMT",
                                                   "status": 0,
                                                   "timeout": 300
                                                   },
                                              "www_taobao_com":
                                                  {"interval": 86400,
                                                   "lastTime": "2017-06-09 09:03:30 GMT",
                                                   "status": 0,
                                                   "timeout": 300
                                                   },
                                              "www_google_com":
                                                  {"interval": 86400,
                                                   "lastTime": "2017-06-09 09:03:30 GMT",
                                                   "status": 0,
                                                   "timeout": 300
                                                   }
                                              }}},
                     {"ip": "188.25.25.5", "port": "80", "ptl": "https", "score": {"www_baidu_com":
                                                                                        {"responseTime": 32,
                                                                                         "transfersVelocity": 3,
                                                                                         "lastTime": "2017-06-09 11:02:30 GMT",
                                                                                         "score": 10,
                                                                                         "usecount": 100,
                                                                                         "suscesscount": 50,
                                                                                         "useInterval": 502
                                                                                         },
                                                                                    "www_jd_com": {"responseTime": 32,
                                                                                                   "transfersVelocity": 3,
                                                                                                   "lastTime": "2017-06-09 11:02:30 GMT",
                                                                                                   "score": 10,
                                                                                                   "usecount": 100,
                                                                                                   "suscesscount": 50,
                                                                                                   "useInterval": 502
                                                                                                   },
                                                                                    "www_taobao_com":
                                                                                        {"responseTime": 32,
                                                                                         "transfersVelocity": 3,
                                                                                         "lastTime": "2017-06-09 11:02:30 GMT",
                                                                                         "score": 10,
                                                                                         "usecount": 100,
                                                                                         "suscesscount": 50,
                                                                                         "useInterval": 502
                                                                                         },
                                                                                    "www_google_com":
                                                                                        {"responseTime": 32,
                                                                                         "transfersVelocity": 3,
                                                                                         "lastTime": "2017-06-09 11:02:30 GMT",
                                                                                         "score": 10,
                                                                                         "usecount": 100,
                                                                                         "suscesscount": 50,
                                                                                         "useInterval": 502
                                                                                         }},
                      "task": {"verificate": {"www_baidu_com":
                                                  {"interval": 86400,
                                                   "lastTime": "2017-06-09 09:03:30 GMT",
                                                   "status": 0,
                                                   "timeout": 300
                                                   },
                                              "www_jd_com":
                                                  {"interval": 86400,
                                                   "lastTime": "2017-06-09 09:03:30 GMT",
                                                   "status": 0,
                                                   "timeout": 300
                                                   },
                                              "www_taobao_com":
                                                  {"interval": 86400,
                                                   "lastTime": "2017-06-09 09:03:30 GMT",
                                                   "status": 0,
                                                   "timeout": 300
                                                   },
                                              "www_google_com":
                                                  {"interval": 86400,
                                                   "lastTime": "2017-06-09 09:03:30 GMT",
                                                   "status": 0,
                                                   "timeout": 300
                                                   }
                                              }}
                      }]
                      """
    """
        return proxylist
    @classmethod
    def generateTask(cls):
        proxylist = cls.getVerificateTask()
        tasks = []
        count = 0
        addN = 3
        for i in range(len(proxylist)):
            guid = str(uuid.uuid1())  # 根据时间戳生成随机的uuid
            dictUpdate = {'guid': guid, 'time': time.time() + count,
                          'body': proxylist[i]}
            basic_task = cls.updateDict(dictUpdate)
            tasks.append(basic_task)
            count += addN
        return tasks
"""
    @classmethod
    def getHostlist(cls,task):
        hostlist=[]
        hostDict = task['body']['ipInfo']['task']['verifi']
        for index,item in enumerate(hostDict):
            host = item.replace('__','/').replace('_','.')
            hostlist.append(host)
        return hostlist

    @classmethod
    def get_urls(cls, task):
        ip = task['body']['ipInfo']['ip']
        port = task['body']['ipInfo']['port']
        ptl = task['body']['ipInfo']['ptl']
        urlList = []
        page = 1
        hostlist=cls.getHostlist(task)
        method = 'GET'
        myheader = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, sdch',
            'accept-language': 'zh-CN,zh;q=0.8',
            'connection': 'keep-alive',
            #   'origin': '',
            #     'host': '',
       #     'referer': '',
            'user-agent': '',
            #   'cookie': ''
        }
      #  myheader['referer'] = 'http://baidu.com/'
      #  myheader['host']='www.baidu.com'
      #  myheader['host']='www.taobao.com'
        myheader['user-agent'] = jd_tools.get_web_useragent()
        useproxy = True
        proxy = {'ip':ip,'port':port,'ptl':ptl}
        for i in range(len(hostlist)):
            url = 'http://'+hostlist[i]
            myurl = {'url': url, 'method': method, 'header': myheader, 'useproxy': useproxy,'proxy_info':{'is_use_proxy':True,'proxy_type':'default','proxy_detail':proxy.get('ip')+':'+str(proxy.get('port'))}}
            urlList.append(myurl)
            url = 'https://' + hostlist[i]
            myurl = {'url': url, 'method': method, 'header': myheader, 'useproxy': useproxy, 'proxy_info': {'is_use_proxy':True,'proxy_type':'default','proxy_detail':proxy.get('ip')+':'+str(proxy.get('port'))}}
            urlList.append(myurl)
        return urlList

    @classmethod
    def parser(cls, html, task):
        print ("验证任务的解析:",task)
     #   print('html:', html)
        data = False
        if task.get('url')=='http://www.baidu.com' or task.get('url')=='https://www.baidu.com':#.get('url')
            if html.find("百度一下，你就知道") != -1:
                data = True
        elif task.get('url')=='http://www.jd.com' or task.get('url')=='https://www.jd.com':#.get('url')
            if html.find("淘宝网")!=-1:
                data = True
        elif task.get('url')=='http://www.taobao.com' or task.get('url')=='https://www.taobao.com':#.get('url')
            if html.find("京东(JD.COM)-正品低价、品质保障、配送及时、轻松购物！")!=-1:
                data=True
        print ('parser result:',data)
        return data

    @classmethod
    def isAntiSpider(cls, html, task):
        return False

    @classmethod
    def score(cls,proxy):
        score = 0
        return score

    @classmethod
    def run(cls, task,obj_db):#此任务需抓取器返回访问一个链接的时间,最好还能返回访问是否成功的状态码

        obj = excutor_cls(obj_db)
        print("proxyverificaterun1+++++++++++")
        try:
            urls = cls.get_urls(task)
            arg = {'urls': urls, 'guid': task['guid'], 'topic': task['topic']}
        except Exception as e:
            print ("proxyverificaterun1e+++++++++++**********",e)
        #print ("arg.urls",arg.get('urls'))
        ptask = obj.yield_interface(arg, timeout=180)  # 第二个参数为超时时间的设定
        print("proxyverificaterun3++++++++++++")
        # print (ptask,"*************ptask")
        zresult = {'guid': task['guid'], 'status': 0, 'result': [], 'data': []}
        passok=False
        if ptask:
            try:
                results = ptask['body']['result']
                for index, _result in enumerate(results):
                    print("proxyverificateloop++++", index,_result.get('proxy_info'),_result.get('error'),len(_result.get('html')))
                    if cls.isAntiSpider(_result['html'], _result):
                        zresult['result'].append({'host': _result['url'], 'proxy':_result['proxy_info'],
                                                  'html': 'isAntiSpider'})
                        continue
                    temphtml = base64.b64decode(_result['html'])
                    html = gzip.decompress(temphtml).decode('utf-8','ignore')
                    data = cls.parser(html, _result)
                    if data:
                        zresult['result'].append({'host': _result['url'],'proxy':_result['proxy_info'],
                                                  'html': 'has parsed'})
                        passok=True
                    else:
                        zresult['result'].append({'host': _result['url'],'proxy':_result['proxy_info'],
                                                  'html': 'error'})#_result['html']
                if passok == True:
                    zresult['topic'] = task.get('topic')
                    zresult['data'] = task.get('body').get('ipInfo')  # .append({'isok':data,'proxy':_result['url']['proxy']})
                    obj.data_lt16M_save(zresult)#obj.data_save(zresult)
                    try:
                        ptb = obj.db_obj.choice_table('jame_proxy')
                        pindex = list(ptb.index_information())
                        if 'ipInfo.ip_1_ipInfo.port_1_ipInfo.ptl_1' not in pindex:
                            ptb.create_index([('ipInfo.ip', pymongo.ASCENDING), ('ipInfo.port', pymongo.ASCENDING),('ipInfo.ptl', pymongo.ASCENDING)], unique=True)
                        obj.db_obj.insert_data(ptb,task.get('body'))#.get('ipInfo')
                        print ("验证完成:",task.get('body').get('ipInfo'))
                    except Exception as e:
                        print ("此代理已有",e,"***",task.get('body').get('ipInfo'))
            except Exception as e:
                print ('run',e)
      #  obj.db_obj.close_connect()
    @classmethod
    def saver(cls):
        pass

    @classmethod
    def saver_server(cls, data, task):  # 运行在server端
        savedata = task['content']['body']['parsing_data']
        #mongodb.insert(savedata, 'jmProxy')

    @classmethod
    def get_next_time(cls):
        pass

    @classmethod
    def parser_run(cls):
        pass

if __name__ == '__main__':
    jpv = jm_task_proxyverificate()
    tasks = jpv.generateTask()
    print (tasks)