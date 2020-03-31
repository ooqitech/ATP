#!/usr/bin/env python
# encoding: utf-8
'''
@time: 2019/12/24 12:38
@desc:
'''
import traceback
import re
import time
from pathlib import Path, PurePosixPath
from atp.api.ssh_client import SSHClient
from atp.api.comm_log import logger


class GetContenFromLog(object):
    """从日志文件中获取信息"""

    def __init__(self, system_name, server_info):
        self.system_path_name = system_name + '-cell01-node01'
        self.sys_log_path = Path('/usr/local/src/logs') / self.system_path_name / 'sys.log'
        self.sys_dubbo_provider_log_path = Path('/usr/local/src/logs') / self.system_path_name / 'sys-dubbo-provider.log'
        self.sys_dubbo_consumer_log_path = Path('/usr/local/src/logs') / self.system_path_name / 'sys-dubbo-consumer.log'
        self.sys_http_log_path = Path('/usr/local/src/logs') / self.system_path_name / 'sys-http.log'
        self.server_info = server_info
        self.start_time = int(time.time() - 600) * 1000
        self.end_time = int(time.time() + 600) * 1000

    def get_mq_log(self, topic, tag):
        """获取mq消息"""
        run_sh = 'grep -A 5 "cn.m*****mq" %s' % (PurePosixPath(self.sys_log_path))
        # 连接服务器并执行shell命令
        with SSHClient(self.server_info) as sh:
            all_mq_log = sh.exec_cmd(run_sh)
        if not all_mq_log:
            return None
        try:
            # 解析返回内容
            for i in all_mq_log.split('\n--\n'):
                clean_data = [x for x in i.split('\n')]
                # 获取日志打印时间
                time_str = clean_data.pop(0)
                mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", time_str)
                log_time = int(time.mktime(time.strptime(mat.group(0), "%Y-%m-%d %H:%M:%S"))) * 1000
                # 只获取最近10分钟的日志
                if self.start_time < log_time < self.end_time:
                    if topic in str(clean_data) and tag in str(clean_data):
                        yield clean_data[4].split('=')[1].strip()
        except Exception as err:
            logger.error(traceback.format_exc())
            raise err


if __name__ == '__main__':
    pass
