
from pymongo import MongoClient
import json,redis

class Merchandise:
    def __init__(self):
        DB = 'merchandise'
        TB  =  'merchandise_details'
        JD_DB='jm_task_list'
        JD_TB = 'task_list'
        conn = MongoClient('localhost', 27017, connect=False)
        self.rides = redis.StrictRedis(host='localhost', port=6379, db=0)
        db = conn[DB]  # 存储任务队列，任务队列数据库
        self.mer_tb = db[TB]
        db = conn[JD_DB]
        self.jd_tb = db[JD_TB]
        """剔除重复值的条件"""
        self.Sku = 'sku'

        self.Category = 'category'
        self.Material = 'relation_data.材质'
        self.Shopping = 'relation_data.选购热点'
        self.Style =  'relation_data.风格'
        self.Usemodel = 'relation_data.适用机型'
        self.Fashion = 'relation_data.款式'
        self.Brand = 'relation_data.品牌'

    def distinct_fun(self,arg,query):#剔除重复的值，返回值为列表
        result_list = self.mer_tb.find(arg).distinct(query)
        return result_list

    def save_redis(self,name,data):
        json_data = json.dumps(data)

        self.rides.set(name,json_data)
    def get_redis_value(self,name):
        return self.rides.get(name)
    def mercha_main(self):
        module= {'category':[],'Material':[],'Shopping':[],'Style':[],'Usemodel':[],'Fashion':[],'Brand':[]}
        Category_list = self.distinct_fun({},self.Category)
        for category in Category_list:
            module['category'] = category
            module['Material'] = self.distinct_fun({'category':category},self.Material)
            module['Shopping'] =self.distinct_fun({'category':category},self.Shopping)
            module['Style']= self.distinct_fun({'category':category},self.Style)
            module['Usemodel'] = self.distinct_fun({'category':category},self.Usemodel)
            module['Fashion'] =self.distinct_fun({'category':category},self.Fashion)
            module['Brand'] = self.distinct_fun({'category':category},self.Brand)
            self.save_redis(str(category),module)

    def sku_jd_data(self,sku):
        jd_data = self.jd_tb.find_one({'Body.sku':sku})
        if jd_data:
            commentCount = jd_data['Body']['productCommentSummary']['commentCount']
            goodCount = jd_data['Body']['productCommentSummary']['goodCount']
            poorCount = jd_data['Body']['productCommentSummary']['poorCount']
            generalCount = jd_data['Body']['productCommentSummary']['generalCount']
            return {'sku':sku,'commentCount':commentCount,' goodCount':goodCount,'poorCount':poorCount,'generalCount':generalCount}
        else:
            return {'sku':None}


    def sku_main(self):
        sku_list= self.distinct_fun({},self.Sku)
        for sku in sku_list:
            res = self.sku_jd_data(int(sku))
            self.save_redis(str(sku),res)

    def get_mercha_value(self):
        Category_list = self.distinct_fun({}, self.Category)
        if Category_list:
            data = self.get_redis_value(str(Category_list[0]))
            print (json.loads(str(data,encoding='utf8')),'+++++')

    def clear_redis(self):
        self.rides.flushdb()



if __name__ =='__main__':

    obj = Merchandise()
    obj.mercha_main()#存储评论相关的内容带redis
    obj.sku_main()#存储sku对应jd_list的数据到redis
    obj.get_mercha_value()