# -*- coding:utf-8 -*-
import os
from atp.api.comm_log import logger
try:
    import paramiko
except ImportError:
    logger.error("ImportError: No module named 'paramiko'")


def server_upload_file(ssh_connect, local_path, remote_path):
    """
    向指定服务器上传文件
    :param ssh_connect:
    :param local_path:
    :param remote_path:
    :return:
    """
    if isinstance(ssh_connect, str):
        ssh_info = eval(ssh_connect)
    else:
        ssh_info = ssh_connect
    # 实例化Transport
    ssh = paramiko.Transport(ssh_info[0], ssh_info[1])
    # 建立连接
    ssh.connect(username=ssh_info[2], password=ssh_info[3])
    # 实例化一个sftp对象
    transport = paramiko.SFTPClient.from_transport(ssh)
    try:
        if os.path.isdir(local_path):  # 判断本地参数是目录还是文件
            local_path_list = os.listdir(local_path)
            for f in local_path_list:  # 遍历本地目录
                transport.put(os.path.join(local_path + f), os.path.join(remote_path + f))  # 上传目录中的文件
            logger.debug("上传{0}目录文件成功：{1}".format(local_path, local_path_list))
        else:
            transport.put(local_path, remote_path)  # 上传文件
            logger.debug("上传文件成功：{}".format(local_path))
    except Exception as e:
        logger.debug('上传文件异常:', e)
    ssh.close()

if __name__ == '__main__':
    server_upload_file('[\"**.**.**.**\",22,\"user\",\"password\"]', 'E:\\test\\settings.xml', '/home/admin/settings.xml')
