# -*- coding:utf-8 -*-

import copy
import functools
import random
import time

# from atp.api import mysql_sql_executor
from atp.engine.api_load_test import merge_request_body
from atp.utils.tools import json_loads, json_dumps, get_current_time
from atp.api.mysql_manager import (
    ApiIntfInfoManager as aiim,
    ApiIntfDefaultRequestManager as aidrm,
    ApiTestcaseInfoManager as atim,
    ApiTestcaseRequestManager as atrm,
    BaseTestcaseInfoManager as btm,
    BaseTestcaseInfoBakManager as btm_bak,
    BaseModuleInfoManager as bmm,
    BaseModuleInfoBakManager as bmm_bak,
    BaseSystemInfoManager as bsm,
    BaseProjectInfoManager as bpm,
    ApiSystemInfoManager as asim,
    ApiTestcaseMainManager,
    ApiTestcaseSubManager,
    ApiTestcaseRequestQllManager,
    ApiPublicVariableInfoManager)
from atp.api.git_api import GitlabAPI


def func_timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        start_time = time.time()

        c = func(*args, **kw)
        end_time = time.time()
        d_time = end_time - start_time
        if d_time > 60:
            d_min = int(d_time/60)
            d_s = d_time % 60
            print("==== Finish [{0}], run {1}min{2:.3}s ====\n".format(func.__name__, d_min, d_s))
        else:
            print("==== Finish [{0}], run {1:.3}s ====\n".format(func.__name__, d_time))
        return c

    return wrapper


def handle_step_dic(request):
    """已废弃，请勿执行"""
    step_dic = request["teststeps"][0]

    # variables
    variables_list = step_dic.pop("variables")
    new_variables_list = []
    replace_v_name = None
    replace_v_value = None
    setup_sql_dic = {}
    teardown_sql_dic = {}

    for v_dic in variables_list:
        for v_name in v_dic:
            if v_name.startswith("V_SQL_"):
                replace_v_name = v_name
                replace_v_value = v_dic[v_name]
                break
            elif v_dic[v_name].startswith("${variable_db_operation"):
                v_dic[v_name] = v_dic[v_name].replace(",", "||")
                v_dic[v_name] = v_dic[v_name].replace("$" + replace_v_name, replace_v_value)
                new_variables_list.append(v_dic)
            elif v_name.startswith("SETUP_SQL_"):
                setup_sql_dic[v_name] = v_dic[v_name]
            elif v_name.startswith("TEARDOWN_SQL_"):
                teardown_sql_dic[v_name] = v_dic[v_name]
            else:
                new_variables_list.append(v_dic)
    step_dic["variables"] = new_variables_list

    # setup_hooks
    setup_hooks_list = step_dic.pop("setup_hooks")
    new_setup_hooks_list = []
    for setup in setup_hooks_list:
        setup = setup.replace(",", "||")
        if setup.startswith("${setup_db_operation"):
            for v_name in setup_sql_dic:
                setup = setup.replace("$" + v_name, setup_sql_dic[v_name])
        new_setup_hooks_list.append(setup)
    step_dic["setup_hooks"] = new_setup_hooks_list

    # teardown_hooks
    teardown_hooks_list = step_dic.pop("teardown_hooks")
    new_teardown_hooks_list = []
    for teardown in teardown_hooks_list:
        teardown = teardown.replace(",", "||")
        if teardown.startswith("${teardown_db_operation"):
            for v_name in teardown_sql_dic:
                teardown = teardown.replace("$" + v_name, teardown_sql_dic[v_name])
        new_teardown_hooks_list.append(teardown)
    step_dic["teardown_hooks"] = new_teardown_hooks_list

    return request


def httprunner_request_update():
    """已废弃，请勿执行"""
    from atp.api.mysql_manager import TestcaseInfoManager
    tc_objs = TestcaseInfoManager.get_all_testcases()
    count = 0
    for tc_obj in tc_objs:
        if tc_obj:
            if tc_obj.request:
                request = json_loads(tc_obj.request)
                count += 1
                new_request = handle_step_dic(request)
                print(count)
                print(json_dumps(new_request))


