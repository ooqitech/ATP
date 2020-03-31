import json
import re
from collections import OrderedDict

import time

from atp.engine.api_chain import parse_setup_case_str, get_testcase_chain
from atp.engine.code_to_desc import get_desc_by_case_type
from atp.utils.map_functions import map_number_to_testcase_type
from atp.utils.common import read_custom

from atp.api.mysql_manager import ApiIntfInfoManager, ApiTestcaseInfoManager, ApiTestcaseRequestManager, \
    ApiTestcaseMainCustomFlowManager
from atp.api.mysql_manager import (
    ApiPublicVariableInfoManager, ApiTestcaseSubManager, ApiTestcaseRequestQllManager, ApiTestcaseMainManager,
    ApiProductLineManager
)
from atp.api.comm_log import logger

from atp.views.wrappers import custom_func_wrapper


def get_api_testcase_detail(tc_obj, without_setup_cases=False):
    """
    新版-获取测试用例详情
    :param tc_obj:
    :param without_setup_cases:
    :return:
    """
    custom = read_custom()
    pvim = ApiPublicVariableInfoManager()

    response = {
        "base": {
            "testcaseId": tc_obj.id,
            "testcaseName": tc_obj.testcase_name,
            "testcaseDesc": tc_obj.simple_desc if tc_obj.simple_desc else '',
            "creator": tc_obj.creator,
            "last_modifier": tc_obj.last_modifier,
            "expectResult": tc_obj.expect_result if tc_obj.expect_result else '',
        },
        "steps": [
            {
                "setupInfo": [],
                "teardownInfo": [],
                "requestTeardownInfo": [],
                "requestInfo": {
                    "type": tc_obj.type
                },
                "validateInfo": [],
                "extractInfo": [],
                "variableInfo": []
            }
        ],
    }
    tcr_obj = ApiTestcaseRequestManager.get_request(api_testcase_id=tc_obj.id)
    request = tcr_obj.request if tcr_obj else None
    include = tc_obj.include
    request_type = tc_obj.type
    setup_case_list = json.loads(tc_obj.setup_case_list) if tc_obj.setup_case_list else []

    # 返回setupCases
    if not without_setup_cases:
        response['setupCases'] = []
        for setup_case_str in setup_case_list:
            setup_case_type, setup_case_id, option = parse_setup_case_str(setup_case_str)
            kwargs = {
                'with_intf_system_name': True,
                'with_extract': False,
                'only_first': True
            }
            if setup_case_type == 1:
                if option == 'self':
                    kwargs['childless'] = True
            elif setup_case_type == 2:
                kwargs['main_case_flow_id'] = option
            setup_chain_list = get_testcase_chain(setup_case_id, setup_case_type, **kwargs)
            setup_case_dic = setup_chain_list.pop()
            setup_case_dic['children'] = setup_chain_list
            response['setupCases'].append(setup_case_dic)

    if request:
        # testcase_request = json.loads(request.replace("'", "\""))
        testcase_request = json.loads(request)
        last_teststeps = len(testcase_request["teststeps"]) - 1
        # 返回variableInfo
        for variable in testcase_request["teststeps"][last_teststeps]["variables"]:
            for variable_key, variable_value in variable.items():
                if 1 == 0:
                    pass
                else:
                    variable_dict = {}
                    # variable_value = str(variable_value)
                    save_as_type = get_save_as_type(variable_value)
                    variable_value = str(variable_value)

                    # 自定义变量-db
                    if variable_value.startswith("${variable_db_operation("):
                        variable_dict["name"] = variable_key
                        variable_dict["type"] = "db"
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
                        for func in custom["functions"]:
                            if func["name"] == func_name:
                                for a, p in zip(args_list, func["parameters"]):
                                    args_dict[p] = a
                                break

                        variable_dict["name"] = variable_key
                        variable_dict["type"] = "function"
                        variable_dict["value"] = func_name
                        variable_dict["args"] = args_dict

                    # 变量类型-constant
                    else:
                        variable_dict["saveAs"] = save_as_type
                        variable_dict["name"] = variable_key
                        variable_dict["type"] = "constant"
                        variable_dict["value"] = variable_value
                    response["steps"][0]["variableInfo"].append(variable_dict)

        # 返回setupInfo
        testcase_setup_hooks = testcase_request["teststeps"][last_teststeps]["setup_hooks"]
        for setup in testcase_setup_hooks:
            setup_func_name = setup.split("${")[1].split("(")[0]
            setup_func_args = setup[:-2].split("(", 1)[-1]
            '''判断request字段里面的setup_hooks里面是否有前置操作，有则返回至detail的setupInfo'''
            for setup_hook in custom["setup-hooks"]:
                if setup_hook["name"] == setup_func_name:
                    if setup_func_name == "setup_db_operation":
                        response["steps"][0]["setupInfo"].append({
                            "name": setup_func_name,
                            "desc": setup_hook["description"],
                            "args": {"sql": setup_func_args.replace("||$DB_CONNECT", "", 1)}
                        })
                    elif setup_func_name == "setup_wait_until_db_result_succeed":
                        args_dict = {}
                        for a, p in zip(setup_func_args.split('||'), setup_hook["parameters"]):
                            if p == "sql":
                                args_dict[p] = a.replace("||$DB_CONNECT", "", 1)
                            else:
                                args_dict[p] = a
                        response["steps"][0]["setupInfo"].append({
                            "name": setup_func_name,
                            "desc": setup_hook["description"],
                            "args": args_dict
                        })
                    else:
                        '''
                                              # {
                                #     "name": "execution_testcase",
                                #     "args": {
                                #         "用例编号": "4173",
                                #         "请求参数": "{\"phone\":\"18260037329\"}"
                                #     }
                                # }
                                #
                            '''
                        args_dict = {}
                        for a, p in zip(setup_func_args.split('||'), setup_hook["parameters"]):
                            args_dict[p] = a

                        response["steps"][0]["setupInfo"].append(
                            {"name": setup_func_name,
                             "desc": setup_hook["description"],
                             "args": args_dict
                             }
                        )
            '''判断request字段里面的setup_hooks里面是否有加签函数，有则返回至detail的requestInfo'''
            for setup_hook in custom["sign"]:
                if setup_hook["name"] == setup_func_name:
                    if "sign" in setup_func_name:
                        '''setup_hooks中是否有加签函数'''
                        response["steps"][0]["requestInfo"]["sign"] = {
                            "name": setup_func_name, "desc": setup_hook["description"]}

        # 返回teardownInfo
        testcase_teardown_hooks = testcase_request["teststeps"][last_teststeps]["teardown_hooks"]
        for teardown in testcase_teardown_hooks:
            teardown_func_name = teardown.split("${")[1].split("(")[0]
            teardown_func_args = teardown[:-2].split("(", 1)[-1]
            for teardown_hook in custom["teardown-hooks"]:
                if teardown_hook["name"] == teardown_func_name:
                    if teardown_func_name == "teardown_db_operation":
                        response["steps"][0]["teardownInfo"].append({
                            "name": teardown_func_name,
                            "desc": teardown_hook["description"],
                            "args": {"sql": teardown_func_args.replace("||$DB_CONNECT", "", 1)}
                        })
                    elif teardown_func_name == "teardown_wait_until_db_result_succeed":
                        args_dict = {}
                        for a, p in zip(teardown_func_args.split('||'), teardown_hook["parameters"]):
                            if p == "sql":
                                args_dict[p] = a.replace("||$DB_CONNECT", "", 1)
                            else:
                                args_dict[p] = a
                        response["steps"][0]["teardownInfo"].append({
                            "name": teardown_func_name,
                            "desc": teardown_hook["description"],
                            "args": args_dict
                        })
                    else:
                        """如果args是列表，返回args列表"""
                        args_dict = OrderedDict()
                        for a, p in zip(teardown_func_args.split('||'), teardown_hook["parameters"]):
                            args_dict[p] = a
                        response["steps"][0]["teardownInfo"].append(
                            {"name": teardown_func_name,
                             "desc": teardown_hook["description"],
                             "args": args_dict
                             }
                        )

        # 返回requestTeardownInfo
        request_teardown_hooks = testcase_request["teststeps"][last_teststeps].get("request_teardown_hooks", [])
        for teardown in request_teardown_hooks:
            teardown_func_name = teardown.split("${")[1].split("(")[0]
            teardown_func_args = teardown[:-2].split("(", 1)[-1]
            for teardown_hook in custom["teardown-hooks"]:
                if teardown_hook["name"] == teardown_func_name:
                    """如果args是列表，返回args列表"""
                    args_dict = OrderedDict()
                    for a, p in zip(teardown_func_args.split('||'), teardown_hook["parameters"]):
                        args_dict[p] = a
                    response["steps"][0]["requestTeardownInfo"].append(
                        {"name": teardown_func_name,
                         "desc": teardown_hook["description"],
                         "args": args_dict
                         }
                    )

        # 返回requestInfo[json]
        requests_dict = testcase_request["teststeps"][last_teststeps]["request"]
        is_merge = requests_dict.pop("isMerge", True)
        if request_type == 1:

            for json_value in requests_dict.values():
                response["steps"][0]["requestInfo"]["json"] = json_value

            # 增加入参校验
            include_li = json.loads(include)

            if len(include_li) >= 3:
                param_check_dic = include_li[2]["param_check"]
                for item, p_list in param_check_dic.items():
                    if item == 'empty':
                        response["steps"][0]["requestInfo"]["emptyCheckParamList"] = p_list

        elif request_type == 2:
            for args_value in requests_dict.values():
                response["steps"][0]["requestInfo"] = args_value

        elif request_type == 3:

            for msg_value in requests_dict.values():
                response["steps"][0]["requestInfo"] = msg_value

        response["steps"][0]["requestInfo"]["isMerge"] = is_merge
        response["steps"][0]["requestInfo"]["type"] = request_type

        # 返回extractInfo
        for extract in testcase_request["teststeps"][last_teststeps]["extract"]:
            for extract_key, extract_value in extract.items():
                response["steps"][0]["extractInfo"].append(
                    {"saveAs": extract_key,
                     "check": extract_value
                     }
                )

        # 返回validateInfo
        for validate in testcase_request["teststeps"][last_teststeps]["validate"]:
            for comparator, veirfy in validate.items():
                if comparator == 'db_validate' and veirfy[0].endswith('$DB_CONNECT'):
                    veirfy[0] = veirfy[0].split("$DB_")[0]
                response["steps"][0]["validateInfo"].append(
                    {
                        "comparator": comparator,
                        "desc": comparator,
                        "check": veirfy[0],
                        "expect": veirfy[1],
                        "comment": veirfy[2] if len(veirfy) >= 3 else '',
                    })

        # 返回include
        if not (include is None or len(include) < 3):
            testcase_include = json.loads(include)
            include_list = [
                {
                    "public_variables": [
                    ]
                }
            ]
            for pv_id in testcase_include[0]["public_variables"]:
                obj = pvim.get_variable(id=pv_id)
                if not obj:
                    continue
                id_, name, type_name, desc = obj.id, obj.variable_name, obj.type, obj.simple_desc
                value = [v.strip() for v in obj.value.strip('##').split('##')][0]
                include_list[0]["public_variables"].append(
                    {
                        "id": id_,
                        "name": name,
                        "value": value,
                        "type": type_name,
                        "desc": desc
                    }
                )
            response["include"] = include_list

    return response


