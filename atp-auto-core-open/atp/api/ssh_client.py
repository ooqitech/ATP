# -*- coding:utf-8 -*-

import paramiko
import time
import traceback
from atp.api.comm_log import logger

from atp.utils.tools import get_current_timestamp, get_current_time


class SSHClient(object):
    """
    SSH客户端
    """

    def __init__(self, servers_info):
        self.client = paramiko.SSHClient()
        # 允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.hostname = servers_info[0]
        self.port = servers_info[1]
        self.username = servers_info[2]
        self.password = servers_info[3]
        self.shell = None
        self.timeout = 5

    def __enter__(self):
        try:
            logger.info(
                '开始连接服务器，服务器连接信息：hostname-{0}，port-{1}， username-{2}, password-{3}'.format(self.hostname, self.port,
                                                                                           self.username,
                                                                                           self.password))
            self.client.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password,
                                timeout=self.timeout)
            return self
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    def exec_cmd(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        data = stdout.read().decode()
        if len(data) > 0:
            logger.info(data.strip())  # 打印正确结果
            return data
        err = stderr.read().decode()
        if len(err) > 0:
            logger.error(err.strip())  # 输出错误结果
            return err

    def run_cmd(self, cmd):
        if self.shell is None:
            self.shell = self.client.invoke_shell()
        self.shell.send(cmd + '\n')
        time.sleep(2)
        out = self.shell.recv(1024).decode('utf8')
        return out

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info('开始清理操作，关闭SSH连接')
        if self.shell:
            self.shell.close()
        if self.client:
            self.client.close()


if __name__ == '__main__':
    server_info_list = ['**.**.**.**', 22, 'user', 'password']
    base_path = '/usr/local/src/logs'
    from pathlib import Path, PurePosixPath
    import json
    log_path = Path(base_path) / 'user-core-cell01-node01' / 'sys.log'
    cmd = 'grep -A 5 "*********" %s' % (PurePosixPath(log_path))
    with SSHClient(server_info_list) as client:
        mq_msg = client.exec_cmd(cmd).split('\n--\n')
        res = []
        for i in mq_msg:
            clean_data = [x.replace(' ', '') for x in i.split('\n')]
            clean_data.pop(0)
            clean_data = filter(lambda x: x != '', clean_data)
            _clean_data = {}
            for k in clean_data:
                _clean_data[k.split('=')[0]] = k.split('=')[1]
            res.append(_clean_data)
        print(json.dumps(res))