def init_testcase_info_index():
    """已废弃，请勿执行"""
    from atp.api.mysql_manager import TestcaseInfoManager as tcim, TestsuiteInfoManager as tsim
    ts_objs = tsim.get_all_testsuites()
    ts_ids = [ts_obj.id for ts_obj in ts_objs]
    print(ts_ids)
    total = len(ts_ids)
    count = 0
    for ts_id in ts_ids:
        count += 1
        tc_objs = tcim.is_case_exists_by_testsuiteid(ts_id)
        index = 0
        for tc_obj in tc_objs:
            # print(tc_obj.id)
            tcim.update_testcase(tc_obj.id, index=index)
            index += 1
        percent = count / total * 100.0
        print("{:.1f}%".format(percent))


def init_column_for_table_api_testcase_info():
    """初始化api_testcase_info表的setup_case_list列数据"""
    to_update_rows = []
    objs = atim.get_testcases()
    for obj in objs:
        if obj.setup_case_list:
            continue
        include_str = obj.include
        if include_str:
            include_list = json_loads(include_str)
            for include in include_list:
                if 'setup_cases' in include and include['setup_cases'] and isinstance(include['setup_cases'], list):
                    setup_case_list = []
                    for case_id_str in include['setup_cases']:
                        setup_case_list.append('1-' + case_id_str)
                    to_update_rows.append(
                        {
                            'id': obj.id,
                            'setup_case_list': json_dumps(setup_case_list)
                        }
                    )
    print(json_dumps(to_update_rows))
    print(len(to_update_rows))
    x_len = len(to_update_rows)
    index = 0
    for row in to_update_rows:
        atim.update_testcase(id_=row['id'], setup_case_list=row['setup_case_list'])
        index += 1
        print(index*100.0/x_len)


def remove_var_mark(body):
    """
    去除body中带$的变量值,改为''
    """
    if isinstance(body, dict):
        for key, value in body.items():
            body[key] = remove_var_mark(value)
        return body
    elif isinstance(body, list):
        temp_list = []
        for child in body:
            temp_list.append(remove_var_mark(child))
        return temp_list
    elif isinstance(body, str):
        if body.startswith('$'):
            body = ''
        return body
    elif isinstance(body, bool):
        return body
    elif isinstance(body, int):
        return body
    elif body is None:
        return body


class ParseBodyToDetail(object):
    def __init__(self, body):
        self.detail = []
        self.body = body

    def parse_data(self, key, body, detail, index=None):
        if not index:
            index = 1

        if isinstance(body, list):
            temp1 = {
                'id': index,
                'paramName': key,
                'paramType': 'array',
                'isRequired': False,
                'children': []
            }
            index = index * 100 + 1
            for i in range(len(body)):
                self.parse_data(i, body[i], detail=temp1['children'], index=index)
                index += 1
            detail.append(temp1)

        elif isinstance(body, dict):
            temp2 = {
                'id': index,
                'paramName': key,
                'paramType': 'object',
                'isRequired': False,
                'children': []
            }
            index = index * 100 + 1
            for k in body:
                self.parse_data(k, body[k], detail=temp2['children'], index=index)
                index += 1
            detail.append(temp2)

        elif isinstance(body, str):
            temp3 = {
                'id': index,
                'paramName': key,
                'paramType': 'string',
                'paramRule': '',
                'paramDefVal': str(body),
                'isRequired': False
            }
            detail.append(temp3)

        elif isinstance(body, int):
            temp3 = {
                'id': index,
                'paramName': key,
                'paramType': 'number',
                'paramRule': '',
                'paramDefVal': str(body),
                'isRequired': False
            }
            detail.append(temp3)

        elif isinstance(body, bool):
            if body:
                body = 'true'
            else:
                body = 'false'
            temp3 = {
                'id': index,
                'paramName': key,
                'paramType': 'boolen',
                'paramRule': '',
                'paramDefVal': str(body),
                'isRequired': False
            }
            detail.append(temp3)

        elif body is None:
            temp3 = {
                'id': index,
                'paramName': key,
                'paramType': 'object',
                'paramRule': '',
                'paramDefVal': 'null',
                'isRequired': False
            }
            detail.append(temp3)

    def parse_main(self):
        id_ = 1
        if isinstance(self.body, dict):
            for key in self.body:
                self.parse_data(key, self.body[key], detail=self.detail, index=id_)
                id_ += 1
        elif isinstance(self.body, list):
            for i in range(len(self.body)):
                self.parse_data(i, self.body[i], detail=self.detail, index=id_)
                id_ += 1


