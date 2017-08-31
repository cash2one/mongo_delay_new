#扫描临时数据库的脚本
import db_oprate
import setting
import time
import copy
class scan_upload_data:
    def __init__(self):
        self.obj_db = db_oprate.collection_db()  #数据库操作对象

    def find_save_script(self,data):#找到该类型任务的保存数据脚本
        topic = data['topic']
        module_name = '.'.join(('upload_data_save', topic))
        m1 = __import__(module_name)  # 找到了脚本所在的目录
        script = getattr(m1, topic)  # 根据类型找到脚本
        cls = getattr(script, topic)(self.obj_db)  # 根据类型找到脚本中的类，实例话
        cls.run(data)#将保存的数据和数据库操作对象传递进去
    def delete_data(self,data):#从临时表删除数据接口
        save_tb = self.obj_db.chocie_db_tb(setting.TMP_DB, setting.TMP_TB)  # 进入临时表
        self.obj_db.del_data(save_tb,{'_id':data['_id']})#将数据从临时表删除

    def update_flag(self,data):#更改标示位，不删除数据
        save_tb = self.obj_db.chocie_db_tb(setting.TMP_DB, setting.TMP_TB)  # 进入临时表
        self.obj_db.find_modify(save_tb,{'_id':data['_id']}, {'$set': {'upload_flag':2}})#处理完成数据将客户端上传的数据的upload_flag字段更改为2
    def script_error(self,data):
        save_tb = self.obj_db.chocie_db_tb(setting.TMP_DB, setting.TMP_TB)  # 进入临时表
        self.obj_db.find_modify(save_tb, {'_id': data['_id']},{'$set': {'upload_flag':1}})  # 处理完成数据将客户端上传的数据的upload_flag字段更改为1
    def run(self):#扫描临时数据表，得到数据调用相应的处理脚本处理数据
        while True:
            try:
                save_tb = self.obj_db.chocie_db_tb(setting.TMP_DB, setting.TMP_TB) #进入临时表
                #query = {'upload_flag':0}#扫描条件
                query = {}#适用于从临时表得到数据并且删除
                data  = self.obj_db.find_one(save_tb,{"upload_flag":{"$lt":1}})
                update_data= copy.copy(data)#深度复制该值，防止中途数值被修改
                if data:
                    data.pop('_id')
                    self.find_save_script(data)#根据数据类型调用相应的脚本,data参数已经剔除_id
                    if setting.CLEAR_UPLOADDATA_MODE:
                        self.delete_data(update_data)#将数据从临时表中删除
                    else:
                        self.update_flag(update_data)#不删除临时表中的数据，只将临时表数据的标识位改变
                else:
                    time.sleep(1)
            except Exception as e:
                print (e)
                self.script_error(update_data)


def main():
    obj = scan_upload_data()
    obj.run()
