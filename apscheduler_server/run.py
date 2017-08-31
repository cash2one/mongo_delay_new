
#服务器运行入口

import aps_server,zmq_server,http_server,setting
import multiprocessing,os,imp
from upload_data_save import scan_upload_data#扫描临时数据库进程

def check_module():#负责安装依赖模块，如果必要模块安装失败程序无法启动
    result = True
    print ('检查本地模块')
    # 自动安装模块的逻辑
    for item in setting.INSTALL_MOUDEL:
        try:  # 已经安装该模块
            imp.find_module(item)
        except ImportError:  # 没有安装该模块，进行安装
            print ('安装模块',item)
            status = os.system('%s %s' % ('pip3 install -i https://pypi.doubanio.com/simple/ ', item))  # 安装依赖模块
            if status == 256:#下载失败
                result =False
    if result:
        print ('检查完成启动程序.....')
    else:
        print ('模块安装失败退出程序....。')
    return result
def run():
    result = check_module()
    if not result:#安装模块失败
        return
    if setting.CONNECT_SERVER_TYPE == setting.CONNECT_TYPE[0]:
        p1 = multiprocessing.Process(target=zmq_server.run)  # 运行zmq 接口，与客户端进行交互
    elif setting.CONNECT_SERVER_TYPE == setting.CONNECT_TYPE[1]:
        p1 = multiprocessing.Process(target=http_server.run)  # 运行web 接口，与客户端进行交互
    p2 = multiprocessing.Process(target=aps_server.main) #运行服务端的逻辑
    p3 = multiprocessing.Process(target=scan_upload_data.main) #扫描临时数据库进程
    p1.start()
    p2.start()
    p3.start()
    print ("".join(['您选择了',setting.CONNECT_SERVER_TYPE,":与客户端交互"]))
if __name__ == '__main__':
    run()