@func_timer
def init_table_api_intf_default_request():
    """初始化api_intf_default_request表"""
    intf_objs = aiim.get_intfs()
    # tc_objs = atim.get_testcases()
    process_len = len(intf_objs)
    process_id = 0
    for intf_obj in intf_objs:
        print('intf_id: {}'.format(intf_obj.id))
        t1 = time.time()

        process_id += 1
        print('{:.1f}%'.format(process_id*100.0/process_len))

        if aidrm.get_request(api_intf_id=intf_obj.id):
            continue

        tc_objs = atim.get_testcases(api_intf_id=intf_obj.id)

        final_body = None
        for tc_obj in tc_objs:
            tc_request_obj = atrm.get_request(api_testcase_id=tc_obj.id)
            if not tc_request_obj or not tc_request_obj.request:
                continue

            request_dic = json_loads(tc_request_obj.request)
            try:
                if tc_obj.type == 1:
                    body = request_dic['teststeps'][0]['request']['json']
                    if not final_body:
                        final_body = body
                    else:
                        final_body = merge_request_body(final_body, body)
                elif tc_obj.type == 2:
                    body = request_dic['teststeps'][0]['request']['json']['args']
                    if not final_body:
                        final_body = body
                    else:
                        final_body = merge_request_body(final_body, body, is_list=True)
                elif tc_obj.type == 3:
                    body_str = request_dic['teststeps'][0]['request']['json']['msg']
                    body = json_loads(body_str)
                    if not final_body:
                        final_body = body
                    else:
                        final_body = merge_request_body(final_body, body)
                else:
                    continue
            except KeyError:
                print('Error!!')
                continue

        t3 = time.time()
        d_time = t3 - t1
        print("==== Finish t3, run {:.3}s ====\n".format(d_time))

        if final_body is not None:
            body = remove_var_mark(final_body)
            p = ParseBodyToDetail(body)
            p.parse_main()
            detail_str = json_dumps(p.detail)
            body_str = json_dumps(body)

            aidrm.insert_request(api_intf_id=intf_obj.id, request=body_str, request_detail=detail_str)


def _change_name_and_parent_id(module_id, module_name=None):
    """根据业务用例最后一层模块id查找系统id"""
    module_obj = bmm_bak.get_module(id=module_id)

    parent_module_id = module_obj.parent_module_id

    if not parent_module_id:
        return module_name, module_id
    else:
        if not module_name:
            module_name = module_obj.module_name
        else:
            module_name = module_obj.module_name + '_' + module_name
        print(module_name, parent_module_id)
        return _change_name_and_parent_id(parent_module_id, module_name)


def _change_base_detail(detail):
    new_detail = []
    for k, v in detail.items():
        row_dic = {
            "前置条件": "",
            "操作步骤": "",
            "预期结果": "",
            "备注": ""
        }
        if k == "预期":
            for expect in v:
                row_dic["预期结果"] = expect
        else:
            row_dic["操作步骤"] = k
            for kk, vv in v.items():
                if kk == "预期":
                    for expect in vv:
                        row_dic["预期结果"] = expect
        new_detail.append(row_dic)
    return new_detail


