# -*- coding:utf-8 -*-

import json
import re

from datetime import datetime

from atp.api.mysql_manager import (
    ApiTestcaseInfoManager, ApiIntfInfoManager,
    ApiTestcaseRequestManager, ApiPublicVariableInfoManager, ApiSystemInfoManager,
    ApiTestcaseSubManager, ApiTestcaseMainManager, ApiTestcaseTagRelationManager, ApiTestcaseMainTagRelationManager,
    ApiTestcaseMainCustomFlowManager)
from atp.engine.code_to_desc import get_case_type_by_desc
from atp.utils.common import read_custom
from atp.engine.exceptions import RunCaseError, LoadCaseError
from atp.utils.map_functions import map_testcase_type_to_number
from atp.utils.tools import json_dumps, json_loads
from atp.api.comm_log import logger

variable_pattern = r'\${([\w_]+)}'
variable_regexp = r"\$([\w_]+)"
env_variable_list = ["DUBBO_ZOOKEEPER", "DB_CONNECT", "REMOTE_HOST", "DISCONF_HOST", "REDIS_CONNECT", "MQ_AK", "MQ_SK",
                     "request"]
CUSTOM = read_custom()


def change_variable_format(request):
    """
    e.g.
        "json": {"pageSize": "${pageSize}"} => "json": {"pageSize": "$pageSize"}

    :param request:
    :return:
    """
    variables_list = re.findall(variable_pattern, request)

    for variable in variables_list:
        request = request.replace("${{{variable}}}".format(variable=variable), "${variable}".format(variable=variable),
                                  1)
    return request


