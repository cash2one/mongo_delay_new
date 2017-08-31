from django.conf.urls import url
from Back_manager import views
from Back_manager import simple_views

urlpatterns = [
    url(r'^ooo', views.test1),
    url(r'^login$', views.login),
    url(r'^logout', views.logout),
    url(r'^change_pwd', views.change_pwd),
    url(r'^task$', views.task_main),
    url(r'^test', views.test),#管理平台普通用户不支持注册功能，目前还没有实现超级用户，该函数负责将账号密码写到用户表中
    url(r'^task_info$', views.task_infomation),
    url(r'^task_type_info/(.+)/$', views.task_type_info),
    url(r'^main_manager$', views.main_manager),
    url(r'^create_type_task', views.create_task),
    url(r'^delete_all_task', views.delete_all_task),#删除单个和集体任务
    url(r'^update_type_task/(.+)/$', views.update_all_task),#更新该类型的所有任务
    url(r'^edit_type_task', views.edit_all_task),#更新该类型的所有任务
    url(r'^update_signal_task', views.update_signal_task),#更新单个任务
    url(r'^lookup_type_task', views.lookup_all_task),#查看该类型下的所有任
    url(r'^get_script_list', views.get_script_list),#展示脚本
    url(r'^excutor_script', views.excutor_script),#执行脚本
    url(r'^get_task_fields', views.get_task_fields),
    url(r'^upload_script', views.upload_script),


]
