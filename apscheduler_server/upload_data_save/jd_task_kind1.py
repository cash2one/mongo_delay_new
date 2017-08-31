#保存二级页面的脚本
class jd_task_kind:
    def __init__(self,obj_db):
        self.obj_db=obj_db
    def run(self,data): #参数1临时表中的上传数据，参数二：封装的数据库操作对象
        db = 'tmp_db'
        tb = data['topic']
        try:
            save_tb = self.obj_db.chocie_db_tb(db, tb)  # 切换到该数据对应存储的数据库和数据表下
            self.obj_db.create_com_index(save_tb, 'guid')  # 为guid建立索引
            self.obj_db.insert_data(save_tb,data)#将数据插入对应的数据库中

        except Exception as e:
            print (e)

