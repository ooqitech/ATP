# -*- coding:utf-8 -*-

import json
from flask import request
from flask import Blueprint
from flask_restful import Resource
from atp.engine.run_uitest import run_uitest
from atp.views.wrappers import timer, developer_check, login_check
from atp.utils.common import get_request_json, make_response
from atp.engine.exceptions import LoadCaseError, RunCaseError, NoSuchElementError
from atp.api.redis_api import RedisManager

redis = RedisManager()
run_ui = Blueprint('run_ui_interface', __name__)


class RunUiTestCase(Resource):
    def __init__(self):
        self.data = get_request_json()

    @timer
    @developer_check
    def post(self):
        try:
            testcase_id_list = self.data.pop("testaCases")
            remote_url = self.data.pop("remoteUrl", None)
            local_browser = self.data.pop("localBrowser",None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})
        try:
            reportUrl = run_uitest(testcase_id_list, remote_url,local_browser)
        except LoadCaseError:
            return make_response({"code": "201", "desc": "组装用例时出错"})
        except RunCaseError:
            return make_response({"code": "200", "desc": "运行UI用例时出错,请检查运行环境"})
        return make_response({"code": "000", "desc": "运行成功", "reportUrl": reportUrl})
