# -*- coding:utf-8 -*-

import copy
import json
import time
import traceback

from atp.api.comm_log import logger
from atp.engine.api_runner import add_memo, identify_errors, summary_remove_file_obj
from atp.engine.api_task_result_collector import save_testcase_reuse_record
from atp.httprunner import HttpRunner
from atp.engine.exceptions import RunCaseError, LoadCaseError
# from atp.engine.load_test_old import load_test
from atp.engine.api_load_test import ApiTestLoader
from atp.engine.api_report import perfect_summary, save_report, save_last_run
from atp.config.default import get_config
from atp.utils.custom import *
from atp.utils.tools import json_dumps, get_host
from atp.httprunner import logger as hr_logger

config = get_config()
run_case_log_dir = config.RUN_CASE_LOG_DIR


def api_run_test(**kwargs):
    report_id = kwargs.pop('report_id', None)
    plan_name = kwargs.pop('plan_name', None)
    project_id = kwargs.pop('project_id', None)
    testcase_main_id_list = kwargs.get('testcase_main_id_list', None)
    failfast = kwargs.pop('failfast', False)
    if testcase_main_id_list:
        is_main = True
    else:
        is_main = False

    try:
        logger.debug(
            '=============================={dir}run_{report_id}.log'.format(dir=run_case_log_dir, report_id=report_id))
        hr_kwargs = {
            "failfast": failfast,
            "log_path": '{dir}run_{report_id}.log'.format(dir=run_case_log_dir, report_id=report_id)
        }
        runner = HttpRunner(**hr_kwargs)

        # res = load_test(**kwargs)
        # testset = res[0]
        # test_meta_list = res[1]
        # project_id = res[2]

        loader = ApiTestLoader(**kwargs)
        testset = loader.get_testset_list()
        test_meta_list = loader.get_test_meta_list()

        if not testset:
            raise LoadCaseError('没有可执行的用例')

        logger.debug("{1} testset:{0}".format(testset, type(testset)))

    except Exception as err:
        save_report(report_path=None, runner_summary=None, project_id=project_id, report_id=report_id)
        hr_logger.log_error("【ERROR】组装用例出错！")
        hr_logger.log_error('\n'.join([str(err), traceback.format_exc()]))
        hr_logger.log_info("【END】测试结束！")
        hr_logger.remove_handler(runner.handler)
        raise LoadCaseError

    try:
        # summary = run(testset, report_name='testMock')

        start_time = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
        hr_logger.log_info("【START】测试开始! (ง •_•)ง")
        hr_logger.log_info("【环境】: {}".format(kwargs.get('env_name', None)))
        # time.sleep(3)
        try:
            testset_json = json_dumps(testset)
        except Exception:
            testset_json = testset
        hr_logger.log_debug("【调用HttpRunner】: {0}".format(testset_json))
        runner.run(testset)
        hr_logger.log_info("【结束调用HttpRunner】")
        # raise RunCaseError
        perfect_summary(runner.summary, test_meta_list)

        """记录用例复用记录"""
        summary_remove_file_obj(runner.summary)
        summary_for_reuse = copy.deepcopy(runner.summary)
        summary_for_reuse = add_memo(summary_for_reuse)
        # 识别错误
        summary_for_reuse = identify_errors(summary_for_reuse)
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

                # '''将body和content字节类型转换dic'''
                # if "body" in record["meta_data"]["request"].keys() and "content" in record["meta_data"]["response"].keys():
                #     request_body = record["meta_data"]["request"].pop("body")
                #     response_content = record["meta_data"]["response"].pop("content")
                #     if not request_body:
                #         request_body_dic = {}
                #     else:
                #         try:
                #             request_body_dic = json.loads(request_body)
                #         except TypeError:
                #             request_body_dic = json.loads(request_body.decode('utf-8'))
                #         # 增加捕获异常
                #         except UnicodeDecodeError:
                #             if isinstance(request_body, bytes):
                #                 request_body_dic = {}
                #                 # request_body_dic = request_body.decode('utf-8', 'ignore')
                #             else:
                #                 request_body_dic = {}
                #
                #     if not response_content:
                #         response_content_dic = {}
                #     else:
                #         try:
                #             response_content_dic = json.loads(response_content)
                #         except TypeError:
                #             response_content_dic = json.loads(response_content.decode('utf-8'))
                #         except json.decoder.JSONDecodeError:
                #             response_content_dic = {}
                #
                #     record["meta_data"]["request"]["body"] = request_body_dic
                #     record["meta_data"]["response"]["content"] = response_content_dic
                #
                # '''将files去除,避免报告超长影响展示效果'''
                # if "files" in record["meta_data"]["request"].keys():
                #     record["meta_data"]["request"].pop("files")

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

        hr_logger.log_info("【runner.summary】: {}".format(json_dumps(runner.summary)))
        runner_summary = copy.deepcopy(runner.summary)
        """把每条用例执行成功与否记录到testcase_info.last_run"""
        try:
            save_last_run(runner_summary, is_main=is_main)
        except Exception as e:
            logger.error('\n'.join([str(e), traceback.format_exc()]))
            # hr_logger.log_error("【ERROR】运行用例出错！")
            # hr_logger.log_error('\n'.join([str(e), traceback.format_exc()]))

        # logger.debug("runner_summary_list{}".format(runner.summary))
        # report_path = runner.gen_html_report(
        #     html_report_name=plan_name if plan_name else 'default',
        #     html_report_template=config.REPORT_TEMPLATE_PATH,
        #     html_report_dir=config.REPORT_DIR
        # )
        # logger.debug('report_path:{}'.format(report_path))
        # report_path = report_path.split('reports')[1]
        # report_url = get_host() + r':8899/reports' + report_path
        #
        # logger.debug('AC report_path:{}'.format(report_path))
        report_url = '不生成报告'
        save_report(report_url, runner_summary, project_id, report_id=report_id, is_main=is_main)

    except Exception as err:
        save_report(report_path=None, runner_summary=runner.summary, project_id=project_id, report_id=report_id)
        hr_logger.log_error("【ERROR】运行用例出错！")
        hr_logger.log_error('\n'.join([str(err), traceback.format_exc()]))
        raise RunCaseError
    finally:
        hr_logger.log_info("【END】测试结束！")
        hr_logger.remove_handler(runner.handler)

    return report_url


