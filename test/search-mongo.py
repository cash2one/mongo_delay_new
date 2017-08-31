

from pymongo import  MongoClient
import time
def mongo_search():
    time_list = []
    conn = MongoClient('192.168.0.210', 27017)
    db = conn['jd_comment']
    def choice_table(tb):
        return db[tb]
    tb = choice_table('comment')
    search_order = [
{'firstCategory':9987,'secondCategory':653,'thirdCategory':655,'userClientShow':'来自京东Android客户端'}]

    for item in range(len(search_order)):
        start = time.time()
        res = tb.find(search_order[item]).limit(10)
        for item in res:
            print (item)
        end = time.time()
        time_list.append(end-start)
    print (time_list)
    count = 0
    for i in time_list:
        count += i
    return 'mongo用时>>>: %s 秒' % (count/len(time_list))



f = open('time.txt','a+')
for _ in range(20):
    tmp = mongo_search()
    f.write(tmp)
    f.write('\n')
