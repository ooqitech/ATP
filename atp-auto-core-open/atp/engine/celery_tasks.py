# -*- coding:utf-8 -*-

import copy
import json
import traceback
import time

from flask_sqlalchemy import SQLAlchemy

# from atp import app, celery
from atp.api.log_push_queue import LogPushQueue
from atp.engine.api_task_result_collector import TaskResultCollector, save_testcase_reuse_record
from atp.extensions import celery
from atp.api.mysql_manager import CeleryTaskRecordManager, ApiTestcaseInfoManager, ApiTestcaseMainManager
from atp.engine import api_runner
from atp.engine.api_load_test import ApiTestLoader
from atp.engine.api_report import perfect_summary, save_report, save_last_run
from atp.engine.exceptions import LoadCaseError, RunCaseError

from atp.utils.tools import json_dumps, json_loads, get_host
from atp.httprunner import logger as hr_logger
from atp.config.default import get_config
from atp.httprunner import HttpRunner

config = get_config()
run_case_log_dir = config.RUN_CASE_LOG_DIR


@celery.task(name='tasks.collect')
def celery_collect_results(summary_path_list):
    # with app.app_context():
    if True:
        print("分步任务完成({})，开始收集结果任务...".format(len(summary_path_list)))
        # print("summary_list:{}".format(json_dumps(summary_list)))
        try:
            # api_runner.save_task_results(summary_path_list)
            collector = TaskResultCollector(summary_path_list)
            collector.save_task_results()
        except Exception as err:
            summary_list_str = json_dumps(summary_path_list)
            print("收集结果任务出现异常, summary_list:{}:".format(summary_list_str))
            print('\n'.join([str(err), traceback.format_exc()]))
            # print("收集结果任务出现异常")
        print("收集结果任务完成")


@celery.task(bind=True, name='tasks.intf_or_main')
def celery_run_single_intf_or_single_main_case(self, run_task_result_id, env_id, intf_id_or_main_case_id, is_intf, log_dir, testcase_id_list=None):
    # with app.app_context():
    if True:
        print("开始分步任务: {0}, 接口id/全链路用例id: {1}, 是否接口:{2}".format(self.request.id, intf_id_or_main_case_id, is_intf))
        CeleryTaskRecordManager.insert_celery(
            celery_task_no=self.request.id, celery_task_status='_loading',
            api_run_task_result_id=run_task_result_id)

        total_cases = 0
        kwargs = None
        intf_id = None
        main_case_id = None
        result_dic = {"run_task_result_id": run_task_result_id, "log_dir": log_dir}
        worker_summary_path = None
        try:
            if is_intf:
                intf_id = intf_id_or_main_case_id
                # testcase_objs = ApiTestcaseInfoManager.get_testcases(api_intf_id=intf_id, case_status=0)
                # testcase_id_list = [testcase_obj.id for testcase_obj in testcase_objs]
                if testcase_id_list:
                    total_cases += len(testcase_id_list)
                    kwargs = {
                        "env_id": env_id,
                        "testcase_id_list": testcase_id_list,
                    }
                worker_summary_path = '{0}task_run_{1}_intf_{2}.summary'.format(log_dir, run_task_result_id, intf_id)
            else:
                main_case_id = intf_id_or_main_case_id
                # valid_main_case_obj = ApiTestcaseMainManager.get_testcase_main(id=main_case_id, case_status=0)
                if main_case_id:
                    total_cases += 1
                    kwargs = {
                        "env_id": env_id,
                        "testcase_main_id_list": [main_case_id],
                    }
                worker_summary_path = '{0}task_run_{1}_main_case_{2}.summary'.format(log_dir, run_task_result_id,
                                                                                     main_case_id)

            if kwargs:
                api_loader = ApiTestLoader(**kwargs)
                testset = api_loader.get_testset_list()
                test_meta_list = api_loader.get_test_meta_list()

                CeleryTaskRecordManager.update_celery_by_task_no(
                    celery_task_no=self.request.id, celery_task_status='_running')

                runner_kwargs = {
                    'log_dir': log_dir,
                    'env_id': env_id,
                    'testset': testset,
                    'test_meta_list': test_meta_list,
                    'run_task_result_id': run_task_result_id,
                    'intf_id': intf_id,
                    'main_case_id': main_case_id,
                }
                result_dic = api_runner.http_runner_run(**runner_kwargs)

                result_dic['total_cases'] = total_cases

                CeleryTaskRecordManager.update_celery_by_task_no(
                    celery_task_no=self.request.id, celery_task_status='_success')

                print("结束分步任务: {0}, 接口id/全链路用例id: {1}, 是否接口:{2}".format(
                    self.request.id, intf_id_or_main_case_id, is_intf))
                # return result_dic
            # 没有有效的测试用例
            else:
                result_dic.update(
                    {
                        'not_run_intf_id_or_main_case_id': intf_id_or_main_case_id,
                        'total_cases': total_cases
                    }
                )
                CeleryTaskRecordManager.update_celery_by_task_no(
                    celery_task_no=self.request.id, celery_task_status='_success')

                print("结束分步任务, 未找到可执行用例: {0}, 接口id/全链路用例id: {1}, 是否接口:{2}".format(
                    self.request.id, intf_id_or_main_case_id, is_intf))
                # return result_dic
        except Exception as err:
            print("分步任务异常退出: {0}, 接口id/全链路用例id: {1}, 是否接口:{2}, 错误信息:".format(
                self.request.id, intf_id_or_main_case_id, is_intf, traceback))
            print('\n'.join([str(err), traceback.format_exc()]))
            result_dic.update(
                {
                    'total_cases': total_cases,
                    'not_run_intf_id_or_main_case_id': intf_id_or_main_case_id
                }
            )
            CeleryTaskRecordManager.update_celery_by_task_no(
                celery_task_no=self.request.id, celery_task_status='_error')
        finally:
            if worker_summary_path:
                with open(worker_summary_path, 'w') as f:
                    f.write(json_dumps(result_dic))
                return worker_summary_path
            else:
                return 'worker_summary_path is None'
            # return result_dic


