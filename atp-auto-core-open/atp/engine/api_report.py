# -*- coding:utf-8 -*-

import datetime

from atp.api.comm_log import logger
from atp.api.mysql_manager import (
    ApiTestReportManager as arm, ApiTestcaseInfoManager as atim,
    ApiTestcaseMainManager as atmm
)
from atp.utils.tools import get_current_time


def perfect_summary(summary, test_meta_list):
    # summary['stat']['successes'] = 996
    intf_id = test_meta_list.pop(0)['intf_id']
    step_list = []
    for testcase in test_meta_list:
        step_list.extend(testcase['step'])

    # print('step_list:{}'.format(step_list))

    # assert len(step_list) == len(summary['details'][0]['records'])
    assert len(step_list) == len(summary['details'])

    # for step in summary['details'][0]['records']:
    #     step_meta = step_list.pop(0)
    #     step['testcase_name'] = step_meta['testcase_name']
    #     if 'error_detail' in step_meta:
    #         pass

    for step in summary['details']:
        step['intf_id'] = intf_id
        for casename in step_list:
            step["records"][0]['testcase_name'] = casename['testcase_name']


def save_report(report_path, runner_summary, project_id, report_id=None, is_main=False):
    """保存测试报告"""
    # 没有report_path，代表运行以非正常状态结束，未生成测试报告
    if not report_path:
        status = 'error'
        if report_id:
            arm.update_report(report_id, status=status)
            for detail in runner_summary['details']:
                is_success = 0 if detail['stat']['failures'] == 0 else 1
                if is_main:
                    atmm.update_testcase_main(detail['case_id'], last_run=is_success)
                else:
                    atim.update_testcase(detail['case_id'], last_run=is_success)
        return

    # start_at = datetime.datetime.strftime(runner_summary['time']['start_at'], '%Y-%m-%d %H:%M:%S')
    start_at = (runner_summary['time']['start_at'])
    duration = '{:.2f}'.format(runner_summary['time']['duration'])
    status = 'fail' if runner_summary['stat']['failures'] else 'success'
    # report = str(runner_summary)
    report = ''

    if report_id:
        # 异步运行，已有测试报告id
        arm.update_report(report_id, start_at=start_at, duration=duration, status=status, run_type='0', report=report,
                          url=report_path, api_project_id=project_id)
    else:
        # 同步运行，无测试报告id
        arm.insert_report(start_at=start_at, duration=duration, status=status, run_type='0', report=report,
                          url=report_path, api_project_id=project_id)


def save_last_run(summary, is_main=False):
    for detail in summary['details']:
        is_success = 0 if detail['stat']['failures'] == 0 else 1
        if is_main:
            atmm.update_testcase_main(detail['case_id'], last_run=is_success, last_run_time=get_current_time())
        else:
            atim.update_testcase(detail['case_id'], last_run=is_success, last_run_time=get_current_time())