@custom_func_wrapper
def get_api_testcase_main_detail(tm_obj):
    """
    新版-获取主测试用例详情
    :param tm_obj:
    :return:
    """
    custom = read_custom()
    pvim = ApiPublicVariableInfoManager()
    public_v_objs = pvim.get_variables()

    case_type = tm_obj.case_type

    main_teardown_info = []
    if tm_obj.main_teardown_hooks:
        main_teardown_hooks = json.loads(tm_obj.main_teardown_hooks)
        for teardown in main_teardown_hooks:
            teardown = teardown.replace("||$DB_CONNECT", "", 1).replace("||$DISCONF_HOST", "", 1)
            teardown_func_name = teardown.split("${")[1].split("(")[0]
            teardown_func_args = teardown[:-2].split("(", 1)[-1]
            for teardown_hook in custom["teardown-hooks"]:
                if teardown_hook["name"] == teardown_func_name:
                    args_dict = {}
                    for a, p in zip(teardown_func_args.split('||'), teardown_hook["parameters"]):
                        args_dict[p] = a
                    main_teardown_info.append(
                        {"name": teardown_func_name,
                         "desc": teardown_hook["description"],
                         "args": args_dict
                         }
                    )

    # # 返回自定义flow信息
    # custom_flow_objs = ApiTestcaseMainCustomFlowManager.get_flows(testcase_id=tm_obj.id)
    # custom_flow_list = [
    #     {
    #         "flowId": obj.id,
    #         "flowName": obj.flow_name,
    #         "startEnd": [obj.start_sub_index, obj.end_sub_index]
    #     }
    #     for obj in custom_flow_objs
    # ]

    response = {
        "base": {
            "testcaseName": tm_obj.testcase_name,
            "testcaseDesc": tm_obj.simple_desc if tm_obj.simple_desc else '',
            "creator": tm_obj.creator,
            "last_modifier": tm_obj.last_modifier,
            "expectResult": tm_obj.expect_result if tm_obj.expect_result else '',
            "mainTeardownInfo": main_teardown_info,
        },
        "steps": [

        ],
    }
    _all_main_case_objs = None
    if case_type == 1:
        response["base"].update(
            {
                "caseType": case_type,
                "intfId": tm_obj.api_intf_id,
            }
        )
        response["setupFlow"] = []
        setup_flow_id_list = json.loads(tm_obj.setup_flow_list)
        for setup_flow_id in setup_flow_id_list:
            flow_obj = ApiTestcaseMainManager.get_testcase_main(id=setup_flow_id)
            pl_obj = ApiProductLineManager.get_product_line(id=flow_obj.api_product_line_id)
            product_line_name = pl_obj.product_line_name if pl_obj else ""
            response["setupFlow"].append(
                {
                    "flowCaseId": setup_flow_id,
                    "flowName": flow_obj.testcase_name,
                    "productLineName": product_line_name,
                    "productLineId": flow_obj.api_product_line_id,
                }
            )

        _all_main_case_objs = ApiTestcaseMainManager.get_testcase_mains()

    sub_id_list = json.loads(tm_obj.sub_list)

    ts_objs = ApiTestcaseSubManager.get_testcase_subs_in_id_list(sub_id_list)
    tr_objs = ApiTestcaseRequestQllManager.get_requests_in_case_id_list(sub_id_list)
    intf_id_list = [ts_obj.api_intf_id for ts_obj in ts_objs]
    intf_objs = ApiIntfInfoManager.get_intfs_in_id_list(intf_id_list)

    for sub_id in sub_id_list:
        sub_dic = {
            "base": {},
            "setupInfo": [],
            "teardownInfo": [],
            "requestTeardownInfo": [],
            "requestInfo": {},
            "validateInfo": [],
            "extractInfo": [],
            "variableInfo": []
        }

        # ts_obj = ApiTestcaseSubManager.get_testcase_sub(id=sub_id)
        # tr_obj = ApiTestcaseRequestQllManager.get_request(api_testcase_id=sub_id)
        # intf_obj = ApiIntfInfoManager.get_intf(id=ts_obj.api_intf_id)
        ts_obj = None
        tr_obj = None
        intf_obj = None
        for obj in ts_objs:
            if obj.id == sub_id:
                ts_obj = obj
                break
        for obj in tr_objs:
            if obj.api_testcase_id == sub_id:
                tr_obj = obj
                break

        if not ts_obj or not tr_obj:
            continue
        for obj in intf_objs:
            if obj.id == ts_obj.api_intf_id:
                intf_obj = obj
                break

        request = tr_obj.request
        include = ts_obj.include
        request_type = ts_obj.request_type

        # 返回base
        sub_dic["base"]["intfId"] = ts_obj.api_intf_id
        sub_dic["base"]["intfName"] = intf_obj.intf_name
        sub_dic["base"]["intfNameInChinese"] = intf_obj.intf_desc if intf_obj.intf_desc else ''
        sub_dic["base"]["subId"] = sub_id
        sub_dic["base"]["subName"] = ts_obj.sub_name
        sub_dic["base"]["subDesc"] = ts_obj.simple_desc if ts_obj.simple_desc else ''
        sub_dic["base"]["subExpectResult"] = ts_obj.expect_result if ts_obj.expect_result else ''
        sub_dic["base"]["isMultiQuote"] = True if ts_obj.main_list and json.loads(ts_obj.main_list) and len(json.loads(ts_obj.main_list)) > 1 else False
        sub_dic["base"]["requestType"] = map_number_to_testcase_type(request_type)
        if case_type == 1:
            sub_dic["base"]["isSelf"] = True if ts_obj.api_intf_id == tm_obj.api_intf_id else False

        # testcase_request = json.loads(request.replace("'", "\""))
        testcase_request = json.loads(request)
        last_teststeps = len(testcase_request["teststeps"]) - 1

        # 返回variableInfo
        for variable in testcase_request["teststeps"][last_teststeps]["variables"]:
            for variable_key, variable_value in variable.items():

                if 1 == 0:
                    pass
                else:
                    variable_dict = {}
                    # variable_value = str(variable_value)
                    save_as_type = get_save_as_type(variable_value)
                    variable_value = str(variable_value)

                    # 自定义变量-db
                    if variable_value.startswith("${variable_db_operation("):
                        variable_dict["name"] = variable_key
                        variable_dict["type"] = "db"
                        variable_dict["value"] = variable_value.replace(
                            "${variable_db_operation(", "", 1).replace(
                            "||$DB_CONNECT)}", "", 1)

                    # 变量类型-function
                    elif variable_value.startswith('${') and variable_value.endswith('}'):
                        func_name = variable_value.split('${')[-1].split('(')[0]
                        if 'variable_db_operation' == func_name:
                            continue
                        args_list = variable_value[:-2].split('(', 1)[-1].split('||')
                        args_dict = {}
                        for func in custom["functions"]:
                            if func["name"] == func_name:
                                for a, p in zip(args_list, func["parameters"]):
                                    args_dict[p] = a
                                break

                        variable_dict["name"] = variable_key
                        variable_dict["type"] = "function"
                        variable_dict["value"] = func_name
                        variable_dict["args"] = args_dict

                    # 变量类型-constant
                    else:
                        variable_dict["saveAs"] = save_as_type
                        variable_dict["name"] = variable_key
                        variable_dict["type"] = "constant"
                        variable_dict["value"] = variable_value
                    sub_dic["variableInfo"].append(variable_dict)

        # 返回setupInfo
        testcase_setup_hooks = testcase_request["teststeps"][last_teststeps]["setup_hooks"]
        for setup in testcase_setup_hooks:
            setup_func_name = setup.split("${")[1].split("(")[0]
            setup_func_args = setup[:-2].split("(", 1)[-1]
            # setup_func_args = re.findall(r'[^()]+', setup.split("{")[-1].split('}')[0])[1]
            # setup_func_args = re.findall(r'[(](.*?)[)]', setup,re.S)[0]
            '''判断request字段里面的setup_hooks里面是否有前置操作，有则返回至detail的setupInfo'''
            for setup_hook in custom["setup-hooks"]:
                if setup_hook["name"] == setup_func_name:
                    if setup_func_name == "setup_db_operation":
                        sub_dic["setupInfo"].append({
                            "name": setup_func_name,
                            "desc": setup_hook["description"],
                            "args": {"sql": setup_func_args.replace("||$DB_CONNECT", "", 1)}
                        })
                    elif setup_func_name == "setup_wait_until_db_result_succeed":
                        args_dict = {}
                        for a, p in zip(setup_func_args.split('||'), setup_hook["parameters"]):
                            if p == "sql":
                                args_dict[p] = a.replace("||$DB_CONNECT", "", 1)
                            else:
                                args_dict[p] = a
                        sub_dic["setupInfo"].append({
                            "name": setup_func_name,
                            "desc": setup_hook["description"],
                            "args": args_dict
                        })
                    else:
                        '''
                                # {
                                #     "name": "execution_testcase",
                                #     "args": {
                                #         "用例编号": "4173",
                                #         "请求参数": "{\"phone\":\"18260037329\"}"
                                #     }
                                # }
                                #
                            '''
                        args_dict = {}
                        for a, p in zip(setup_func_args.split('||'), setup_hook["parameters"]):
                            args_dict[p] = a
                        sub_dic["setupInfo"].append(
                            {"name": setup_func_name,
                             "desc": setup_hook["description"],
                             "args": args_dict
                             }
                        )
            '''判断request字段里面的setup_hooks里面是否有加签函数，有则返回至detail的requestInfo'''
            for setup_hook in custom["sign"]:
                if setup_hook["name"] == setup_func_name:
                    if "sign" in setup_func_name:
                        '''setup_hooks中是否有加签函数'''
                        sub_dic["requestInfo"]["sign"] = {
                            "name": setup_func_name, "desc": setup_hook["description"]}

        # 返回teardownInfo
        testcase_teardown_hooks = testcase_request["teststeps"][last_teststeps]["teardown_hooks"]
        for teardown in testcase_teardown_hooks:
            teardown_func_name = teardown.split("${")[1].split("(")[0]
            teardown_func_args = teardown[:-2].split("(", 1)[-1]
            for teardown_hook in custom["teardown-hooks"]:
                if teardown_hook["name"] == teardown_func_name:
                    if teardown_func_name == "teardown_db_operation":
                        sub_dic["teardownInfo"].append({
                            "name": teardown_func_name,
                            "desc": teardown_hook["description"],
                            "args": {"sql": teardown_func_args.replace("||$DB_CONNECT", "", 1)}
                        })
                    elif teardown_func_name == "teardown_wait_until_db_result_succeed":
                        args_dict = {}
                        for a, p in zip(teardown_func_args.split('||'), teardown_hook["parameters"]):
                            if p == "sql":
                                args_dict[p] = a.replace("||$DB_CONNECT", "", 1)
                            else:
                                args_dict[p] = a
                        sub_dic["teardownInfo"].append({
                            "name": teardown_func_name,
                            "desc": teardown_hook["description"],
                            "args": args_dict
                        })
                    else:
                        """如果args是列表，返回args列表"""

                        args_dict = {}
                        for a, p in zip(teardown_func_args.split('||'), teardown_hook["parameters"]):
                            args_dict[p] = a
                        sub_dic["teardownInfo"].append(
                            {"name": teardown_func_name,
                             "desc": teardown_hook["description"],
                             "args": args_dict
                             }
                        )

        # 返回requestTeardownInfo
        request_teardown_hooks = testcase_request["teststeps"][last_teststeps].get("request_teardown_hooks", [])
        for teardown in request_teardown_hooks:
            teardown_func_name = teardown.split("${")[1].split("(")[0]
            teardown_func_args = teardown[:-2].split("(", 1)[-1]
            for teardown_hook in custom["teardown-hooks"]:
                if teardown_hook["name"] == teardown_func_name:
                    """如果args是列表，返回args列表"""
                    args_dict = {}
                    for a, p in zip(teardown_func_args.split('||'), teardown_hook["parameters"]):
                        args_dict[p] = a
                    sub_dic["requestTeardownInfo"].append(
                        {"name": teardown_func_name,
                         "desc": teardown_hook["description"],
                         "args": args_dict
                         }
                    )

        # 返回requestInfo[json]
        requests_dict = testcase_request["teststeps"][last_teststeps]["request"]
        is_merge = requests_dict.pop("isMerge", True)
        if request_type == 1:

            for json_value in requests_dict.values():
                sub_dic["requestInfo"]["json"] = json_value

            # 增加入参校验
            include_li = json.loads(include)

            if len(include_li) >= 3:
                param_check_dic = include_li[2]["param_check"]
                for item, p_list in param_check_dic.items():
                    if item == 'empty':
                        sub_dic["requestInfo"]["emptyCheckParamList"] = p_list

        elif request_type == 2:
            for args_value in requests_dict.values():
                sub_dic["requestInfo"] = args_value

        elif request_type == 3:

            for msg_value in requests_dict.values():
                sub_dic["requestInfo"] = msg_value

        sub_dic["requestInfo"]["isMerge"] = is_merge
        sub_dic["requestInfo"]["type"] = request_type

        # 返回extractInfo

        for extract in testcase_request["teststeps"][last_teststeps]["extract"]:
            for extract_key, extract_value in extract.items():
                sub_dic["extractInfo"].append(
                    {"saveAs": extract_key,
                     "check": extract_value
                     }
                )

        # 返回validateInfo
        for validate in testcase_request["teststeps"][last_teststeps]["validate"]:
            for comparator, veirfy in validate.items():
                if comparator == 'db_validate' and veirfy[0].endswith('$DB_CONNECT'):
                    veirfy[0] = veirfy[0].split("$DB_")[0]
                sub_dic["validateInfo"].append(
                    {
                        "comparator": comparator,
                        "desc": comparator,
                        "check": veirfy[0],
                        "expect": veirfy[1],
                        "comment": veirfy[2] if len(veirfy) >= 3 else '',
                    })

        # 返回include
        if not (include is None or len(include) < 3):
            testcase_include = json.loads(include)
            include_list = [
                {
                    "public_variables": [
                    ]
                }
            ]
            for pv_id in testcase_include[0]["public_variables"]:
                # obj = pvim.get_variable(id=pv_id)
                obj = None
                for public_v_obj in public_v_objs:
                    if public_v_obj.id == pv_id:
                        obj = public_v_obj
                        break
                if not obj:
                    continue
                id_, name, type_name, desc = obj.id, obj.variable_name, obj.type, obj.simple_desc
                value = [v.strip() for v in obj.value.strip('##').split('##')][0]
                include_list[0]["public_variables"].append(
                    {
                        "id": id_,
                        "name": name,
                        "value": value,
                        "type": type_name,
                        "desc": desc
                    }
                )
            sub_dic["include"] = include_list

        # 返回relatedMainCases
        if case_type == 1:
            sub_dic.update({"relatedCases": []})
            for main_case_obj in _all_main_case_objs:
                if main_case_obj.case_type == 2:
                    continue
                other_case_sub_list = json.loads(main_case_obj.sub_list)
                if sub_id in other_case_sub_list:
                    sub_dic["relatedCases"].append(
                        {
                            "testcaseId": main_case_obj.id,
                            "testcaseName": main_case_obj.testcase_name
                        }
                    )

        response["steps"].append(sub_dic)

    return response


def get_save_as_type(variable_value):
    if isinstance(variable_value, bool):
        return 'bool'
    elif isinstance(variable_value, int) or isinstance(variable_value, float):
        return 'num'
    elif isinstance(variable_value, list):
        return 'list'
    elif isinstance(variable_value, dict):
        return 'dict'
    else:
        return 'str'

if __name__ == '__main__':
    variable_value_ = "${encrypt_by_public_key(qwertyuiopasdfghjklzxcv()bnm|| qweer)}"
    args_list_ = variable_value_[:-2].split('(', 1)[-1].split('||')
    print(args_list_)