def run_api_test(**kwargs):
    '''
    UI用例中的操作步骤为执行接口用例时调用的方法
    :param kwargs: testcase_id_list
    :return:
    '''
    try:
        report_id = kwargs.pop('report_id', None)
        hr_kwargs = {
            "failfast": False,
            "log_path": '{dir}run_{report_id}.log'.format(dir=run_case_log_dir, report_id=report_id)
        }
        runner = HttpRunner(**hr_kwargs)
        loader = ApiTestLoader(**kwargs)
        testset = loader.get_testset_list()
        if not testset:
            raise LoadCaseError('没有可执行的用例')
        runner.run(testset)
        print(runner.summary)
    except Exception as err:
        raise LoadCaseError


if __name__ == '__main__':
    from atp.app import create_app

    app = create_app()
    with app.app_context():
        kwargs_ = {
            "failfast": True,
            # "testcase_main_id_list": ['258'],  # http demo
            "testcase_id_list": ['5142'],  # http demo
            # "testcase_id_list": ['3807'],  # dubbo demo
            # "testcase_id_list": ['1091', '1258', '1259'],  # mq demo
            "env_name": "ALIUAT",
            # "test_tree": {"5": {"66": ["140"]}},
            # "test_tree": {"5": {"66": ["140", "142"]}, "68": {"71": ["141"]}}
        }
        api_run_test(**kwargs_)

    # run_test(testcase_id='1', env_ name='mo2ck')