@func_timer
def migrate_base(step):
    """
    迁移基线用例数据
    前置条件：先把 base_testcase_info, base_module_info表数据分别导出到相应备份表，并清空 base_module_info表
    注意按顺序执行，中途报错不可继续
    """
    if step == 1:
        # migrate testcase
        bt_objs = btm.get_all_testcase()
        process_len = len(bt_objs)
        process_id = 0
        for bt_obj in bt_objs:
            process_id += 1
            print('{:.1f}%'.format(process_id * 100.0 / process_len))

            id_ = bt_obj.id
            print(id_)
            try:
                detail_dic = json_loads(bt_obj.detail)
            except Exception:
                detail_dic = {}

            if isinstance(detail_dic, list):
                continue

            new_detail_dic = _change_base_detail(detail_dic)
            btm.update_base_testcase(id_, detail=json_dumps(new_detail_dic))

    if step == 2:
        # migrate module
        bm_bak_objs = bmm_bak.get_modules()
        process_len = len(bm_bak_objs)
        process_id = 0
        for bm_bak_obj in bm_bak_objs:
            process_id += 1
            print('{:.1f}%'.format(process_id * 100.0 / process_len))

            if bm_bak_obj.system_id:
                bmm.insert_base_module(id=bm_bak_obj.id, module_name=bm_bak_obj.module_name, system_id=bm_bak_obj.system_id)
                second_bm_objs = bmm_bak.get_modules(parent_module_id=bm_bak_obj.id)
                if not second_bm_objs:
                    new_module_name = bm_bak_obj.module_name
                    bt_objs = btm.get_all_testcase(module_id=bm_bak_obj.id)
                    if bt_objs:
                        bmm.insert_base_module(module_name=new_module_name, parent_module_id=bm_bak_obj.id)
                        second_bm_obj = bmm.get_module(module_name=new_module_name, parent_module_id=bm_bak_obj.id)
                        new_module_id = second_bm_obj.id

                        for bt_obj in bt_objs:
                            btm.update_base_testcase(bt_obj.id, module_id=new_module_id)

            else:
                sub_bm_bak_objs = bmm_bak.get_modules(parent_module_id=bm_bak_obj.id)
                if sub_bm_bak_objs:
                    continue
                else:
                    new_module_name, new_parent_id = _change_name_and_parent_id(bm_bak_obj.id)
                    bmm.insert_base_module(id=bm_bak_obj.id, module_name=new_module_name, parent_module_id=new_parent_id)


def export_base_system_excel(system_id):
    """按系统id导出基线用例到excel"""
    from atp.api.excel_parser import ExcelParser

    def remove_spaces(name):
        if '\r\n' in name:
            nameList = name.split('\r\n')
            name = nameList[0] + nameList[1]
            if '/' in name:
                name = name.replace('/', '-')
            return name
        elif '/' in name:
            name = name.replace('/', '-')
            return name
        else:
            return name

    header_func = ["编号", "模块", "用例标题", "前置条件", "操作步骤", "预期结果", "执行结果", "备注"]
    value_list = []
    value_list.append(header_func)
    """查询系统名称和项目id"""
    s_obj = bsm.query_system(id=system_id)
    if not s_obj:
        return print({"code": "100", "desc": "系统不存在"})
    project_id = s_obj.project_id
    system_name = s_obj.system_name
    """处理项目名称"""
    p_obj = bpm.get_project(id=project_id)
    if not p_obj:
        return print({"code": "100", "desc": "项目不存在"})
    project_name = p_obj.project_name
    """查询系统下模块"""
    parent_module_list = bmm.get_modules(system_id=system_id)
    testcase_objs = {}
    for module_obj in parent_module_list:
        module_name = module_obj.module_name
        module_name = remove_spaces(module_name)
        sub_module_list = bmm.get_modules(parent_module_id=module_obj.id)
        module_list = [header_func]
        idx = 1
        for sub_module_obj in sub_module_list:
            sub_module_name = sub_module_obj.module_name
            case_objs = btm.get_all_testcase(module_id=sub_module_obj.id)
            for case_obj in case_objs:
                '''处理操作步骤和预期结果'''
                detail = eval(case_obj.detail)
                setup_list = []
                step_list = []
                expect_list = []
                remark_list = []
                actualResult_list = []
                for i in range(0, len(detail)):
                    setup_list.append(detail[i]["前置条件"])
                    step_list.append(detail[i]["操作步骤"])
                    expect_list.append(detail[i]["预期结果"])
                    remark_list.append(detail[i]["备注"])
                    actualResult_list.append('')
                """封装写入Excel的数据"""
                case_list = [idx, sub_module_name, case_obj.testcase_name, setup_list, step_list, expect_list,
                             actualResult_list, remark_list]
                module_list.append(case_list)
                idx += 1
        testcase_objs[module_name] = module_list

    ep = ExcelParser(project_name + '_' + system_name)
    file_name = ep.writeExcel(values=testcase_objs)
    print(file_name)


def export_all_base_to_excel():
    """导出数据库中所有基线用例到本地excel"""
    s_objs = bsm.get_total_systems()
    for s_obj in s_objs:
        export_base_system_excel(system_id=s_obj.id)


