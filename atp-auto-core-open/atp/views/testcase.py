# -*- coding:utf-8 -*-

import json

from flask import Blueprint, request

from atp.api.mysql_manager import BaseModuleInfoManager, BaseTestcaseInfoManager
from atp.utils.tools import json_dumps
from flask_restful import Resource

# from atp.api.comm_log import logger
# from atp.engine.handle_testcase import handle_testcase
# from atp.api.mysql_manager import (
#     TestsuiteInfoManager, TestcaseInfoManager, ModuleInfoManager, SystemInfoManager, TestcaseTagManager,
#     query_testcase_belong, TestcaseTagRelationManager, BaseTestcaseInfoManager, BaseModuleInfoManager,
#     UITestCaseInfoManage,BaseSystemInfoManager,UiSystemInfoManager,UiModuleInfoManager
#     )
from atp.views.wrappers import timer, login_check, developer_check

from atp.utils.common import get_request_json, make_response, username_to_nickname
# from atp.engine.testcase_detail import get_testcase_detail
from atp.api.redis_api import RedisManager

redis = RedisManager()
testcase = Blueprint('testcase_interface', __name__)


class Testcase(Resource):
    def __init__(self):
        self.list = []
        self.chain_no = 0
        self.data = get_request_json()
        self.btim = BaseTestcaseInfoManager
        self.username = redis.get_username(request.headers.get('X-Token'))
        if self.username:
            self.data["userName"] = self.username

    @timer
    def post(self, action):

        if action == 'detailBaseCase':
            return self.detail_base_case()

        elif action == 'queryByModuleId':
            return self.query_basecase_list()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def query_basecase_list(self):
        try:
            module_id = int(self.data.pop("moduleId"))
            page_no = int(self.data.pop('pageNo'))
            page_size = int(self.data.pop('pageSize'))
            testcase_name = self.data.pop('testcaseName', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})
        if not module_id:
            return make_response({"code": "101", "desc": "moduleId不能为空"})
        if not BaseModuleInfoManager.get_module(id=module_id):
            return make_response({"code": "200", "desc": "业务功能名不存在"})
        result = BaseTestcaseInfoManager.query_all_basecase(module_id, page_no, page_size, testcase_name)
        # operator = self.data.pop("userName")
        base_case_list = []
        for obj in result.items:
            base_case_list.append({
                "id": obj.id,
                "testcase_name": obj.testcase_name,
                "test_type": obj.test_type,
                "req_num": obj.req_num
            })
        return make_response({"code": "000", "desc": base_case_list, "totalNum": result.total})

    @developer_check
    def detail_base_case(self):
        respone = {
            "steps":
                {
                    "stepsInfo": [],
                }
        }
        try:
            base_case_id = self.data.pop("id")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})
        obj = self.btim.get_testcase(id=base_case_id)
        if not obj:
            return make_response({"code": "101", "desc": "查询失败,用例不存在"})

        detail_list = json.loads(obj.detail)
        step_no = 0
        for detail_dic in detail_list:
            step_no += 1
            temp_dic = {}
            for k, v in detail_dic.items():
                temp_dic["stepNo"] = step_no
                if k == "前置条件":
                    temp_dic["setup"] = v
                elif k == "操作步骤":
                    temp_dic["operating"] = v
                elif k == "预期结果":
                    temp_dic["expected"] = v
                elif k == "备注":
                    temp_dic["memo"] = v

            respone["steps"]["stepsInfo"].append(temp_dic)

        return make_response({"code": "000", "data": respone})


def query_systemid_by_moduleid(self,_id):
    '''根据业务用例最后一层模块id查找系统id'''
    module_obj = BaseModuleInfoManager.get_module(id=_id)
    parent_module_id = module_obj.parent_module_id
    system_id= module_obj.system_id
    if not parent_module_id:
        return system_id
    else:
        return self.query_systemid_by_moduleid(parent_module_id)
