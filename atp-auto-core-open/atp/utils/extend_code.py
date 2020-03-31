# -*- coding:utf-8 -*-

import functools
import json
import random
import traceback
import time

from atp.api.mysql_manager import (
    BaseTestcaseInfoManager as btim, query_testcase_belong, TestsuiteInfoManager, TestcaseTagRelationManager,
    TestcaseTagManager, TestcaseInfoManager
)

from atp.utils.tools import json_dumps, json_loads


def func_timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        start_time = time.time()
        c = func(*args, **kw)
        end_time = time.time()
        d_time = end_time - start_time
        print("==================== custom_func[{0}], run {1:.3}s ====================>\n".format(
            func.__name__, d_time))
        return c
    return wrapper


@func_timer
def count_base_subtree(subtree):
    grouped_case_data = btim.group_testcases_by_module_id()

    def count_base_case_by_node(node_dic):
        current_node_count = 0
        if 'children' in node_dic:
            for sub_node_dic in node_dic['children']:
                current_node_count += count_base_case_by_node(sub_node_dic)
            node_dic['label'] += ' ({})'.format(current_node_count)
        else:
            for row in grouped_case_data:
                if row[0] == node_dic['moduleId_last']:
                    current_node_count = row[1]
                    break
            node_dic['label'] += ' ({})'.format(current_node_count)
        return current_node_count

    for s_dic in subtree:
        count_base_case_by_node(s_dic)

    return subtree


@func_timer
def init_testcase_info_index():
    """适用于初始化用例表index列为空的情况, 可重复执行"""
    from atp.api.mysql_manager import TestcaseInfoManager as tcim
    tc_objs = tcim.get_testcases_by(index=None)
    tmp_index_dic = {}
    for tc_obj in tc_objs:
        if tc_obj.testsuite_id not in tmp_index_dic:
            last_obj = tcim.get_last_obj_by_testsuite(tc_obj.testsuite_id)
            if last_obj.index is not None:
                next_index = last_obj.index + 1
            else:
                next_index = 0
            tmp_index_dic[tc_obj.testsuite_id] = next_index
        else:
            tmp_index_dic[tc_obj.testsuite_id] += 1

        tcim.update_testcase(tc_obj.id, index=tmp_index_dic[tc_obj.testsuite_id])

    print(tmp_index_dic)


@func_timer
def migrate_testcase_desc_to_tag():
    """适用于导入用例后, 把导入用例的描述信息迁移为tag关系, 可重复执行"""
    from atp.api.mysql_manager import TestcaseInfoManager as tcim, TestcaseTagRelationManager as ttrm
    tag_map = {
        6: '正常场景',
        7: '异常场景'
    }
    normal_r_objs = ttrm.query_by_tag(tag_id=6)
    exception_r_objs = ttrm.query_by_tag(tag_id=7)
    for tag_id, tag_desc in tag_map.items():
        t_objs = tcim.get_testcases_by(simple_desc=tag_desc)
        insert_list = []
        for t_obj in t_objs:
            has_tag = False
            for r_obj in normal_r_objs:
                if t_obj.id == r_obj.testcase_id:
                    has_tag = True
                    break
            if not has_tag:
                for r_obj in exception_r_objs:
                    if t_obj.id == r_obj.testcase_id:
                        has_tag = True
                        break
            if not has_tag:
                insert_list.append(
                    {
                        'testcase_id': t_obj.id,
                        'tag_id': tag_id
                    }
                )
        print((insert_list))
        if insert_list:
            ttrm.batch_insert_relation(insert_list)


@func_timer
def count_call_chain(testcase_id, previous_count=None):
    """
    遍历所有前置testcase_id
    :param testcase_id:
    :return:
    """
    if not previous_count:
        current_count = 1
    else:
        current_count = previous_count
    row = query_testcase_belong(testcase_id)
    if row[0]:
        setup_cases = eval(row[0])[1]['setup_cases']
    else:
        setup_cases = []

    for setup_case_id in setup_cases:
        if str(testcase_id) != str(setup_case_id):
            current_count = count_call_chain(setup_case_id, current_count)
            current_count += 1

    return current_count


@func_timer
def init_api_test_data():
    """
    初始化接口测试数据，包含：
        api_company_info
        api_system_info
        api_project_info
    :return:
    """
    from atp.api.mysql_manager import ApiCompanyInfoManager, ApiSystemInfoManager, ApiProjectInfoManager



@func_timer
def migrate_api_test_data():
    """
    迁移接口测试数据，包含：
        api_intf_info
        api_testcase_info
        api_testcase_request
        api_public_variable_info
        api_testcase_tag_relation
    :return:
    """
    from atp.api.mysql_manager import (
        TestsuiteInfoManager, TestcaseInfoManager, PublicVariableInfoManage, TestcaseTagRelationManager,
        ModuleInfoManager, SystemInfoManager, ProjectInfoManager
    )
    from atp.api.mysql_manager import (
        ApiCompanyInfoManager, ApiSystemInfoManager, ApiIntfInfoManager, ApiTestcaseInfoManager,
        ApiTestcaseRequestManager, ApiPublicVariableInfoManager, ApiTestcaseTagRelationManager,
        ApiProjectIntfRelationManager, ApiProjectSystemRelationManager
    )



def download_xmind_api():
    from atp.api.mysql_manager import ApiCompanyInfoManager as acim, ApiTestcaseTagRelationManager as attrm
    project_id = 1
    xmind_dic = {}
    res = acim.query_api_subtree_for_xmind(project_id)
    for row in res:
        print(row)
        if row[0] not in xmind_dic:
            xmind_dic[row[0]] = {}
        if row[1] and row[1] not in xmind_dic[row[0]]:
            xmind_dic[row[0]][row[1]] = {}
        if row[2] and row[2] not in xmind_dic[row[0]][row[1]]:
            xmind_dic[row[0]][row[1]][row[2]] = {}
        if row[3] and row[3] not in xmind_dic[row[0]][row[1]][row[2]]:
            xmind_dic[row[0]][row[1]][row[2]][row[3]] = {}
        if row[4]:
            tag_objs = attrm.query_tag_info_by_testcase(row[4])
            tag_name_list = [t_obj[1] for t_obj in tag_objs] if tag_objs else []
            tag = '异常场景' if '异常场景' in tag_name_list else '正常场景'
            if tag not in xmind_dic[row[0]][row[1]][row[2]][row[3]]:
                xmind_dic[row[0]][row[1]][row[2]][row[3]].update({tag: {}})

            expect = row[6] if row[6] else ''
            xmind_dic[row[0]][row[1]][row[2]][row[3]][tag].update({row[5]: {'预期': {expect: {}}}})

    print(json_dumps(xmind_dic))
    from atp.api.xmind_parser import export_xmind_api
    filename = export_xmind_api(xmind_dic)

if __name__ == '__main__':
    pass