@celery.task(bind=True, name='tasks.main')
def celery_run_main_case_list(self, run_task_result_id, env_id, main_case_id_list, log_dir):
    # with app.app_context():
    if True:
        print("开始分步任务: {0}, 全链路用例id列表: {1}".format(self.request.id, main_case_id_list))
        try:
            CeleryTaskRecordManager.insert_celery(
                celery_task_no=self.request.id, celery_task_status='_loading',
                api_run_task_result_id=run_task_result_id)
        except Exception as err:
            print("开始分步任务时存在错误: {0}, 全链路用例id列表: {1}, 错误信息:".format(
                self.request.id, main_case_id_list, traceback))
            print('\n'.join([str(err), traceback.format_exc()]))
            CeleryTaskRecordManager.insert_celery(
                celery_task_no=self.request.id, celery_task_status='_loading',
                api_run_task_result_id=run_task_result_id)

        total_cases = 0
        result_dic = {"run_task_result_id": run_task_result_id, "log_dir": log_dir}
        kwargs = {"env_id": env_id, "testcase_main_id_list": []}
        worker_summary_path = '{0}task_run_{1}_main_case_list_{2}.summary'.format(
            log_dir, run_task_result_id, main_case_id_list)
        try:

            # for main_case_id in main_case_id_list:
            #     valid_main_case_obj = ApiTestcaseMainManager.get_testcase_main(id=main_case_id, case_status=0)
            #     if valid_main_case_obj:
            #         total_cases += 1
            #         kwargs["testcase_main_id_list"].append(main_case_id)
            total_cases = len(main_case_id_list)
            kwargs["testcase_main_id_list"] = main_case_id_list

            if kwargs["testcase_main_id_list"]:
                api_loader = ApiTestLoader(**kwargs)
                testset = api_loader.get_testset_list()
                test_meta_list = api_loader.get_test_meta_list()

                CeleryTaskRecordManager.update_celery_by_task_no(
                    celery_task_no=self.request.id, celery_task_status='_running')

                runner_kwargs = {
                    'log_dir': log_dir,
                    'env_id': env_id,
                    'testset': testset,
                    'test_meta_list': test_meta_list,
                    'run_task_result_id': run_task_result_id,
                    'main_case_id_list': main_case_id_list,
                }
                result_dic = api_runner.http_runner_run(**runner_kwargs)

                result_dic['total_cases'] = total_cases

                CeleryTaskRecordManager.update_celery_by_task_no(
                    celery_task_no=self.request.id, celery_task_status='_success')

                print("结束分步任务: {0}, 全链路用例id列表: {1}".format(
                    self.request.id, main_case_id_list))
                # return result_dic
            # 没有有效的测试用例
            else:
                result_dic.update(
                    {
                        'main_case_id_list': main_case_id_list,
                        'total_cases': total_cases
                    }
                )
                CeleryTaskRecordManager.update_celery_by_task_no(
                    celery_task_no=self.request.id, celery_task_status='_success')

                print("结束分步任务, 未找到可执行用例: {0}, 全链路用例id列表: {1}".format(
                    self.request.id, main_case_id_list))
                # return result_dic
        except Exception as err:
            print("分步任务异常退出: {0}, 全链路用例id列表: {1}, 错误信息:".format(
                self.request.id, main_case_id_list, traceback))
            print('\n'.join([str(err), traceback.format_exc()]))
            result_dic.update(
                {
                    'total_cases': total_cases,
                    'main_case_id_list': main_case_id_list
                }
            )
            CeleryTaskRecordManager.update_celery_by_task_no(
                celery_task_no=self.request.id, celery_task_status='_error')
        finally:
            if worker_summary_path:
                with open(worker_summary_path, 'w') as f:
                    f.write(json_dumps(result_dic))
                return worker_summary_path
            else:
                return 'worker_summary_path is None'
            # return result_dic


