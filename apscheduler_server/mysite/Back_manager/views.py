from django.shortcuts import render,HttpResponse,redirect
import time,json,os,sys

from Back_manager import models,db_oprate
# Create your views here.
from bson.objectid import ObjectId
#后台管理
path = os.path.join(os.path.dirname(os.getcwd()),'create_task_script')#存放创建任务的脚本目录
from apscheduler_server import setting#将平台服务的seeting文件导入

#path = "/Users/cn/Desktop/mongo_delay/apscheduler_server/create_task_script"#脚本存放目录
#path = "/home/cnadmin/桌面/apscheduler_server/create_task_script"
session_time = 5  # 分钟 #指定seesion有效时间
save_day = 7#指定免登录天数
from datetime import datetime
mongo_obj = db_oprate.collection_db()#数据库操作对象

def operation_record(requests,msg):#操作记录函数，用于动作记录
    user  =requests.session.get('user', '')
    #msg 可能有的字段 {'action':'','query':'',update:'','script_path'}
    cur_time = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    oprate_msg = {'user':user,'time':cur_time,'msg':msg}#填充时间
    or_tb = mongo_obj.chocie_db_tb(setting.OPT_RECORD_DATABASE,setting.OPT_RECORD_TABLE)#存储管理员操作的记录
    mongo_obj.insert_data(or_tb,oprate_msg)#将操作记录存储

def auth_required(view):
    """身份认证装饰器，
    """
    def decorator(requests, *args, **kwargs):
        user = requests.session.get('user', '')
        flag = models.user_info.objects.filter(username=user).count()
        if not flag:
            return login(requests, *args, **kwargs)
        try:
            #print ('是否免登录',requests.session["save_me"],requests.session["otime"])
            if requests.session["login_flag"] == True and (time.time() - requests.session["otime"] < session_time * 60):  # 满足条件重置session时间
                if not requests.session["save_me"]:#不是免登录
                    requests.session["otime"] = time.time()
                return view(requests, *args, **kwargs)
            else:
                return login(requests)
        except ValueError:

            return auth_fail_handler(requests)

    return decorator

def auth_fail_handler(requests):
    """非法请求处理
    :param request:
    :return:
    """
    return HttpResponse("非法请求")


def login(requests):#登陆视图
    import json
    msg = {"status": True, "mesg": None,'login':'login'}#login字段其他ajax请求都不可以返回该字段
    if requests.method == "POST":
        tmp = models.user_info.objects.filter(username=requests.POST.get("username"),passwd=requests.POST.get("password")).count()
        if tmp:
            save_me = requests.POST.get("save_me")#是否在规定天数免除登陆
            requests.session["login_flag"] = True
            requests.session["user"] = requests.POST.get("username")
            requests.session["otime"] = time.time()
            requests.session["save_me"] = False
            if save_me == 'true':
                requests.session["otime"] = time.time()+save_day*24*3600
                requests.session["save_me"]=True

        else:
            msg["status"] = False
            msg["mesg"] = "帐号密码错误"
        return HttpResponse(json.dumps(msg))
    else:
        try:
            if requests.session["login_flag"] == True and (time.time() - requests.session["otime"] < session_time * 60):
                return redirect("/Back_manager/main_manager")
        except:
            pass
        return render(requests,'login.html')

def logout(requests):#注销视图
    requests.session["login_flag"] = False
    return redirect("/Back_manager/login")

@auth_required
def change_pwd(requests):#更改密码视图
    msg = {"status": True, "mesg": None}
    if requests.method == 'POST':
        old_pwd = requests.POST.get("old")
        new_pwd = requests.POST.get("new")
        ok_pwd = requests.POST.get("ok")
        user_flag = models.user_info.objects.filter(username= requests.session["user"],
                                              passwd=old_pwd).count()
        if user_flag:
            if new_pwd == ok_pwd:
                models.user_info.objects.filter(username=requests.session["user"],
                                                ).update(passwd=new_pwd)

            else:
                msg['status'] =False
                msg['mesg'] = '新密码与确认密码不一致'
        else:
            msg['status'] = False
            msg['mesg'] = '密码错误'

        return HttpResponse(json.dumps(msg))