# def handle_testcase(action, **kwargs):
#     """
#     旧版-保存测试用例到数据库
#     :param action:
#     :param kwargs:
#     :return:
#     """
#     # 处理base
#     base = kwargs.pop("base")
#     system_id = base.pop("systemId")
#     module_id = base.pop("moduleId")
#     testsuite_id = base.pop("testsuiteId")
#     testcase_name = base.pop("testcaseName")
#     simple_desc = base.pop("testcaseDesc", "")
#     expect_result = base.pop("expectResult")
#     operator = kwargs.pop("userName")
#
#     intf_type = TestsuiteInfoManager.query_testsuite_by_id(testsuite_id).intf_type
#     testcase_type = map_testcase_type_to_number(intf_type)
#
#     hr_request = {
#         "name": testcase_name,
#         "config": {
#             "variables": [],
#             "request": {
#                 "base_url": "",
#             }
#         },
#         "teststeps": []
#     }
#
#     # 处理steps
#     steps = kwargs.pop("steps")
#     step_no = 0
#     setup_case_list = []
#     # empty_check_params = None
#     empty_check_param_list = None
#
#     for step in steps:
#         step_no += 1
#         setup_info = step.pop("setupInfo")
#         variable_info = step.pop("variableInfo")
#         request_info = step.pop("requestInfo")
#         validate_info = step.pop("validateInfo")
#         extract_info = step.pop("extractInfo")
#         teardown_info = step.pop("teardownInfo")
#
#         testcase = {
#             "name": "{testcase}.{step}".format(testcase=testcase_name, step=step_no),
#             "variables": [],
#             "request": {},
#             "validate": [],
#             "extract": [],
#             "setup_hooks": [],
#             "teardown_hooks": []
#         }
#
#         # variable
#         for variable in variable_info:
#             # 自定义函数
#             if variable["type"] == "function":
#                 func_args = ''
#                 input_args_dic = variable["args"]
#                 for custom_func in CUSTOM["functions"]:
#                     if custom_func["name"] == variable["value"]:
#                         for x in custom_func["parameters"]:
#                             for input_arg in input_args_dic:
#                                 if input_arg == x:
#                                     if func_args == '':
#                                         func_args += input_args_dic[input_arg]
#                                     else:
#                                         func_args += '||{}'.format(input_args_dic[input_arg])
#
#                 testcase["variables"].append({
#                     variable["name"].strip(): "${{{func}({args})}}".format(func=variable["value"], args=func_args)
#                 })
#
#             # 数据库
#             elif variable["type"] == "db":
#                 """
#                 从
#                 {
#                     "type": "db",
#                     "name": "next_member_id",
#                     "value": "SELECT NEXT_VALUE FROM user_db.sequence WHERE SEQ_NAME='MEMBER_ID';",
#                     "args": {}
#                 }
#                 变换成
#                 {
#                     'V_SQL_next_member_id': "SELECT NEXT_VALUE FROM user_db.sequence WHERE SEQ_NAME='MEMBER_ID';"
#                 },
#                 {
#                     'next_member_id': '${variable_db_operation(V_SQL_next_member_id||$DB_CONNECT)}'
#                 },
#                 """
#                 sql = variable["value"]
#                 default_func = 'variable_db_operation'
#                 testcase["variables"].append({
#                     variable["name"].strip(): "${{{func}({sql}||$DB_CONNECT)}}".format(func=default_func, sql=sql)
#                 })
#
#             # key-value
#             else:
#                 testcase["variables"].append({
#                     variable["name"].strip(): variable["value"]
#                 })
#
#         # validate
#         for validate in validate_info:
#             if validate["comparator"] == "db_validate":
#                 validate["check"] += "$DB_CONNECT"
#
#             '''替换validate["expect"]的中文冒号'''
#             if "：" in validate["expect"]:
#                 validate["expect"] = validate["expect"].replace("：", ":")
#
#             testcase["validate"].append({
#                 validate["comparator"]: [
#                     validate["check"].strip(), validate["expect"]
#                 ]
#             })
#
#         # extract
#         for extract in extract_info:
#             testcase["extract"].append({
#                 extract["saveAs"].strip(): extract["check"]
#             })
#
#         # setup
#         # setup_sql_count = 0
#         case_step_count = 0
#         for setup in setup_info:
#             '''添加前置步骤：执行用例
#              ******teststeps[]字典列表中，最后一个字典为当前用例，'''
#             if setup["name"] == "execution_testcase":
#                 setupcase_id = setup["args"]["用例编号"]
#                 #setupcase_variable = setup["args"]["请求参数"]
#                 try:
#                     '''获取1.前置用例编号和request里面的teststeps，3.所属测试集和测试集的apiUrl'''
#                     tc_obj = TestcaseInfoManager.get_testcase(setupcase_id)
#                     ts_obj = TestsuiteInfoManager.query_testsuite_by_id(tc_obj.testsuite_id)
#                     setup_case_list.append(setupcase_id)
#                 except AttributeError:
#                     raise LoadCaseError('前置执行用例id不存在')
#
#
#
#             for setup_hook in CUSTOM["setup-hooks"]:
#                 if setup_hook["name"] == setup["name"]:
#                     # if setup["name"] == "setup_db_operation":
#                     #     setup_sql_count += 1
#                     #     setup_cell = "${{setup_db_operation($SETUP_SQL_{no},$DB_CONNECT)}}".format(
#                     #         no=setup_sql_count)
#                     #     testcase["variables"].append({
#                     #         "SETUP_SQL_{no}".format(no=setup_sql_count): setup["args"]["sql"]
#                     #     })
#                     # else:
#                     #     if isinstance(setup["args"], dict):
#                     #         func_args = ''
#                     #         for i in setup["args"]:
#                     #             if func_args == '':
#                     #                 func_args += setup["args"][i]
#                     #             else:
#                     #                 func_args += ',{}'.format(setup["args"][i])
#                     #     elif isinstance(setup["args"], list):
#                     #         func_args = ",".join(setup["args"])
#                     #     else:
#                     #         func_args = setup["args"]
#                     #
#                     #     setup_cell = "${{{func_name}({func_args})}}".format(
#                     #         func_name=setup["name"], func_args=func_args)
#
#                     if setup["name"] == "setup_db_operation":
#                         setup_cell = "${{setup_db_operation({0}||$DB_CONNECT)}}".format(setup["args"]["sql"])
#                     elif setup["name"] == "setup_wait_until_db_result_succeed":
#                         setup_cell = "${{setup_wait_until_db_result_succeed({0}||{1}||{2}||$DB_CONNECT)}}".format(setup["args"]["wait_time"], setup["args"]["sql"], setup["args"]["expect_value"])
#                     elif setup["name"] == "setup_server_upload_file":
#                         setup_cell = "${{setup_server_upload_file({0}||{1}||{2})}}".format(setup["args"]["ssh_connect"], setup["args"]["local_path"].replace("\\", "/"), setup["args"]["remote_path"].replace("\\", "/"))
#                     else:
#                         if isinstance(setup["args"], dict):
#                             func_args = ''
#                             for i in setup["args"]:
#                                 if func_args == '':
#                                     func_args += setup["args"][i]
#                                 else:
#                                     func_args += '||{}'.format(setup["args"][i])
#                         elif isinstance(setup["args"], list):
#                             func_args = "||".join(setup["args"])
#                         else:
#                             func_args = setup["args"]
#
#                         setup_cell = "${{{func_name}({func_args})}}".format(
#                             func_name=setup["name"], func_args=func_args)
#
#                     testcase["setup_hooks"].append(setup_cell)
#
#         # teardown
#         # teardown_sql_count = 0
#         for teardown in teardown_info:
#             for teardown_hook in CUSTOM["teardown-hooks"]:
#                 if teardown_hook["name"] == teardown["name"]:
#                     # if teardown["name"] == "teardown_db_operation":
#                     #     teardown_sql_count += 1
#                     #     teardown_cell = "${{teardown_db_operation($TEARDOWN_SQL_{no},$DB_CONNECT)}}".format(
#                     #         no=teardown_sql_count)
#                     #     testcase["variables"].append({
#                     #         "TEARDOWN_SQL_{no}".format(no=teardown_sql_count): teardown["args"]["sql"]
#                     #     })
#                     # else:
#                     #     if isinstance(teardown["args"], dict):
#                     #         func_args = ''
#                     #         for i in teardown["args"]:
#                     #             if func_args == '':
#                     #                 func_args += teardown["args"][i]
#                     #             else:
#                     #                 func_args += ',{}'.format(teardown["args"][i])
#                     #     elif isinstance(teardown["args"], list):
#                     #         func_args = ",".join(teardown["args"])
#                     #     else:
#                     #         func_args = teardown["args"]
#                     #     teardown_cell = "${{{func_name}({func_args})}}".format(
#                     #         func_name=teardown["name"], func_args=func_args)
#
#                     if teardown["name"] == "teardown_db_operation":
#                         teardown_cell = "${{teardown_db_operation({0}||$DB_CONNECT)}}".format(teardown["args"]["sql"])
#                     elif teardown["name"] == "teardown_wait_until_db_result_succeed":
#                         teardown_cell = "${{teardown_wait_until_db_result_succeed({0}||{1}||{2}||$DB_CONNECT)}}".format(teardown["args"]["wait_time"],teardown["args"]["sql"],teardown["args"]["expect_value"])
#                     else:
#                         if isinstance(teardown["args"], dict):
#                             func_args = ''
#                             for i in teardown["args"]:
#                                 if func_args == '':
#                                     func_args += teardown["args"][i]
#                                 else:
#                                     func_args += '||{}'.format(teardown["args"][i])
#                         elif isinstance(teardown["args"], list):
#                             func_args = "||".join(teardown["args"])
#                         else:
#                             func_args = teardown["args"]
#                         teardown_cell = "${{{func_name}({func_args})}}".format(
#                             func_name=teardown["name"], func_args=func_args)
#
#                     testcase["teardown_hooks"].append(teardown_cell)
#
#         # request(分为HTTP，DUBBO，MQ三种情况)
#         if intf_type == "HTTP":
#             json_body = request_info.pop("json", None)
#             sign_func = request_info.pop("sign", None)
#             # empty_check_params = request_info.pop("emptyCheckParams", None)
#             empty_check_param_list = request_info.pop("emptyCheckParamList", None)
#
#             if json_body is not None:
#                 testcase["request"]["json"] = json_body
#
#             if sign_func:
#                 for setup_hook in CUSTOM["sign"]:
#                     if setup_hook["name"] == sign_func:
#                         testcase["setup_hooks"].append(
#                             "${{{sign_func}($request||$REMOTE_HOST)}}".format(sign_func=sign_func)
#                         )
#
#         elif intf_type == "DUBBO":
#             testcase["request"]["json"] = {"args": []}
#             dubbo_args = request_info.pop("args", None)
#
#             if dubbo_args is not None:
#                 if isinstance(dubbo_args, list):
#                     testcase["request"]["json"]["args"] = dubbo_args
#                 else:
#                     testcase["request"]["json"]["args"].append(dubbo_args)
#
#         elif intf_type == "MQ":
#             testcase["request"]["json"] = {"msg": "{}"}
#             mq_msg = request_info.pop("msg", None)
#
#             if mq_msg is not None:
#                 testcase["request"]["json"]["msg"] = mq_msg
#
#         hr_request["teststeps"].append(testcase)
#
#
#
#
#     # 处理include
#     include = kwargs.pop("include")
#     if not isinstance(include, list):
#         include = [{"public_variables": []}]
#     include.append({"setup_cases": setup_case_list})
#     """加载public_variables"""
#     case_variable = re.findall(variable_regexp, str(testcase))
#     target_pv_name_list = list(set(case_variable).difference(set(env_variable_list)))
#     for target_pv_name in target_pv_name_list:
#         variable_obj = ApiPublicVariableInfoManager.get_variable(api_system_id=system_id, variable_name=target_pv_name)
#         if variable_obj and variable_obj.id not in include[0]["public_variables"]:
#             include[0]["public_variables"].append(variable_obj.id)
#
#     """保存必填字段校验"""
#     # if empty_check_params:
#     #     empty_list = [k.strip() for k in str(empty_check_params).strip().strip(',').split(',')]
#     #     include.append({"param_check": {"empty": empty_list}})
#     if empty_check_param_list:
#         include.append({"param_check": {"empty": empty_check_param_list}})
#     # request = change_variable_format(request)
#
#     if action == 'add':
#         TestcaseInfoManager.insert_testcase(
#             testcase_name=testcase_name,
#             type=testcase_type,
#             include=json_dumps(include),
#             request=json_dumps(hr_request),
#             testsuite_id=testsuite_id,
#             module_id=module_id,
#             system_id=system_id,
#             simple_desc=simple_desc,
#             case_status=0,
#             creator=operator,
#             last_modifier=operator,
#             expect_result=expect_result,
#         )
#     elif action == 'edit':
#         testcase_id = base.pop("id", None)
#         # testcase_id = base.pop("testcaseId")
#         TestcaseInfoManager.update_testcase(
#             id_=testcase_id,
#             testcase_name=testcase_name,
#             include=json_dumps(include),
#             request=json_dumps(hr_request),
#             case_status=0,
#             simple_desc=simple_desc,
#             last_modifier=operator,
#             expect_result=expect_result,
#         )
#     # print(json_dumps(hr_request))