@celery.task
def celery_run_debug(**kwargs):
    # with app.app_context():
    if True:
        log_dir = kwargs.get('log_dir')
        report_id = kwargs.pop('report_id', None)
        plan_name = kwargs.pop('plan_name', None)
        project_id = kwargs.pop('project_id', None)
        testcase_main_id_list = kwargs.get('testcase_main_id_list', None)
        if testcase_main_id_list:
            is_main = True
        else:
            is_main = False

        print(
            '=============================={dir}run_{report_id}.log'.format(dir=log_dir, report_id=report_id))
        hr_kwargs = {
            "failfast": True,
            "log_path": '{dir}run_{report_id}.log'.format(dir=log_dir, report_id=report_id)
        }
        runner = HttpRunner(**hr_kwargs)

        try:
            loader = ApiTestLoader(**kwargs)
            testset = loader.get_testset_list()
            test_meta_list = loader.get_test_meta_list()

            if not testset:
                raise LoadCaseError('没有可执行的用例')

            # logger.debug("{1} testset:{0}".format(testset, type(testset)))

        except Exception as err:
            save_report(report_path=None, runner_summary=None, project_id=project_id, report_id=report_id)
            hr_logger.log_error("【ERROR】组装用例出错！")
            hr_logger.log_error('\n'.join([str(err), traceback.format_exc()]))
            hr_logger.log_info("【END】测试结束！")
            hr_logger.remove_handler(runner.handler)
            raise LoadCaseError

        try:
            hr_logger.log_info("【START】测试开始! (ง •_•)ง")
            hr_logger.log_info("【环境】: {}".format(kwargs.get('env_name', None)))
            # time.sleep(3)
            try:
                testset_json = json_dumps(testset)
            except Exception:
                testset_json = testset
            hr_logger.log_info("【调用HttpRunner】: {0}".format(testset_json))
            runner.run(testset)
            hr_logger.log_info("【结束调用HttpRunner】")
            # raise RunCaseError
            perfect_summary(runner.summary, test_meta_list)

            """记录用例复用记录"""
            api_runner.summary_remove_file_obj(runner.summary)
            summary_for_reuse = copy.deepcopy(runner.summary)
            # print(json_dumps(summary_for_reuse))
            summary_for_reuse = api_runner.add_memo(summary_for_reuse)
            # 识别错误
            summary_for_reuse = api_runner.identify_errors(summary_for_reuse)
            # 更新api_testcase_reuse_record表, 并获取covered_intf_id_set, run_cases, success_cases
            save_testcase_reuse_record([{"summary": json_loads(json_dumps(summary_for_reuse))}])
            del summary_for_reuse

            # hr_logger.log_info("【runner.summary】: {}".format(runner.summary))
            '''报告优化:1、汉化(包括日志里面的字段)
                        2、开始时间和持续时间合并成一行
                        3、增加一个字段“错误类型”，如果用例错误，显示该字段，并说明期望与预期值；
                                                    否则该字段不显示
                        4.log里面去掉一些数据重复和不重要的；行和字段（请求headers，返回体的headers,reason，url，“”ok”）
                        5.将请求体和返回值数据缩进，且字典里面的key颜色加粗
                        6.新增接口请求类型字段，http、dubbo、mq'''

            from atp.utils.custom import json_contains, db_validate, db_json_validate
            for detail in runner.summary["details"]:
                for record in detail["records"]:
                    '''增加用例类型:test_meta_list["intf_type"]'''
                    record["intf_type"] = test_meta_list[0]["intf_type"]

                    '''删除报告一些无需关注的字段'''
                    request_keys = ["json", "start_timestamp"]
                    response_keys = ["elapsed_ms", "encoding", 'ok', 'url', 'reason', 'cookies']
                    for request_key in request_keys:
                        if request_key in record["meta_data"]["request"]:
                            del record["meta_data"]["request"][request_key]
                    for respones_key in response_keys:
                        if respones_key in record["meta_data"]["response"]:
                            del record["meta_data"]["response"][respones_key]

                    '''record.status出现error, 抛出错误信息'''
                    if record['status'] == 'error':
                        error_msg = record['attachment']
                        raise Exception(error_msg)

                    '''报告增加一列：错误类型:'''
                    for validate in record["meta_data"]["validators"]:
                        if validate["comparator"] == "json_contains":
                            check_value = validate["check_value"]
                            expect_value = validate["expect"]
                            if json_contains(check_value, expect_value) is not True:
                                validate["check_result"] = "fail"
                                record["status"] = "failure"
                                detail["stat"]["failures"] += 1
                                detail["stat"]["successes"] -= 1
                                runner.summary["stat"]["failures"] += 1
                                runner.summary["stat"]["successes"] -= 1
                                error_log = ("预期:{}未在返回报文内".format(expect_value))
                                validate["error_log"] = {"json_contains": error_log}
                        elif validate["comparator"] == "db_validate":
                            check_value = validate["check_value"]
                            expect_value = validate["expect"]
                            if db_validate(check_value, expect_value) is not True:
                                validate["check_result"] = "fail"
                                record["status"] = "failure"
                                detail["stat"]["failures"] += 1
                                detail["stat"]["successes"] -= 1
                                runner.summary["stat"]["failures"] += 1
                                runner.summary["stat"]["successes"] -= 1
                                error_log = ("预期:{0},实际是：{1}".format(expect_value, check_value))
                                validate["error_log"] = {"db_validate": error_log}
                        elif validate["comparator"] == "db_json_validate":
                            check_value = validate["check_value"]
                            expect_value = validate["expect"]
                            if not db_json_validate(check_value, expect_value):
                                validate["check_result"] = "fail"
                                record["status"] = "failure"
                                detail["stat"]["failures"] += 1
                                detail["stat"]["successes"] -= 1
                                runner.summary["stat"]["failures"] += 1
                                runner.summary["stat"]["successes"] -= 1
                                error_log = ("预期:{0},实际是：{1}".format(expect_value,
                                                                     json.dumps(check_value).encode('utf-8').decode(
                                                                         'unicode_escape')))
                                validate["error_log"] = {"db_json_validate": error_log}

            hr_logger.log_info("【runner.summary】: {}".format(runner.summary))
            runner_summary = copy.deepcopy(runner.summary)
            """把每条用例执行成功与否记录到testcase_info.last_run"""
            try:
                save_last_run(runner_summary, is_main=is_main)
            except Exception as e:
                print('\n'.join([str(e), traceback.format_exc()]))
                # hr_logger.log_error("【ERROR】运行用例出错！")
                # hr_logger.log_error('\n'.join([str(e), traceback.format_exc()]))

            # print("runner_summary_list{}".format(runner.summary))
            # report_path = runner.gen_html_report(
            #     html_report_name=plan_name if plan_name else 'default',
            #     html_report_template=config.REPORT_TEMPLATE_PATH,
            #     html_report_dir=config.REPORT_DIR
            # )
            # print('report_path:{}'.format(report_path))
            # report_path = report_path.split('reports')[1]
            # report_url = get_host() + r':8899/reports' + report_path
            #
            # print('AC report_path:{}'.format(report_path))
            report_url = '不生成报告'
            save_report(report_url, runner_summary, project_id, report_id=report_id, is_main=is_main)

        except Exception as err:
            save_report(report_path=None, runner_summary=runner.summary, project_id=project_id, report_id=report_id)
            hr_logger.log_error("【ERROR】运行用例出错！")
            hr_logger.log_error('\n'.join([str(err), traceback.format_exc()]))
            time.sleep(1)
            raise RunCaseError
        finally:
            time.sleep(1)
            hr_logger.log_info("【END】测试结束！")
            hr_logger.remove_handler(runner.handler)

        return report_url


@celery.task
def celery_push_log(running_env, queue_name, report_id):
    log_push_queue = LogPushQueue(running_env, queue_name=queue_name, report_id=report_id)
    log_push_queue.push_debug_log()


@celery.task
def celery_push_task_log(running_env, queue_name, **kwargs):
    log_push_queue = LogPushQueue(running_env, queue_name=queue_name, **kwargs)
    log_push_queue.push_task_run_log()

if __name__ == '__main__':
    pass