def update_git_url_to_api_system():
    """
    将git url更新到系统表api_system_info
    :return:
    """
    # 从gitlab上获取所有工程git url
    git = GitlabAPI()
    all_projects = git.get_all_projects()
    for project in all_projects:
        git_url = project
        git_system_name = project.split("/")[1].strip(".git")
        system_obj = asim.get_system(system_name=git_system_name)
        if system_obj:
            system_id = system_obj.id
            asim.update_system(system_id, git_url=git_url)
            print("系统 " + git_system_name + "更新git url " + git_url + " 成功")


@func_timer
def init_column_main_list_for_table_api_testcase_sub():
    """初始化api_testcase_sub.main_list, 可重复执行"""
    main_objs = ApiTestcaseMainManager.get_testcase_mains()
    len_main_objs = len(main_objs)
    print('总计：{}'.format(len_main_objs))
    index = 0
    for main_obj in main_objs:
        index += 1
        process = index * 100.0 / len_main_objs
        print('进度：{:.2f}%'.format(process))
        sub_list = json_loads(main_obj.sub_list)
        for sub_id in sub_list:
            sub_obj = ApiTestcaseSubManager.get_testcase_sub(id=sub_id)
            if not sub_obj:
                print('sub_obj not found, main_obj.id:{0}, sub_id:{1}'.format(main_obj.id, sub_id))
                break
            old_main_list_str = sub_obj.main_list
            if old_main_list_str:
                old_main_list = json_loads(old_main_list_str)
                if old_main_list:
                    if main_obj.id not in old_main_list:
                        old_main_list.append(main_obj.id)
                        main_list_str = json_dumps(old_main_list)
                    else:
                        continue
                else:
                    main_list_str = '[{}]'.format(main_obj.id)
            else:
                main_list_str = '[{}]'.format(main_obj.id)
            print(main_list_str)
            ApiTestcaseSubManager.update_testcase_sub(sub_id, main_list=main_list_str)


@func_timer
def merge_sub_case():
    """合并相同的sub_case, 可重复执行"""
    to_update_main_sub_list_dic = {}
    testcase_main_objs = ApiTestcaseMainManager.get_testcase_mains()
    main_sub_list_dic = {}
    for testcase_main_obj in testcase_main_objs:
        main_sub_list_dic[testcase_main_obj.id] = json_loads(testcase_main_obj.sub_list)
    redundant_requests = ApiTestcaseRequestQllManager.get_redundant_requests()
    len_redundant_requests = len(redundant_requests)
    print('总计：{}'.format(len_redundant_requests))
    index = 0
    for row in redundant_requests:
        index += 1
        process = index*100.0/len_redundant_requests
        print('进度：{:.2f}%'.format(process))
        print('开始处理：{}'.format(row[0]))
        request = row[0]
        request_objs = ApiTestcaseRequestQllManager.get_requests(request=request)
        print('重复个数：{}'.format(len(request_objs)))
        target_sub_id = request_objs[0].api_testcase_id
        for request_obj in request_objs:
            print(request_obj.api_testcase_id)
            to_update_sub_id = request_obj.api_testcase_id
            if to_update_sub_id == target_sub_id:
                continue
            else:
                for main_id in main_sub_list_dic:
                    if to_update_sub_id in main_sub_list_dic[main_id]:
                        new_sub_list = [
                            target_sub_id if i == to_update_sub_id else i for i in main_sub_list_dic[main_id]
                        ]
                        main_sub_list_dic[main_id] = copy.deepcopy(new_sub_list)
                        print(new_sub_list)
                        to_update_main_sub_list_dic[main_id] = new_sub_list

    for main_id, sub_list in to_update_main_sub_list_dic.items():
        ApiTestcaseMainManager.update_testcase_main(main_id, sub_list=json_dumps(sub_list))


