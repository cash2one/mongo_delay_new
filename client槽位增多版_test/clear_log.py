
import os
def kill_process_by_name(self, name):  # 杀死进程的方法
    cmd = "ps -e | grep %s" % name
    f = os.popen(cmd)
    txt = f.readlines()
    print(txt)
    if len(txt) == 0:
        print("no process \"%s\"!!" % name)
        return
    else:
        for line in txt:
            colum = line.split()
            pid = colum[0]
            cmd = "kill -9 %d" % int(pid)
            rc = os.system(cmd)
            if rc == 0:
                print("exec \"%s\" success!!" % cmd)
            else:
                print("exec \"%s\" failed!!" % cmd)
    return


cmd = "ps -e | grep %s" % ('mongod')
f = os.popen(cmd)
txt = f.readlines()
print(txt)