@auth_required
def main_manager(requests):#展示各个类型任务的详情(类型，该类型任务的周期列表，该类型任务的超时列表，该类型任务的任务总数)
    """
    task_tb = mongo_obj.choice_main_table('task_main')
    task_obj = mongo_obj.find_data(task_tb, {})
    task_type = mongo_obj.obj_distinct(task_obj,'topic')#得到具体的任务类型
    return render(requests,'index.html',{"task_type":task_type})#将得到的任务类型在html文件中替换
    """
    show_list = []
    task_tb = mongo_obj.choice_main_table(setting.TASKS_LIST)
    task_obj = mongo_obj.find_data(task_tb, {})
    task_type = mongo_obj.obj_distinct(task_obj, 'topic')  # 得到具体的任务类型
    for item in task_type:
        task_data = mongo_obj.find_data(task_tb, {'topic': item})
        task_sum = task_data.count()
        inter_list = mongo_obj.obj_distinct(task_data, 'interval')
        timeout_list = mongo_obj.obj_distinct(task_data, 'timeout')
        show_list.append({'topic': item, 'interval_list': inter_list, 'timeout_list': timeout_list, 'task_count': task_sum})
        #print({'topic': item, 'interval_list': inter_list, 'timeout_list': timeout_list, 'task_count': task_sum})
    return render(requests, 'index.html', {"show_list": show_list}) #将任务的展示数据在前台展示

def task_main(requests):
    return HttpResponse('开始任务操作')

@auth_required
def create_task(requests):#创建任务视图
    return render(requests, 'create_type_task.html')

#对一类任务的操作
@auth_required
def delete_all_task(requests):#删除一类和单个任务的视图函数
    msg = {"status": True, "mesg": None}
    if requests.method == "POST":
        query = {}
        topic = requests.POST.get("topic")#获取任务类型
        if topic:
            query['topic'] = topic
        guid  = requests.POST.get("guid")#获取任务的guid
        if guid:
            query['guid'] = guid
            #进入该条件代表删除单个任务
        task_tb = mongo_obj.choice_main_table(setting.TASKS_LIST)#任务表
        job_tb= mongo_obj.chocie_db_tb(setting.JOB_DB,setting.JOB_COLL)#作业表
        recode_tb = mongo_obj.choice_main_table(setting.RECODE_LIST)#切换到记录删除表
        task_data = mongo_obj.find_data(task_tb,query)#找到符合条件的任务数据
        for item in task_data:
            if item['device']['id']:#将被分配过的任务记录，为了被剥夺任务的客户端删除任务
                mongo_obj.insert_data(recode_tb,{'guid':item['guid'],'device_id':item['device']['id'],'topic':item['topic']})
            mongo_obj.del_data(task_tb, {'guid':item['guid'],'topic':item['topic']}) #删除任务
            job_id = ':'.join([item['topic'], str(item['guid'])])
            mongo_obj.del_data(job_tb,job_id)#删除作业
            operation_record(requests,{'action':'del_data','query':{'guid':item['guid'],'topic':item['topic']}})#将内容记录
        #1：将要删除的任务放到记录删除表中(recode_list)，用于通知客户端删除任务
        #2：删除任务

        return HttpResponse(json.dumps(msg))

@auth_required
def update_all_task(requests,arg):#更新任务视图
    if requests.method == "GET":
        return render(requests, 'update_type_task.html',{'type_task':arg})

@auth_required
def edit_all_task(requests):#编辑一类任务的所有周期,和超时时间，统一修改只支持修改这两项
    if requests.method == "POST":
        interval =int(requests.POST.get("interval"))
        timeout = int(requests.POST.get("timeout"))
        topic = requests.POST.get("topic")
        task_tb = mongo_obj.choice_main_table(setting.TASKS_LIST)
        mongo_obj.much_update_data(task_tb,{'topic':topic},{'$set':{'interval':interval,'timeout':timeout}})
        operation_record(requests, {'action':'much_update_data','query':{'topic':topic},'update':{'set':{'interval':interval,'timeout':timeout}}})  # 将内容记录
        #return render(requests, 'update_type_task.html')
        return redirect("/Back_manager/main_manager")
