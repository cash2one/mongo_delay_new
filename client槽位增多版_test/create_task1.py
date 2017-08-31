
from pymongo import MongoClient
import time,uuid,random

class jd_task_kind:

    def __init__(self):
        conn = MongoClient('localhost', 27017, connect=False)
        self.db = conn['jame_bd']

    @classmethod
    def updateDict(cls, args):
        basic_task = {'device': {'type': '', 'version': '127.22', 'id': ''},
                      'guid': args['guid'],
                      'time': args['time'],  # time.time(),
                      'timeout': 1200,
                      'topic': 'jd_task_kind',
                      'interval': 86400,  # 任务执行周期间隔时间
                      'suspend': 0,  # 暂停标识
                      'status': 0,
                      'body': {
                          'kind': args['body']['kind'], 'platform': args['body']['platform'],
                          'sort': args['body']['sort'],
                      }
                      }
        return basic_task

    @classmethod
    def generateTask(cls):
        tasks = []
        kinds = []
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
        basic_task = {'device': {'type': '', 'version': '127.22', 'id': ''},
                      'guid': '',
                      'time': '',  # time.time(),
                      'timeout': 1200,
                      'topic': 'jd_task_kind',
                      'interval': 86400,  # 任务执行周期间隔时间
                      'suspend': 0,  # 暂停标识
                      'status': 0,
                      'body': {
                          'kind': '', 'platform': '', 'sort': '',
                      }
                      }
        sortlist = ['sort_totalsales15_desc', 'sort_rank_asc', 1, None]  # pc/mobile
        #   platformlist = ['jd_app','jd_web']
        for i in range(len(kinds)):
            for index2, item2 in enumerate(sortlist):
                guid = str(uuid.uuid1())  # 根据时间戳生成随机的uuid
                if item2 == 'sort_totalsales15_desc':
                    dictUpdate = {'guid': guid, 'time': time.time(),
                                  'body': {'kind': kinds[i], 'platform': 'jd_web', 'sort': item2}}
                    basic_task = cls.updateDict(dictUpdate)
                    tasks.append(basic_task)
                elif item2 == 'sort_rank_asc' and (
                            kinds[i] == '9987,830,867' or kinds[i] == '9987,830,866' or kinds[i] == '9987,653,655'):
                    dictUpdate = {'guid': guid, 'time': time.time(),
                                  'body': {'kind': kinds[i], 'platform': 'jd_web', 'sort': item2}}
                    basic_task = cls.updateDict(dictUpdate)
                    tasks.append(basic_task)
                elif item2 == 1:
                    dictUpdate = {'guid': guid, 'time': time.time(),
                                  'body': {'kind': kinds[i], 'platform': 'jd_app', 'sort': item2}}
                    basic_task = cls.updateDict(dictUpdate)
                    tasks.append(basic_task)
                elif item2 is None:
                    dictUpdate = {'guid': guid, 'time': time.time(),
                                  'body': {'kind': kinds[i], 'platform': 'jd_app', 'sort': item2}}
                    basic_task = cls.updateDict(dictUpdate)
                    tasks.append(basic_task)
        return tasks

    def insert_db(self):
        task_list = self.generateTask()

        for task in task_list:

            self.db['task_main'].insert(
               task
            )

