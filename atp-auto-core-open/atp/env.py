# -*- coding:utf-8 -*-

# import os
import socket
import re
import platform
import psutil

# try:
#     import psutil
# except Exception as e:
#     #pip.exe install psutil
#     print('psutil not found.pip install psutil')
#


# 从环境变量获取RUNNING_ENV
# os_env = os.environ.get('ATP_AUTO_ENV')

# 根据{ip:环境}映射关系获取RUNNING_ENV
ip_env_map = {
    'XX.XX.XX': 'DEV',
    'XX.XX.XX': 'ALIUAT'
}

RUNNING_ENV = None
current_ip = None

for interface, snics in psutil.net_if_addrs().items():
    for snic in snics:
        ## ipv4
        if snic.family == socket.AF_INET:
            for k, v in ip_env_map.items():
                if re.search(k, snic.address):
                    RUNNING_ENV = v
                    current_ip = snic.address
                    break

if RUNNING_ENV:
    print("current IP:{0}, get ENV: {1}".format(current_ip, RUNNING_ENV))
else:
    RUNNING_ENV = 'DEV'
    print("current IP: {0}, not found in ip_env_map, use default ENV: {1}".format(current_ip, RUNNING_ENV))

# print(psutil.net_if_addrs().items())