@func_timer
def insert_member(batch_no, user_num):
    mobile_no_list = ['18705141272', '18705141272', '18705141272']
    app_id_list = ['13c05cabbd7e55195f32d7eff5adced3', 'd2c4017bfa3f0d0450ef2205ac9a678c', 'f0a42dfa087d66de81ab000f54951356']
    open_id_list = ['ogHLAt2vtwYF4_1RI6c-LI2CTeVQ', 'ogHLAt2RNarLSDHYIOkwJZGm_Wn0', 'ogHLAt7F7--z1xsZvgiijjk3WESk']
    time_str = get_current_time()

    if user_num >= 10000:
        times = user_num/10000
    else:
        times = 0
    tail = user_num % 10000

    for t in range(int(times)):
        insert_total_sql = ''
        for i in range(10000):
            app_id = random.choice(app_id_list)
            index = app_id_list.index(app_id)
            mobile_no = mobile_no_list[index]
            open_id = open_id_list[index]
            member_sql = "INSERT INTO `message_center_batch`.`message_target_member` (`member_id`, `mobile_no`, `app_push_id`, `open_id`, `phone_operators`, `member_name`, `credit_limit`, `user_loan_status`, `residue_limit`, `loan_limit`, `batch_no`, `create_time`, `status`) VALUES (123456, '{0}', '{1}', '{2}', '移动', '王二', '500000', '40', '100000', '400000', '{3}', '{4}', '0');".format(
                mobile_no, app_id, open_id, batch_no, time_str
            )
            insert_total_sql += member_sql
        mysql_sql_executor.sql_execute(insert_total_sql, 'ALIUAT')
    insert_total_sql = ''
    for i in range(tail):
        app_id = random.choice(app_id_list)
        index = app_id_list.index(app_id)
        mobile_no = mobile_no_list[index]
        open_id = open_id_list[index]
        member_sql = "INSERT INTO `message_center_batch`.`message_target_member` (`member_id`, `mobile_no`, `app_push_id`, `open_id`, `phone_operators`, `member_name`, `credit_limit`, `user_loan_status`, `residue_limit`, `loan_limit`, `batch_no`, `create_time`, `status`) VALUES (123456, '{0}', '{1}', '{2}', '移动', '王二', '500000', '40', '100000', '400000', '{3}', '{4}', '0');".format(
            mobile_no, app_id, open_id, batch_no, time_str
        )
        insert_total_sql += member_sql
    mysql_sql_executor.sql_execute(insert_total_sql, 'ALIUAT')