@auth_required
def update_signal_task(requests):
    #{'nModified': 1, 'n': 1, 'updatedExisting': True, 'ok': 1.0}
    #{'nModified': 1, 'ok': 1.0, 'updatedExisting': True, 'n': 1} +++++
    msg = {"status": True, "mesg": None}
    if requests.method == "POST":
        type = requests.POST.get("type")
        task = requests.POST.get("task")
        task = json.loads(task)
        guid = task['guid']#得到任务id
        topic = task['topic']#得到任务类型
        task_tb = mongo_obj.choice_main_table(setting.TASKS_LIST)
        task['interval'] = int(task['interval'])
        task['timeout'] = int(task['timeout'])
        task['status'] = int(task['status'])
        result = mongo_obj.update_term_data(task_tb,{'topic':topic,'guid':guid},task)#将数据更新到数据库
        operation_record(requests,
                         {'action': 'update_term_data', 'query':{'topic':topic,'guid':guid},'update':task})  #将内容记录
        return HttpResponse(json.dumps(msg))


def test(requests):
    requests.session["login_flag"] = False
    user='jay'
    pwd='123'
    models.user_info.objects.create(
        username=user,
        passwd=pwd,
        ctime=datetime.now()
    )
    return HttpResponse('ok')
@auth_required
def get_script_list(requests):#返回脚本名称视图
    msg = {"status": True, "mesg": None}
    if requests.method == "POST":
        msg['mesg'] = {}
        for f in os.listdir(path):
            tmp = os.path.join(path, f)
            if os.path.isfile(tmp):
                msg['mesg'][f] = time.time()

        return HttpResponse(json.dumps(msg))
@auth_required
def excutor_script(requests):#执行脚本视图
    msg = {"status": True, "mesg": None}
    if requests.method == "POST":
        script_name = requests.POST.get("script_name")#得到脚本名称
        flag = os.path.exists(os.path.join(path,script_name))
        script_path = os.path.join(path,script_name)
        if not flag:
            msg["status"] = False
        reslut= os.system("python3 %s"%(script_path))
        print (reslut)
        operation_record(requests,
                         {'action': 'excutor_script', 'script_path':script_path
                          })  # 将内容记录
        return HttpResponse(json.dumps(msg))

@auth_required
def lookup_all_task(requests):#查看某类型的所有任务，提供翻页，上下翻页一次翻5页
    task_tb = mongo_obj.choice_main_table(setting.TASKS_LIST)
    limit = 15 # 默认一页20条数据
    page_sum = 5
    value = 0
    disable = 1
    if requests.method == "GET":
        topic = requests.GET.get('topic')#获取任务的类型
        page = requests.GET.get('page')#获取第几页
        if page.isdigit():#点击页码
            disable = int(page)
            value = disable//(page_sum+1)*page_sum
            task_list = mongo_obj.skip_data_limit(task_tb, {'topic': topic}, (disable-1) * limit, limit)  # 得到任务
        else:#点击上下翻页
            value = int(requests.GET.get('value'))#记录的页码数
            if page == "p":#向上翻页
                #防止用户恶意修改url
                disable = 1
                if (value-1)%page_sum == 0:
                    if value ==1:#起始页不允许翻页
                        value = 0
                        task_list = mongo_obj.skip_data_limit(task_tb, {'topic': topic}, 0 * limit,
                                                              limit)  # 得到任务
                    else:
                        disable = value - page_sum
                        value = value-page_sum-1
                        print (disable,value,'*********')
                        task_list = mongo_obj.skip_data_limit(task_tb, {'topic': topic}, (disable-1) * limit,
                                                              limit)  # 得到任务


                else:#恶意修改，跳转到第一页
                    task_list = mongo_obj.skip_data_limit(task_tb, {'topic': topic}, 0 * limit,
                                                          limit)  # 得到任务

            elif page == 'n':#向下翻页
                data_count= mongo_obj.get_data_count(task_tb, {'topic': topic})
                if data_count<= value*limit:#没有数据不允许翻页，默认翻到有数据的最后一页
                    value = value-page_sum
                    disable,end_data = divmod(data_count,limit)
                    if end_data:#不是limit的倍数
                        task_list = mongo_obj.skip_data_limit(task_tb, {'topic': topic}, disable * limit, limit)  # 得到任务
                        disable += 1  # 选中的页数
                    else:
                        task_list = mongo_obj.skip_data_limit(task_tb, {'topic': topic}, (disable-1) * limit, limit)  # 得到任务

                else:#还有数据
                    disable = value+1
                    task_list = mongo_obj.skip_data_limit(task_tb, {'topic': topic}, (value ) * limit,
                                                          limit)  # 得到任务

        task1_list = []
        for task in task_list:
            task['_id']= ObjectId(task['_id'])
            task['time'] =datetime.fromtimestamp(task['time']).strftime('%Y-%m-%d %H:%M:%S')
            task1_list.append(task)

        return render(requests, 'lookup_type_task.html',{"task_list":task1_list,'topic':topic,'disable_page':disable,'pagination':range(value+1,value+page_sum+1)})
        #数据列表，选中的页数，重置页码

