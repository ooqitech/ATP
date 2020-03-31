# -*- coding:utf-8 -*-

import json
import os
import platform
import time
import traceback

from celery import chord, group
from datetime import datetime
from copy import deepcopy

from atp.api.comm_log import logger
from atp.engine.api_chain import smart_filter_testcase, get_testcase_id_list_filter_by_tag, get_table_data
from atp.engine.api_load_test import ApiTestLoader
from atp.engine.api_report import perfect_summary
from atp.engine.celery_tasks import celery_collect_results, celery_run_single_intf_or_single_main_case, celery_run_debug, \
    celery_run_main_case_list
from atp.httprunner import HttpRunner, logger as hr_logger
from atp.api.mysql_manager import (
    ApiTestcaseInfoManager, ApiRunTaskResultManager, ApiTaskInfoManager, CeleryTaskRecordManager,
    ApiTestcaseReuseRecordManager, ApiTestcaseMainManager,
    ApiIntfInfoManager, ApiSystemInfoManager, ApiProductLineManager, GenerateDataRecordManager)
from atp.config.default import get_config
from atp.utils.common import read_custom
from atp.utils.tools import json_loads, json_dumps

config = get_config()
custom = read_custom()


class ApiRunner(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.env_id = self.kwargs.get('env_id', None)
        self.env_name = self.kwargs.get('env_name', None)
        self.executor = self.kwargs.get('executor', None)
        self.times = int(self.kwargs.get('times', 1))
        self.times = 100 if 100 < self.times else self.times
        self.run_main_case_in_parallel = self.kwargs.get('run_main_case_in_parallel', 0)
        self.reboot_sleep = self.kwargs.get('reboot_sleep', 0)

        self.testset = None
        self.test_meta_list = None
        self.run_task_result_id = None
        self.task_obj = None
        self.run_task_log_dir = None
        self.run_debug_log_dir = None
        self.table_data = get_table_data()

    def __del__(self):
        pass

    def load_test(self, testcase_id_list=None, testcase_main_id_list=None):
        """加载testset"""
        kwargs = {
            "env_id": self.env_id,
            "testcase_id_list": testcase_id_list,
            "testcase_main_id_list": testcase_main_id_list,
        }
        api_loader = ApiTestLoader(**kwargs)
        self.testset = api_loader.get_testset_list()
        self.test_meta_list = api_loader.get_test_meta_list()

    def set_run_task_log_dir(self):
        base_run_task_log_dir = config.RUN_TASK_LOG_DIR
        today_str = datetime.now().strftime('%Y-%m-%d')
        if platform.system() == 'Windows':
            self.run_task_log_dir = '{0}{1}\\task_run_{2}\\'.format(
                base_run_task_log_dir, today_str, self.run_task_result_id)
        else:
            self.run_task_log_dir = '{0}{1}/task_run_{2}/'.format(
                base_run_task_log_dir, today_str, self.run_task_result_id)

        if not os.path.exists(self.run_task_log_dir):
            os.makedirs(self.run_task_log_dir)

    def set_run_debug_log_dir(self):
        base_run_debug_log_dir = config.RUN_CASE_LOG_DIR
        today_str = datetime.now().strftime('%Y-%m-%d')
        if platform.system() == 'Windows':
            self.run_debug_log_dir = '{0}{1}\\'.format(
                base_run_debug_log_dir, today_str, self.run_task_result_id)
        else:
            self.run_debug_log_dir = '{0}{1}/'.format(
                base_run_debug_log_dir, today_str, self.run_task_result_id)

        if not os.path.exists(self.run_debug_log_dir):
            os.makedirs(self.run_debug_log_dir)

    def get_task_obj(self, task_id):
        """获取回归测试任务详细内容"""
        self.task_obj = ApiTaskInfoManager.get_task(id=task_id)

    def set_run_task_result(self, task_id):
        """写入回归任务运行记录"""
        self.run_task_result_id = ApiRunTaskResultManager.get_next_result_id()
        start_time = datetime.now()
        ApiRunTaskResultManager.insert_result(
            id=self.run_task_result_id, api_task_id=task_id, creator=self.executor, start_time=start_time,
            run_env_id=self.env_id, run_main_case_in_parallel=self.run_main_case_in_parallel)

        self.set_run_task_log_dir()

    def get_testcase_id_list_filter_by_tag(self, intf_id=None, product_line_id=None):
        """ 根据任务配置的测试标签，过滤接口用例和全链路用例"""
        try:
            related_tag_id_list = json_loads(self.task_obj.related_tag_id_list)
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

    def run_task(self, task_id):
        """运行回归测试任务"""

        # 获取回归测试任务详细内容
        self.get_task_obj(task_id)

        # celery_no_list = []
        # total_cases = 0

        # 获取待测试的接口id列表
        to_run_intf_id_list = []
        product_line_id_list = []
        if self.task_obj.task_type in (1, 3):
            to_run_dic = json_loads(self.task_obj.case_tree)
            to_run_intf_id_list = to_run_dic.get('intf_id_list', [])
            # to_run_testcase_main_id_list = to_run_dic.get('testcase_main_id_list', [])
            product_line_id_list = to_run_dic.get('product_line_id_list', [])

        elif self.task_obj.task_type == 2:
            to_run_intf_id_list = json_loads(self.task_obj.effect_intf_id_list)

        # 待测试列表为空
        if not isinstance(to_run_intf_id_list, list) or not isinstance(product_line_id_list, list) or \
                (not to_run_intf_id_list and not product_line_id_list):
            # if self.run_task_result_id:
            #     ApiRunTaskResultManager.delete_result(self.run_task_result_id)
            return None

        # 接口用例智能去重
        intf_testcase_map = {}
        for intf_id in to_run_intf_id_list:
            testcase_id_list = self.get_testcase_id_list_filter_by_tag(intf_id=intf_id)
            if testcase_id_list:
                intf_testcase_map[intf_id] = testcase_id_list

        if not intf_testcase_map:
            # 如果没有可运行的用例，直接返回
            return None
        filtered_intf_testcases_map = smart_filter_testcase(intf_testcase_map, self.table_data)

        # 写入回归测试任务记录表
        self.set_run_task_result(task_id)

        # 拆分测试任务
        header = []
        countdown = self.reboot_sleep if self.reboot_sleep else 1
        print(countdown)

        # 拆分全链路测试用例
        if self.run_main_case_in_parallel:
            # 每条全链路用例分配一个worker
            timed_to_run_product_line_id_list = []
            for _ in range(self.times):  # 循环次数
                timed_to_run_product_line_id_list.extend(product_line_id_list)
            for product_line_id in timed_to_run_product_line_id_list:
                testcase_main_id_list = self.get_testcase_id_list_filter_by_tag(product_line_id=product_line_id)
                for testcase_main_id in testcase_main_id_list:
                    header.append(
                        celery_run_single_intf_or_single_main_case.signature(
                            (self.run_task_result_id, self.env_id, testcase_main_id, False, self.run_task_log_dir),
                            countdown=countdown
                        )
                    )
                    countdown = self.get_next_countdown(countdown)
                    print(countdown)
        else:
            # 每个最末产品线分配一个worker
            for product_line_id in product_line_id_list:
                testcase_main_id_list = self.get_testcase_id_list_filter_by_tag(product_line_id=product_line_id)
                if testcase_main_id_list:
                    timed_testcase_main_id_list = []
                    for _ in range(self.times):  # 循环次数
                        timed_testcase_main_id_list.extend(testcase_main_id_list)
                    header.append(
                        celery_run_main_case_list.signature(
                            (self.run_task_result_id, self.env_id, timed_testcase_main_id_list, self.run_task_log_dir),
                            countdown=countdown
                        )
                    )
                    countdown = self.get_next_countdown(countdown)
                    print(countdown)

        # 拆分接口测试用例 -- 每个接口分配一个worker
        for intf_id, testcase_id_list in filtered_intf_testcases_map.items():
            if testcase_id_list:
                timed_testcase_id_list = []
                for _ in range(self.times):  # 循环次数
                    timed_testcase_id_list.extend(testcase_id_list)
                header.append(
                    celery_run_single_intf_or_single_main_case.signature(
                        (self.run_task_result_id, self.env_id, intf_id, True, self.run_task_log_dir,
                         timed_testcase_id_list),
                        countdown=countdown
                    )
                )
                countdown = self.get_next_countdown(countdown)
                print(countdown)

        # worker_num = len(header)
        # logger.info('本次运行总共需要的worker数量: {}'.format(worker_num))
        # # time.sleep(3)
        # # 分配异步测试任务, 增加回调任务收集测试结果
        # callback = celery_collect_results.s()
        # chord_result = chord(header)(callback)
        # callback_celery_no = chord_result.id
        #
        # # 更新api_run_task_result表，本次运行总共需要的worker数量
        # ApiRunTaskResultManager.update_result(id_=self.run_task_result_id, worker_num=worker_num)
        # # 写入celery任务表
        # CeleryTaskRecordManager.insert_celery(celery_task_no=callback_celery_no, celery_task_status='WAITING',
        #                                       api_run_task_result_id=self.run_task_result_id)
        #
        # return callback_celery_no

        # 分配异步测试任务, 增加回调任务收集测试结果
        callback_celery_no = self._assign_celery_tasks(header)
        return callback_celery_no

    def run_task_failed_retry(self, task_id, failed_intf_dic, failed_full_dic):
        """回归测试任务运行失败的用例重新运行"""

        # 获取回归测试任务详细内容
        self.get_task_obj(task_id)

        # 写入回归测试任务记录表
        self.set_run_task_result(task_id)

        # 拆分测试任务
        header = []
        countdown = self.reboot_sleep if self.reboot_sleep else 1
        print(countdown)

        # 拆分全链路测试用例
        if self.run_main_case_in_parallel:
            # 每条全链路用例分配一个worker
            for testcase_main_id_list in failed_full_dic.values():
                for testcase_main_id in testcase_main_id_list:
                    header.append(
                        celery_run_single_intf_or_single_main_case.signature(
                            (self.run_task_result_id, self.env_id, testcase_main_id, False, self.run_task_log_dir),
                            countdown=countdown
                        )
                    )
                    countdown = self.get_next_countdown(countdown)

        else:
            # 每个最末产品线分配一个worker
            for testcase_main_id_list in failed_full_dic.values():
                if testcase_main_id_list:
                    header.append(
                        celery_run_main_case_list.signature(
                            (self.run_task_result_id, self.env_id, testcase_main_id_list, self.run_task_log_dir),
                            countdown=countdown
                        )
                    )
                    countdown = self.get_next_countdown(countdown)

        # 拆分接口测试用例 -- 每个接口分配一个worker
        for intf_id, testcase_id_list in failed_intf_dic.items():
            if testcase_id_list:
                header.append(
                    celery_run_single_intf_or_single_main_case.signature(
                        (self.run_task_result_id, self.env_id, intf_id, True, self.run_task_log_dir, testcase_id_list),
                        countdown=countdown
                    )
                )
                countdown = self.get_next_countdown(countdown)

        # 分配异步测试任务, 增加回调任务收集测试结果
        callback_celery_no = self._assign_celery_tasks(header)
        return callback_celery_no

    def _assign_celery_tasks(self, header):
        """分配异步测试任务, 增加回调任务收集测试结果"""
        worker_num = len(header)
        logger.info('本次运行总共需要的worker数量: {}'.format(worker_num))

        callback = celery_collect_results.s()
        chord_result = chord(header)(callback)
        callback_celery_no = chord_result.id

        # 更新api_run_task_result表，本次运行总共需要的worker数量
        ApiRunTaskResultManager.update_result(id_=self.run_task_result_id, worker_num=worker_num)
        # 写入celery任务表
        CeleryTaskRecordManager.insert_celery(celery_task_no=callback_celery_no, celery_task_status='WAITING',
                                              api_run_task_result_id=self.run_task_result_id)
        return callback_celery_no

    def run_debug(self, **kwargs):
        self.set_run_debug_log_dir()
        kwargs.update({'log_dir': self.run_debug_log_dir})
        celery_run_debug.apply_async(kwargs=kwargs)

    def get_next_countdown(self, countdown):
        if 20 <= (countdown - self.reboot_sleep):
            return 1
        else:
            return countdown + 1


def get_full_product_line_name(p_obj, tail_name=''):
    """获取全链路用例完整节点信息"""
    full_product_line_name = '{0} -> {1}'.format(p_obj.product_line_name, tail_name)
    if not p_obj.parent_id:
        return full_product_line_name.strip(' ->')
    else:
        parent_p_obj = ApiProductLineManager.get_product_line(id=p_obj.parent_id)
        return get_full_product_line_name(parent_p_obj, tail_name=full_product_line_name)


def add_memo(summary):
    """增加一些备注，并且记录生成的公共变量"""

    details = summary['details']
    for detail_dic in details:
        # 每条用例
        in_out = detail_dic.pop('in_out', None)
        # 全链路用例增加信息
        if detail_dic['is_main']:
            case_id = 'M' + str(detail_dic['case_id'])
            if 'testcase_main_id' not in summary:
                # summary['testcase_main_id'] = detail_dic['case_id']
                testcase_main_obj = ApiTestcaseMainManager.get_testcase_main(id=detail_dic['case_id'])
                # summary['testcase_main_name'] = testcase_main_obj.testcase_name
                p_obj = ApiProductLineManager.get_product_line(id=testcase_main_obj.api_product_line_id)
                summary['product_line_id'] = p_obj.id
                summary['product_line_name'] = get_full_product_line_name(p_obj)
        # 接口用例增加信息
        else:
            case_id = str(detail_dic['case_id'])
            if 'intf_id' not in summary:
                summary['intf_id'] = detail_dic['intf_id']
                intf_obj = ApiIntfInfoManager.get_intf(id=detail_dic['intf_id'])
                summary['intf_name'] = '{0}-{1}'.format(intf_obj.intf_desc, intf_obj.intf_name)
                system_obj = ApiSystemInfoManager.get_system(id=intf_obj.api_system_id)
                summary['system_id'] = system_obj.id
                summary['system_name'] = system_obj.system_name
        # 记录随机生成的数据，方便追溯和定时清理数据
        if in_out:
            record_keys = ['MOBILE_NO', 'ID_NO', 'BANK_CARD_NO_CREDIT', 'BANK_CARD_NO_DEBIT']
            mobile_no, id_no, bank_card_no_credit, bank_card_no_debit = '', '', '', ''
            is_found = False
            for var, var_value in in_out['in'].items():
                for key in record_keys:
                    if key == var:
                        is_found = True
                        if var == 'MOBILE_NO':
                            mobile_no = var_value
                        elif var == 'ID_NO':
                            id_no = var_value
                        elif var == 'BANK_CARD_NO_CREDIT':
                            bank_card_no_credit = var_value
                        elif var == 'BANK_CARD_NO_DEBIT':
                            bank_card_no_debit = var_value
                        break
            if is_found:
                GenerateDataRecordManager.insert_record(
                    case_id=case_id, mobile_no=mobile_no, id_no=id_no, bank_card_no_credit=bank_card_no_credit,
                    bank_card_no_debit=bank_card_no_debit)

    return summary


def identify_errors(summary):
    """识别错误, 更新case_id和error_type到每个record"""
    error_map = {
        '环境问题': {
            'Http 404': [
                'Failed to establish a new connection: [Errno 111] Connection refused'
            ],
            'Http 502': [
                '502 Bad Gateway'
            ],
            'Dubbo请求应用前报错': [
                ['远程服务返回失败', '"remoteResponseCode": "101"']
            ],
            'Dubbo请求应用后报错': [
                ['应用服务返回失败', '"remoteResponseCode": "201"']
            ]
        },
        '用例问题': {
            '提取变量错误': [
                'httprunner.exceptions.ExtractFailure: Failed to extract'
            ],
            '变量未找到': [
                'httprunner.exceptions.VariableNotFound:'
            ],
        },
        '框架报错': {},
        '断言失败': {
            '断言报错': [
                'atp.httprunner.exceptions.ValidationFailure'
            ],
        },
        '前后置失败': {
            '前置步骤报错': [
                'atp.httprunner.exceptions.SetupHooksFailure'
            ],
            '后置步骤报错': [
                'atp.httprunner.exceptions.TeardownHooksFailure'
            ],
        }
    }
    details = summary['details']
    summary['stat'] = {
            'testsRun': 0, 'failures': 0, "errors": 0, 'skipped': 0, 'successes': 0
        }
    for detail_dic in details:
        detail_dic['stat'] = {
            'testsRun': 1, 'failures': 0, "errors": 0, 'skipped': 0, 'successes': 0
        }
        case_success = True
        chain_list = detail_dic['chain_list']
        records = detail_dic['records']
        for i in range(len(records)):
            # 每个子用例
            records[i].update(
                {
                    'case_id': chain_list[i],
                    'error_type': ''
                }
            )
            step_success = True

            # 处理attachment中的错误
            if records[i]['attachment']:
                step_success = False
                records[i]['status'] = 'fail'
                # 已知的attachment错误，识别为具体错误
                found_error = False
                for error_type, sub_error_dic in error_map.items():
                    if found_error:
                        break
                    for sub_error, error_kw_list in sub_error_dic.items():
                        if found_error:
                            break
                        for error_kw in error_kw_list:
                            if isinstance(error_kw, list):
                                all_found = True
                                for kw in error_kw:
                                    if kw not in records[i]['attachment']:
                                        all_found = False
                                        break
                                if all_found:
                                    records[i]['error_type'] = error_type
                                    records[i]['attachment'] = sub_error + ' -- ' + records[i]['attachment']
                                    found_error = True
                                    break
                            else:
                                if error_kw in records[i]['attachment']:
                                    records[i]['error_type'] = error_type
                                    records[i]['attachment'] = sub_error + ' -- ' + records[i]['attachment']
                                    found_error = True
                                    break
                # 未知的attachment错误, 识别为框架报错
                if not records[i]['error_type']:
                    records[i]['error_type'] = '框架报错'

            # 处理断言错误
            else:
                for validator_dic in records[i]['meta_data']['validators']:
                    if validator_dic['check_result'] != 'pass':
                        step_success = False
                        records[i]['status'] = 'fail'
                        if isinstance(validator_dic['check_value'], dict):
                            actual_str = json_dumps(validator_dic['check_value'])
                        else:
                            actual_str = str(validator_dic['check_value'])

                        found_error = False
                        # 已知的断言错误，识别为具体错误
                        for error_type, sub_error_dic in error_map.items():
                            if found_error:
                                break
                            for sub_error, error_kw_list in sub_error_dic.items():
                                if found_error:
                                    break
                                for error_kw in error_kw_list:
                                    if isinstance(error_kw, list):
                                        all_found = True
                                        for kw in error_kw:
                                            if kw not in actual_str:
                                                all_found = False
                                                break
                                        if all_found:
                                            records[i]['error_type'] = error_type
                                            records[i]['attachment'] = sub_error + ' -- ' + actual_str
                                            found_error = True
                                            break
                                    else:
                                        if error_kw in actual_str:
                                            records[i]['error_type'] = error_type
                                            records[i]['attachment'] = sub_error + ' -- ' + actual_str
                                            found_error = True
                                            break
                        if found_error:
                            break
                        # 未知的断言错误, 识别为断言失败
                        if not records[i]['error_type']:
                            records[i]['error_type'] = '断言失败'
                            records[i]['attachment'] = '断言失败 -- 校验方法: {0}, 校验内容: {1}, 预期结果: {2}, 实际结果: {3}'.format(
                                get_validator_desc(validator_dic['comparator']), validator_dic['check'],
                                validator_dic['expect'], actual_str
                            )
                            break

            # 如果有子用例失败，则用例失败
            if not step_success:
                case_success = False

        # 用例成功或失败的数据累加
        if case_success:
            detail_dic['stat']['successes'] = 1
            summary['stat']['testsRun'] += 1
            summary['stat']['successes'] += 1
        else:
            detail_dic['stat']['failures'] = 1
            summary['stat']['testsRun'] += 1
            summary['stat']['failures'] += 1

    return summary


def http_runner_run(**kwargs):
    """调用HttpRunner运行测试"""
    log_dir = kwargs.pop('log_dir')
    env_id = kwargs.pop('env_id')
    testset = kwargs.pop('testset')
    test_meta_list = kwargs.pop('test_meta_list')
    run_task_result_id = kwargs.pop('run_task_result_id')
    intf_id = kwargs.pop('intf_id', None)
    main_case_id = kwargs.pop('main_case_id', None)
    main_case_id_list = kwargs.pop('main_case_id_list', None)

    if intf_id:
        log_path = '{0}task_run_{1}_intf_{2}.log'.format(log_dir, run_task_result_id, intf_id)
    elif main_case_id:
        log_path = '{0}task_run_{1}_main_case_{2}.log'.format(log_dir, run_task_result_id, main_case_id)
    else:
        log_path = '{0}task_run_{1}_main_case_list_{2}.log'.format(log_dir, run_task_result_id, main_case_id_list)

    # 初始化hr_runner
    hr_kwargs = {
        "failfast": True,
        "log_path": log_path
    }
    hr_runner = HttpRunner(**hr_kwargs)

    start_time = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
    hr_logger.log_warning("【START】测试开始! (ง •_•)ง")
    hr_logger.log_warning("【环境】: {}".format(env_id))
    # time.sleep(3)
    try:
        testset_json = json_dumps(testset)
    except Exception:
        testset_json = testset

    # 执行测试
    try:
        # hr_logger.log_warning("【调用HttpRunner】: {0}".format(testset_json))
        hr_runner.run(testset)
        hr_logger.log_info("【结束调用HttpRunner】")
    except Exception:
        raise Exception(traceback.format_exc())

    for detail in hr_runner.summary["details"]:
        for record in detail["records"]:
            record["meta_data"]["request"].pop("files", None)

    # 去除summary中的文件对象
    summary_remove_file_obj(hr_runner.summary)

    # 完善summary
    summary = deepcopy(hr_runner.summary)
    # summary = hr_runner.summary
    perfect_summary(summary, test_meta_list)

    # print(json_dumps(summary))
    summary = add_memo(summary)

    # 识别错误
    # print(json_dumps(summary))
    summary = identify_errors(summary)

    return {"summary": json_loads(json_dumps(summary)), "run_task_result_id": run_task_result_id, 'log_dir': log_dir}


# def save_task_results(summary_path_list):
#     """保存测试结果到任务运行结果表api_run_task_result和用例复用表api_testcase_reuse_record"""
#
#     summary_list = []
#     run_task_result_id = None
#     log_dir = None
#     for summary_path in summary_path_list:
#         if not summary_path or 'worker_summary_path is None' == summary_path:
#             continue
#         with open(summary_path, 'r') as f:
#             summary_str = f.readline()
#             summary_dict = json_loads(summary_str)
#             summary_list.append(summary_dict)
#             if not run_task_result_id:
#                 run_task_result_id = summary_dict['run_task_result_id'] if 'run_task_result_id' in summary_dict else None
#             if not log_dir:
#                 log_dir = summary_dict['log_dir'] if 'log_dir' in summary_dict else None
#
#     # run_task_result_id = summary_list[0]['run_task_result_id']
#     # log_dir = summary_list[0]['log_dir']
#
#     # 保存summary_list到服务器文件目录run_task_logs
#     with open('{0}task_run_{1}_summary.log'.format(log_dir, run_task_result_id), 'w') as f:
#         f.write(json_dumps(summary_list))
#
#     callback_task_obj = CeleryTaskRecordManager.get_celery(
#         api_run_task_result_id=run_task_result_id, celery_task_status='WAITING')
#
#     try:
#         # 更新celery_task_record表的字段celery_task_status为RUNNING
#         CeleryTaskRecordManager.update_celery(callback_task_obj.id, celery_task_status='RUNNING')
#
#         total_cases = 0
#         for summary in summary_list:
#             total_cases += summary.pop('total_cases')
#
#         res_obj = ApiRunTaskResultManager.get_result(id=run_task_result_id)
#         task_obj = ApiTaskInfoManager.get_task(id=res_obj.api_task_id)
#
#         # 获取task全部的intf_id_list
#         if task_obj.task_type == 1:
#             task_intf_id_list = json_loads(task_obj.case_tree)['intf_id_list']
#         else:
#             task_intf_id_list = json_loads(task_obj.effect_intf_id_list)
#
#         # 更新api_testcase_reuse_record表, 并获取covered_intf_id_set, run_cases, success_cases
#         res_list = save_testcase_reuse_record(summary_list)
#
#         # 本次测试包含的接口id集合
#         covered_intf_id_set = res_list[0]
#         # 本次运行的用例数
#         run_cases = res_list[1]
#         # 本次成功的用例数
#         success_cases = res_list[2]
#         # 本次未覆盖的接口id列表
#         uncovered_intf_id_list = list(set(task_intf_id_list) ^ covered_intf_id_set)
#         # 本次失败的用例数
#         fail_cases = run_cases - success_cases
#         # 本次未运行的用例数
#         not_run_cases = total_cases - run_cases
#
#         # 更新api_run_task_result表
#         ApiRunTaskResultManager.update_result(
#             run_task_result_id, total_cases=total_cases,
#             not_run_cases=not_run_cases, run_cases=run_cases, success_cases=success_cases, fail_cases=fail_cases,
#             end_time=datetime.now(), covered_intf_id_list=json_dumps(list(covered_intf_id_set)),
#             uncovered_intf_id_list=json_dumps(uncovered_intf_id_list)
#         )
#
#         # 更新celery_task_record表的字段celery_task_status为SUCCESS
#         CeleryTaskRecordManager.update_celery(callback_task_obj.id, celery_task_status='SUCCESS')
#
#     except Exception as err:
#         # 更新api_run_task_result表
#         ApiRunTaskResultManager.update_result(run_task_result_id, end_time=datetime.now())
#         # 更新celery_task_record表的字段celery_task_status为ERROR
#         CeleryTaskRecordManager.update_celery(callback_task_obj.id, celery_task_status='ERROR')
#         print('\n'.join([str(err), traceback.format_exc()]))
#         raise Exception(err)


def get_validator_desc(comparator):
    custom_comparators = custom['comparators']
    for custom_comparator in custom_comparators:
        if comparator == custom_comparator['name']:
            return custom_comparator['description']
    return comparator


def summary_remove_file_obj(summary):
    for detail in summary["details"]:
        for record in detail["records"]:
            '''将body和content字节类型转换dic'''
            if "body" in record["meta_data"]["request"].keys() and "content" in record["meta_data"]["response"].keys():
                request_body = record["meta_data"]["request"].pop("body")
                response_content = record["meta_data"]["response"].pop("content")
                if not request_body:
                    request_body_dic = {}
                else:
                    try:
                        request_body_dic = json.loads(request_body)
                    except TypeError:
                        request_body_dic = json.loads(request_body.decode('utf-8'))
                    except json.decoder.JSONDecodeError:
                        request_body_dic = {}
                    # 增加捕获异常
                    except UnicodeDecodeError:
                        if isinstance(request_body, bytes):
                            request_body_dic = {}
                            # request_body_dic = request_body.decode('utf-8', 'ignore')
                        else:
                            request_body_dic = {}

                if not response_content:
                    response_content_dic = {}
                else:
                    try:
                        response_content_dic = json.loads(response_content)
                    except TypeError:
                        response_content_dic = json.loads(response_content.decode('utf-8'))
                    except json.decoder.JSONDecodeError:
                        response_content_dic = {}
                    except UnicodeDecodeError:
                        response_content_dic = {}

                record["meta_data"]["request"]["body"] = request_body_dic
                record["meta_data"]["response"]["content"] = response_content_dic

            '''将files去除,避免报告超长影响展示效果'''
            if "files" in record["meta_data"]["request"].keys():
                record["meta_data"]["request"].pop("files")
    return summary



if __name__ == '__main__':
    # summ = {}
    # su_dic = identify_errors(summ)
    # print(json_dumps(su_dic))
    pass