@func_timer
def insert_batch(index, user_num):
    num = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    today_str = get_current_time(time_format='%Y%m%d')
    time_str = get_current_time()
    random_6 = ''
    for _ in range(6):
        random_6 += random.choice(num)
    batch_no = 'cash' + today_str + random_6
    batch_name = '压测批次' + str(index)
    # member_batch_sql = "INSERT INTO `message_center_batch`.`message_target_member_batch` (`batch_name`, `batch_no`, `temp_table_ame`, `temp_table_sql`, `user_id`, `create_time`, `update_time`, `sync_status`) VALUES ('{0}', '{1}', '{1}', 'CREATE TABLE `message_target_member{1}`(`id` int(11) NOT NULL AUTO_INCREMENT,\n  `member_id` bigint(20) NOT NULL COMMENT \'会员号\',\n  `mobile_no` varchar(11) DEFAULT NULL COMMENT \'手机号码\',\n  `app_push_id` varchar(50) DEFAULT NULL COMMENT \'app推送ID\',\n  `open_id` varchar(50) DEFAULT NULL COMMENT \'openId\',\n  `phone_operators` varchar(5) DEFAULT NULL COMMENT \'手机营运商\',\n  `member_name` varchar(10) DEFAULT NULL COMMENT \'用户名称\',\n  `credit_limit` varchar(10) DEFAULT NULL COMMENT \'授信额度\',\n  `user_loan_status` varchar(10) DEFAULT NULL COMMENT \'用户贷款状态\',\n  `residue_limit` varchar(10) DEFAULT NULL COMMENT \'剩余额度\',\n  `loan_limit` varchar(10) DEFAULT NULL COMMENT \'在贷额度\',\n  `batch_no` varchar(18) DEFAULT NULL COMMENT \'批次号 【命名规则 固定的前缀+年月日(8位)  6固定随机数  前缀取值范围(cash:现金贷) 例如： cash20190626000001】\',\n  `create_time` datetime DEFAULT NULL,\n  `update_time` datetime DEFAULT NULL,\n  PRIMARY KEY (`id`)\n) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT=\'消息发送目标会员\';', '1', '{2}', '{2}', '3');".format(
    #     batch_name, batch_no, time_str)
    member_batch_sql = "INSERT INTO `message_center_batch`.`message_target_member_batch` (`batch_name`, `batch_no`, `temp_table_ame`, `user_id`, `create_time`, `update_time`, `sync_status`) VALUES ('{0}', '{1}', '{1}', '1', '{2}', '{2}', '3');".format(
        batch_name, batch_no, time_str)
    print(member_batch_sql)
    mysql_sql_executor.sql_execute(member_batch_sql, 'ALIUAT')

    # create_table_sql = "CREATE TABLE `message_center_batch`.`message_target_member{0}`(`id` int(11) NOT NULL AUTO_INCREMENT,\n  `member_id` bigint(20) NOT NULL COMMENT \'会员号\',\n  `mobile_no` varchar(11) DEFAULT NULL COMMENT \'手机号码\',\n  `app_push_id` varchar(50) DEFAULT NULL COMMENT \'app推送ID\',\n  `open_id` varchar(50) DEFAULT NULL COMMENT \'openId\',\n  `phone_operators` varchar(5) DEFAULT NULL COMMENT \'手机营运商\',\n  `member_name` varchar(10) DEFAULT NULL COMMENT \'用户名称\',\n  `credit_limit` varchar(10) DEFAULT NULL COMMENT \'授信额度\',\n  `user_loan_status` varchar(10) DEFAULT NULL COMMENT \'用户贷款状态\',\n  `residue_limit` varchar(10) DEFAULT NULL COMMENT \'剩余额度\',\n  `loan_limit` varchar(10) DEFAULT NULL COMMENT \'在贷额度\',\n  `batch_no` varchar(18) DEFAULT NULL COMMENT \'批次号 【命名规则 固定的前缀+年月日(8位)  6固定随机数  前缀取值范围(cash:现金贷) 例如： cash20190626000001】\',\n  `create_time` datetime DEFAULT NULL,\n  `update_time` datetime DEFAULT NULL,\n  PRIMARY KEY (`id`)\n) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT=\'消息发送目标会员\';".format(
    #     batch_no)
    # print(create_table_sql)
    # mysql_sql_executor.sql_execute(create_table_sql, 'ALIUAT')

    # # 插入member表
    # insert_member(batch_no, user_num)
    print(batch_no)


@func_timer
def repair_sub_case_public_var_error():
    import re
    variable_regexp = r"\$([\w_]+)"
    sub_objs = ApiTestcaseSubManager.get_testcase_subs()
    repair_count = 0
    for sub_obj in sub_objs:
        if not sub_obj.include or sub_obj.include in ['[]', '[{"public_variables": []}]']:
            continue
        include_list = json_loads(sub_obj.include)
        pv_id_list = include_list[0]['public_variables']
        pv_dic = {}
        for public_v_id in pv_id_list:
            pv_obj = ApiPublicVariableInfoManager.get_variable(id=public_v_id)
            pv_dic[public_v_id] = pv_obj.variable_name
        request_obj = ApiTestcaseRequestQllManager.get_request(api_testcase_id=sub_obj.id)
        new_pv_id_list = []
        if request_obj and request_obj.request:
            variables = re.findall(variable_regexp, str(request_obj.request))
            variables = list(set(variables))
            for variable_name in variables:
                for pv_id, pv_name in pv_dic.items():
                    if pv_name == variable_name:
                        new_pv_id_list.append(pv_id)
                        break
        if set(pv_id_list) != set(new_pv_id_list):
            new_pv_id_list.append(137)
            if set(pv_id_list) != set(new_pv_id_list):
                if 137 not in pv_id_list:
                    new_pv_id_list.remove(137)
                print('sub_obj.id:{2}, old:{0}, new:{1}'.format(pv_id_list, new_pv_id_list, sub_obj.id))
                new_include = [{"public_variables": new_pv_id_list}]
                include_str = json_dumps(new_include)
                print(include_str)
                ApiTestcaseSubManager.update_testcase_sub(id_=sub_obj.id, include=include_str)
                repair_count += 1

    print(repair_count)


if __name__ == '__main__':
    from atp.app import create_app
    app = create_app()
    with app.app_context():
        repair_sub_case_public_var_error()
    pass