def handle_api_testcase(action, **kwargs):
    """
    新版-保存测试用例到数据库
    :param action:
    :param kwargs:
    :return:
    """
    # 处理base
    base = kwargs.pop("base")
    # system_id = base.pop("systemId")
    # module_id = base.pop("moduleId")
    # testsuite_id = base.pop("testsuiteId")
    testcase_name = base.pop("testcaseName")[:200]
    simple_desc = base.pop("testcaseDesc", "")[:1000]
    expect_result = base.pop("expectResult")[:200]
    intf_id = base.pop("intfId")
    operator = kwargs.pop("userName")
    tag_id_list = base.pop("tagIdList")

    intf_obj = ApiIntfInfoManager.get_intf(id=intf_id)
    intf_type = intf_obj.intf_type

    testcase_type = map_testcase_type_to_number(intf_type)

    hr_request = {
        "name": testcase_name,
        "config": {
            "variables": [],
            "request": {
                "base_url": "",
            }
        },
        "teststeps": []
    }
    # 处理setupCases
    setup_cases = kwargs.pop("setupCases", [])
    setup_cases_list = []
    for setup_case_dic in setup_cases:
        case_type_code = get_case_type_by_desc(setup_case_dic["caseType"])
        if case_type_code == 1:
            setup_case_str = '{0}-{1}'.format(case_type_code, setup_case_dic["testcaseId"])
            if not setup_case_dic["hasChildren"]:
                # 保存是否仅引用本身
                setup_case_str += '-self'
            setup_cases_list.append(setup_case_str)
        elif case_type_code == 2:
            setup_case_str = '{0}-{1}'.format(case_type_code, setup_case_dic["testcaseId"])
            flow_id = setup_case_dic.get("customFlowId", None)
            if flow_id:
                # 保存自定义链路信息
                setup_case_str += '-{0}'.format(flow_id)
            setup_cases_list.append(setup_case_str)

    # 处理steps
    steps = kwargs.pop("steps")
    step_no = 0
    # setup_case_list = []
    # empty_check_params = None
    empty_check_param_list = None

    for step in steps:
        step_no += 1
        setup_info = step.pop("setupInfo")
        variable_info = step.pop("variableInfo")
        request_info = step.pop("requestInfo")
        validate_info = step.pop("validateInfo")
        extract_info = step.pop("extractInfo")
        teardown_info = step.pop("teardownInfo")
        request_teardown_info = step.pop("requestTeardownInfo", [])

        testcase = {
            "name": "{testcase}.{step}".format(testcase=testcase_name, step=step_no),
            "variables": [],
            "request": {},
            "validate": [],
            "extract": [],
            "setup_hooks": [],
            "teardown_hooks": [],
            "request_teardown_hooks": []
        }

        # variable
        for variable in variable_info:
            # 自定义函数
            if variable["type"] == "function":
                func_args = ''
                input_args_dic = variable["args"]
                for custom_func in CUSTOM["functions"]:
                    if custom_func["name"] == variable["value"]:
                        for x in custom_func["parameters"]:
                            for input_arg in input_args_dic:
                                if input_arg == x:
                                    if func_args == '':
                                        func_args += input_args_dic[input_arg]
                                    else:
                                        func_args += '||{}'.format(input_args_dic[input_arg])

                testcase["variables"].append({
                    variable["name"].strip(): "${{{func}({args})}}".format(func=variable["value"], args=func_args)
                })

            # 数据库
            elif variable["type"] == "db":
                """
                从
                {
                    "type": "db",
                    "name": "next_member_id",
                    "value": "SELECT NEXT_VALUE FROM user_db.sequence WHERE SEQ_NAME='MEMBER_ID';",
                    "args": {}
                }
                变换成
                {
                    'V_SQL_next_member_id': "SELECT NEXT_VALUE FROM user_db.sequence WHERE SEQ_NAME='MEMBER_ID';"
                },
                {
                    'next_member_id': '${variable_db_operation(V_SQL_next_member_id||$DB_CONNECT)}'
                },
                """
                sql = variable["value"]
                default_func = 'variable_db_operation'
                testcase["variables"].append({
                    variable["name"].strip(): "${{{func}({sql}||$DB_CONNECT)}}".format(func=default_func, sql=sql)
                })

            # key-value
            else:
                actual_var_value = transfer_to_actual_value(variable)
                testcase["variables"].append({
                    variable["name"].strip(): actual_var_value
                })

        # validate
        for validate in validate_info:
            # if validate["comparator"] == "db_validate":
            #     validate["check"] += "$DB_CONNECT"

            # '''替换validate["expect"]的中文冒号'''
            # if "：" in validate["expect"]:
            #     validate["expect"] = validate["expect"].replace("：", ":")

            testcase["validate"].append({
                validate["comparator"]: [
                    validate["check"].strip('\n').strip(), validate["expect"], validate["comment"]
                ]
            })

        # extract
        for extract in extract_info:
            testcase["extract"].append({
                extract["saveAs"].strip(): extract["check"]
            })

        # setup
        # setup_sql_count = 0
        case_step_count = 0
        for setup in setup_info:
            '''添加前置步骤：执行用例
             ******teststeps[]字典列表中，最后一个字典为当前用例，'''
            # if setup["name"] == "execution_testcase":
            #     setupcase_id = setup["args"]["用例编号"]
            #     setup_case_list.append(setupcase_id)

            for setup_hook in CUSTOM["setup-hooks"]:
                if setup_hook["name"] == setup["name"]:
                    # if setup["name"] == "setup_db_operation":
                    #     setup_cell = "${{setup_db_operation({0}||$DB_CONNECT)}}".format(setup["args"]["sql"])
                    # elif setup["name"] == "setup_wait_until_db_result_succeed":
                    #     setup_cell = "${{setup_wait_until_db_result_succeed({0}||{1}||{2}||$DB_CONNECT)}}".format(setup["args"]["wait_time"], setup["args"]["sql"], setup["args"]["expect_value"])
                    # elif setup["name"] == "setup_server_upload_file":
                    if setup["name"] == "setup_server_upload_file":
                        setup_cell = "${{setup_server_upload_file({0}||{1}||{2})}}".format(setup["args"]["ssh_connect"], setup["args"]["local_path"].replace("\\", "/"), setup["args"]["remote_path"].replace("\\", "/"))
                    else:
                        if isinstance(setup["args"], dict):
                            func_args = ''
                            # for i in setup["args"]:
                            #     if func_args == '':
                            #         func_args += setup["args"][i]
                            #     else:
                            #         func_args += '||{}'.format(setup["args"][i])
                            for base_key in setup_hook["parameters"]:
                                for key, value in setup["args"].items():
                                    if key == base_key:
                                        if func_args == '':
                                            func_args += value
                                        else:
                                            func_args += '||{}'.format(value)
                        elif isinstance(setup["args"], list):
                            func_args = "||".join(setup["args"])
                        else:
                            func_args = setup["args"]

                        setup_cell = "${{{func_name}({func_args})}}".format(
                            func_name=setup["name"], func_args=func_args)

                    testcase["setup_hooks"].append(setup_cell)

        # teardown
        # teardown_sql_count = 0
        for teardown in teardown_info:
            for teardown_hook in CUSTOM["teardown-hooks"]:
                if teardown_hook["name"] == teardown["name"]:
                    # if teardown["name"] == "teardown_db_operation":
                    #     teardown_cell = "${{teardown_db_operation({0}||$DB_CONNECT)}}".format(teardown["args"]["sql"])
                    # elif teardown["name"] == "teardown_wait_until_db_result_succeed":
                    #     teardown_cell = "${{teardown_wait_until_db_result_succeed({0}||{1}||{2}||$DB_CONNECT)}}".format(teardown["args"]["wait_time"],teardown["args"]["sql"],teardown["args"]["expect_value"])
                    if isinstance(teardown["args"], dict):
                        func_args = ''
                        # for i in teardown["args"]:
                        #     if func_args == '':
                        #         func_args += teardown["args"][i]
                        #     else:
                        #         func_args += '||{}'.format(teardown["args"][i])
                        for base_key in teardown_hook["parameters"]:
                            for key, value in teardown["args"].items():
                                if key == base_key:
                                    if func_args == '':
                                        func_args += value
                                    else:
                                        func_args += '||{}'.format(value)
                    elif isinstance(teardown["args"], list):
                        func_args = "||".join(teardown["args"])
                    else:
                        func_args = teardown["args"]
                    teardown_cell = "${{{func_name}({func_args})}}".format(
                        func_name=teardown["name"], func_args=func_args)

                    testcase["teardown_hooks"].append(teardown_cell)

        # requestTeardown
        for teardown in request_teardown_info:
            for teardown_hook in CUSTOM["teardown-hooks"]:
                if teardown_hook["name"] == teardown["name"]:
                    if isinstance(teardown["args"], dict):
                        args_list = []
                        for base_key in teardown_hook["parameters"]:
                            for key, value in teardown["args"].items():
                                if key == base_key:
                                    args_list.append(value)
                                    break
                        func_args = "||".join(args_list)
                    elif isinstance(teardown["args"], list):
                        func_args = "||".join(teardown["args"])
                    else:
                        func_args = teardown["args"]
                    teardown_cell = "${{{func_name}({func_args})}}".format(
                        func_name=teardown["name"], func_args=func_args)

                    testcase["request_teardown_hooks"].append(teardown_cell)

        # request(分为HTTP，DUBBO，MQ三种情况)
        is_merge = request_info.pop("isMerge", None)
        testcase["request"]["isMerge"] = True if is_merge else False

        if intf_type == "HTTP":
            json_body = request_info.pop("json", None)
            sign_func = request_info.pop("sign", None)
            empty_check_param_list = request_info.pop("emptyCheckParamList", None)

            if json_body is not None:
                testcase["request"]["json"] = json_body

            if sign_func:
                for setup_hook in CUSTOM["sign"]:
                    if setup_hook["name"] == sign_func:
                        testcase["setup_hooks"].append(
                            "${{{sign_func}($request||$REMOTE_HOST)}}".format(sign_func=sign_func)
                        )

        elif intf_type == "DUBBO":
            testcase["request"]["json"] = {"args": []}
            dubbo_args = request_info.pop("args", None)

            if dubbo_args is not None:
                if isinstance(dubbo_args, list):
                    testcase["request"]["json"]["args"] = dubbo_args
                else:
                    testcase["request"]["json"]["args"].append(dubbo_args)

        elif intf_type == "MQ":
            testcase["request"]["json"] = {"msg": "{}"}
            mq_msg = request_info.pop("msg", None)

            if mq_msg is not None:
                testcase["request"]["json"]["msg"] = mq_msg

        hr_request["teststeps"].append(testcase)

    # 处理include
    include = kwargs.pop("include")
    if not isinstance(include, list) or include == []:
        include = [{"public_variables": []}]
    # include.append({"setup_cases": setup_case_list})
    """加载public_variables"""
    intf_variables = re.findall(variable_regexp, str(intf_obj.intf_info))
    case_variables = re.findall(variable_regexp, str(testcase))
    case_variables.extend(intf_variables)
    target_pv_name_list = list(set(case_variables).difference(set(env_variable_list)))
    for target_pv_name in target_pv_name_list:
        # todo 公共变量作用域
        # system_id = ApiIntfInfoManager.get_intf(id=intf_id).api_system_id
        system_id = intf_obj.api_system_id
        s_var_obj = ApiPublicVariableInfoManager.get_variable(variable_name=target_pv_name, api_system_id=system_id)

        if s_var_obj:
            if s_var_obj.id not in include[0]["public_variables"]:
                include[0]["public_variables"].append(s_var_obj.id)
        else:
            company_id = ApiSystemInfoManager.get_system(id=system_id).api_company_id
            c_var_obj = ApiPublicVariableInfoManager.get_variable(
                variable_name=target_pv_name, api_company_id=company_id)
            if c_var_obj and c_var_obj.id not in include[0]["public_variables"]:
                include[0]["public_variables"].append(c_var_obj.id)

    """保存必填字段校验"""
    # if empty_check_params:
    #     empty_list = [k.strip() for k in str(empty_check_params).strip().strip(',').split(',')]
    #     include.append({"param_check": {"empty": empty_list}})
    if empty_check_param_list:
        include.append({"param_check": {"empty": empty_check_param_list}})
    # request = change_variable_format(request)

    if action == 'add':
        ApiTestcaseInfoManager.insert_testcase(
            testcase_name=testcase_name,
            type=testcase_type,
            include=json_dumps(include),
            simple_desc=simple_desc,
            case_status=0,
            api_intf_id=intf_id,
            creator=operator,
            last_modifier=operator,
            expect_result=expect_result,
            setup_case_list=json_dumps(setup_cases_list),
            last_modify_time=datetime.now(),
        )
        tc_objs = ApiTestcaseInfoManager.get_testcases_order_by_create_time_desc(
            api_intf_id=intf_id, testcase_name=testcase_name, creator=operator, expect_result=expect_result)
        if not tc_objs:
            logger.error("tc_objs not found")
            raise LoadCaseError
        else:
            testcase_id = tc_objs[0].id

        ApiTestcaseRequestManager.insert_request(
            api_testcase_id=testcase_id,
            request=json_dumps(hr_request),
        )
        # tcr_obj = ApiTestcaseRequestManager.get_request(api_testcase_id=testcase_id)
        # if not tcr_obj:
        #     logger.error("tcr_obj not found")
        #     raise LoadCaseError
        # else:
        #     request_id = tcr_obj.id
        # ApiTestcaseInfoManager.update_testcase(
        #     id_=testcase_id,
        #     api_request_id=request_id,
        # )
        set_testcase_tag(testcase_id, tag_id_list)

    elif action == 'edit':
        testcase_id = base.pop("testcaseId")
        ApiTestcaseInfoManager.update_testcase(
            id_=testcase_id,
            testcase_name=testcase_name,
            include=json_dumps(include),
            simple_desc=simple_desc,
            last_modifier=operator,
            expect_result=expect_result,
            setup_case_list=json_dumps(setup_cases_list),
            last_modify_time=datetime.now(),
        )
        r_obj = ApiTestcaseRequestManager.get_request(api_testcase_id=testcase_id)
        ApiTestcaseRequestManager.update_request(
            id_=r_obj.id,
            request=json_dumps(hr_request),
        )

        set_testcase_tag(testcase_id, tag_id_list)

        # print(json_dumps(hr_request))


