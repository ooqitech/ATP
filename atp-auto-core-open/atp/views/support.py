# -*- coding:utf-8 -*-

import hashlib
import json
import subprocess

from flask import Blueprint, request
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.engine.return_code_desc import CODE_DESC_MAP
from atp.utils.encryption import Encryption
from atp.utils.tools import str_time_to_timestamp, get_current_timestamp, json_dumps, generate_idcard
from atp.views.wrappers import timer, login_check, developer_check
from atp.utils.common import get_request_json, make_response, read_custom
from atp.api.mysql_manager import BaseJobHistoryManager as bjm
from atp.api.redis_api import RedisManager

redis = RedisManager()
support = Blueprint('support_interface', __name__)


def generate_id_card():
    return make_response({"idcard": generate_idcard()})


class Support(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))

    @timer
    # @login_check
    def post(self, action):
        custom = read_custom()

        if action == "querySupportVariableTypes":
            variable_types = [
                {"description": "key-value", "type": "constant"},
                {"description": "数据库操作", "type": "db"},
                {"description": "特定函数生成", "type": "function"}
            ]

            return make_response({"code": "000", "data": variable_types})

        elif action == "querySignFunctions":
            signs = custom['sign']

            return make_response({"code": "000", "data": signs})

        elif action == 'queryCustomFunctions':
            functions = custom['functions']

            return make_response({"code": "000", "data": functions})

        elif action == 'queryCustomComparators':
            comparators = custom['comparators']

            return make_response({"code": "000", "data": comparators})

        elif action == 'queryCustomSetupHooks':
            setup_hooks = custom['setup-hooks']

            return make_response({"code": "000", "data": setup_hooks})

        elif action == 'queryCustomTeardownHooks':
            teardown_hooks = custom['teardown-hooks']

            return make_response({"code": "000", "data": teardown_hooks})

        elif action == 'syncBaseline':
            return self.synchronize_baseline()

        elif action == 'generateIdCard':
            return generate_id_card()

        elif action == 'logDecrypt':
            return self.log_decrypt()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def synchronize_baseline(self):
        """立即同步业务用例"""
        obj = bjm.get_last_record()
        if obj:
            last_time = format(obj.last_time)
            last_timestamp = str_time_to_timestamp(last_time)
            now_timestamp = get_current_timestamp()
            if last_timestamp + 300 > now_timestamp:
                return make_response({"code": "200", "desc": "距离上次同步不到5分钟，请稍后再试"})

        # git pull
        code, output = subprocess.getstatusoutput('sh /usr/local/src/git_folder/git_pull_baseline.sh')
        if code != 0:
            return make_response({"code": "300", "desc": "git pull动作失败"})

        # parse baseline
        summary_info = parse_main()

        return make_response({"code": "000", "data": "业务用例同步已完成, 详情:{}".format(json_dumps(summary_info))})

    def log_decrypt(self):
        try:
            mmrid = self.data.pop('mmrid')
            mmts = self.data.pop('mmts')
            salt = self.data.pop('salt')
            cipherText = self.data.pop('cipherText')
            ec = self.data.pop('ec', None)
            if not ec:
                ec = None
        except (KeyError, ValueError):
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        origin = ''.join([mmrid, mmts, salt])

        m = hashlib.md5()
        m.update(origin.encode(encoding='UTF-8'))
        key = m.hexdigest()

        e = Encryption()
        response_text = e.decript(Key=key, cipherText=cipherText, ec=ec)

        return make_response(json.loads(response_text))
