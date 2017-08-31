#-*- coding -*-
from excutor_doc.jd_tools import *
from excutor_doc.excutor_main import *
import json,requests


class jd_task_ad_kind:

    @classmethod
    def get_urls(cls, task):
        kind = task['body']['kind']
        platform = task['body']['platform']
        nkind = kind.replace(',', '-')
        kindlist = kind.split(',')
        if platform == 'jd_web':
            myheader = {
                'accept': '*/*',
                'accept-encoding': 'gzip, deflate, sdch',
                'accept-language': 'zh-CN,zh;q=0.8',
                'connection': 'keep-alive',
               # 'origin': '',
              #  'host': '',
                'referer': '',
                'user-agent': '',
                'cookie': ''
            }
            myheader['referer'] = 'https://list.jd.com/list.html?cat='+kind
            myheader['user-agent'] = jd_tools.get_web_useragent()
            #myheader['cookie'] = '__jda=122270672.1494312539932474915468.1494312539.1494397179.1494403391.5'#'1755''46''47'
          #  mycookie_jda='122270672.1494312539932474915468.1494312539.1494316225.1494387263.3'
            url_top = 'https://x.jd.com/ShowInterface?ad_ids=46%3A3&ad_type=7&spread_type=1&cai_type=1&cid='+nkind+'&new_list=1&page=1' #callback=jQuery6103743&
            url_left1 = 'https://x.jd.com/ShowInterface?ad_ids=47%3A10&ad_type=7&spread_type=1&cai_type=1&cid='+nkind+'&new_list=1&page=1'  #callback=jQuery6247725&
            url_left2 = 'https://mixer.jd.com/mixer?p=504000&pin=&uuid=1316223881&lid=1&lim=10&ec=utf-8&c1='+kindlist[0]+'&c2='+kindlist[1]+'&c3='+kindlist[2]+'&hi=brand%3A%2Cprice%3A%2Cpage%3A1&_=1493277510336' #callback=call37761&
            url_left3 = 'https://x.jd.com/ShowInterface?ad_ids=547%3A2&ad_type=7&spread_type=1&cai_type=2&cid='+nkind+'&new_list=1&page=1' #callback=jQuery335458&
            url_center = 'https://x.jd.com/ShowInterface?ad_type=7&new_list=1&spread_type=1&ad_ids=1755%3A6&urlcid3='+kindlist[2]+'&ev=&location_info=1_72_2799_0&my=gg666'#callback=jQuery6438130&   &pin=&__jda='+mycookie_jda+'
            url_bottom1 = 'https://x.jd.com/ShowInterface?ad_ids=48%3A5&ad_type=7&spread_type=1&cai_type=1&cid='+nkind+'&new_list=1&template=0&page=1' #callback=jQuery4042230&
            url_bottom2 = 'https://mixer.jd.com/mixer?lid=1&lim=20&ec=utf-8&uuid=1316223881&pin=&p=202002&sku=&ck=pinId,lighting,pin,ipLocation,atw,aview&c1='+kindlist[0]+'&c2='+kindlist[1]+'&c3='+kindlist[2]+'&hi=brand:,price:,page:1&_=1493277921044' #&callback=jQuery2269180
            method = 'GET'
            myurl = {'url': url_top, 'method': method, 'header': myheader,'position':'top'}
            urls.append(myurl)
            myurl = {'url': url_left1, 'method': method, 'header': myheader,'position':'left1'}
            urls.append(myurl)
            myurl = {'url': url_left2, 'method': method, 'header': myheader, 'position':'left2'}#加不加cookie结果都一样
            urls.append(myurl)
            myurl = {'url': url_left3, 'method': method, 'header': myheader, 'position':'left3'}
            urls.append(myurl)
            myurl = {'url': url_center, 'method': method, 'header': myheader, 'position':'center'}
            urls.append(myurl)
            myurl = {'url': url_bottom1, 'method': method, 'header': myheader, 'position':'bottom1'}
            urls.append(myurl)
            myurl = {'url': url_bottom2, 'method': method, 'header': myheader,'position':'bottom2'}

            return  myurl
        elif platform == 'jd_app':
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
                'referer': '',
                'user-agent': '',
                #   'cookie': '',
            }
            myheader['origin'] = 'https://so.m.jd.com'
            myheader['referer'] = 'https://so.m.jd.com/products/'+nkind+'.html'
            myheader['user-agent'] = jd_tools.get_app_useragent()
            url = 'https://so.m.jd.com/ware/searchList.action'
            method = 'POST'
            data = {'_format_':'json','sort':None,'stock':0,'page':1,'categoryId':kindlist[2],'c1':kindlist[0],'c2':kindlist[1]}
            return {'url':url, 'method':method,'header': myheader,'data':data, 'position':'center'}

    @classmethod
    def parser_top(cls, html):
      #  left = 'jQuery6103743('
      #  right = ')'
      #  page = html[html.find(left) + left.__len__():html.rfind(right)]
        page = html
        page = json.loads(page)
        productlist = page['46']
        skuInfoList = []
        for index, item in enumerate(productlist):
            imagePath = 'http://img12.360buyimg.com/n4/'+ item['image_url'].replace('\/','/')
            skuInfoList.append({'sku':item['sku_id'], 'ad_image':imagePath})
        return skuInfoList

    @classmethod
    def parser_left1(cls, html):
      #  left = 'jQuery6247725('
      #  right = ')'
      #  page = html[html.find(left) + left.__len__():html.rfind(right)]
        page = html
        page = json.loads(page)
        productlist = page['47']  # '1755''46'
        skuInfoList = []
        for index, item in enumerate(productlist):
            imagePath = 'http://img13.360buyimg.com/cms/s190x190_' + item['image_url'].replace('\/', '/')
            skuInfoList.append({'sku': item['sku_id'], 'ad_image': imagePath})
        return skuInfoList

    @classmethod
    def parser_left2(cls, html):
      #  left = 'call37761('
      #  right = ')'
      #  page = html[html.find(left) + left.__len__():html.rfind(right)]
        page = html
        page = json.loads(page)
        productlist = page['data']
        skuInfoList = []
        for index, item in enumerate(productlist):
            imagePath = 'http://img13.360buyimg.com/cms/s190x190_' + item['img']
            skuInfoList.append({'sku': item['sku'], 'ad_image': imagePath})
        return skuInfoList

    @classmethod
    def parser_left3(cls, html):
      #  left = 'jQuery335458('
      #  right = ')'
      #  page = html[html.find(left) + left.__len__():html.rfind(right)]
        page = html
        page = json.loads(page)
        productlist = page['547']
        shopInfoList = []
        for index, item in enumerate(productlist):
            imagePath = 'http://img12.360buying.com/n7/'+item['image_url'].replace('\/','/')
            shopInfoList.append({'shopid':item['shop_id'],'ad_image':imagePath})
        return shopInfoList

    @classmethod
    def parser_center(cls, html):
      #  left='jQuery6438130('
      #  right = ')'
      #  page = html[html.find(left) + left.__len__():html.rfind(right)]
        page = html
        page = json.loads(page)
        productlist = page['1755']
        skuInfoList=[]
        for index, item in enumerate(productlist):
            imagePath = 'http://img11.360buyimg.com/n7/'+ item['image_url'].replace('\/','/')
            skuInfoList.append({'sku':item['sku_id'],'ad_image':imagePath})
        return skuInfoList

    @classmethod
    def parser_bottom1(cls, html):
      #  left = 'jQuery4042230('
      #  right = ')'
      #  page = html[html.find(left) + left.__len__():html.rfind(right)]
        page = html
        page = json.loads(page)
        productlist = page['48']
        skuInfoList = []
        for index, item in enumerate(productlist):
            imagePath = 'http://img13.360buyimg.com/cms/s190x190_'+ item['image_url'].replace('\/','/')
            skuInfoList.append({'sku':item['sku_id'],'ad_image':imagePath})
        return skuInfoList

    @classmethod
    def parser_bottom2(cls, html):
      #  left = 'jQuery2269180('
      #  right = ')'
      #  page = html[html.find(left) + left.__len__():html.rfind(right)]
        page = html
        page = json.loads(page)
        productlist = page['data']
        skuInfoList = []
        for index, item in enumerate(productlist):
            imagePath = 'http://img11.360buyimg.com/n3/' + item['img']
            skuInfoList.append({'sku':item['sku'],'ad_image':imagePath})
        return skuInfoList

    @classmethod
    def parser_center_app(cls,html):
        page = json.loads(html)
        page = page['value']
        page = json.loads(page)
        mydatalist = page['wareList']['wareList']
        adlist = []
        for index, item in enumerate(mydatalist):
            if item['exposalUrl'] is not '':
                adlist.append({'sku': item['wareId'],'ad_image':item['imageurl']})
        return adlist

    @classmethod
    def parser(cls,html,task):
        para = task['body']['url']['position']
        platform = task['body']['platform']
        if platform == 'jd_web':
            if para=='top':
                data = cls.parser_top(html)
            elif para == 'left1':
                data = cls.parser_left1(html)
            elif para == 'left2':
                data = cls.parser_left2(html)
            elif para == 'left3':
                data = cls.parser_left3(html)
            elif para == 'center':
                data = cls.parser_center(html)
            elif para =='bottom1':
                data = cls.parser_bottom1(html)
            elif para == 'bottom2':
                data = cls.parser_bottom2(html)
            return data
        elif platform == 'jd_app':
            if para == 'center':
                data = cls.parser_center_app(html)
            return data

    @classmethod
    def run(cls,task,obj_db):
        urls = cls.get_urls(task)
        header = urls['header']
        url = urls['url']
        data = urls['data']
        text = requests.post(headers=header, url=url,data=data,timeout=task['timeout'])
        res = cls.parser(text.text, task)
        result = {'guid': task['guid'], 'result': [], 'data': [], 'topic': task['topic']}
        result['data'] = res
        print (res)
        obj = excutor_cls(obj_db)
        obj.data_lt16M_save(result)  # 小于16m的存储数据接口




if __name__ == '__main__':
    kind = '9987,830,13658'
    platform = 'jd_app'
    task = {
        'device': {'type': '', 'version': '127.22', 'id': ''},
        'guid': 'wwewewewew',
        'time': 444452,  # time.time(),
        'timeout': 60,  # 任务执行超时时间，从执行到完成的时间，超时则退出执行
        'topic': 'jd_task_ad_kind',
        'interval': 86400,  # 任务执行周期间隔时间
        'suspend': 0,  # 暂停标识
        'status': 0,
        'body': {
            'kind':'9987,830,13658', 'platform': platform,'url':{'position':'center'}
        }

    }
    obj = jd_task_ad_kind()
    obj.run(task)