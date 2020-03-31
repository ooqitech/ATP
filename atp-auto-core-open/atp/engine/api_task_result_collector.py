# -*- coding:utf-8 -*-

import os
import traceback
from datetime import datetime

from atp.api.mysql_manager import (
    ApiRunTaskResultManager, CeleryTaskRecordManager, ApiTaskInfoManager, ApiTestcaseReuseRecordManager)
from atp.utils.tools import json_dumps, json_loads
from atp.config.default import Config


class TaskResultCollector(object):
    def __init__(self, summary_path_list=None, run_task_id=None):
        self.summary_path_list = summary_path_list
        self.run_task_result_id = run_task_id
        self.log_dir = None
        if self.run_task_result_id:
            run_date = format(ApiRunTaskResultManager.get_result(id=self.run_task_result_id).run_date)
            self.log_dir = '{0}{1}/task_run_{2}/'.format(Config.RUN_TASK_LOG_DIR, run_date, self.run_task_result_id)

    def save_task_results(self):
        """保存测试结果到任务运行结果表api_run_task_result和用例复用表api_testcase_reuse_record"""

        summary_list = []
        for summary_path in self.summary_path_list:
            if not summary_path or 'worker_summary_path is None' == summary_path:
                continue
            with open(summary_path, 'r') as f:
                summary_str = f.readline()
                summary_dict = json_loads(summary_str)
                summary_list.append(summary_dict)
                if not self.run_task_result_id:
                    self.run_task_result_id = summary_dict['run_task_result_id'] if 'run_task_result_id' in summary_dict else None
                if not self.log_dir:
                    self.log_dir = summary_dict['log_dir'] if 'log_dir' in summary_dict else None

        # run_task_result_id = summary_list[0]['run_task_result_id']
        # log_dir = summary_list[0]['log_dir']

        # 保存summary_list到服务器文件目录run_task_logs
        with open('{0}task_run_{1}_summary.log'.format(self.log_dir, self.run_task_result_id), 'w') as f:
            f.write(json_dumps(summary_list))

        callback_task_obj = CeleryTaskRecordManager.get_callback_celery(api_run_task_result_id=self.run_task_result_id)

        try:
            # 更新celery_task_record表的字段celery_task_status为RUNNING
            CeleryTaskRecordManager.update_celery(callback_task_obj.id, celery_task_status='RUNNING')

            total_cases = 0
            for summary in summary_list:
                total_cases += summary.pop('total_cases')

            res_obj = ApiRunTaskResultManager.get_result(id=self.run_task_result_id)
            task_obj = ApiTaskInfoManager.get_task(id=res_obj.api_task_id)

            # 获取task全部的intf_id_list
            if task_obj.task_type in (1, 3):
                task_intf_id_list = json_loads(task_obj.case_tree)['intf_id_list']
            else:
                task_intf_id_list = json_loads(task_obj.effect_intf_id_list)

            # 更新api_testcase_reuse_record表, 并获取covered_intf_id_set, run_cases, success_cases
            res_list = save_testcase_reuse_record(summary_list)

            # 本次测试包含的接口id集合
            covered_intf_id_set = res_list[0]
            # 本次运行的用例数
            run_cases = res_list[1]
            # 本次成功的用例数
            success_cases = res_list[2]
            # 本次未覆盖的接口id列表
            uncovered_intf_id_list = list(set(task_intf_id_list) ^ covered_intf_id_set)
            # 本次失败的用例数
            fail_cases = run_cases - success_cases
            # 本次未运行的用例数
            not_run_cases = total_cases - run_cases

            # 更新api_run_task_result表
            ApiRunTaskResultManager.update_result(
                self.run_task_result_id, total_cases=total_cases,
                not_run_cases=not_run_cases, run_cases=run_cases, success_cases=success_cases, fail_cases=fail_cases,
                end_time=datetime.now(), covered_intf_id_list=json_dumps(list(covered_intf_id_set)),
                uncovered_intf_id_list=json_dumps(uncovered_intf_id_list)
            )

            # 更新celery_task_record表的字段celery_task_status为SUCCESS
            CeleryTaskRecordManager.update_celery(callback_task_obj.id, celery_task_status='SUCCESS')

        except Exception as err:
            # 更新api_run_task_result表
            ApiRunTaskResultManager.update_result(self.run_task_result_id, end_time=datetime.now())
            # 更新celery_task_record表的字段celery_task_status为ERROR
            CeleryTaskRecordManager.update_celery(callback_task_obj.id, celery_task_status='ERROR')
            print('\n'.join([str(err), traceback.format_exc()]))
            raise Exception(err)

    def re_save_task_results(self):
        if not self.summary_path_list:
            if os.path.isdir(self.log_dir):
                items = os.listdir(self.log_dir)
                self.summary_path_list = [self.log_dir + item for item in items if item.endswith('.summary')]

        if self.summary_path_list:
            self.save_task_results()
            return 0, '重新收集结果成功'
        else:
            return 1, '失败, summary_path_list为空'


