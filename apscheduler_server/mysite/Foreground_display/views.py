from django.shortcuts import render,HttpResponse
from django.http import StreamingHttpResponse,HttpResponse
# Create your views here.
import os



def test(requests):
    cur_doc = os.path.abspath(os.path.dirname(__file__))#得到当前目录
    download_doc = os.path.join(cur_doc,'download_file')#拼接下载文件目录

    return render(requests,'test.html')
def login(requests):
    pass

def readFile(filename,chunk_size=512):
    with open(filename,'rb') as f:
        while True:
            c=f.read(chunk_size)
            if c:
                print (c)
                yield c
            else:
                break
def download_file(requests):
    cur_doc = os.path.abspath(os.path.dirname(__file__))  # 得到当前目录
    download_doc = os.path.join(cur_doc, 'download_file')  # 拼接下载文件目录
    the_file_name = '11.png'  # 显示在弹出对话框中的默认的下载文件名
    filename = os.path.join(download_doc,the_file_name)
    response = HttpResponse(readFile(filename))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    return response


