import requests,json,base64,gzip
from gridfs import *
from bson import ObjectId


from pymongo import MongoClient
import time,copy
conn = MongoClient('localhost', 27017, connect=False)
db = conn['data_db']  # 存储任务队列，任务队列数据库
tb = db['data_tb']
fs = GridFS(db, 'body')  # 存储任务body的大文档，无空间限制
SERVER_IP = '192.168.0.210'
SERVER_PORT = '6688'

head = {
    "device": {"type": 'pc', "id": 1, "mac": '', "api_key": ''},
    "command": {"action": '', "version": ''},
    "body":
        {"taskstats": {"time": time.time(), "status": ''}, "get_tasks": '', "tasks": '',
         "data": "", "client_status": '', "proxy_data": '', "cookie_data": ''
         }

}

def get_data():
    data_list = []
    tmp_list = tb.find({'upload_flag': 0}).limit(5)
    tmp_list1 = copy.copy(tmp_list)
    if not tmp_list.count():#没有数据
        return
    for data in tmp_list:
        if data['data_lenth_flag']:# 数据大于16m标识
            try:
                data.pop('_id')
                obj_id = data['body'] #得到存储数据的id
                body = fs.get(ObjectId(obj_id)).read()
              # 从文档中读出body字段{'result':'',data:''}
                body = eval(body)  # 还原body
                data['result'] = body['result']
                data['data'] = body['data']
                data['upload_time'] = time.time()#上传时间
                data_list.append(data)  # 将所有数据追加到列表
            except Exception as e:
                print('上传大于16M数据报错', e)

        else:#小于16m的数据
            try:
                data.pop('_id')
                data['upload_time'] = time.time()  # 上传时间
                data_list.append(data)  # 将所有数据追加到列表
            except Exception as e:
                print ('上传小于16M数据出错',e)
    tmp = bytes(json.dumps(data_list), encoding='utf-8')
    tmp = base64.b64encode(gzip.compress(tmp))
    tmp = str(tmp, encoding='utf-8').replace('\n', '')
    head['body']['data'] = tmp  # 将上传数据添加到该字段
    recv_data = send_data()  # 将数据发送
    if not recv_data:
        return
    for data1 in tmp_list1:
        tb.find_and_modify(query={'_id': data1['_id']},update={'$set':{'upload_flag': 1}})





def send_data():
    print ('send')
    try:
        text = requests.post("http://%s:%s/" %(SERVER_IP, SERVER_PORT), json=head,headers={'Connection':'close'})

        print (text.status_code,'*******服务器返回码')
        if text.status_code == 200:
            return json.loads(text.text)
        else:
            return
    except Exception as e:
        print (e,'无法连接服务器或者数据异常')
        return

send_data()

