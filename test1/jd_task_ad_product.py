#-*- utf-8 -*-
#移动端产品后面有"为你推荐"
#from excutor_doc.jd_tools import jd_tools
from jd_tools import jd_tools
import json,requests,time

#13860081643


class jd_task_ad_product:
    @classmethod
    def get_urls(cls, task):
        sku = task['body']['sku']
        platform = task['body']['platform']

        if platform == 'jd_app':
            myheader={
                'accept':'application/json',
                'accept-encoding':'gzip, deflate, sdch, br',
                'accept-language':'zh-CN,zh;q=0.8',
                'referer':'https://item.m.jd.com/product/'+str(sku)+'.html',
                'user-agent':''
            }
            myheader['user-agent'] = jd_tools.get_app_useragent()
            url = 'https://item.m.jd.com/ware/uniformRecommend.json?wareId='+str(sku)

        return {'url':url,'header':myheader}

    @classmethod
    def parser(cls, html, task):
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S BJT", time.localtime(time.time()))
        platform = task['body']['platform']
        skulist = []
        if platform == 'jd_app':
            page = json.loads(html)
            mylist = page['uniformRecommendList']
            for index, item in enumerate(mylist):
                skulist.append(item['wareId'])
        return skulist
        """
        {'time': timeStr, 'key_search': 0, 'key_word': None, 'platform': platform, 'sort': sort,
         'kind': kind, 'page': ppage, 'order': data}
        """

    @classmethod
    def run(cls,task):#task,obj_db
        item= cls.get_urls(task)
        header = item['header']
        url = item['url']
        print ('header>>>>:',header)
        print('url>>>>:',url)
        text = requests.get(headers=header,url=url,timeout=task['timeout'])
        data = cls.parser(text.text,task)
        print (data,'********')
        result = {'guid': task['guid'], 'result': [], 'data': [], 'topic': task['topic']}
        if data:#得到解析结果
            result['result'].append({'platform': task['body']['platform'], 'html': 'has parsed'})
            result['data'] = data
        else:#没有解析结果
            result['result'].append({'platform': task['body']['platform'], 'html': 'error'})
            result['data'].append(data)

        print (result)
        #obj.data_lt16M_save(result)  # 小于16m的存储数据接口
if __name__ =='__main__':
    task = {
        'device': {'type': '', 'version': '127.22', 'id': ''},
        'guid': 'wwwwee',
        'time': 444452,  # time.time(),
        'timeout': 60,#任务执行超时时间，从执行到完成的时间
        'topic': 'jd_task_ad_product',
        'interval': 86400,  # 任务执行周期间隔时间
        'suspend': 0,  # 暂停标识
        'status': 0,
        'body': {
            'sku':13860081643 , 'platform': 'jd_app',
        }

    }
    obj = jd_task_ad_product()
    obj.run(task)
