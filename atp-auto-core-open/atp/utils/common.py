# -*- coding:utf-8 -*-

import json
import re

from flask import request
from flask import jsonify

from atp.api.comm_log import logger
from atp.utils.tools import json_dumps
from atp.config.default import get_config

CONFIG = get_config()

from atp.api.redis_api import r
# r = RedisManager()

GL_USERNAME_NICKNAME_CACHE_DIC = {}


def get_request_json():
    data = request.get_json()
    logger.info('<Request> url= {url}, body= {body}'.format(url=request.url, body=json.dumps(data, ensure_ascii=False)))
    return data


def make_response(response_dict):
    response_str = json.dumps(response_dict, ensure_ascii=False)
    if len(response_str) <= 5000:
        logger.info("<Response> body= {body}".format(body=response_str))
    else:
        logger.info("<Response> body= {len} characters".format(len=len(response_str)))
    return jsonify(response_dict)


def read_custom():
    function_name_pattern = r'def ([\w_]+)\('
    function_description_pattern = r'    """ ([\w_、()-]+)'
    function_param_description_pattern = r' : ([\w_, ]+)'
    custom_type_pattern = r'""" custom ([\w_-]+)'
    custom = {}
    custom_type = None
    function_name = None
    with open(CONFIG.CUSTOM_FILE, mode='r', encoding='utf8') as f:
        for line in f:
            if line.startswith('""" custom '):
                # 自定义函数类型
                custom_type = re.findall(custom_type_pattern, line)[0]
                custom[custom_type] = []

            elif line.startswith('def '):
                # 自定义函数名称
                function_name = re.findall(function_name_pattern, line)[0]
                custom[custom_type].append(
                    {
                        "name": function_name,
                        "description": "",
                        "parameters": [],
                        "introduction": [],
                    }
                )

            elif line.startswith('    """ '):
                # 自定义函数名描述
                function_description = re.findall(function_description_pattern, line)[0]
                try:
                    function_param_description = re.findall(function_param_description_pattern, line)[0]
                except IndexError:
                    function_param_description = None
                for func in custom[custom_type]:
                    if func['name'] == function_name:
                        func['description'] = function_description
                        if function_param_description:
                            func['parameters'] = function_param_description.replace(' ', '').split(',')
                        else:
                            func['parameters'] = []
                        break
            elif line.startswith('    :desc:'):
                # 自定义函数具体描述
                desc = line.strip('    :desc:').strip('\n')
                for func in custom[custom_type]:
                    if func['name'] == function_name:
                        label, value = [i.strip() for i in desc.split(':', 1)]
                        func['introduction'].append({"label": label, "value": value})
                        break
            elif line.startswith('    :param '):
                # 自定义函数参数具体描述
                param = line.split(':', 2)[2].strip('\n')
                for func in custom[custom_type]:
                    if func['name'] == function_name:
                        param_list = param.split(':', 1)
                        label = param_list[0]
                        value = param_list[1] if len(param_list) > 1 else ''
                        func['introduction'].append({"label": label, "value": value})
                        break

    return custom


def username_to_nickname(username):
    if not username:
        return username

    # 在这里初始化redis特别耗时！！！
    # from atp.api.redis_api import RedisManager
    # r = RedisManager()

    global GL_USERNAME_NICKNAME_CACHE_DIC
    if username in GL_USERNAME_NICKNAME_CACHE_DIC:
        return GL_USERNAME_NICKNAME_CACHE_DIC[username]
    else:
        nickname = r.get_user_info(username, 'nickname')
        if nickname:
            GL_USERNAME_NICKNAME_CACHE_DIC[username] = nickname
            return nickname
        else:
            return username
    # return nickname if nickname else username


def db_result_to_map(query_res, patch_res=None):
    mapped_dic = {}
    if not patch_res:
        patch_res = []
    for row in query_res:
        width = len(row)
        # print(row)
        if row[0] not in mapped_dic:
            mapped_dic[row[0]] = {'name': row[1]}
            if width >= 4 and row[2]:
                mapped_dic[row[0]][row[2]] = {'name': row[3]}
                if width >= 6 and row[4]:
                    mapped_dic[row[0]][row[2]][row[4]] = {'name': row[5]}
                    if width >= 8 and row[6]:
                        mapped_dic[row[0]][row[2]][row[4]][row[6]] = {'name': row[7]}
        else:
            if width >= 4 and row[2] not in mapped_dic[row[0]]:
                mapped_dic[row[0]][row[2]] = {'name': row[3]}
                if width >= 6 and row[4]:
                    mapped_dic[row[0]][row[2]][row[4]] = {'name': row[5]}
                    if width >= 8 and row[6]:
                        mapped_dic[row[0]][row[2]][row[4]][row[6]] = {'name': row[7]}
            else:
                if width >= 6 and row[4] not in mapped_dic[row[0]][row[2]]:
                    mapped_dic[row[0]][row[2]][row[4]] = {'name': row[5]}
                    if width >= 8 and row[6]:
                        mapped_dic[row[0]][row[2]][row[4]][row[6]] = {'name': row[7]}
                else:
                    if width >= 8 and row[6] not in mapped_dic[row[0]][row[2]][row[4]]:
                        mapped_dic[row[0]][row[2]][row[4]][row[6]] = {'name': row[7]}

    for row in patch_res:
        if row[0] in mapped_dic:
            if row[2] and row[2] not in mapped_dic[row[0]]:
                mapped_dic[row[0]][row[2]] = {'name': row[3]}

    # print(json_dumps(mapped_dic))
    # print(mapped_dic)
    return mapped_dic


if __name__ == '__main__':
    print(json_dumps(read_custom()))


