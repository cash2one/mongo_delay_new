
SERVER_IP = '192.168.0.210'#绑定本地ip'192.168.0.210'
SERVER_PORT = '5500'#服务器与客户端交互的对外端口

DATABASES_IP = 'localhost'#数据库地址

CLEAR_UPLOADDATA_MODE=True#从临时表中扫描得到的上传数据处理完成后的处理模式，默认为干净模式
# True为处理完数据后临时表将数据删除，
# False只是将临时表的数据upload_flag置为2不删除临时表的数据

CHECK_PROXY_TIME = 24 * 3600#客户端的请求时间time.time(),服务器下发的代理的搜索条件为 :{gte:time.time()-CHECK_PROXY_TIME,lte:time.time()}

CONNECT_TYPE = ['zmq','http']#选择服务器的通信方式,http更加稳定
CONNECT_SERVER_TYPE = CONNECT_TYPE[1]#选择连接方式，服务器与客户端的通信方式必须保持一致

#任务类型及其任务是否是下载任务，每种类型所要下发的任务个数配置
DOWN_LOGO = {'down':["jd_task_kind",'Crawl_getproxi_es_js','jm_task_proxycrawl'],'notdown':['sku2',]}
DOWN_COUNT = {'down':1000,'notdown':200}
TASK_TYPE_COUNT = {"jd_task_kind":1,'Crawl_getproxi_es_js':1,}#任务类型对应每种任务下发的个数，该配置暂时还没有实现

###################################"""数据库相关"""####################################################################
JOB_DB = 'aps_all_copy'#aps储存作业的数据库名称
JOB_COLL = 'server_job'#aps储存作业的集合

DATABASES = 'jame_server'  #数据库
TASKS_LIST = 'task_main'  #总任务列表
RECODE_LIST = "recode_list"  #记录超时任务的id和该任务上次分配的设备id，任务重新分配以后提醒客户端删除该任务
CLIENT_CPU_DATA = 'cpu_data'#存储客户端的硬件信息数据表{'time':time,'system_info':sys_info,'device_id':device_id}
RECODE_ERROR_LIST = 'error_task'#记录任务的超时次数大于任务默认的最大超时次数的表

#存放客户端上传数据相关的数据库
TMP_DB = 'tmp_db'
TMP_TB = 'tmp_tb1'


###################################"""数据库相关"""####################################################################


INSTALL_MOUDEL = ('pymongo','zmq','flask','gzip','base64','apscheduler')#服务器依赖的第三方库



###########################"""任务字段即字段status对应的状态码"""##########################################################
#属性状态码含义
STATUS_DELAY = 0  # 任务处于等待状态
STATUS_READY = 1  # 任务处于就绪状态，可以执行
STATUS_EXCUTING = 2  # 任务正在执行
STATUS_TIMEOUT = 3  # 任务超时
STATUS_DELETED = 4  # 任务处于删除状态，不再被扫描
STATUS_FINISH = 5  # 任务完成，控制权交回队列
"""任务属相关"""
ROW_GUID = 'guid'
ROW_TOPIC = 'topic'
ROW_TIME = 'time'
ROW_TIMEOUT = 'timeout'
ROW_BODY = 'Body'
ROW_STATUS = 'status'
###########################"""任务字段即字段status对应的状态码"""##########################################################




####################################"""本地任务相关"""###################################################################
SCAN_TASK_TIME = 0.1 #扫描总任务队列的间隔时间
INTERFACE_TIME = 0.1#对外zmq交互的间隔时间
SCAN_TASK = "scan_task"
INTERFACE = 'excutor_process'
#本地任务作业id
LOCAL_TASK_LIST = [SCAN_TASK,INTERFACE]
####################################"""本地任务相关"""###################################################################

OPT_RECORD_DATABASE = 'operation_record'#记录后台操作的数据库
OPT_RECORD_TABLE = 'operation_record'#记录后台操作的数据表

"""外部端口"""
OUT_PORT = '9002'


