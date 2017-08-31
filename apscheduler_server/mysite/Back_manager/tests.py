#from django.test import TestCase

# Create your tests here.
from datetime import datetime
import db_oprate

import os,sys

mongo_obj = db_oprate.collection_db()#数据库操作对象
task_tb = mongo_obj.choice_main_table('task_main')
task_obj = mongo_obj.find_data(task_tb, {})
task_type = mongo_obj.obj_distinct(task_obj, 'topic')  # 得到具体的任务类型
for item in task_type:
    task_data = mongo_obj.find_data(task_tb, {'topic':item})
    task_sum = task_data.count()
    inter_list = mongo_obj.obj_distinct(task_data, 'interval')
    timeout_list =mongo_obj.obj_distinct(task_data, 'timeout')
    print ({'topic':item,'interval':inter_list,'timeount':timeout_list,'count':task_sum})