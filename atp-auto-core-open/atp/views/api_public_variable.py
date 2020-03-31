# -*- coding:utf-8 -*-

import json

import re
from flask import request
from flask import Blueprint
from flask_restful import Resource
from atp.api.mysql_manager import (
    ApiPublicVariableInfoManager, ApiTestcaseInfoManager, ApiSystemInfoManager, ApiProjectInfoManager,
    ApiCompanyInfoManager, ApiIntfInfoManager, ApiTestcaseMainManager, ApiTestcaseSubManager
)
from atp.engine.api_chain import parse_setup_case_str
from atp.utils.tools import json_loads, transfer_function_variable_to_expression
from atp.views.wrappers import timer, developer_check, login_check
from atp.utils.common import get_request_json, make_response, username_to_nickname, read_custom
from atp.api.redis_api import RedisManager

redis = RedisManager()
api_public_variable = Blueprint('api_public_variable_interface', __name__)


class ApiPublicVariable(Resource):
    def __init__(self):
        self.apv = ApiPublicVariableInfoManager()
        self.atim = ApiTestcaseInfoManager()
        self.asim = ApiSystemInfoManager()
        self.apim = ApiProjectInfoManager()
        self.acim = ApiCompanyInfoManager()
        self.aiim = ApiIntfInfoManager()
        self.atmm = ApiTestcaseMainManager()
        self.atsm = ApiTestcaseSubManager()
        self.custom = read_custom()

        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))

    @timer
    @login_check
    def get(self, action):
        if action == 'list':
            page = request.args.get('page', 1, type=int)
            num = request.args.get('num', 10, type=int)
            keywords = request.args.get('keywords', None, type=str)
            variable_objs = self.apv.public_variable_paginate(page, num, keywords=keywords)
            total = variable_objs.total
            data = []
            for variable in variable_objs.items:
                if variable.api_system_id:
                    system_obj = self.asim.get_system(id=variable.api_system_id)
                    company_obj = self.acim.get_company(id=system_obj.api_company_id)
                    company_id = system_obj.api_company_id
                    system_id = variable.api_system_id
                    company_name = company_obj.company_name
                    system_name = system_obj.system_name
                elif variable.api_company_id:
                    company_obj = self.acim.get_company(id=variable.api_company_id)
                    company_id = variable.api_company_id
                    company_name = company_obj.company_name
                    system_id = None
                    system_name = None
                else:
                    company_id = None
                    system_id = None
                    company_name = None
                    system_name = None
                variable_dict = {}
                variable_value = variable.value
                # 变量类型-files
                if variable.type == 'files':
                    if isinstance(variable_value, str):
                        '''windows下文件路径 C:\\users: \\json解析报错，先替换成\\\\'''
                        try:
                            variable_value = json.loads(variable_value.replace('\\', '\\\\'))
                            variable_value = json.loads(json.dumps(variable_value).replace('\\\\', '\\'))
                        except TypeError:
                            variable_value = json.loads(variable_value)
                    variable_dict["name"] = variable.variable_name
                    variable_dict["type"] = "files"
                    variable_dict["type_desc"] = "文件"
                    variable_dict["value"] = variable_value

                # 自定义变量-db
                elif variable_value.startswith("${variable_db_operation("):
                    variable_dict["name"] = variable.variable_name
                    variable_dict["type"] = "db"
                    variable_dict["type_desc"] = "数据库操作"
                    variable_dict["value"] = variable_value.replace(
                        "${variable_db_operation(", "", 1).replace(
                        "||$DB_CONNECT)}", "", 1)

                # 变量类型-function
                elif variable_value.startswith('${') and variable_value.endswith('}'):
                    func_name = variable_value.split('${')[-1].split('(')[0]
                    if 'variable_db_operation' == func_name:
                        continue
                    # args_list = variable_value.split('(')[-1].split(')')[0].split(',')
                    args_list = variable_value[:-2].split('(', 1)[-1].split('||')
                    args_dict = {}
                    for func in self.custom["functions"]:
                        if func["name"] == func_name:
                            for a, p in zip(args_list, func["parameters"]):
                                args_dict[p] = a
                            break

                    variable_dict["name"] = variable.variable_name
                    variable_dict["type"] = "function"
                    variable_dict["type_desc"] = "特定函数生成"
                    variable_dict["value"] = func_name
                    variable_dict["args"] = args_dict

                # 变量类型-constant
                else:
                    variable_dict["name"] = variable.variable_name
                    variable_dict["type"] = "constant"
                    variable_dict["type_desc"] = "key-value"
                    variable_dict["value"] = variable_value
                    variable_dict["saveAs"] = variable.save_as if variable.save_as else 'str'

                variable_dict.update(
                    {
                        "variable_id": variable.id,
                        "simple_Desc": variable.simple_desc,
                        "creator": username_to_nickname(variable.creator),
                        "system_id": system_id,
                        "company_id": company_id,
                        "company_name": company_name,
                        "system_name": system_name
                    }
                )
                data.append(variable_dict)
            return make_response({"code": "000", "total": total, "desc": data})

    @timer
    def post(self, action):
        if action == 'addVariable':
            return self.add_variable()

        elif action == "delete":
            return self.delete_variable()

        elif action == "edit":
            return self.edit_variable()

        elif action == "detail":
            return self.detail()

        elif action == "querySupportPubVariables":
            return self.query_support_pub_variables()

        elif action == "queryPubVariablesByTestcaseList":
            return self.query_pub_variables_by_testcase_list()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def add_variable(self):
        """
            input：
            {
                "variableName":1,
                "type":"function",
                "value":"123",
                "simpleDesc":"s",
                "systemId":"1",
                "companyId":"1",
                "saveAs": "str",
            }
            """
        try:
            system_id = self.data.pop("systemId", None)
            company_id = self.data.pop("companyId", None)
            variable_name = self.data.pop("variableName")
            variable_type = self.data.pop("variableType")
            value = self.data.pop("value")
            args = self.data.pop("args", None)
            simple_desc = self.data.pop("simpleDesc", None)
            save_as = self.data.pop("saveAs", "str")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        if system_id:
            if self.apv.get_variable(variable_name=variable_name, api_system_id=system_id):
                return make_response({"code": "201", "desc": "变量名{}已经存在，请重新添加".format(variable_name)})
        elif company_id:
            if self.apv.get_variable(variable_name=variable_name, api_company_id=company_id):
                return make_response({"code": "202", "desc": "变量名{}已经存在，请重新添加".format(variable_name)})
        else:
            return make_response({"code": "300", "desc": "systemId/companyId二选一必填"})

        if variable_type == 'files' and isinstance(value, list):
            value_str = json.dumps(value)
        elif variable_type == 'function':
            value_str = transfer_function_variable_to_expression(value, args)
        else:
            value_str = value
        self.apv.insert_variable(
            api_company_id=company_id, api_system_id=system_id, variable_name=variable_name, type=variable_type,
            value=value_str, simple_desc=simple_desc, creator=self.username, save_as=save_as)
        return make_response({"code": "000", "desc": "变量{}新增成功".format(variable_name)})

    @developer_check
    def delete_variable(self):
        """根据变量名称（唯一）删除变量
            input:
            {
              "variable_name":"test",
              "systemId":"1"
            }
        """
        try:
            variable_id = int(self.data.pop("variableId"))
            # id_=data.pop("id")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        pv_obj = self.apv.get_variable(id=variable_id)
        if not pv_obj:
            return make_response({"code": "000", "desc": "变量id{}不存在，请刷新后重试".format(variable_id)})

        include_list = self.atim.query_all_testcases_include()
        for row in include_list:
            if not row[0]:
                continue
            include = json_loads(row[0])
            if 'public_variables' in include[0]:
                if variable_id in include[0]['public_variables']:
                    return make_response({"code": "200", "desc": "存在用例引用公共变量，无法直接删除"})

        self.apv.delete_variable(pv_obj.id)
        return make_response({"code": "000", "desc": "变量删除成功"})

    @developer_check
    def edit_variable(self):
        """
            根据变量id或者变量名称编辑变量
            input：
                {
                 "variable_name:"
                }
            """
        try:
            id_ = self.data.pop('id')
            variable_name = self.data.pop("variableName")
            value = self.data.pop("value", None)
            variable_type = self.data.pop("variableType", None)
            simple_desc = self.data.pop("simpleDesc", None)
            system_id = self.data.pop("systemId", None)
            company_id = self.data.pop("companyId", None)
            args = self.data.pop("args", None)
            save_as = self.data.pop("saveAs", "str")
        except KeyError:
            return make_response({"code": "100", "desc": "传参错误"})

        # 变量名称唯一：如果想修改的变量名称，在作用域内被其它变量已使用，不能修改
        if system_id:
            if not self.asim.get_system(id=system_id):
                return make_response({"code": "101", "desc": "systemId不存在"})
            if self.apv.whether_variable_name_canbeupdated(variable_name, id_, system_id):
                return make_response({"code": "102", "desc": "变量名{}已存在，请重新修改".format(variable_name)})
        elif company_id:
            if not self.acim.get_company(id=company_id):
                return make_response({"code": "101", "desc": "companyId不存在"})
            if self.apv.whether_variable_name_canbeupdated_in_company_id(variable_name, id_, company_id):
                return make_response({"code": "102", "desc": "变量名{}已存在，请重新修改".format(variable_name)})
        else:
            return make_response({"code": "201", "desc": "systemId/companyId二选一必填"})

        if variable_type == 'files' and isinstance(value, list):
            value_str = json.dumps(value)
        elif variable_type == 'function':
            value_str = transfer_function_variable_to_expression(value, args)
        else:
            value_str = value
        self.apv.update_variable(
            id_, variable_name=variable_name, value=value_str, type=variable_type, simple_desc=simple_desc,
            api_system_id=system_id, api_company_id=company_id, save_as=save_as
        )
        return make_response({"code": "000", "desc": "变量{}已修改".format(variable_name)})

    @login_check
    def detail(self):
        """根据变量名称，获取变量详情 ----未找到使用场景"""
        try:
            system_id = self.data.pop("systemId")
            variable_name = self.data.pop("variableName")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        variable = self.apv.get_variable(api_system_id=system_id, variable_name=variable_name)
        if not variable:
            return make_response({"code": "200", "desc": "该系统下的变量名{}不存在".format(variable_name)})
        id_ = variable.id
        variable_name = variable.variable_name
        value = variable.value
        simple_desc = variable.simple_desc
        variable_type = variable.type
        if variable.system_id:
            system_obj = self.asim.get_system(id=variable.system_id)
            company_obj = self.acim.get_company(id=system_obj.api_company_id)
            company_name = company_obj.company_name
            system_name = system_obj.system_name
        else:
            company_name = None
            system_name = None
        return make_response(
            {"code": "000",
             "data": {
                 "id": id_,
                 "company_name": company_name,
                 "system_name": system_name,
                 "variable_name": variable_name,
                 "value": value,
                 "type": variable_type,
                 "simpleDesc": simple_desc
             }}
        )

    @login_check
    def query_support_pub_variables(self):
        """获取某一类型下的变量列表
            input: {variable_type:"constant"}
            output:{
                   "code": "000",
                   "desc": {
                       "constant": [
                           {
                               "id": 7,
                               "simpleDesc": "ssd",
                               "value": "dfssfds",
                               "variable_name": "hejianhao05"
                           },
                           {
                               "id": 11,
                               "simpleDesc": "gdfg",
                               "value": "dfgdf",
                               "variable_name": "dgfdfgfdg"
                           },
                           {
                               "id": 16,
                               "simpleDesc": null,
                               "value": "select * from fromfrormrmf",
                               "variable_name": "hjhdf"
                           }
                       ]
                   }
               }"""

        objs = self.apv.get_variables()
        desc_dic = {
            "constant": [],
            "db": [],
            "function": [],
            "files": []
        }
        for obj in objs:
            for desc_key in desc_dic.keys():
                if obj.type == desc_key:
                    desc_dic[desc_key].append({
                        "id": obj.id,
                        "variable_name": obj.variable_name,
                        "value": obj.value,
                        "simpleDesc": obj.simple_desc
                    })
                    break
        return make_response({
            "code": "000",
            "desc": desc_dic
        }
        )

    @login_check
    def query_pub_variables_by_testcase_list(self):
        """
        根据testcase_id_list查询当前用例以及所有前置用例引用的公共变量信息
        url:/atp/apiPublicVariable/queryPubVariablesByTestcaseList
        input:{"testcaseList":["666", "999"]}
        output:{
            "code": "000",
            "pubVariablesList": [
                {
                    "id": "",
                    "name": "",
                    "value": "",
                    "type": "",
                    "optionValues": ["" , ""]
                },
                {
                    "id": "",
                    "name": "",
                    "value": "",
                    "type": "",
                    "optionValues": []
                }
            ]
        }
        """
        try:
            testcase_id_list = self.data.pop("testcaseList", None)
            testcase_main_id_list = self.data.pop("testcaseMainList", None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        if not testcase_id_list and not testcase_main_id_list:
            return make_response({"code": "100", "desc": "入参校验失败"})

        target_pv_id_list = self.get_all_pv_id_list(
            [], testcase_id_list=testcase_id_list, testcase_main_id_list=testcase_main_id_list)
        print(target_pv_id_list)
        pv_objs = self.apv.get_variables_in_id_list(target_pv_id_list)

        data_list = []
        for pv_obj in pv_objs:
            """
            from
            pv_obj.value : "12|| wudi || sad2s||"
            to
            pv_value_list : ['12', 'wudi', 'sad2s']
            """
            '''如果是文件类型的变量，暂不支持可选值'''
            if pv_obj.type == 'files':
                continue
            elif pv_obj.type == 'function':
                pv_value_list = []
                default_value = str(pv_obj.value).strip()
            else:
                pv_value_list = [v.strip() for v in str(pv_obj.value).strip('##').split('##')]
                default_value = pv_value_list.pop(0)

            tmp_dic = {
                "id": pv_obj.id,
                "name": pv_obj.variable_name,
                "value": default_value,
                "type": pv_obj.type,
                "optionValues": pv_value_list
            }
            data_list.append(tmp_dic)

        return make_response({
            "code": "000",
            "pubVariablesList": data_list
        })

    def get_all_pv_id_list(self, target_pv_id_list, testcase_id_list=None, testcase_main_id_list=None):
        if testcase_id_list:
            for testcase_id in testcase_id_list:
                obj = self.atim.get_testcase(id=testcase_id)
                include_list = json_loads(obj.include)
                public_variables_list = []
                for include in include_list:
                    if 'public_variables' in include:
                        public_variables_list = include['public_variables']
                # public_variables_list = include_list[0]['public_variables']
                # setup_cases_list = include_list[1]['setup_cases']

                for public_variable_id in public_variables_list:
                    if public_variable_id not in target_pv_id_list:
                        target_pv_id_list.append(public_variable_id)

                if obj.setup_case_list:
                    setup_case_list = json_loads(obj.setup_case_list)
                    for setup_case_str in setup_case_list:
                        case_type, case_id, case_flow_id = parse_setup_case_str(setup_case_str)
                        if case_type == 1:
                            testcase_id_list = [case_id]
                            target_pv_id_list = self.get_all_pv_id_list(target_pv_id_list, testcase_id_list=testcase_id_list)
                        elif case_type == 2:
                            testcase_main_id_list = [case_id]
                            target_pv_id_list = self.get_all_pv_id_list(target_pv_id_list, testcase_main_id_list=testcase_main_id_list)
        elif testcase_main_id_list:
            exist_main_teardown_var_name = set()   # 已加载的全链路独立后置中的公共变量名称集合
            for testcase_id in testcase_main_id_list:
                tm_obj = self.atmm.get_testcase_main(id=testcase_id)
                sub_list = json_loads(tm_obj.sub_list)
                for sub_id in sub_list:
                    ts_obj = self.atsm.get_testcase_sub(id=sub_id)
                    include_list = json_loads(ts_obj.include)
                    public_variables_list = include_list[0]['public_variables']

                    for public_variable_id in public_variables_list:
                        if public_variable_id not in target_pv_id_list:
                            target_pv_id_list.append(public_variable_id)

                    # 处理全链路用例独立后置步骤中的公共变量
                    if tm_obj.main_teardown_hooks:
                        variable_regexp = r"\$([\w_]+)"
                        main_teardown_variables = re.findall(variable_regexp, str(tm_obj.main_teardown_hooks))
                        for target in main_teardown_variables:
                            if target in exist_main_teardown_var_name:
                                continue
                            intf_id = ts_obj.api_intf_id
                            intf_obj = ApiIntfInfoManager.get_intf(id=intf_id)
                            system_id = intf_obj.api_system_id
                            s_var_obj = ApiPublicVariableInfoManager.get_variable(variable_name=target, api_system_id=system_id)

                            if s_var_obj:
                                target_pv_id_list.append(s_var_obj.id)
                            else:
                                company_id = ApiSystemInfoManager.get_system(id=system_id).api_company_id
                                c_var_obj = ApiPublicVariableInfoManager.get_variable(
                                    variable_name=target, api_company_id=company_id)
                                if c_var_obj:
                                    target_pv_id_list.append(c_var_obj.id)
                            exist_main_teardown_var_name.add(target)

        return target_pv_id_list
