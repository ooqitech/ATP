# -*- coding:utf-8 -*-
import copy
import json

from atp.api.mysql_manager import (
    ApiSystemInfoManager, ApiIntfInfoManager, ApiTestcaseInfoManager, ApiTestcaseRequestManager,
    ApiTestcaseMainManager,
    ApiPublicVariableInfoManager, ApiTestcaseMainCustomFlowManager)
from atp.engine.code_to_desc import get_desc_by_case_type
from atp.utils.tools import get_current_timestamp, get_current_time
# from atp.views.wrappers import custom_func_wrapper


def parse_setup_case_str(setup_case_str):
    """
    处理接口用例的setup_case_str
    "1-6606"   =>   (1, 6606, None)
    "1-6606-self"   =>   (1, 6606, 'self')
    "2-183"   =>   (2, 183, None)
    "2-183-12"   =>   (2, 183, 12)
    """
    case_type = int(setup_case_str[:1])
    # option = None
    # if case_type == 1:
    #     if '-' not in setup_case_str[2:]:
    #         case_id = int(setup_case_str[2:])
    #     else:
    #         case_info_list = setup_case_str[2:].split('-')
    #         case_id = int(case_info_list[0])
    #         option = case_info_list[1]
    # else:
    #     if '-' not in setup_case_str[2:]:
    #         case_id = int(setup_case_str[2:])
    #     else:
    #         case_info_list = setup_case_str[2:].split('-')
    #         case_id = int(case_info_list[0])
    #         option = int(case_info_list[1])
    # return case_type, case_id, option
    case_info_list = setup_case_str.split('-')
    case_info_list = [int(v) if not (i == 2 and case_type == 1) else v for i, v in enumerate(case_info_list)]
    if len(case_info_list) < 3:
        case_info_list.append(None)

    return tuple(case_info_list)


def parse_case_tree(case_tree):
    tree_dic = json.loads(case_tree)
    intf_id_list = tree_dic.get('intf_id_list', [])
    product_line_id_list = tree_dic.get('product_line_id_list', [])
    return intf_id_list, product_line_id_list


