
from excutor_doc import db_oprate
import threading
import time
def threading_get():
    while True:
        obj_db = db_oprate.collection_db()  # 操作数据库对象
        tb = obj_db.choice_crawl_table()  # 进入抓取任务表
        task_data = obj_db.find_one(tb, {})
        if task_data:
            obj_id = task_data['body']
            body = obj_db.gridfs_get_crawldata(obj_id)  # 读出gridfs
            # obj_db.gridfs_del_crawldata(obj_id)  # 将body从文档中删除
            body = eval(body)  # 还原body
            task_data['body'] = body
            #print(body)
            print('get_data')
            time.sleep(1)



t = threading.Thread(target=threading_get,
                     args=())  # 开启固定的线程，并将该进程所属的对象传递进去
t.start()

t.join()



