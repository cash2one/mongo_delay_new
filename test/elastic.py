import requests,json
from pymongo import  MongoClient
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

def look_index():
    text = requests.get('http://localhost:9200/_cat/indices?v')
    print(text.text)

def create_index(index_name):
    print ('创建索引')
    text = requests.put('http://localhost:9200/%s?pretty'%(index_name))
    print(text.text)
# 插入文档
def insert(index,data):
    #print ('插入数据')
    text = requests.post('http://localhost:9200/%s?pretty'%(index),json=data)
    #print(text.text)
def delete(index):
    text = requests.delete('http://localhost:9200/%s/?pretty' %(index))
    print(text.text)




def data_search(index):#数据查找
    print ('数据搜索')
    ret_list = []
    text = requests.post('http://localhost:9200/%s/_search?pretty' %(index),json=  {
        "query":{



            'match':
            {
                'body': '597949fd092e7740797b0ee9'

            }
      },

    })
    print (text.text)
    rest = json.loads(text.text)
    for item in rest['hits']['hits']:
        ret_list.append(item['_source'])
    return ret_list


def set_date(es, line_list, index_name="content_engine", doc_type_name="en"):
    # 读入数据
    # 创建ACTIONS
    ACTIONS = []
    for line in line_list:
        action = {
            "_index": index_name,
            "_type": doc_type_name,
            "_source": line
        }
        ACTIONS.append(action)

        # 批量处理
    success, _ = bulk(es, ACTIONS, index=index_name, raise_on_error=True)
    print('Performed %d actions' % success)
es = Elasticsearch()
conn = MongoClient('192.168.0.210', 27017)
db = conn['jd_comment']
def choice_table(tb):
    return db[tb]
tb = choice_table('comment1')
flag = 1
i = 0
index = 'customer/external'
if flag :
    data_list = tb.find()
    for item in data_list:
        i +=1
        item.pop('_id')
        print ('insert>:',i)
        insert(index,item)
#create_index('customer')
#delete('customer')
index = 'customer'
look_index()




"""
start = time.time()
rest = data_search('customer')
end =time.time()
print (rest,len(rest))
print (end-start)
"""