# @custom_func_wrapper
def get_testcase_chain(testcase_id, case_type, chain_list=None, with_intf_system_name=None, with_extract=None,
                       only_first=False, main_case_flow_id=None, childless=False):
    """
    根据testcase_id获取调用链, 包含接口用例和全链路用例
    return example:
    [
        {
            "preCaseId": 1,
            "preCaseName": "指定手机获取验证码",
            "preCaseType": "接口用例",
            "preIntfName": "接口描述-/url/api"
        },
        {
            "preCaseId": 27,
            "preCaseName": "新户申请钱包",
            "preCaseType": "全链路用例"
        },
        {
            "preCaseId": 2,
            "preCaseName": "登录",
            "preCaseType": "接口用例"
        }
    ]
    """
    if not chain_list:
        chain_list = []

    # 调用链最大长度保护
    if len(chain_list) >= 100:
        return chain_list

    if case_type == 1:
        tc_obj = ApiTestcaseInfoManager.get_testcase(id=testcase_id)
        if tc_obj:
            if with_intf_system_name:
                intf_obj = ApiIntfInfoManager.get_intf(id=tc_obj.api_intf_id)
                system_obj = ApiSystemInfoManager.get_system(id=intf_obj.api_system_id)
                chain_row_dic = {
                    "preCaseName": '{0}__{1}'.format(tc_obj.testcase_name, tc_obj.expect_result),
                    "preCaseId": tc_obj.id,
                    "preCaseType": get_desc_by_case_type(case_type),
                    "preIntfName": '{0}-{1}'.format(intf_obj.intf_desc, intf_obj.intf_name),
                    "preSystemName": system_obj.system_name
                }
                if with_extract:
                    # 解析出用例中提取变量
                    extract_v_names = get_extract_v_names(testcase_id)
                    public_v_names = get_public_v_names(tc_obj)
                    chain_row_dic.update({"extract_v_names": extract_v_names, "public_v_names": public_v_names})
                chain_list.insert(0, chain_row_dic)
            else:
                chain_row_dic = {
                    "preCaseName": '{0}__{1}'.format(tc_obj.testcase_name, tc_obj.expect_result),
                    "preCaseId": tc_obj.id,
                    "preCaseType": get_desc_by_case_type(case_type),
                }
                if with_extract:
                    # 解析出用例中提取变量
                    extract_v_names = get_extract_v_names(testcase_id)
                    public_v_names = get_public_v_names(tc_obj)
                    chain_row_dic.update({"extract_v_names": extract_v_names, "public_v_names": public_v_names})
                chain_list.insert(0, chain_row_dic)
            if childless:
                chain_list[0]['hasChildren'] = False
                return chain_list
            setup_case_list = json.loads(tc_obj.setup_case_list) if tc_obj.setup_case_list else []
            setup_case_list.reverse()
            if setup_case_list:
                if only_first:
                    chain_list[0]['hasChildren'] = True
                    return chain_list
                else:
                    # 继续递归查询前置
                    for setup_case_str in setup_case_list:
                        setup_case_type, setup_case_id, option = parse_setup_case_str(setup_case_str)
                        kwargs = {
                            'chain_list': chain_list,
                            'with_intf_system_name': with_intf_system_name,
                            'with_extract': with_extract
                        }
                        if setup_case_type == 1:
                            if option == 'self':
                                kwargs['childless'] = True
                        elif setup_case_type == 2:
                            kwargs['main_case_flow_id'] = option
                        chain_list = get_testcase_chain(setup_case_id, setup_case_type, **kwargs)
                        # setup_case_type, setup_case_id, setup_case_flow_id = parse_setup_case_str(setup_case_str)
                        # chain_list = get_testcase_chain(
                        #     setup_case_id, setup_case_type, chain_list=chain_list,
                        #     with_intf_system_name=with_intf_system_name, with_extract=with_extract,
                        #     main_case_flow_id=setup_case_flow_id
                        # )
            else:
                if only_first:
                    chain_list[0]['hasChildren'] = False
                    return chain_list
        return chain_list

    elif case_type == 2:
        tm_obj = ApiTestcaseMainManager.get_testcase_main(id=testcase_id)
        if tm_obj:
            chain_list.insert(
                0,
                {
                    "preCaseName": '{0}__{1}'.format(tm_obj.testcase_name, tm_obj.expect_result),
                    "preCaseId": tm_obj.id,
                    "preCaseType": get_desc_by_case_type(case_type),
                    "preIntfName": '',
                    "preSystemName": '',
                    "customFlowId": None,
                    "customFlowName": ''
                }
            )
            if only_first:
                chain_list[0]['hasChildren'] = False
            if main_case_flow_id:
                flow_obj = ApiTestcaseMainCustomFlowManager.get_flow(id=main_case_flow_id)
                if flow_obj:
                    chain_list[0]['customFlowName'] = flow_obj.flow_name
                    chain_list[0]['customFlowId'] = flow_obj.id
        return chain_list