def save_testcase_reuse_record(summary_list):
    """根据summary_list记录用例复用表，获取覆盖的接口列表、运行的用例数，成功的用例数"""
    today_date = datetime.date(datetime.now())
    # 本次测试包含的接口id集合
    covered_intf_id_set = set()
    # 本次运行的用例数
    run_cases = 0
    # 本次成功的用例数
    success_cases = 0

    for summary in summary_list:
        if 'summary' not in summary:
            continue
        # covered_intf_id_list.append(summary['summary']['details'][0]['intf_id'])
        run_cases += summary['summary']['stat']['testsRun']
        for detail_dic in summary['summary']['details']:
            is_case_success = False
            if detail_dic['stat']['testsRun'] == detail_dic['stat']['successes']:
                success_cases += 1
                is_case_success = True
            # 更新api_testcase_reuse_record表
            testcase_id = detail_dic['case_id']
            is_main = detail_dic['is_main']
            # 根据is_main判断是否全链路用例
            if is_main:
                been_setup_testcase_id = 0
                reuse_obj = ApiTestcaseReuseRecordManager.get_record(
                    record_date=today_date, api_testcase_main_id=testcase_id, is_setup=0,
                    been_setup_testcase_id=been_setup_testcase_id
                )
                plus_success_times = 1 if is_case_success else 0
                plus_fail_times = 0 if is_case_success else 1
                if not reuse_obj:
                    ApiTestcaseReuseRecordManager.insert_record(
                        record_date=today_date, api_testcase_main_id=testcase_id, total_times=1,
                        success_times=plus_success_times, fail_times=plus_fail_times, is_setup=0,
                        been_setup_testcase_id=been_setup_testcase_id
                    )
                else:
                    ApiTestcaseReuseRecordManager.update_record(
                        reuse_obj.id,
                        total_times=reuse_obj.total_times + 1,
                        success_times=reuse_obj.success_times + plus_success_times,
                        fail_times=reuse_obj.fail_times + plus_fail_times
                    )
            else:
                covered_intf_id_set.add(detail_dic['intf_id'])
                last_step_main_i = 1
                for record_dic in detail_dic['records']:
                    is_step_success = True if record_dic['status'] == 'success' else False
                    plus_success_times = 1 if is_step_success else 0
                    plus_fail_times = 0 if is_step_success else 1
                    step_case_id = record_dic['case_id']
                    # 根据step_case_id是int还是str判断是接口用例还是全链路用例的步骤
                    if isinstance(step_case_id, int):
                        # 是否为前置用例，0否，1是
                        is_setup = 0 if step_case_id == testcase_id else 1
                        been_setup_testcase_id = testcase_id if is_setup else 0

                        reuse_obj = ApiTestcaseReuseRecordManager.get_record(
                            record_date=today_date, api_testcase_id=step_case_id, is_setup=is_setup,
                            been_setup_testcase_id=been_setup_testcase_id
                        )
                        if not reuse_obj:
                            ApiTestcaseReuseRecordManager.insert_record(
                                record_date=today_date, api_testcase_id=step_case_id, total_times=1,
                                success_times=plus_success_times, fail_times=plus_fail_times, is_setup=is_setup,
                                been_setup_testcase_id=been_setup_testcase_id
                            )
                        else:
                            ApiTestcaseReuseRecordManager.update_record(
                                reuse_obj.id,
                                total_times=reuse_obj.total_times + 1,
                                success_times=reuse_obj.success_times + plus_success_times,
                                fail_times=reuse_obj.fail_times + plus_fail_times
                            )
                    else:
                        step_main_case_id, step_main_i = [int(x) for x in str(step_case_id).split('-', maxsplit=1)]
                        if step_main_i > last_step_main_i:
                            continue
                        is_setup = 1
                        been_setup_testcase_id = testcase_id
                        reuse_obj = ApiTestcaseReuseRecordManager.get_record(
                            record_date=today_date, api_testcase_main_id=step_main_case_id, is_setup=is_setup,
                            been_setup_testcase_id=been_setup_testcase_id
                        )
                        if not reuse_obj:
                            ApiTestcaseReuseRecordManager.insert_record(
                                record_date=today_date, api_testcase_main_id=step_main_case_id, total_times=1,
                                success_times=plus_success_times, fail_times=plus_fail_times, is_setup=is_setup,
                                been_setup_testcase_id=been_setup_testcase_id
                            )
                        else:
                            ApiTestcaseReuseRecordManager.update_record(
                                reuse_obj.id,
                                total_times=reuse_obj.total_times + 1,
                                success_times=reuse_obj.success_times + plus_success_times,
                                fail_times=reuse_obj.fail_times + plus_fail_times
                            )
                        last_step_main_i = step_main_i

    return covered_intf_id_set, run_cases, success_cases
