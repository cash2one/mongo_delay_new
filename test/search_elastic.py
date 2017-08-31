from elasticsearch import Elasticsearch
import time


search_order = [
{'firstCategory':9987,'thirdCategory':655,'userClientShow':'来自京东Android客户端'}]


# 连接elasticsearch,默认是9200
es = Elasticsearch()
# 创建索引，索引的名字是my-index,如果已经存在了，就返回个400，
# 这个索引可以现在创建，也可以在后面插入数据的时候再临时创建
#es.indices.create(index='my-index', ignore)
# {u'acknowledged':True}


# 插入数据,(这里省略插入其他两条数据，后面用)
#es.index(index="my-index", doc_type="test-type", id=01, body={"any": "data01", "timestamp": datetime.now()})
# {u'_type':u'test-type',u'created':True,u'_shards':{u'successful':1,u'failed':0,u'total':2},u'_version':1,u'_index':u'my-index',u'_id':u'1}
# 也可以，在插入数据的时候再创建索引test-index
#es.index(index="test-index", doc_type="test-type", id=42, body={"any": "data", "timestamp": datetime.now()})

# 查询数据，两种get and search
# get获取
#res = es.get(index="my-index", doc_type="test-type", id=01)
#print(res)
# {u'_type': u'test-type', u'_source': {u'timestamp': u'2016-01-20T10:53:36.997000', u'any': u'data01'}, u'_index': u'my-index', u'_version': 1, u'found': True, u'_id': u'1'}
#print(res['_source'])
# {u'timestamp': u'2016-01-20T10:53:36.997000', u'any': u'data01'}

# search获取
def elastic_search():
    time_list = []
    count =0
    for item in range(len(search_order)):
        start = time.time()
        res = es.search(index="customer", body={"query": {"match": search_order[item ]}})
        end = time.time()
        print(res)
        time_list.append(end - start)
    for i in time_list:
        count += i
    return 'elasticsearch用时>>>: %s 秒' %(count/len(time_list))
#print(res)
# {u'hits':
#    {
#    u'hits': [
#        {u'_score': 1.0, u'_type': u'test-type', u'_id': u'2', u'_source': {u'timestamp': u'2016-01-20T10:53:58.562000', u'any': u'data02'}, u'_index': u'my-index'},
#        {u'_score': 1.0, u'_type': u'test-type', u'_id': u'1', u'_source': {u'timestamp': u'2016-01-20T10:53:36.997000', u'any': u'data01'}, u'_index': u'my-index'},
#        {u'_score': 1.0, u'_type': u'test-type', u'_id': u'3', u'_source': {u'timestamp': u'2016-01-20T11:09:19.403000', u'any': u'data033'}, u'_index': u'my-index'}
#    ],
#    u'total': 5,
#    u'max_score': 1.0
#    },
# u'_shards': {u'successful': 5, u'failed': 0, u'total':5},
# u'took': 1,
# u'timed_out': False
# }
f = open('time.txt','a+')
for _ in range(20):
    tmp = elastic_search()
    f.write(tmp)
    f.write('\n')

"""
for hit in res['hits']['hits']:
    print(hit["_source"])
"""