def get_testcase_chain_objs(testcase_id, case_type, chain_list=None):
    """
        根据testcase_id获取调用链, 包含接口用例和全链路用例
        return example:
        [
            {
                "preCaseId": 1,
                "preCaseName": "指定手机获取验证码",
                "preCaseType": "接口用例"
            },
            {
                "preCaseId": 27,
                "preCaseName": "新户申请钱包",
                "preCaseType": "全链路用例"
            },
            {
                "preCaseId": 2,
                "preCaseName": "登录",
                "preCaseType": "接口用例"
            }
        ]
        """
    if not chain_list:
        chain_list = []

    # 调用链最大长度保护
    if len(chain_list) >= 100:
        return chain_list

    if case_type == 1:
        tc_obj = ApiTestcaseInfoManager.get_testcase(id=testcase_id)
        if tc_obj:
            chain_list.insert(
                0,
                {
                    "case_type": case_type,
                    "obj": tc_obj
                }
            )
            setup_case_list = json.loads(tc_obj.setup_case_list) if tc_obj.setup_case_list else []
            setup_case_list.reverse()
            if setup_case_list:
                for setup_case_str in setup_case_list:
                    setup_case_type, setup_case_id, setup_case_flow_id = parse_setup_case_str(setup_case_str)
                    chain_list = get_testcase_chain_objs(
                        setup_case_id, setup_case_type, chain_list=chain_list)
        return chain_list

    elif case_type == 2:
        tm_obj = ApiTestcaseMainManager.get_testcase_main(id=testcase_id)
        if tm_obj:
            chain_list.insert(
                0,
                {
                    "case_type": case_type,
                    "obj": tm_obj
                }
            )
        return chain_list


def get_extract_v_names(testcase_id):
    """
    根据testcase_id获取用例中提取的变量名
    Args:
        testcase_id:

    Returns:
        "$serialNo, $MOBILE_NO, $DEVICE_ID, $current_timestamp"
    """
    extract_v_names = ''
    r_obj = ApiTestcaseRequestManager.get_request(api_testcase_id=testcase_id)
    if r_obj:
        testset = json.loads(r_obj.request)
        for extract_dic in testset['teststeps'][0]['extract']:
            for v_name in extract_dic:
                if extract_v_names:
                    extract_v_names += ', $' + v_name
                else:
                    extract_v_names = '$' + v_name

    return extract_v_names


def get_public_v_names(tc_obj, v_names=None):
    """
        根据tc_obj获取用例中公共变量的名称
        Args:
            tc_obj:
            v_names:

        Returns:
            "$serialNo, $MOBILE_NO, $DEVICE_ID, $current_timestamp"
        """
    if not v_names:
        v_names = ''
    include_list = json.loads(tc_obj.include)
    public_variables_list = []
    for include in include_list:
        if 'public_variables' in include:
            public_variables_list = include['public_variables']
    for public_variable_id in public_variables_list:
        public_v_obj = ApiPublicVariableInfoManager.get_variable(id=public_variable_id)
        if public_v_obj:
            if v_names:
                v_names += ', $' + public_v_obj.variable_name
            else:
                v_names = '$' + public_v_obj.variable_name

    return v_names


def get_testcase_id_chain(testcase_id, table_data, chain_list=None):
    """
        根据testcase_id获取调用链[id]
        return example:
        [1,2,3,4]
        """
    if not chain_list:
        chain_list = []

    # 调用链最大长度保护
    if len(chain_list) >= 100:
        return chain_list

    chain_list.insert(
        0,
        testcase_id
    )
    for table_testcase_id, setup_case_id_list in table_data.items():
        if testcase_id == table_testcase_id:
            setup_case_list = copy.copy(setup_case_id_list)
            setup_case_list.reverse()
            if setup_case_list:
                for setup_case_id in setup_case_list:
                    chain_list = get_testcase_id_chain(setup_case_id, table_data, chain_list=chain_list)

    return chain_list


