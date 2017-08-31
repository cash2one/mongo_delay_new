#-*- coding:utf-8 -*-

from jd_tools import jd_tools
import requests,re,json
class jd_task_ad_keyword:
    @classmethod
    def getMaxPage(cls, task):
        platform = task['body']['platform']
        keyword = task['body']['keyword']
        sort = task['body']['sort']
        if platform == 'jd_web':
            url = 'https://search.jd.com/Search?keyword='+ keyword['urlCoding'] +'&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&click=0'+'&psort='+ sort
            myheader = {}
            myheader['host'] = 'search.jd.com'
            myheader['user_agent'] = jd_tools.get_web_useragent()
         #  myheader['cookie'] = jd_tools.get_jd_web_cookie()
            myheader = jd_tools.get_headers(myheader)
            urldata = requests.get(url, headers=myheader)
            rst = re.search(r'class=\"fp-text\"', urldata)
            if rst is not None:
                strEndPos = rst.end()
                rst1 = re.findall(r'\d+', urldata[strEndPos:strEndPos + 50])
                if rst1 is not None and len(rst1) >= 2:
                    totalPageS = rst1[1]
                    totalPage = int(totalPageS)
        elif platform == 'jd_app':
            url = 'https://so.m.jd.com/ware/search.action?keyword=' + keyword['urlCoding']
            myheader = {}
            myheader['origin'] = 'so.m.jd.com'
            myheader['user-agent'] = jd_tools.get_app_useragent()
            myheader['host'] =None
            myheader['referer']=None
            myheader['cookie']=None
         #  myheader['cookie'] = jd_tools.get_jd_app_cookie()
            myheader = jd_tools.get_headers(myheader)
            urldata = requests.get(url, headers=myheader)
            rst = re.search(r'wareCount', urldata.text)
            if rst is not None:
                strEndPos = rst.end()
                rst1 = re.findall(r'\d+', urldata.text[strEndPos:strEndPos + 15])
                if rst1 is not None and len(rst1) >= 1:
                    totalPageS = rst1[0]
                    totalPage = int(totalPageS)/10
        print (totalPage,'+++++***++++')
        return totalPage

    @classmethod
    def get_urls(cls, task):
        platform = task['body']['platform']
        keyword = task['body']['keyword']
        sort = task['body']['sort']
        urlList=[]
        maxpage = cls.getMaxPage(task)
        if platform == 'jd_web':
            page = 1
            url = 'https://search.jd.com/s_new.php?'
            method = 'GET'
        elif platform == 'jd_app':
            page = 1
            url = 'https://so.m.jd.com/ware/searchList.action'
            method = 'POST'
            myheader = {
                'accept': 'application/json',
                'accept-encoding': 'gzip, deflate, sdch',
                'accept-language': 'zh-CN,zh;q=0.8',
                'content-length': '59',
                'connection': 'keep-alive',
                'content-type': 'application/x-www-form-urlencoded',
                'x-requested-with': 'XMLHttpRequest',
                'origin': '',
                #  'host': '',
                #'cookie':'',
                'referer': '',
                'user-agent': '',
            }
            myheader['user-agent'] = jd_tools.get_app_useragent()
            myheader['origin'] = 'https://so.m.jd.com'
            myheader['referer'] = 'https://so.m.jd.com/ware/search.action?keyword='+ keyword['urlCoding']
         #   myheader['cookie'] = jd_tools.get_jd_app_cookie()
        while(page<=maxpage):
            if platform == 'jd_web':
                myheader = {
                    'accept': '*/*',
                    'accept-encoding': 'gzip, deflate, sdch',
                    'accept-language': 'zh-CN,zh;q=0.8',
                    'connection': 'keep-alive',
                    'origin': '',
                    'host': '',
                    'referer': '',
                    'user-agent': '',
                    'cookie': ''
                }
                myheader['host'] = 'search.jd.com'
                myheader['user_agent'] = jd_tools.get_web_useragent()
              #  myheader['cookie'] = jd_tools.get_jd_web_cookie()
                if page % 2 == 1:
                    data = {'keyword': keyword['urlCoding'], 'enc': 'utf-8', 'qrst': '1', 'rt': '1', 'stop': '1', 'vt': '2', 'page': str(page), 's': str((page - 1) * 30 + 1), 'click': '0', 'psort':sort}
                    myheader['referer'] = 'https://search.jd.com/s_new.php?keyword='+ keyword['urlCoding']+'&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&page='+str(page)+'&s='+str((page - 1) * 30 + 1)+'&click=0&psort='+ sort
                elif page % 2 == 0:
                    data = {'keyword': keyword['urlCoding'], 'enc': 'utf-8', 'qrst': '1', 'rt': '1', 'stop': '1', 'vt': '2', 'page': str(page), 's': str((page - 1) * 30 + 1), 'scrolling': 'y', 'pos': '30','psort': sort}
                    myheader['referer'] = 'https://search.jd.com/s_new.php?keyword='+ keyword['urlCoding']+'&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&page='+str(page)+'&s='+str((page - 1) * 30 + 1)+ '&scrolling=y&pos=30&psort='+ sort
                myheader = jd_tools.get_headers(myheader)
            elif platform == 'jd_app':
                data = {'_format_':'json','stock':'0','sort':sort,'page':page,'keyword':keyword['urlCoding']}
            myurl={'url':url,'method':method,'data':data,'header':myheader}
            urlList.append(myurl)
            page=page+1
        return urlList

    @classmethod
    def parser(cls,html, task):
        platform = task['body']['platform']
        data = []
        if platform == 'jd_web':
            page = html
            rst = re.finditer(r'<li class=\"gl-item\" data-sku=\"', page)
            for index, item in enumerate(rst):
                strEndPos = item.end()
                rst1 = re.search(r'\d+', page[strEndPos:strEndPos + 20])
                if rst1 is not None:
                    data.append(rst1.group(0))
        elif platform == 'jd_app':
            page = json.loads(html)
            page = page['value']
            page = json.loads(page)
            mydatalist = page['wareList']['wareList']
            for index, item in enumerate(mydatalist):
                data.append(item['wareId'])
        return data

    @classmethod
    def run(cls,task):
        print('run')
        urls = cls.get_urls(task)
        """
        obj = excutor_cls(obj_db)
        urls = cls.get_urls(task)  # url['useproxy']字段为true,interface内部如果有代理会分配代理
        arg = {'urls': urls, 'guid': task['guid'], 'topic': task['topic']}
        ptask = obj.yield_interface(arg, timeout=30000)  # 第二个参数为超时时间的设定
        result = {'guid': task['guid'], 'result': [], 'data': [], 'topic': task['topic']}
        # 生成的存储任务字段，增加data_lenth_flag字段代表数据长度是否（1，0）大于16M，upload_type 字段代表存储的数据类型，无法解析的html/解析数据／其他
        if ptask:
            results = ptask['body']['result']
            for index, _result in enumerate(results):
                if cls.isAntiSpider(_result['html'], _result):
                    result['result'].append({'platform': _result['platform'], 'sort': _result['other']['sort'],
                                             'kind': _result['other']['kind'], 'page': _result['other']['page'],
                                             'html': 'isAntiSpider'})
                    continue
                data = cls.parser(_result['html'], _result)
                if data and len(data.get('order')) >= 1:
                    result['result'].append({'platform': _result['platform'], 'sort': _result['other']['sort'],
                                             'kind': _result['other']['kind'], 'page': _result['other']['page'],
                                             'html': 'has parsed'})
                else:
                    result['result'].append({'platform': _result['platform'], 'sort': _result['other']['sort'],
                                             'kind': _result['other']['kind'], 'page': _result['other']['page'],
                                             'html': 'error'})
                result['data'].append(data)
            obj.data_lt16M_save(result)  # 小于16m的存储数据接口
        """
if __name__ == '__main__':
    platform= 'jd_app'
    keyword = '防摔手机壳'
    sort = 'sort_totalsales15_desc'
    task = {
        'device': {'type': '', 'version': '127.22', 'id': ''},
        'guid': 'ttrtrereter',
        'time': 444452,  # time.time(),
        'timeout': 60,  # 任务执行超时时间，从执行到完成的时间，超时则退出执行
        'topic': 'jd_task_ad_keyword',
        'interval': 86400,  # 任务执行周期间隔时间
        'suspend': 0,  # 暂停标识
        'status': 0,
        'body': {
            'platform': platform, 'keyword': {'urlCoding':keyword,}, 'sort': sort
        }
    }
    obj = jd_task_ad_keyword()
    obj.run(task)