# _*_ coding: utf-8 _*_
# @Time    : 2017/7/5 下午3:00
# @Author  : Strongc
# @Author_Email   : qncz2006 # gmail dot com
# @Explain :
# @File    : crawl_list4proxy_de.py
# @Software: PyCharm Community Edition
#45399

import requests
from pyquery import PyQuery as pq
from excutor_doc.excutor_main import *
inhome = 1
climb_wall_proxies = {
    'http':'http://127.0.0.1:45399',#8466
    'https':'https://127.0.0.1:45399'
    }

if inhome == 1:
    climb_wall_proxies = {
        'http':'http://127.0.0.1:43078', #8466
        'https':'https://127.0.0.1:43078'
    }

#抓取流程
#先用普通抓取抓地区分布，得到国家URL，代理数量
#按代理数量逆序排序
#抓数量最多的国家页
#循环国家
#如果代理总数大于300：
#       抓glype,然后抓phproxy
#       抓分类时，返回页面结果和总数。当页号大于根据总数算的页面时，退出。
#       总数初值设为国家总的代理数量
#如果代理总数小于300：
#       抓国家页，分类为空

import time
#import js2py
import base64

js =r"""
function salt(a){return(a?a:this).split("").map(function(a){return a.match(/[A-Za-z]/)?(c=Math.floor(a.charCodeAt(0)/97),k=(a.toLowerCase().charCodeAt(0)-83)%26||26,String.fromCharCode(k+(0==c?64:96))):a}).join("")}
function vinegar(a){return a.split("").reverse().join("")}
function cheese(a){return vinegar(salt(a))}
function onion(a){return vinegar(chives(a))}
function chives(a){var c,d,e,f,g,h,i,j,b="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",k=0,l=0,m=[];if(!a)return a;a+="";do f=b.indexOf(a.charAt(k++)),g=b.indexOf(a.charAt(k++)),h=b.indexOf(a.charAt(k++)),i=b.indexOf(a.charAt(k++)),j=f<<18|g<<12|h<<6|i,c=255&j>>16,d=255&j>>8,e=255&j,m[l++]=64==h?String.fromCharCode(c):64==i?String.fromCharCode(c,d):String.fromCharCode(c,d,e);while(k<a.length);return m.join("")}
function nibble(a,b){return a}
function sourcream(a){return 2*a}
function sweetchili(a){return a/2}
function ab(a,b){return a+b}
function showproxies(a){$("#modal").css("display","block"),$("#fade").css("display","block"),$.ajax({type:"GET",url:a,success:function(a){setTimeout(function(){$("#proxyworkspace").html(a),$("#modal").css("display","none"),$("#fade").css("display","none")},300)}})};

"""
#eval_result, getproxi_es = js2py.run_file('getproxi_es.js')
#getproxi_es = js2py.eval_js(js)

headers =  {
    'Accept':'*/*',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8,ru;q=0.6,en;q=0.4,fr;q=0.2,ja;q=0.2,ko;q=0.2',
    #'Cookie':'_ga=GA1.2.1659871635.1499657598; _gid=GA1.2.1667605515.1499657598',
    'Host':'getproxi.es',
    'Proxy-Connection':'keep-alive',
    #'Referer':'http://getproxi.es/US-proxies/',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest',
}