class jm_task_proxycrawl:

    def __init__(self):
        conn = MongoClient('localhost', 27017, connect=False)
        self.db = conn['jame_bd']

    def updateDict(self, args):
        basic_task = {'device': {'type': '', 'version': '127.22', 'id': ''},
                      'guid': args.get('guid'),
                      'time': args.get('time'),  # time.time(),
                      'timeout': 1200,
                      'topic': 'jm_task_proxycrawl',
                      'interval': 43200,  # 任务执行周期间隔时间
                      'suspend': 0,  # 暂停标识
                      'status': 0,
                      'body': {
                          'host': args.get('body').get('host'),
                          'script':args.get('body').get('script')
                            }
                      }
        return basic_task

    def generateTask(self):
        hostlist={'crawl_data5u':'http://www.data5u.com',#只首页可用
                  'crawl_xdaili':'http://www.xdaili.cn/freeproxy.html',#只首页可用
                  'crawl_zdaye1':'http://s.zdaye.com',
                #'http://ip.zdaye.com',#nook暂不能运行 #只首页可用['http://s.zdaye.com/?api=201612191506234219&count=200&fitter=2&px=2',]
                  'crawl_bigdaili':'http://www.bigdaili.com/',#只首页可用
                  'crawl_kxdaili':'http://www.kxdaili.com/dailiip.html',#只首页可用['http://svip.kuaidaili.com/api/getproxy/?orderid=919102497581478&num=100&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=2&an_an=1&an_ha=1&sp1=1&sp2=1&sort=2&format=text&sep=1',访问时过期
                  'crawl_kuaidaili1':'http://dev.kuaidaili.com/api/getproxy/',# 'http://dev.kuaidaili.com/api/getproxy/?orderid=904107757119940&num=100&area=%E5%A4%A7%E9%99%86&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=2&an_ha=1&sp1=1&sep=1',
                                                                    #'http://dev.kuaidaili.com/api/getproxy/?orderid=977747109732956&num=100&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=2&an_an=1&an_ha=1&format=text&sep=1&sort=1&sp1=1',]
                'crawl_kuaidaili':'http://img.kuaidaili.com/free/',#ok
                'crawl_yundaili':'http://www.yun-daili.com',#3页可用,但有四种类型
                'crawl_goubanjia':'http://www.goubanjia.com/free/',#解析方法不同->wp-pagenavi可获得总页数
                'crawl_xicidaili':'http://www.xicidaili.com',#ok#->previous_page可获得总页数,4种类型
                'crawl_httpsdaili':'http://httpsdaili.com/free.asp',#ok#->第六个(最后一个)'页'字附近可获得总页数,4种类型#['http://www.httpsdaili.com/?stype=1','http://www.httpsdaili.com/?stype=2','http://www.httpsdaili.com/?stype=3','http://www.httpsdaili.com/?stype=4',]
                'crawl_dlip':'http://www.dlip.cn',#ok#4种类型
                'crawl_ip002':'http://www.ip002.net/free.html',#ok#共9页
                'crawl_iphai':'http://www.iphai.com/free',#['http://www.iphai.com/free/ng','http://www.iphai.com/free/np','http://www.iphai.com/free/wg','http://www.iphai.com/free/wp', ]
                'crawl_fengyunip':'http://www.fengyunip.com',#只首页可用
                'crawl_swei360':'http://www.swei360.com',#['http://www.swei360.com/?stype=1','http://www.swei360.com/?stype=2','http://www.swei360.com/?stype=3','http://www.swei360.com/?stype=4',]
                'crawl_nyloner':'https://nyloner.cn/proxy',
                'crawl_proxy360':'http://www.proxy360.cn/default.aspx',#ok
                'crawl_qiaodm':'http://ip.qiaodm.com/free/index1.html',#ok
                'crawl_nntime':'http://nntime.com/proxy-list-01.htm',#
               'crawl_myproxy':'https://www.my-proxy.com/free-elite-proxy.html',#ok
               'crawl_proxylists':'http://www.proxylists.net',#nook 暂不能运行#只ip和port#'http://www.proxylists.net/countries.html'us,br,cn
               'crawl_freeproxy':'https://free-proxy-list.net',#需翻墙['http://free-proxy-list.net/','http://free-proxy-list.net/anonymous-proxy.html','http://free-proxy-list.net/uk-proxy.html','http://www.us-proxy.org/',]
               'crawl_baizhongsou':'http://ip.baizhongsou.com',#只首页
                'crawl_ip181':'http://www.ip181.com',#只首页,可检测代理ip
                'crawl_mimiip':'http://www.mimiip.com',#似乎没什么价值，时间都很老['http://www.mimiip.com/gngao/','http://www.mimiip.com/gnpu/','http://www.mimiip.com/gntou/','http://www.mimiip.com/hw','http://www.mimiip.com/']
                'crawl_sitedigger':'http://www.site-digger.com',#['http://www.site-digger.com/html/articles/20110516/proxieslist.html',]
                'crawl_coolproxy':'http://www.cool-proxy.net',# ['http://www.cool-proxy.net/proxies/http_proxy_list/page:%d/sort:score/direction:desc' % i for i in range(1,22)]
                #'http://www.freeproxylists.com'#有很多链接,需找其获取规律,eg:'http://www.freeproxylists.com/fr/d1496432428.html'
                #'http://www.proxz.com/'#有很多链接,需找其获取规律,eg:'http://www.proxz.com/proxy_list_transparent_0.html'
                'crawl_xroxy':'http://www.xroxy.com',#有很多链接,需找其获取规律,eg:'http://www.xroxy.com/proxylist.php?port=&type=Transparent&ssl=&country=&latency=&reliability=#table'
                #'http://www.httptunnel.ge/ProxyListForFree.aspx',#需翻墙#只首页
                #'http://m.66ip.cn/mo.php?tqsl=10000'#此链接暂不能访问#只有ip和port,只国内ip内访问
                'crawl_mimvp1':'http://proxy.mimvp.com/api/fetch.php?',#只首页可用#'http://proxy.mimvp.com/api/fetch.php?orderid=860160922170106912&country=中国&http_type=1&num=500&result_fields=1&result_format=txt'
                'crawl_mimvp':'http://proxy.mimvp.com/free.php?',
                'crawl_coobobo':'http://www.coobobo.com',
                'crawl_ipadress':'https://www.ip-adress.com',#可查询ip
                'crawl_proxydb':'http://proxydb.net',
                #'http://rebro.weebly.com',#http://rebro.weebly.com/proxy-list.html
                #'http://www.ajshw.net/news/gnip/20170625/3032.html',
                #'http://www.ndaili.com/free#',
                #'http://ip.zdaye.com/dayProxy.html',
                'crawl_echolink':'http://www.echolink.org',
               # 'http://dl.dainar.net'
                  }
        tasks=[]
        count = 0
        addN = 0#60
        for index, item in enumerate(hostlist):
            guid = str(uuid.uuid1())+ str(random.randint(0,1000000))   # 根据时间戳生成随机的uuid
            dictUpdate = {'guid': guid, 'time': time.time() + count,
                          'body': {'host': hostlist.get(item),'script':item}}
            basic_task = self.updateDict(dictUpdate)
            tasks.append(basic_task)
            count += addN
        return tasks

    def insert_db(self):
        task_list = self.generateTask()

        for task in task_list:

            self.db['task_main'].insert(
               task
            )

if __name__ =='__main__':
    obj = jd_task_kind()
    obj.insert_db()
