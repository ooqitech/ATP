# coding=utf-8

import os, time, logging
from flask import request
from flask import Blueprint
from flask_restful import Resource
from atp.views.wrappers import timer, developer_check
from atp.utils.common import get_request_json, make_response
from atp.engine.import_xmind_cases import xmind_parser, upload_file
from atp.api.redis_api import RedisManager
redis = RedisManager()
basedir = os.path.abspath(os.path.join(os.getcwd(), ".."))
file = Blueprint('file_interface', __name__)

class File(Resource):
    def __init__(self):
        self.username = redis.get_username(request.headers.get("Cookie").
                                           split("; token=")[1])
    @timer
    def post(self, action):
        if action == 'upload':
            '''上传文件接口，导入规则： '''
            try:
                # file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
                file_dir = os.path.join(basedir, 'upload')
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                f = request.files['file']
                '''判断上传文件格式；上传timeout=5s
                    返回文件路径，是否上传成功布尔值'''
                tup = upload_file(f, file_dir)
                if isinstance(tup, tuple) and len(tup)>=2:
                    import_xmind_path = tup[0]
                    is_file_exits = tup[1]
                    if is_file_exits:
                        '''如果上传的是png和jpg图片直接返回图片的时间戳文件名称
                            如果上传的是xmind，先解析再插入用例'''
                        if not tup[2].endswith('xmind'):
                            return make_response({"code": "000", "desc": tup[0]})
                        else:
                            pass
                            # testcase_dict = xmind_parser(import_xmind_path)
                            # count = generate_testcases(testcase_dict,self.username)
                            # return make_response({"code": "000", "desc": "导入成功，新增用例{}条".format(count)})
                    else:
                        return make_response({"code": "001", "desc": "文件上传超时路径{}未找到".format(import_xmind_path)})
                else:
                    return make_response({"code": "003", "desc": "不支持的文件上传类型"})
            except FileNotFoundError as e:
                return e
        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})
