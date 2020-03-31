# -*- coding:utf-8 -*-

import requests
import json
import urllib3
import traceback
from atp.utils.tools import json_loads, json_dumps
from atp.api.comm_log import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HttpClient:
    # 初始化
    def __init__(self):
        # 'content-type': 'application/json',
        self.isSession = True
        self.jason_info = ''
        self.cookie_info = ''

        self.is_session = self.isSession
        if self.is_session:
            self._sobj = requests.Session()
        self.resp = None

    # get请求，返回的是对象
    def http_get(self, url, heard_info, param=None, time_data=30):

        try:
            if param:
                param = eval(param)
            self.resp = self._sobj.get(url, headers=heard_info, params=param, verify=False, timeout=time_data,
                                       allow_redirects=False)
        except Exception as e:
            logger.error(traceback.format_exc())
            self.resp = None
        return self.resp

    # post 请求 ，返回的是对象
    def http_post(self, url, heard_info, param=None, files=None, time_data=30):

        try:
            if param and 'Content-Type' in heard_info and 'application/x-www-form-urlencoded' not in heard_info['Content-Type']:  # 短路规则
                param = json.dumps(param)

            self.resp = requests.post(url, headers=heard_info, data=param, files=files, verify=False, timeout=time_data,
                                      allow_redirects=False)

        except Exception as e:
            logger.error(traceback.format_exc())
            self.resp = None
        return self.resp

    def http_post_file(self, url, heard_info, param=None, files=None, time_data=30):

        try:

            self.resp = requests.post(url, headers=heard_info, data=param, files=files, verify=False, timeout=time_data,
                                      allow_redirects=False)

        except Exception as e:
            logger.error(traceback.format_exc())
            self.resp = None
        return self.resp

    # post 请求 ，返回的是对象
    def http_put(self, url, heard_info, param=None, files=None, time_data=30):

        try:
            # print("请求URL链接为:\n\n{0}".format(url))
            # print("请求体为：\n\n{0}".format(json.dumps(param,ensure_ascii=False,indent=4)))
            if param and 'Content-Type' in heard_info and 'application/x-www-form-urlencoded' not in heard_info['Content-Type']:  # 短路规则
                param = json.dumps(param)
            self.resp = requests.put(url, headers=heard_info, data=param, files=files, verify=False, timeout=time_data,
                                     allow_redirects=False)

        except Exception as e:
            logger.error(traceback.format_exc())
            self.resp = None
        return self.resp


if __name__ == '__main__':
    pass
