#下拉脚本文件依赖的软件：ssh客户端，sshpass
import imp
import os
from client_doc import setting#获得该设备的类型
def _check():#检查下拉脚本依赖的模块和软件
    #辅助安装系统软件
    if setting.SYETEM_TYPE == 'linux':#目前仅支持linux系统自动安装ssh,sshpass软件
        status = os.system('sudo apt-get install ssh')
        if status == 256:
            raise Exception('ssh软件安装失败')
        status = os.system('sudo apt-get install sshpass')
        if status == 256:
            raise Exception('sshpass软件安装失败')
    item = 'configparser'
    try: #已经安装该模块
        imp.find_module(item)
    except ImportError:  # 没有安装该模块，进行安装
        print('安装模块', item)
        status = os.system('%s %s' % ('pip3 install -i https://pypi.doubanio.com/simple/ ',item))  # 安装依赖模块
        if status == 256:  # 下载失败
            raise Exception(item, '模块安装失败')


#_check()
#从服务器下拉脚本逻辑
import configparser
user_ip = "@".join([setting.SERVER_USER,setting.SERVER_IP])#下拉脚本的服务器的用户与ip

#从服务器下拉的配置文件和脚本都会存放在脚本目录

def pull_script():
    result = True
    cur_doc =os.path.join(os.getcwd(),'script_main')  #返回当前文件所在的目录
    #下拉配置文件
    setting_file = 'test.txt'#下拉服务器的配置文件
    server_doc = '/home/cnadmin/script_doc/script_collection'#服务器配置文件所在目录
    local_doc = cur_doc  #'/home/cnadmin'#文件下载到本地的目录
    setting_order = 'sshpass -p jiemidata2017 scp -r %s:%s/%s %s'%(user_ip,server_doc,setting_file,local_doc)#下拉配置文件
    print (setting_order)
    os.system(setting_order)

    #打开新重服务器下拉的配置文件
    config=configparser.ConfigParser()
    with open(os.path.join(cur_doc,'test.txt'),'r') as f:
        config.readfp(f)
    server_doc = config.get('info','script_doc')#获取脚本所在目录
    #查找设备所属字段
    script = config.get('info',setting.DEVICE_TYPE)#读出该设备需要的脚本{'file':version}，根据设备类型获取脚本
    module = eval(config.get('info','module'))#配置文件中携带的该脚本所依赖的模块,是一个列表

    #自动安装模块的逻辑
    for item in module:
        try:#已经安装该模块
            imp.find_module(item)
        except ImportError:#没有安装该模块，进行安装
            print('安装模块', item)
            status = os.system('%s %s' % ('pip3 install -i https://pypi.doubanio.com/simple/ ', item))  # 安装依赖模块
            if status == 256:  # 下载失败
                print (item,'模块安装失败')
                result = False

    #打开旧配置文件
    if os.path.exists(os.path.join(cur_doc,'old_test.txt')):#有配置文件代表下拉过脚本
        config=configparser.ConfigParser()
        with open(os.path.join(cur_doc,'old_test.txt'),'r') as f:
            config.readfp(f)
        old_script = eval(config.get('info','pc'))#从老版本中读出脚本相关信息
        keys = old_script.keys()
        for script_file in eval(script):#遍历需要的脚本
            pull_order = 'sshpass -p jiemidata2017 scp -r %s:%s/%s %s' % (user_ip,
                server_doc, script_file, local_doc)  # 下拉配置文件
            # 检查本地是否有该脚本，如果已有则检查版本
            if script_file in keys:#如果新下拉的配置文件在旧配置文件中
                if eval(script)[script_file] != old_script[script_file]:  # 发现新版本，替换旧版本
                    os.system(pull_order)  # 下拉脚本
                old_script.pop(script_file)
            else:
                os.system(pull_order) #下拉脚本
        if old_script.keys():#老配置文件还有文件说明服务器有删除的文件
            for item in old_script:
                try:
                    try:
                        os.remove(os.path.join(cur_doc, item))  # 删除老脚本
                    except Exception as e:
                        os.system('rm -rf %s' % (os.path.join(cur_doc, item)))  # 删除目录
                except:
                    pass

        os.remove(os.path.join(local_doc, 'old_test.txt'))  # 删除

    else:#没有旧配置文件删除该目录下的所有脚本，根据新配置文件重新拉取
        for script_file in eval(script):#遍历需要的脚本
            pull_order = 'sshpass -p jiemidata2017 scp -r %s:%s/%s %s' % (user_ip,
                server_doc, script_file, local_doc)  # 下拉配置文件
            os.system(pull_order)  # 下拉脚本

        # 将新配置文件修改为老配置文件
    os.rename(os.path.join(local_doc, 'test.txt'), os.path.join(cur_doc, 'old_test.txt'))
    return result
if __name__ == '__main__':
    a = pull_script()
    print (a,'script pull success>>>>>')
