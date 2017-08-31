import platform
import psutil
import os
import json
#platform.uname()
#uname_result(system='Darwin', node='cnadmindeiMac.local',
# release='16.3.0', version='Darwin Kernel Version 16.3.0: Thu Nov 17 20:23:58 PST 2016;
# root:xnu-3789.31.2~1/RELEASE_X86_64', machine='x86_64', processor='i386')
#machine 处理器类型
#processor  处理器的具体型号
def system_info():
    system =  platform.uname()
    mem = psutil.virtual_memory()#查看系统内存
    swap = psutil.swap_memory()
    disk = psutil.disk_partitions() #利用psutil模块的disk_partitions()方法
    partition = psutil.disk_usage('/')
    sdiskio = psutil.disk_io_counters()
    ret1 = []
    for i in disk:#分区
        ret1.append({'device':i.device,'fstype':i.fstype,' opts':i. opts})


    ret = []#获得该目录下的进程对象链表
    for i in psutil.pids():#正在运行的所有进程
        p = psutil.Process(i)
        try:
            if p.cwd() == os.getcwd():#得到在当前目录工作的进程
                cen = p.memory_info()
                pro = {"uid":i,'create_time':p.create_time(),'memory_info':{'rss':cen.rss,'vms':cen.vms,'pfaults':cen.pfaults,'pageins':cen.pageins},
                       'status':p.status(),'cwd':p.cwd(),'exe':p.exe(),'memory_percent':p.memory_percent()}
                ret.append(pro)
        except Exception:
            pass

    sysinfo = {'system':system,'memory':{'mem':mem,'swap':swap},'disk':{'sdiskkpart':ret1,'sdiskusage':partition,'sdiskio':sdiskio},'proinfo':ret}
    return sysinfo

if __name__ == '__main__':
    a = system_info()
    print (a)