def handle_api_testcase_main(action, **kwargs):
    """
    新版-保存主测试用例到数据库
    :param action:
    :param kwargs:
    :return:
    """
    # 处理base
    base = kwargs.pop("base")

    tag_id_list = base.pop("tagIdList")
    base_intf_id = base.pop("intfId", None)
    product_line_id = base.pop("productLineId", None)
    main_teardown_info = base.pop("mainTeardownInfo", [])
    case_type = base.pop("caseType", 0)
    if product_line_id and case_type != 1:
        case_type = 2
        testcase_name = base.pop("testcaseName")[:200]
        simple_desc = base.pop("testcaseDesc", "")[:1000]
        expect_result = base.pop("expectResult")[:200]
    else:
        case_type = 1

    # 处理main_teardown_hooks
    main_teardown_hooks = []
    for teardown in main_teardown_info:
        for teardown_hook in CUSTOM["teardown-hooks"]:
            if teardown_hook["name"] == teardown["name"]:
                if isinstance(teardown["args"], dict):
                    func_args = ''
                    for i in teardown["args"]:
                        if func_args == '':
                            func_args += teardown["args"][i]
                        else:
                            func_args += '||{}'.format(teardown["args"][i])
                elif isinstance(teardown["args"], list):
                    func_args = "||".join(teardown["args"])
                else:
                    func_args = teardown["args"]
                teardown_cell = "${{{func_name}({func_args})}}".format(
                    func_name=teardown["name"], func_args=func_args)

                main_teardown_hooks.append(teardown_cell)

    # 处理setup_flow
    setup_flow = kwargs.pop("setupFlow", None)
    if setup_flow:
        setup_flow_list = [int(flow_dic["flowCaseId"]) for flow_dic in setup_flow]
    else:
        setup_flow_list = []

    operator = kwargs.pop("userName")

    sub_info_list = []

    # 处理steps
    steps = kwargs.pop("steps")
    step_no = 0
    # empty_check_params = None
    empty_check_param_list = None

    for step in steps:
        sub_info = {}
        step_no += 1
        sub_base = step.pop("base")

        # 判断是否为引用的子用例
        is_referenced_sub = True if not step else False
        if is_referenced_sub:
            sub_info["sub_id"] = sub_base["subId"]
        else:
            setup_info = step.pop("setupInfo")
            variable_info = step.pop("variableInfo")
            request_info = step.pop("requestInfo")
            validate_info = step.pop("validateInfo")
            extract_info = step.pop("extractInfo")
            teardown_info = step.pop("teardownInfo")
            request_teardown_info = step.pop("requestTeardownInfo", [])

            sub_name = sub_base["subName"][:200]
            sub_info["sub_name"] = sub_name
            intf_id = sub_base["intfId"] if case_type == 2 else base_intf_id

            intf_obj = ApiIntfInfoManager.get_intf(id=intf_id)
            intf_type = intf_obj.intf_type
            sub_info["request_type"] = map_testcase_type_to_number(intf_type)
            sub_info["simple_desc"] = sub_base.get("subDesc", "")[:1000]
            sub_info["expect_result"] = sub_base["subExpectResult"][:200]
            sub_info["case_type"] = case_type
            sub_info["api_intf_id"] = intf_id
            if "subId" in sub_base:
                sub_info["sub_id"] = sub_base["subId"]
            else:
                sub_info["sub_id"] = None

            hr_request = {
                "name": sub_name,
                "config": {
                    "variables": [],
                    "request": {
                        "base_url": "",
                    }
                },
                "teststeps": []
            }

            testcase = {
                "name": sub_name,
                "variables": [],
                "request": {},
                "validate": [],
                "extract": [],
                "setup_hooks": [],
                "teardown_hooks": [],
                "request_teardown_hooks": []
            }

            # variable
            for variable in variable_info:
                # 自定义函数
                if variable["type"] == "function":
                    func_args = ''
                    input_args_dic = variable["args"]
                    for custom_func in CUSTOM["functions"]:
                        if custom_func["name"] == variable["value"]:
                            for x in custom_func["parameters"]:
                                for input_arg in input_args_dic:
                                    if input_arg == x:
                                        if func_args == '':
                                            func_args += input_args_dic[input_arg]
                                        else:
                                            func_args += '||{}'.format(input_args_dic[input_arg])

                    testcase["variables"].append({
                        variable["name"].strip(): "${{{func}({args})}}".format(func=variable["value"], args=func_args)
                    })

                # 数据库
                elif variable["type"] == "db":
                    """
                    从
                    {
                        "type": "db",
                        "name": "next_member_id",
                        "value": "SELECT NEXT_VALUE FROM user_db.sequence WHERE SEQ_NAME='MEMBER_ID';",
                        "args": {}
                    }
                    变换成
                    {
                        'next_member_id': '${variable_db_operation(SELECT NEXT_VALUE FROM user_db.sequence WHERE SEQ_NAME=\'MEMBER_ID\';||$DB_CONNECT)}'
                    },
                    """
                    sql = variable["value"]
                    default_func = 'variable_db_operation'
                    testcase["variables"].append({
                        variable["name"].strip(): "${{{func}({sql}||$DB_CONNECT)}}".format(func=default_func, sql=sql)
                    })

                # key-value
                else:
                    actual_var_value = transfer_to_actual_value(variable)
                    testcase["variables"].append({
                        variable["name"].strip(): actual_var_value
                    })

            # validate
            for validate in validate_info:
                if validate["comparator"] == "db_validate":
                    validate["check"] += "$DB_CONNECT"

                # '''替换validate["expect"]的中文冒号'''
                # if "：" in validate["expect"]:
                #     validate["expect"] = validate["expect"].replace("：", ":")

                testcase["validate"].append({
                    validate["comparator"]: [
                        validate["check"].strip(), validate["expect"], validate["comment"]
                    ]
                })

            # extract
            for extract in extract_info:
                testcase["extract"].append({
                    extract["saveAs"].strip(): extract["check"]
                })

            # setup
            case_step_count = 0
            for setup in setup_info:
                '''遇到前置执行用例，跳过'''
                if setup["name"] == "execution_testcase":
                    continue

                for setup_hook in CUSTOM["setup-hooks"]:
                    if setup_hook["name"] == setup["name"]:
                        if setup["name"] == "setup_db_operation":
                            setup_cell = "${{setup_db_operation({0}||$DB_CONNECT)}}".format(setup["args"]["sql"])
                        elif setup["name"] == "setup_wait_until_db_result_succeed":
                            setup_cell = "${{setup_wait_until_db_result_succeed({0}||{1}||{2}||$DB_CONNECT)}}".format(setup["args"]["wait_time"], setup["args"]["sql"], setup["args"]["expect_value"])
                        elif setup["name"] == "setup_server_upload_file":
                            setup_cell = "${{setup_server_upload_file({0}||{1}||{2})}}".format(setup["args"]["ssh_connect"], setup["args"]["local_path"].replace("\\", "/"), setup["args"]["remote_path"].replace("\\", "/"))
                        else:
                            if isinstance(setup["args"], dict):
                                func_args = ''
                                # for i in setup["args"]:
                                #     if func_args == '':
                                #         func_args += setup["args"][i]
                                #     else:
                                #         func_args += '||{}'.format(setup["args"][i])
                                for base_key in setup_hook["parameters"]:
                                    for key, value in setup["args"].items():
                                        if key == base_key:
                                            if func_args == '':
                                                func_args += value
                                            else:
                                                func_args += '||{}'.format(value)
                            elif isinstance(setup["args"], list):
                                func_args = "||".join(setup["args"])
                            else:
                                func_args = setup["args"]

                            setup_cell = "${{{func_name}({func_args})}}".format(
                                func_name=setup["name"], func_args=func_args)

                        testcase["setup_hooks"].append(setup_cell)

            # teardown
            # teardown_sql_count = 0
            for teardown in teardown_info:
                for teardown_hook in CUSTOM["teardown-hooks"]:
                    if teardown_hook["name"] == teardown["name"]:
                        if teardown["name"] == "teardown_db_operation":
                            teardown_cell = "${{teardown_db_operation({0}||$DB_CONNECT)}}".format(teardown["args"]["sql"])
                        elif teardown["name"] == "teardown_wait_until_db_result_succeed":
                            teardown_cell = "${{teardown_wait_until_db_result_succeed({0}||{1}||{2}||$DB_CONNECT)}}".format(teardown["args"]["wait_time"],teardown["args"]["sql"],teardown["args"]["expect_value"])
                        else:
                            if isinstance(teardown["args"], dict):
                                func_args = ''
                                # for i in teardown["args"]:
                                #     if func_args == '':
                                #         func_args += teardown["args"][i]
                                #     else:
                                #         func_args += '||{}'.format(teardown["args"][i])
                                for base_key in teardown_hook["parameters"]:
                                    for key, value in teardown["args"].items():
                                        if key == base_key:
                                            if func_args == '':
                                                func_args += value
                                            else:
                                                func_args += '||{}'.format(value)
                            elif isinstance(teardown["args"], list):
                                func_args = "||".join(teardown["args"])
                            else:
                                func_args = teardown["args"]
                            teardown_cell = "${{{func_name}({func_args})}}".format(
                                func_name=teardown["name"], func_args=func_args)

                        testcase["teardown_hooks"].append(teardown_cell)

            # requestTeardown
            for teardown in request_teardown_info:
                for teardown_hook in CUSTOM["teardown-hooks"]:
                    if teardown_hook["name"] == teardown["name"]:
                        if isinstance(teardown["args"], dict):
                            args_list = []
                            for base_key in teardown_hook["parameters"]:
                                for key, value in teardown["args"].items():
                                    if key == base_key:
                                        args_list.append(value)
                                        break
                            func_args = "||".join(args_list)
                        elif isinstance(teardown["args"], list):
                            func_args = "||".join(teardown["args"])
                        else:
                            func_args = teardown["args"]
                        teardown_cell = "${{{func_name}({func_args})}}".format(
                            func_name=teardown["name"], func_args=func_args)

                        testcase["request_teardown_hooks"].append(teardown_cell)

            # request(分为HTTP，DUBBO，MQ三种情况)
            is_merge = request_info.pop("isMerge", None)
            testcase["request"]["isMerge"] = True if is_merge else False

            if intf_type == "HTTP":
                json_body = request_info.pop("json", None)
                sign_func = request_info.pop("sign", None)
                empty_check_param_list = request_info.pop("emptyCheckParamList", None)

                if json_body is not None:
                    testcase["request"]["json"] = json_body

                if sign_func:
                    for setup_hook in CUSTOM["sign"]:
                        if isinstance(sign_func, dict):
                            sign_func = sign_func.get("name", "")
                        if setup_hook["name"] == sign_func:
                            testcase["setup_hooks"].append(
                                "${{{sign_func}($request||$REMOTE_HOST)}}".format(sign_func=sign_func)
                            )

            elif intf_type == "DUBBO":
                testcase["request"]["json"] = {"args": []}
                dubbo_args = request_info.pop("args", None)

                if dubbo_args is not None:
                    if isinstance(dubbo_args, list):
                        testcase["request"]["json"]["args"] = dubbo_args
                    else:
                        testcase["request"]["json"]["args"].append(dubbo_args)

            elif intf_type == "MQ":
                testcase["request"]["json"] = {"msg": "{}"}
                mq_msg = request_info.pop("msg", None)

                if mq_msg is not None:
                    testcase["request"]["json"]["msg"] = mq_msg

            hr_request["teststeps"].append(testcase)

            # include
            include = [{"public_variables": []}]
            """加载public_variables"""
            intf_variables = re.findall(variable_regexp, str(intf_obj.intf_info))
            case_variables = re.findall(variable_regexp, str(testcase))
            # main_teardown_variables = re.findall(variable_regexp, str(main_teardown_hooks))
            # case_variables.extend(main_teardown_variables)
            case_variables.extend(intf_variables)
            target_pv_name_list = list(set(case_variables).difference(set(env_variable_list)))
            for target_pv_name in target_pv_name_list:
                system_id = intf_obj.api_system_id
                s_var_obj = ApiPublicVariableInfoManager.get_variable(variable_name=target_pv_name, api_system_id=system_id)

                if s_var_obj:
                    if s_var_obj.id not in include[0]["public_variables"]:
                        include[0]["public_variables"].append(s_var_obj.id)
                else:
                    company_id = ApiSystemInfoManager.get_system(id=system_id).api_company_id
                    c_var_obj = ApiPublicVariableInfoManager.get_variable(
                        variable_name=target_pv_name, api_company_id=company_id)
                    if c_var_obj and c_var_obj.id not in include[0]["public_variables"]:
                        include[0]["public_variables"].append(c_var_obj.id)

            sub_info["include"] = json_dumps(include)
            sub_info["request"] = hr_request

            # 全部新增
            if action == 'add':
                sub_info["creator"] = operator
            else:
                # 部分更新
                if sub_info["sub_id"]:
                    sub_info["last_modifier"] = operator
                # 部分新增
                else:
                    sub_info["creator"] = operator
                    sub_info["last_modifier"] = operator

        if case_type == 1 and not is_referenced_sub:
            testcase_name = sub_base.get("subName", "")[:200]
            simple_desc = sub_base.get("subDesc", "")[:200]
            expect_result = sub_base.get("subExpectResult", "")[:200]

        sub_info_list.append(sub_info)

    # 保存子用例和相应的request
    sub_id_list = ApiTestcaseSubManager.batch_update_testcase_sub(sub_info_list)

    if action == 'add':
        last_sub_obj = ApiTestcaseMainManager.get_last_obj()
        next_main_id = last_sub_obj.id + 1 if last_sub_obj else 1
        ApiTestcaseMainManager.insert_testcase_main(
            id=next_main_id,
            testcase_name=testcase_name,
            simple_desc=simple_desc,
            expect_result=expect_result,
            case_type=case_type,
            case_status=0,
            api_intf_id=base_intf_id,
            api_product_line_id=product_line_id,
            sub_list=str(sub_id_list),
            creator=operator,
            setup_flow_list=str(setup_flow_list),
            main_teardown_hooks=json_dumps(main_teardown_hooks)
        )
        # 更新api_testcase_sub.main_list
        update_main_list_for_sub_objs(sub_id_list, main_id=next_main_id)
        # 设置tag
        set_testcase_tag(next_main_id, tag_id_list, is_main=True)
    else:
        testcase_id = base.pop("testcaseId", None)
        tm_obj = ApiTestcaseMainManager.get_testcase_main(id=testcase_id)
        origin_sub_id_list = json_loads(tm_obj.sub_list)
        ApiTestcaseMainManager.update_testcase_main(
            id_=testcase_id,
            testcase_name=testcase_name,
            simple_desc=simple_desc,
            expect_result=expect_result,
            sub_list=str(sub_id_list),
            last_modifier=operator,
            setup_flow_list=str(setup_flow_list),
            main_teardown_hooks=json_dumps(main_teardown_hooks)
        )
        # 更新api_testcase_sub.main_list
        update_main_list_for_sub_objs(sub_id_list, main_id=testcase_id)
        # 删除多余的子用例
        delete_sub_id_list = []
        if case_type == 2:
            for sub_id in origin_sub_id_list:
                if sub_id not in sub_id_list:
                    delete_sub_id_list.append(sub_id)
            # for sub_id in delete_sub_id_list:
            #     ApiTestcaseSubManager.delete_testcase_sub(sub_id)
        else:
            for sub_id in origin_sub_id_list:
                if sub_id not in sub_id_list:
                    sub_obj = ApiTestcaseSubManager.get_testcase_sub(id=sub_id)
                    if sub_obj.api_intf_id == base_intf_id:
                        delete_sub_id_list.append(sub_id)
        for sub_id in delete_sub_id_list:
            # ApiTestcaseSubManager.delete_testcase_sub(sub_id)
            sub_obj = ApiTestcaseSubManager.get_testcase_sub(id=sub_id)
            main_list = json_loads(sub_obj.main_list)
            if testcase_id in main_list:
                main_list.remove(testcase_id)
                ApiTestcaseSubManager.update_testcase_sub(sub_id, main_list=json_dumps(main_list))
        # 设置tag
        set_testcase_tag(testcase_id, tag_id_list, is_main=True)


