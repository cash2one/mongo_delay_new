# coding:utf-8
import json
import random

from _interface import oprate_task_job
from utils import get_page_nouse_proxy

'''

id: 10362686122,
guid: "2390603f-e3af-4fa7-a2ed-e20cc94c76ac",
content: "挺好的，老人用足够了，好好好，不卡，内存大，外观好看，直",
creationTime: "2017-05-01 22:21:40",
isTop: false,
referenceId: "2249594",
referenceImage: "jfs/t2359/140/1910645068/303777/36d06010/5680a02dN848c1634.jpg",
referenceName: "华为 畅享5S 金色 移动联通电信4G手机 双卡双待",
referenceTime: "2017-03-30 13:24:52",
referenceType: "Product",
referenceTypeId: 0,
firstCategory: 9987,
secondCategory: 653,
thirdCategory: 655,
replyCount: 0,
score: 5,
status: 1,
title: "",
usefulVoteCount: 0,
uselessVoteCount: 0,
userImage: "storage.360buyimg.com/i.imageUpload/6a645f3538343062653565376461656331343533353430343036323138_sma.jpg",
userImageUrl: "storage.360buyimg.com/i.imageUpload/6a645f3538343062653565376461656331343533353430343036323138_sma.jpg",
userLevelId: "62",
userProvince: "",
viewCount: 0,
orderId: 0,
isReplyGrade: false,
nickname: "h***9",
userClient: 2,
productColor: "金",
productSize: "全网通",
integral: -20,
userImgFlag: 1,
anonymousFlag: 1,
userLevelName: "金牌会员",
plusAvailable: 103,
productSales: [ ],
recommend: false,
userLevelColor: "#666666",
userClientShow: "来自京东iPhone客户端",
isMobile: true,
days: 32,
afterDays: 0
'''
'''
Host: club.jd.com
Connection: keep-alive
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36
Accept: */*
Referer: https://item.jd.com/3133498.html
Accept-Encoding: gzip, deflate, sdch, br
Accept-Language: zh-CN,zh;q=0.8,ru;q=0.6,en;q=0.4,fr;q=0.2,ja;q=0.2,ko;q=0.2

'''

# 任务分为首页任务和块任务
# 首页任务是一个特殊的块任务，永远只有1页
# 块任务属性有起始页，结束页，下一次执行页，对与应此页号，保存了当时的maxpage
# 同时还有对应的起始时间，结束时间，下一次执行执行
# 块任务的页用于快速找到上次执行的具体位置
# 块任务的几个时间用于精确定位上次扫描的位置

# 现在确定0~69页不防爬
# 由于京东改版maxpage现在只精确到前2位数字，maxpage不再有很大的意义
# 因此修改为重点监控前70页，通过监控前70页，得知增加了多少评论（减少的会很麻烦）
# 知道增加了多少页，可以推出后面需要跳转多少页。
# 如果中间有删除的，需要逆向抓取

'''
抓取逻辑：
    现在只记录起始时间，结束时间
        起始页，结束页
        
    共有这种工作模式：RunInit，RunFirst，RunHead,RunTail,RunTailRev
  
    RunInit：
        抓首页，初始化资料。 
        
        如果maxPge大于0，进入RunTail模式
        
        否则进入RunFirst
        
    RunFirst：
        抓首页：
            如果结果的起始时间比task中的记录更晚，说明有空档，进入RunHead模式，RunHead.StartTime更新，RunHeadPage=1
            如果起始时间没变，说明头部无空缺，进入RunTail模式
            
    RunHead:
        页号递增，抓取
            没遇到StratTime,继续前进，更新页号，返回
            直到遇到StartTime，更新任务StartTime，根据本次新增的页（incPage），修正RunTail.NextPage，设置为RunFirst
            
    RunTail：
         状态不是结束(遇到终点设置为结束），继续下面
         抓RunTail.NextPage，看本页最晚时间（StartTime）
            如果比EndTime晚（大），说明有重复数据，继续向前抓就好了
            如果比EndTime早（小），说明中间有空档，进入RunTailRev模式
          
            如果本次执行已向前抓了100页(可并发），或遇到终点，模式返回RunFirst        
            如果遇到某页不足10个，说明已全部抓光，模式设置为结束，模式返回RunFirst

    RunTailRev:
        抓当前页，逆向，直到遇到EndTime，返回RunTail
    

    执行器策略：
        先看看是否有首页到时间的，有，执行
             （这种是针对没有评论和已经抓结束的）
        首页都执行过了，依次执行别的页
        循环
    
'''

