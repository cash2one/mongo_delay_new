import db_oprate

db_obj = db_oprate.collection_db()#操作数据库对象
data_tb = db_obj.choice_data_table()  # 切换到存储数据表
data = db_obj.find_modify(data_tb, {'upload_flag': 0}, {'$set': {'upload_flag': 0}})

obj_id = data['body']  # 得到存储数据的id
body = db_obj.gridfs_get_data(obj_id)  # 从文档中读出body字段{'result':'',data:''}
body = eval(body)  # 还原body
data['result'] = body['result']
data['data'] = body['data']
print (data)