def parse_intf_testcases_map_to_testcase_group(intf_testcases_map, table_data=None, cache_testcase_chain_dict=None):
    """
        e.g.
        input：
        intf_testcases_map = {434: [6948, 6947, 6606], 858: [6578]}

        return：
        testcase_group = [[5948, 6579, 6578, 6948], [6947], [5948, 6579, 6578, 6606], [5948, 6579, 6578]]

    """
    if not table_data:
        table_data = get_table_data()

    testcase_group = []
    for intf, testcase_list in intf_testcases_map.items():
        for testcase_id in testcase_list:

            if cache_testcase_chain_dict is None:
                # 不走缓存
                chain_id_list = get_testcase_id_chain(testcase_id, table_data)
            else:
                # 走缓存
                if testcase_id not in cache_testcase_chain_dict:
                    chain_id_list = []
                    for chain in cache_testcase_chain_dict.values():
                        if testcase_id in chain:
                            chain_id_list = chain[:1 + chain.index(testcase_id)]
                            cache_testcase_chain_dict[testcase_id] = chain_id_list
                            break
                    if not chain_id_list:
                        chain_id_list = get_testcase_id_chain(testcase_id, table_data)
                        cache_testcase_chain_dict[testcase_id] = chain_id_list
                else:
                    chain_id_list = cache_testcase_chain_dict[testcase_id]
            testcase_group.append(chain_id_list)
    return testcase_group


def smart_filter_testcase(intf_testcases_map, table_data, cache_testcase_chain_dict=None):
    """
    e.g.
    input：
    intf_testcases_map = {434: [6948, 6947, 6606], 858: [6578]}
    processing:
    testcase_group = [[5948, 6579, 6578, 6948], [6947], [5948, 6579, 6578, 6606], [5948, 6579, 6578]]
    return：
    filtered_intf_testcases_map = {434: [6948, 6947, 6606]}

    """
    testcase_group = parse_intf_testcases_map_to_testcase_group(
        intf_testcases_map, table_data=table_data, cache_testcase_chain_dict=cache_testcase_chain_dict)
    # print(testcase_group)

    for i in range(len(testcase_group) - 1, -1, -1):
        for compare_chain_list in testcase_group:
            if testcase_group[i] != compare_chain_list:
                if testcase_group[i][-1] in compare_chain_list:
                    testcase_group.pop(i)
                    break

    filtered_intf_testcases_map = {}
    for chain_id_list in testcase_group:
        for intf, testcase_list in intf_testcases_map.items():
            if chain_id_list[-1] in testcase_list:
                if intf not in filtered_intf_testcases_map:
                    filtered_intf_testcases_map[intf] = [chain_id_list[-1]]
                else:
                    filtered_intf_testcases_map[intf].append(chain_id_list[-1])
    return filtered_intf_testcases_map


def get_table_data():
    """
    查询接口用例表，获取结构 {接口用例id1:[前置接口用例id2,前置接口用例id3, ...], ...}
    Returns:{2: [1], 3: [2], 4: [2], 199: [198, 666]}

    """
    res = ApiTestcaseInfoManager.get_id_and_setup_case_list()
    table_data = {}
    for row in res:
        try:
            setup_case_list = json.loads(row[1])
        except Exception:
            continue
        if setup_case_list:
            parsed_setup_case_list = []
            for setup_case_str in setup_case_list:
                setup_case_type, setup_case_id, setup_case_flow_id = parse_setup_case_str(setup_case_str)
                if setup_case_type == 1:
                    parsed_setup_case_list.append(setup_case_id)
            table_data[row[0]] = parsed_setup_case_list

    return table_data


# @custom_func_wrapper
def get_setupped_case_id_list(case_id, case_type):
    """
    获取前置了输入用例的所有用例列表
    Returns:[5, 19, 54, 99, 199]
    """
    res = ApiTestcaseInfoManager.get_id_and_setup_case_list()
    setupped_case_id_set = set()
    for row in res:
        try:
            setup_case_list = json.loads(row[1])
        except Exception:
            continue
        if setup_case_list:
            for setup_case_str in setup_case_list:
                setup_case_type, setup_case_id, setup_case_flow_id = parse_setup_case_str(setup_case_str)
                if case_type == setup_case_type and case_id == setup_case_id:
                    setupped_case_id_set.add(row[0])
                    break

    return sorted(setupped_case_id_set)