#对单个任务的操作
@auth_required
def get_task_fields(requests):
    msg = {"status": True, "mesg": None}
    if requests.method == "POST":
        task_tb = mongo_obj.choice_main_table(setting.TASKS_LIST)
        guid = requests.POST.get('guid')
        task = mongo_obj.find_one(task_tb,{'guid':guid})
        task.pop('_id')
        msg['mesg'] = task
        if not task:
            msg['status'] = False
        return HttpResponse(json.dumps(msg))
@auth_required
def task_infomation(requests):#展示任务对应的任务个数
    task_tb = mongo_obj.choice_main_table(setting.TASKS_LIST)
    task_obj = mongo_obj.find_data(task_tb, {})
    task_type = mongo_obj.obj_distinct(task_obj, 'topic')  # 得到具体的任务类型  # 得到具体的任务类型
    taskinfo_list = []
    for item in task_type:
        task_data = mongo_obj.find_data(task_tb, {'topic': item})
        task_sum = task_data.count()
        taskinfo_list.append({'value':task_sum,'topic':item})

    return render(requests,'task_infomation.html',{'taskinfo_list':json.dumps(taskinfo_list)})  # 返回上传数据框

@auth_required
def upload_script(requests):#上传脚本视图
    if requests.method == "GET":
        return render(requests, 'upload_script.html')  # 返回上传数据框
    elif requests.method == "POST":
        myFile = requests.FILES.get("myfile", None)  # 获取上传的文件，如果没有文件，则默认为None
        if not myFile:
            return HttpResponse("no files for upload!")
        destination = open(os.path.join(path, myFile.name), 'wb+')  # 打开特定的文件进行二进制的写操作
        for chunk in myFile.chunks():  # 分块写入文件
            destination.write(chunk)
        destination.close()
        operation_record(requests,
                         {'action': 'upload_script', 'script_path':os.path.join(path, myFile.name)
                          }
                         )  # 将内容记录
        return render(requests, 'upload_script.html')  # 返回上传数据框

@auth_required
def task_type_info(requests,topic):#展示每种类型任务的详细信息,图形显示
    #topic为任务类型
    if requests.method == 'GET':
        task_tb = mongo_obj.choice_main_table(setting.TASKS_LIST)
        task_sum = mongo_obj.find_data(task_tb, {'topic':topic}).count()#得到该类型的任务总数
        complete_count=mongo_obj.find_data(task_tb,{'topic':topic,'status':{'$in': [4,5]}}).count()#得到该类型的任务完成个数
        timeout_count=mongo_obj.find_data(task_tb,{'topic':topic,'status':3}).count()#超时任务个数
        return HttpResponse('pok')

def test1(req):
    print (setting.TASKS_LIST)
    return HttpResponse('')