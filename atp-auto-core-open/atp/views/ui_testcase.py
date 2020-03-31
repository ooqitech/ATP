
from flask import Blueprint
from flask_restful import Resource
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.mysql_manager import UITestCaseInfoManage, UICasePageInfoManager, UICasePageInfo, BaseSystemInfoManager
from atp.engine.exceptions import LoadCaseError
from atp.utils.tools import json_dumps, json_loads

ui_testcase = Blueprint('ui_testcase_interface', __name__)


class UiTestCase(Resource):
    def __init__(self):
        self.utcim = UITestCaseInfoManage()
        self.data = get_request_json()

    def post(self, action):
        if action == 'add':
            try:
                self.handle_ui_testcase(action, **self.data)
            except LoadCaseError:
                return make_response({"code": "200", "desc": "新增用例时出错"})
            return make_response({"code": "000", "desc": "用例新增成功"})

        elif action == "edit":
            try:
                self.handle_ui_testcase(action, **self.data)
            except LoadCaseError:
                return make_response({"code": "200", "desc": "编辑用例时出错"})
            return make_response({"code": "000", "desc": "编辑用例成功"})
        elif action == "delete":
            try:
                id_ = self.data.pop("id")
            except KeyError:
                return make_response({"code": "100", "desc": "入参校验失败"})
            self.utcim.delete_ui_testcase(id_)
            return make_response({"code": "000", "desc": "测试用例{}删除成功".format(id_)})

    def handle_ui_testcase(self, action, **kwargs):
        '''
        :param kwargs:
        :return:
        '''
        base = kwargs.pop("base")
        module_id = base.pop("moduleId")
        system_id = base.pop("systemId")
        testcase_name = base.pop("testcaseName")
        simple_desc = base.pop("testcaseDesc")
        setup_info = kwargs.pop("setupInfo")
        variable_info = kwargs.pop("variableInfo")
        validate_Info = kwargs.pop("validateInfo")
        include = kwargs.pop("include")
        steps = kwargs.pop("steps")
        setup_case_list = []

        # 配置URL
        # system_obj =BaseSystemInfoManager.query_system(id=system_id)
        # system_url = system_obj.base_host

        # setup_info
        for setup in setup_info:
            if setup["setup_type"] == 'setupcase':
                setup_case_list.append(setup["setup_args"])
            elif setup["setup_type"] == 'setup_db_operation':
                # sql = setup["args"]["sql"]
                pass
        # steps操作步骤
        for step in steps:
            '''根据页面id返回page名称'''
            if step["page_id"]:
                page_id = step["page_id"]
                obj = UICasePageInfoManager.query_ui_page(id=page_id)
                page_name = obj.page_name
                step["page_name"] = page_name
            # ui_request = {
            #     "systemId":system_id,
            #     "testcases": [
            #         {
            #             "name": testcase_name,
            #             "teststeps": steps,
            #             "variables": variable_info,
            #             "validates": validate_Info,
            #         }
            #     ]
            # }
        # 结果验证
        if validate_Info:
            for validate in validate_Info:
                page_id = validate["page_id"]
                obj = UICasePageInfoManager.query_ui_page(id=page_id)
                page_name = obj.page_name
                validate["page_name"] = page_name
        ui_request = {
            "systemId": system_id,
            "testcases": [
                {
                    "name": testcase_name,
                    "teststeps": steps,
                    "variables": variable_info,
                    "validates": validate_Info,
                }
            ]
        }
        '''公共变量'''
        if not isinstance(include, list):
            include = [{"public_variables": []}]
        include.append({"setup_cases": setup_case_list})

        if action == 'add':
            UITestCaseInfoManage.insert_ui_testcase(
                testcase_name=testcase_name,
                simple_desc=simple_desc,
                request=json_dumps(ui_request),
                inlude=json_dumps(include),
                module_id=module_id
            )
        elif action == 'edit':
            testcase_id = base.pop("id", None)
            UITestCaseInfoManage.update_ui_testcase(
                id_=testcase_id,
                testcase_name=testcase_name,
                inlude=json_dumps(include),
                request=json_dumps(ui_request),
                simple_desc=simple_desc,
                module_id=module_id
            )
