from django.shortcuts import render,HttpResponse,redirect
import time,json,os

from Back_manager import models,db_oprate

mongo_obj = db_oprate.collection_db()#数据库操作对象

def view_operation_record(requests):
    pass
