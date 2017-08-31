#安装客户端依赖的第三方模块脚本

#出现End 字样安装完成
import os
from client_doc import setting

print ('Starting....')
for moudel in setting.INSTALL_MOUDEL:
    os.system('%s %s' % ('pip3 install', moudel)) #安装依赖模块
print ('End......')