def update_main_list_for_sub_objs(sub_id_list, main_id):
    to_update_sub_objs = ApiTestcaseSubManager.get_testcase_subs_in_id_list(sub_id_list)
    for to_update_sub_obj in to_update_sub_objs:
        old_main_list_str = to_update_sub_obj.main_list
        if old_main_list_str:
            old_main_list = json_loads(old_main_list_str)
            if old_main_list:
                if main_id not in old_main_list:
                    old_main_list.append(main_id)
                new_main_list = json_dumps(old_main_list)
            else:
                new_main_list = '[{}]'.format(main_id)
        else:
            new_main_list = '[{}]'.format(main_id)
        ApiTestcaseSubManager.update_testcase_sub(to_update_sub_obj.id, main_list=new_main_list)


def set_testcase_tag(testcase_id, tag_id_list, is_main=None):
    if is_main:
        manager = ApiTestcaseMainTagRelationManager
    else:
        manager = ApiTestcaseTagRelationManager

    objs = manager.get_relations(api_testcase_id=testcase_id)
    to_delete_id_list = [str(obj.id) for obj in objs]

    for tag_id in tag_id_list:
        exist_tag_obj = manager.get_relation(api_testcase_id=testcase_id, tag_id=tag_id)
        if exist_tag_obj:
            to_delete_id_list.remove(str(exist_tag_obj.id))
        else:
            manager.insert_relation(api_testcase_id=testcase_id, tag_id=tag_id)

    for id_ in to_delete_id_list:
        manager.delete_relation(id_)


