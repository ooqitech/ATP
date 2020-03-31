# -*- coding:utf-8 -*-

import json

from datetime import datetime

from atp.api.excel_parser import ExcelParser
from atp.api.mysql_manager import (
    ApiTestcaseInfoManager, ApiTestcaseRequestManager, ApiTestcaseTagRelationManager, UserManager,
    ApiProjectIntfRelationManager, ApiTestcaseReuseRecordManager)
from atp.utils.tools import get_current_time
from atp.views.wrappers import custom_func_wrapper


@custom_func_wrapper
def get_testcases_by_create_time(create_time):
    return ApiTestcaseInfoManager.get_recent_testcases_by_time(create_time)


@custom_func_wrapper
def get_testcases_by_create_time_not_belong_project(create_time):
    res = ApiProjectIntfRelationManager.get_distinct_intf_ids()
    intf_id_list = [row[0] for row in res]
    # print(intf_id_list)
    return ApiTestcaseInfoManager.get_recent_testcases_by_time_not_belong_project(create_time, intf_id_list)


def check_validate(testcase_id):
    r_obj = ApiTestcaseRequestManager.get_request(api_testcase_id=testcase_id)
    request_dic = json.loads(r_obj.request)
    validate = request_dic["teststeps"][0]["validate"]
    if validate:
        has_validate = '是'
    else:
        has_validate = '否'
    return has_validate


def check_tag(testcase_id):
    r_objs = ApiTestcaseTagRelationManager.get_relations(api_testcase_id=testcase_id)
    is_auto = '是'
    for r_obj in r_objs:
        if r_obj.tag_id == 10:
            # 去除构造数据tag的用例
            return
        if r_obj.tag_id == 13:
            is_auto = '否'
            continue
    return is_auto


def get_record_summary(testcase_id, start_date):
    res = ApiTestcaseReuseRecordManager.get_recent_summary(testcase_id, start_date)
    if res:
        return res[0] if res[0] else 0, res[1] if res[1] else 0
    return 0, 0


def calc_success_rate(total, success):
    if total == 0:
        return ''
    if total == success:
        return '100%'
    return '{}%'.format(int(success * 100 / total))


def get_duration(create_time, last_modify_time):
    if last_modify_time:
        last_time = last_modify_time
    else:
        last_time = create_time

    today = get_current_time(time_format='%Y-%m-%d')
    d1_list = [int(i) for i in today.split('-')]
    d1 = datetime(d1_list[0], d1_list[1], d1_list[2])
    d2_list = [int(i) for i in format(last_time).split(' ')[0].split('-')]
    d2 = datetime(d2_list[0], d2_list[1], d2_list[2])
    return (d1 - d2).days


@custom_func_wrapper
def export_by_time(start_time):
    user_res = UserManager.get_all_username_nickname()
    user_map = {row[0]: row[1] for row in user_res}

    def get_nickname(username):
        if username in user_map:
            return user_map[username]
        else:
            return username

    res = get_testcases_by_create_time(start_time)
    value_lists = [[
        '项目',
        '归属系统',
        '测试用例ID',
        '创建时间',
        '最后修改时间',
        '创建人',
        '最后修改人',
        '是否包含断言',
        '是否可自动化',
        '问题持续天数',
        '运行总次数',
        '运行成功次数',
        '运行成功率'
    ]]
    filtered_case_map = {}
    # 按项目id过滤掉重复的用例，只保留在最近项目存在的用例记录
    for row in res:
        if row[2] not in filtered_case_map:
            filtered_case_map[row[2]] = row[7]
        else:
            if row[7] > filtered_case_map[row[2]]:
                filtered_case_map[row[2]] = row[7]
    for row in res:
        testcase_id = row[2]
        if filtered_case_map[testcase_id] != row[7]:
            continue
        # 检查用例是否可自动化
        is_auto = check_tag(testcase_id)
        if not is_auto:
            continue
        # 检查用例是否有断言
        has_validate = check_validate(testcase_id)

        # 获取问题持续时间
        duration = ''
        if is_auto == '否' or has_validate == '否':
            duration = get_duration(row[3], row[4])

        # 获取指定时间内运行总次数和成功次数
        total, success = get_record_summary(testcase_id, start_time)

        value_lists.append(
            [
                row[0],
                row[1],
                testcase_id,
                row[3],
                row[4],
                get_nickname(row[5]),
                get_nickname(row[6]),
                has_validate,
                is_auto,
                duration,
                total,
                success,
                calc_success_rate(total, success)
            ]
        )

    # 未归属到项目的用例
    res = get_testcases_by_create_time_not_belong_project(start_time)
    for row in res:
        testcase_id = row[1]

        # 检查用例是否可自动化
        is_auto = check_tag(testcase_id)
        if not is_auto:
            continue

        # 检查用例是否有断言
        has_validate = check_validate(testcase_id)

        # 获取问题持续时间
        duration = ''
        if is_auto == '否' or has_validate == '否':
            duration = get_duration(row[2], row[3])

        # 获取指定时间内运行总次数和成功次数
        total, success = get_record_summary(testcase_id, start_time)

        value_lists.append(
            [
                '',
                row[0],
                testcase_id,
                row[2],
                row[3],
                get_nickname(row[4]),
                get_nickname(row[5]),
                has_validate,
                is_auto,
                duration,
                total,
                success,
                calc_success_rate(total, success)
            ]
        )
    # 写入excel
    ep = ExcelParser(start_time)
    excel_name = ep.write_export_to_excel(start_time=start_time, value_lists=value_lists)
    print(excel_name)
    return excel_name


if __name__ == '__main__':
    from atp.app import create_app
    app = create_app()
    with app.app_context():
        create_time = '2019-09-01'
        export_by_time(create_time)
        pass