from JD_Comments_Task import JdComments_task, JdComments_task_mode
from JD_Comments_Parse import JdCommentsParse
import config
from utils import JM_Time

import urllib.parse


class JdCommentTaskExec(object):
    TOPIC = 'JDCOMMENTSTASK'
    VERISON = '1.1.0'
    # BaseUrl = 'http://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98vv51384&productId=2712431&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0 '
    def __init__(self, task):
        self.jdtask = JdComments_task(task)
        self.sync = False  # 执行模式
        return

    # 此函数用于测试
    @staticmethod
    def crawl(sku, page=0):
        url = JdCommentTaskExec.make_url(sku, page)
        html = get_page_nouse_proxy(url)
        #print('Crawal')
        return html

    @property
    def task(self):
        return self.jdtask.task

    @staticmethod
    def make_url(sku, page=0):
        # 按时间排序  sortType = 6
        baseurl = 'https://club.jd.com/comment/skuProductPageComments.action?&score=0&sortType=6&pageSize=10&isShadowSku=0&productId='
        pagestr = '&page=%d' % page
        callback = '&callback=fetchJSON_comment98vv'

        url = baseurl + str(sku) + pagestr + callback + str(random.randint(311, 99455))
        return url

    @staticmethod
    def parse_url(url):
        '''
        从url中提取sku,page
        :param url: 
        :return: sku,page
        '''
        q = urllib.parse.urlsplit(url).query
        parse = dict(urllib.parse.parse_qsl(q))

        return parse

    @staticmethod
    def make_headers(sku):
        base_headers = {
            'Host': 'club.jd.com',
            'Connection': 'close',
            # 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'https://item.jd.com/%d.html' % sku,
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,ru;q=0.6,en;q=0.4,fr;q=0.2,ja;q=0.2,ko;q=0.2',
        }

        return base_headers

    def do_init(self):
        # print(task)
        ret, code, task = JdComments_task.check_task(self.jdtask)
        if code != 0:
            return self.make_crawl_task([0])

        jdtask = JdComments_task()
        jdtask.task = task

        # print('mode=',jdtask.CurRunMode)
        if jdtask.CurRunMode == JdComments_task_mode.RunInit:
            return self.make_crawl_task([0])

    def do_First(self):
        return self.make_crawl_task([0])

    def do_Head(self, task):
        jdtask = self.jdtask
        if not jdtask.RunHead_NextPage:
            jdtask.RunHead_NextPage = 1

        sku = jdtask.sku
        return JdCommentTaskExec.make_crawl_task([jdtask.RunHead_NextPage])

    def do_Tail(self):

        if self.jdtask.RunTail_isOver:
            self.jdtask.CurRunMode = JdComments_task_mode.RunFirst
            return None

        jdtask = self.jdtask
        if not jdtask.RunTail_NextPage:
            jdtask.RunTail_NextPage = 1

        if not jdtask.RunTail or jdtask.RunTail == {} or jdtask.RunTail_createtime == None:
            jdtask.RunTail_createtime = config.NOW()
            jdtask.RunTail_StartPage = jdtask.RunTail_NextPage
            jdtask.RunTail_EndPage = min(100 + jdtask.RunTail_NextPage, jdtask.maxPage)

            pages = []
            for page in range(jdtask.RunTail_StartPage, jdtask.RunTail_EndPage):
                pages.append(page)

            JdCommentTaskExec.save_task(jdtask.task)
            return self.make_crawl_task(pages)
        else:
            # 检查任务是否超时，如果超时，重置任务
            if (JM_Time(config.NOW()) - jdtask.RunTail_createtime) >= 3600 * 2:
                jdtask.initRunTail()
                jdtask.CurRunMode = JdComments_task_mode.RunFirst
        return None

    def do_TailRev(self):
        return JdCommentTaskExec.make_crawl_task([self.jdtask.RunTailRev_PrevPage])

    def do_init_parse(self, parse):
        jdtask = self.jdtask
        if parse.page != 0:
            raise ValueError('page 应该为0，请检查是不是哪里搞错了')

        # 如果没有评论
        if jdtask.maxPage == 0:
            jdtask.CurRunMode = JdComments_task_mode.RunFirst

            return
        # 有评论
        # print(parse.comments)
        # 修改好预期的状态，准备上传

        jdtask.StartTime = parse.StartTime
        jdtask.EndTime = parse.EndTime

        # 如果本次不足10个
        if parse.comments_count < 10:
            jdtask.RunTail_isOver = True
            jdtask.CurRunMode = JdComments_task_mode.RunFirst
        else:
            jdtask.CurRunMode = JdComments_task_mode.RunTail

        JdCommentTaskExec.save_comments(parse.comments, jdtask.task)
        # 当评论成功上传后修改数据库中的task，解除锁定
        return

    def do_first_parse(self, parse):
        jdtask = self.jdtask
        if parse.page != 0:
            raise ValueError('page 应该为0，请检查是不是哪里搞错了')

        # 没有新的数据
        if jdtask.StartTime == parse.StartTime:
            if not jdtask.RunTail_isOver:
                # 转入抓尾部模式
                jdtask.CurRunMode = JdComments_task_mode.RunTail
                JdCommentTaskExec.save_task(jdtask.task)
            return

        # 如果任务StartTime 比 结果的 StartTime 小（早）
        if jdtask.StartTime < parse.StartTime:
            # 说明有新的记录
            # 以下又可以分为两种情况：
            # 新增的就在本页，没有新的页，存储

            if jdtask.StartTime <= parse.EndTime:
                jdtask.StartTime = parse.StartTime
                if not jdtask.RunTail_isOver:
                    jdtask.CurRunMode = JdComments_task_mode.RunTail

                JdCommentTaskExec.save_comments(parse.comments, jdtask.task)
            else:
                jdtask.CurRunMode = JdComments_task_mode.RunHead
                jdtask.RunHeadInit()
                # 设置本次Head任务终点为之前的StartTime
                jdtask.RunHead_StartTime = jdtask.StartTime

                jdtask.StartTime = parse.StartTime
                JdCommentTaskExec.save_comments(parse.comments, jdtask.task)
        else:
            raise ValueError('正常不会这样')

        JdCommentTaskExec.save_task(jdtask.task)
        return

    # 由于并发问题，批量抓取需要批量返回结果，否则靠数据库同步也会很复杂
    # 批量的情况只有RunTail
    def do_tail_parse(self, parses):
        jdtask = self.jdtask
        '''
            抓RunTail.NextPage，看本页最晚时间（StartTime）
            如果比EndTime晚（大），说明有重复数据，继续向前抓就好了
            如果比EndTime早（小），说明中间有空档，进入RunTailRev模式
          
            如果本次执行已向前抓了100页(可并发），或遇到终点，模式返回RunFirst        
            如果遇到某页不足10个，说明已全部抓光，模式设置为结束，模式返回RunFirst
        '''
        # 如果是最小的页，并且创建时间比较久，检查是不是有空档，修改EndTime

        minnotokpage = jdtask.RunTail_EndPage + 1
        isOverPage = jdtask.RunTail_EndPage + 1
        EndTime = None

        need2rev = False
        lastEndTime = jdtask.EndTime

        for parse in parses:
            if parse.isAntiSpider:
                minnotokpage = min(minnotokpage, parse.page)
                continue

            if parse.comments_count < 10:
                print(type(parse.page), page, type(isOverPage), isOverPage)
                isOverPage = min(parse.page, isOverPage)

            if parse.comments_count > 0:
                JdCommentTaskExec.save_comments(parse.comments, jdtask.task)

            if parse.page == jdtask.RunTail_StartPage:
                if ((JM_Time(config.NOW()) - jdtask.RunTail_createtime) > 3600):
                    if jdtask.RunTail_StartPage > 1:
                        if parse.StartTime < jdtask.EndTime:
                            need2rev = True

        if minnotokpage > jdtask.RunTail_StartPage and (minnotokpage != jdtask.RunTail_EndPage + 1):
            jdtask.EndTime = parses[minnotokpage - 1]
            jdtask.RunTail_NextPage = minnotokpage
            jdtask.EndPage = minnotokpage - 1

        if isOverPage >= jdtask.RunTail_StartPage and (isOverPage != jdtask.RunTail_EndPage + 1):
            jdtask.maxPage = isOverPage
            jdtask.RunTail_isOver = True

        if need2rev:
            jdtask.CurRunMode = JdComments_task_mode.RunTailRev
            jdtask.RunTailRev_EndTime = lastEndTime
            jdtask.RunTailRev_EndPage = jdtask.RunTail_StartPage
            jdtask.RunTailRev_CurEndTime = None
            jdtask.RunTailRev_PrevPage = jdtask.RunTailRev_EndPage - 1
        else:
            jdtask.CurRunMode = JdComments_task_mode.RunFirst

        jdtask.initRunTail()
        JdCommentTaskExec.save_task(self.task)

    '''
        # 反向运行
        task[config.ROW_BODY][JdComments_task_mode.RunTailRev] = {}
        task[config.ROW_BODY][JdComments_task_mode.RunTailRev]['EndTime'] = None  # 进入时的结束时间，用于比较是不是填满空
        task[config.ROW_BODY][JdComments_task_mode.RunTailRev]['EndPage'] = None  # 进入时的页数
        task[config.ROW_BODY][JdComments_task_mode.RunTailRev]['PrevPage'] = None
        task[config.ROW_BODY][JdComments_task_mode.RunTailRev]['CurEndTime'] = None  # 进入后第一页的EndTime
    '''

    def do_tailrev_parse(self, parse):
        jdtask = self.jdtask

        if jdtask.RunTailRev_CurEndTime == None:
            jdtask.RunTailRev_CurEndTime = parse.EndTime

        if parse.comments_count > 0:
            JdCommentTaskExec.save_comments(parse.comments, jdtask.task)
        # 填充结束
        if JM_Time(parse.StartTime) > jdtask.RunTailRev_EndTime:
            jdtask.CurRunMode = JdComments_task_mode.RunTail

        if jdtask.RunTailRev_PrevPage < 2:
            jdtask.RunTailRev_PrevPage = jdtask.RunTailRev_PrevPage - 1

    '''
        RunHead:
        页号递增，抓取
            没遇到StratTime,继续前进，更新页号，返回
            直到遇到StartTime，更新任务StartTime，根据本次新增的页（incPage），修正RunTail.NextPage，设置为RunFirst
            
        task[config.ROW_BODY][JdComments_task_mode.RunHead] = {}
        task[config.ROW_BODY][JdComments_task_mode.RunHead]['IncPage'] = 0  # 本次头部新增页数
        task[config.ROW_BODY][JdComments_task_mode.RunHead]['NextPage'] = None
        task[config.ROW_BODY][JdComments_task_mode.RunHead]['StartTime'] = None  # 进入时的StarTime,用于检查是否填满
    '''

    def do_head_parse(self, parse):
        jdtask = self.jdtask
        jdtask.RunHead_IncPage += 1

        if parse.comments_count > 0:
            JdCommentTaskExec.save_comments(parse.comments, jdtask.task)

        if JM_Time(parse.EndTime) < jdtask.RunHead_StartTime:
            # 结束头部填充模式
            jdtask.CurRunMode = JdComments_task_mode.RunFirst
            jdtask.RunTail_NextPage += jdtask.RunHead_IncPage
            JdCommentTaskExec.save_task(jdtask.task)
        else:
            jdtask.RunHead_NextPage += 1

    def do_Parse(self, html, page):
        parse = JdCommentsParse(html, page)
        # print('aaaa',parse.comments)
        jdtask = self.jdtask

        if parse.comments_count > 0:
            JdCommentTaskExec.save_comments(parse.comments, jdtask.task)

        if parse.page == 0:
            # 修正间隔历史
            jdtask.addStartTimeRecord(parse.comments)
            jdtask.First_Page_Scan_last_scan_time = config.NOW()
            jdtask.productCommentSummary = parse.productCommentSummary
            jdtask.hotCommentTagStatistics = parse.hotCommentTagStatistics

        jdtask.maxPage = parse.maxPage

        if jdtask.CurRunMode == JdComments_task_mode.RunInit:
            self.do_init_parse(parse)
            return

        if jdtask.CurRunMode == JdComments_task_mode.RunFirst:
            self.do_first_parse(parse)
            return

        if jdtask.CurRunMode == JdComments_task_mode.RunHead:
            self.do_head_parse(parse)
            return

        if jdtask.CurRunMode == JdComments_task_mode.RunTail:
            self.do_tail_parse([parse])
            return

        if jdtask.CurRunMode == JdComments_task_mode.RunTailRev:
            self.do_tailrev_parse(parse)
            return

    def do_Parses(self, htmls, pages):
        if self.jdtask.CurRunMode != JdComments_task_mode.RunTail:
            raise ValueError('多个网页同时解析只能用于RunTail模式')

        parses = []
        hp = zip(htmls, pages)
        for html, page in hp:
            parse = JdCommentsParse(html, page)

            if parse.comments_count > 0:
                JdCommentTaskExec.save_comments(parse.comments, self.task)

            parses.append(parse)

        self.do_tail_parse(parses)

    def run(self, task={}):
        if task != {}:
            self.jdtask = JdComments_task(task)
        # RunInit，RunFirst，RunHead,RunTail,RunTailRev
        if self.jdtask.CurRunMode == JdComments_task_mode.RunInit:
            return self.do_init()

        if self.jdtask.CurRunMode == JdComments_task_mode.RunFirst:
            return self.do_First()

        if self.jdtask.CurRunMode == JdComments_task_mode.RunHead:
            return self.do_Head()

        if self.jdtask.CurRunMode == JdComments_task_mode.RunTail:
            return self.do_Tail()

        if self.jdtask.CurRunMode == JdComments_task_mode.RunTailRev:
            return self.do_TailRev()

        return self.do_init()

    def sync_run(self):
        '''
        同步执行任务
        :param task: json格式的任务或python对象或JdComments_task
        :return:
        '''
        jdtask = self.jdtask
        self.sync = True

        if jdtask.CurRunMode == JdComments_task_mode.RunInit:
            results = self.do_init()
            if len(results) > 0:
                results[0]['']

    # 获得任务实体，正常是从数据库里获得，测试时内存获得
    @staticmethod
    def get_task(sku, task=None):
        if task:
            return task
        # 从数据库里获得task
        return JdCommentTaskExec.get_task_from_database(sku)

    # 在这里填写从数据库获得task的相关的代码
    @staticmethod
    def get_task_from_database(sku):
        info = {"body.sku": sku, "topic": ""}  # 定义查询条件
        oprate_task_jobs=oprate_task_job()
        task = oprate_task_jobs.pop_task(info)  # 根据条件获取任务信息
        return json.loads(task)

    # 把修正后的task写入数据库
    @staticmethod
    def save_task(task):
        oprate_task_jobs = oprate_task_job()
        oprate_task_jobs.update_task(task)

    # 评论写入数据库
    @staticmethod
    def save_comments(comments, task):
        # 数据上传成功后才能修改任务状态
        # recv data
        tasks = task
        tasks['Body']['result'] = comments  # 将评论数据添加到body中
        oprate_task_jobs = oprate_task_job()
        status = oprate_task_jobs.upload_data(content=tasks)  # 上传数据
        if status == 'recv data':  # 数据上传成功
            JdCommentTaskExec.save_task(task)  # 将当前任务状态保存

    def make_crawl_task(self, pages):
        '''

        :param pages: 要抓的页
        :param sync: 同步
        :return: 同步方式发送抓取任务，等待结果，返回带抓取结果的任务
                异步发送抓取任务，返回抓取任务
        '''
        # ToDo 需要完善成完整任务
        '''
        {
            'topic':'JM_Crawl',
            'guid':'',#沿用服务器下发的任务id
            'body':
            {
             'crawl':{'name':'','version':''},
             'urls':[url,url],
             'abstime':'',
             #content主要是一组任务共有的关键信息
             'content':{

                        'proxymode':'auto','encode':'utf-8',
                        'lib':'requests','max_retry':0,'bulk':False,
                        'cookie':'','debug':False,'usephantomjs':False,

                       },
             'result':[{'url':'','time':'','html':'','retry':''},],
             'callback':{},
            }
        }
        '''
        task_info = {
            'topic': 'JM_Crawl',
            'guid': 'JDCOMMENTSTASK_%d' % self.jdtask.sku,  # 沿用服务器下发的任务id
            'body':
                {
                    'sku': self.jdtask.sku,
                    'crawl': {'name': 'JDCOMMENTSTASK', 'version': '1.0.0'},
                    'urls': [],
                    'abstime': '',
                    # content主要是一组任务共有的关键信息
                    'content': {
                        'proxymode': 'auto',
                        'encode': 'utf-8',
                        'lib': 'requests',
                        'max_retry': 0,
                        'bulk': False,
                        'cookie': '',
                        'debug': False,
                        'usephantomjs': False
                    },
                    # 'result': [{'url': '', 'time': '', 'html': '', 'retry': ''}, ],
                    'callback': {}
                }}
        urls = []
        for page in pages:
            if page>=70:
                continue
            url_info = {
                'url': self.make_url(self.jdtask.sku, page),
                'header': self.make_headers(self.jdtask.sku),
                'useproxy': False,
                'platform': 'jd_pc',
                'method': 'GET'
            }
            if page >= 70:
                url_info['useproxy'] = True

            urls.append(url_info)
        task_info['body']['urls'] = urls
        return task_info


if __name__ == "__main__":
    print(JdComments_task_mode.RunTail)


    def getmode(task):
        return task['Body']['CurRunMode']


    task = JdComments_task.make_task(3938531)
    print(task)
    # print(json.dumps(task))
    exec = JdCommentTaskExec(task)
    pages = exec.run(task)
    print(pages, getmode(task))

    html = JdCommentTaskExec.crawl(3938531)

    print('aaa', getmode(task))
    exec.do_Parse(html, 0)

    print('bbb', getmode(task), task)

    pages = exec.run(task)

    # print('cccc',exec.task)
    print('ccc', pages)

    htmls = []
    for page in pages:
        html = JdCommentTaskExec.crawl(3938531, page)
        htmls.append(html)

    exec.do_Parses(htmls, pages)

    pages = exec.run()

    print('dddd',pages)