def transfer_to_actual_value(variable):
    if 'saveAs' in variable and variable["saveAs"] in ['num', 'bool', 'list', 'dict']:
        actual_var_value = eval(variable["value"])
    else:
        actual_var_value = variable["value"]
    return actual_var_value


def save_flow(testcase_id, flow_list):
    """全链路用例保存自定义链路信息"""
    old_flow_objs = ApiTestcaseMainCustomFlowManager.get_flows(testcase_id=testcase_id)
    old_flow_id_list = [obj.id for obj in old_flow_objs]
    if flow_list:
        for flow_dic in flow_list:
            if 'flowId' in flow_dic and flow_dic['flowId']:
                # 编辑原有的flow
                if flow_dic['flowId'] in old_flow_id_list:
                    old_flow_id_list.remove(flow_dic['flowId'])
                ApiTestcaseMainCustomFlowManager.update_flow(
                    id_=flow_dic['flowId'], flow_name=flow_dic['flowName'],
                    flow_index_list=json_dumps(flow_dic['flowIndexList'])
                )
            else:
                # 新增的flow
                ApiTestcaseMainCustomFlowManager.insert_flow(
                    testcase_id=testcase_id, flow_name=flow_dic['flowName'],
                    flow_index_list=json_dumps(flow_dic['flowIndexList'])
                )

    # 删除多余的旧flow
    for old_flow_id in old_flow_id_list:
        ApiTestcaseMainCustomFlowManager.delete_flow(id_=old_flow_id)


if __name__ == '__main__':
    for teardown_hook in CUSTOM["teardown-hooks"]:
        print(teardown_hook)