def get_testcase_id_list_filter_by_tag(related_tag_id_list, intf_id=None, product_line_id=None):
    """ 根据任务配置的测试标签，过滤接口用例和全链路用例"""
    try:
        related_tag_id_list = json.loads(related_tag_id_list)
    except Exception:
        related_tag_id_list = None

    if not related_tag_id_list:
        return []

    if intf_id:
        res = ApiTestcaseInfoManager.filter_task_testcase_ids(intf_id, related_tag_id_list)
        return [row[0] for row in res]
    elif product_line_id:
        res = ApiTestcaseMainManager.filter_task_testcase_ids(product_line_id, related_tag_id_list)
        return [row[0] for row in res]


def get_testcase_id_list_filter_by_tag_(related_tag_id_list, intf_ids=None, product_line_ids=None):
    """ 根据任务配置的测试标签，过滤接口用例和全链路用例"""
    try:
        related_tag_id_list = json.loads(related_tag_id_list)
    except Exception:
        related_tag_id_list = None

    if not related_tag_id_list:
        return []

    if intf_ids:
        res = ApiTestcaseInfoManager.filter_task_testcase_ids_(intf_ids, related_tag_id_list)
        return [[row[0], row[1]] for row in res]
    elif product_line_ids:
        res = ApiTestcaseMainManager.filter_task_testcase_ids_(product_line_ids, related_tag_id_list)
        return [row[0] for row in res]


# @custom_func_wrapper
def count_testcase_total(task_obj, table_data, cache_testcase_chain_dict):
    total = 0
    intf_testcases_map = {}
    if task_obj.task_type in (1, 3):
        intf_id_list, product_line_id_list = parse_case_tree(task_obj.case_tree)
        if intf_id_list:
            intf_testcase_id_maps = get_testcase_id_list_filter_by_tag_(task_obj.related_tag_id_list, intf_id_list)
            for intf_testcase_id_map in intf_testcase_id_maps:
                if intf_testcase_id_map[1] in intf_testcases_map:
                    intf_testcases_map[intf_testcase_id_map[1]].append(intf_testcase_id_map[0])
                else:
                    intf_testcases_map[intf_testcase_id_map[1]] = [intf_testcase_id_map[0]]
        # for intf_id in intf_id_list:
        #     testcase_id_list = get_testcase_id_list_filter_by_tag(task_obj.related_tag_id_list, intf_id=intf_id)
        #     intf_testcases_map[intf_id] = testcase_id_list
        # for product_line_id in product_line_id_list:
        #     total += len(get_testcase_id_list_filter_by_tag(
        #         task_obj.related_tag_id_list, product_line_id=product_line_id))
        if product_line_id_list:
            total += len(get_testcase_id_list_filter_by_tag_(
                task_obj.related_tag_id_list, product_line_ids=product_line_id_list))

    else:
        intf_id_list = json.loads(task_obj.effect_intf_id_list)
        for intf_id in intf_id_list:
            testcase_id_list = get_testcase_id_list_filter_by_tag(task_obj.related_tag_id_list, intf_id=intf_id)
            intf_testcases_map[intf_id] = testcase_id_list

    # 接口用例智能去重
    filtered_intf_testcases_map = smart_filter_testcase(
        intf_testcases_map, table_data, cache_testcase_chain_dict)
    for testcase_list in filtered_intf_testcases_map.values():
        total += len(testcase_list)

    return total


if __name__ == '__main__':
    # print(json_dumps(get_testcase_chain(6606, 1, with_extract=1)))
    # res1 = smart_filter_testcase({434: [6948, 6947, 6606], 858: [6578]})
    # print(res1)
    from atp.app import create_app

    app = create_app()
    with app.app_context():
        # print(get_setupped_case_id_list(6579, 1))
        # ApiTestcaseMainManager.update_testcase_main(id_=27, last_run_time=get_current_time())
        # kwargs = {"only_first": False}
        # print(get_testcase_chain(5141, 1, **kwargs))
        print(parse_setup_case_str('1-6606-self'))