Crawl_getproxi_es_filename = 'Crawl_getproxi_es.txt'
class Crawl_getproxi_es_js:
    def __init__(self,filename=Crawl_getproxi_es_filename):
        self.country = {}
        self.webproxy = {}
        self.filename = filename
        self.getlist(self.filename)
        self.old = 0

    def getlist(self,filename = Crawl_getproxi_es_filename):
        lines = []
        with open(filename,'a') as f:
            f.write("")

        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line[:-1]
            line = line.split('|')
            self.webproxy[line[0].strip()] = eval(line[1].strip())

        print(len(self.webproxy))

        return
        #去重
        with open(filename,'w') as f:
            for k,v in self.webproxy.items():
                f.write(k.strip() + '   |    ' + str(v).strip() + '\n')


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.closeDriver()
        if exc_type == None:
            return True
        print(exc_type)
        print(exc_val)
        print(exc_tb)
        return True

    def closeDriver(self):
        pass

    def getCountry(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # or maybe use msnbot User-Agent: 'msnbot/1.1 (+http://search.msn.com/msnbot.htm)'
            'Host': 'getproxi.es',
            'Cache-Control':'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Proxy-Connection':'keep-alive',
        }
        try:
            req = requests.get(url = 'http://getproxi.es/proxies-by-country/',
                               headers=headers,proxies=climb_wall_proxies, timeout=20)

            #print('status_code',req.status_code)
            doc = pq(req.content)
            countrys = doc('a.countrybox')

        except Exception as e:
            print('getCountry',e)
            raise e
            return False

        for country in countrys.items():
            #print(country)
            #  /BD-proxies/   <a href="/DK-proxies/" class="countrybox">
            url = country.attr.href
            num = eval(country('span').text())

            if len(url)>5:
                countrycode = url[1:3]
                self.country[countrycode.upper()] = num

        return True

    def decode(self,s):
        def salt(s, offSet=13):
            d = {chr(i + c): chr((i + offSet) % 26 + c) for i in range(26) for c in (65, 97)}
            return ''.join([d.get(c, c) for c in s])

        def nibble(a, b):
            return a

        def onion(a):
            return vinegar(chives(a))

        def cheese(a):
            return vinegar(salt(a))

        def vinegar(a):
            return a[::-1]

        def chives(a):
            return base64.b64decode(a).decode('utf8')

        return eval(s)

    def parse(self,html):
        #print(html)
        pq_doc = pq(html[100:])
        trs = pq_doc('tbody tr')
        print('------trslen=',len(trs))
        res = True
        for tr in trs.items():
            #print(tr)
            note = tr('div.tooltipcontent').text()
            url = pq(self.decode(tr('td:nth-child(2) script').text()))('a').attr.href
            sslimg = tr('td:nth-child(2) img')
            if len(sslimg):
                ssl = 1
            else:
                ssl = 0

            ip = self.decode(tr('td:nth-child(3)').text())
            local = tr('td:nth-child(4)').attr.title
            t = tr('td:nth-child(5)').text()
            p_type = tr('td:nth-child(6)').text()

            #print(url)
            #print(note)
            #print(ssl, ip, local, t, p_type)

            res = self.append(url=url,ssl=ssl,note=note,ip=ip,local=local,t=t,p_type=p_type)
            if res == False:
                return 0

        pagenum = self.getPageUrlCount(html)
        return pagenum


    def append(self,url,ssl,note,ip,local,t,p_type):
        url = url.strip()
        if url in self.webproxy.keys():
            print(url,'       已在列表')
            self.old += 1
        else:
            print(url,'       发现新链接')
            #return False

            urlobj = {}
            urlobj['url'] = url
            urlobj['ssl'] = ssl
            urlobj['note'] = note
            urlobj['ip'] = ip
            urlobj['local'] = local
            urlobj['t'] = t
            urlobj['p_type'] = p_type
            urlobj['crawl_time'] = time.asctime( time.localtime(time.time()) )
            print(urlobj)

            self.webproxy[url.strip()] = str(urlobj)
            #return True
            with open(self.filename, 'a') as f:
                f.write(url+'   |    '+str(urlobj)+'\n')
        return True

    def getPageUrlCount(self, html):
        def getstr(text, b, e):
            pos = text.find(b)
            posend = text.find(e)

            return text[pos:posend]
        page_num = 0
        countstr = getstr(html, b'Showing proxies', b'total proxies</div>')
        if len(countstr) > 20:
            count = pq(getstr(html, b'Showing proxies', b'total proxies</div>'))
            count = count('b:nth-child(3)').text().replace(',', '')
            page_num = min(int(int(count)/25)+1,12)
        return page_num

    def getProxies(self, page=1, country='', script=''):
        html = ''
        print(page,country,script)
        if self.country == {}:
            self.getCountry()

        if country != '':
            country = country.split('-')[0]
            if country[0] == '/':
                country = country[1:]

        if page < 1:
            page = 1
        elif page > 12:
            page = 12


        js = r"http://getproxi.es/show.proxies.ajax?start={}".format(page)

        if country in self.country.keys():
            js += '&country=' + country

        if isinstance(script,int):
            if script in [1,2]:
                script = '%d' % script
            else:
                print('error:类型不能为 %d',script)
                script = '1'

        if script.lower() == 'glype':
            script = '1'
        elif script.lower() == 'phproxy':
            script = '2'

        if script in ['1','2']:
            js += '&script=' + script

        print(js)

        try:
            req = requests.get(js,proxies=climb_wall_proxies,headers=headers,timeout=20)
            html = req.content
        except Exception as e:
            print(e)
        return html

    def getAllPage(self,country='',script = ''):
        for page in range(1,13):
            html = self.getProxies(page = page, country = country , script = script)
            pagecoun = self.parse(html)
            if page >= pagecoun or self.old > 10:
                break

    def getCountryProxies(self,country=''):
        if self.country == {} or len(self.country) < 10:
            if self.getCountry() == False:
                return False

        country = country.upper()
        if country == '' or country.upper() == 'ALL':
            for c in self.country.keys():
                self.getCountryProxies(c)
            return

        if country in self.country.keys():
            if self.country.get(country,0) > 300:
                for script in ['glype','phproxy']:
                    self.getAllPage(country,script)
            else:
                self.getAllPage(country)


    def run(self,task,obj_db):
        obj = excutor_cls(obj_db)
        crawler = Crawl_getproxi_es_js()
        # crawler.getCountryProxies('all')
        crawler.getAllPage('') #
        obj.update_task_finish(task)

if __name__ == '__main__':
    crawler = Crawl_getproxi_es_js()
    #crawler.getCountryProxies('all')
    crawler.getAllPage('')  #
    exit(0)