# -*- coding:utf-8 -*-

import json
import time

from flask import Blueprint
from flask_restful import Resource
# import concurrent.futures

# from multiprocessing import Process
# from atp.api.comm_log import logger
# from atp.api.log_push_queue import LogPushQueue
from atp.api.mysql_manager import ApiTestReportManager, ApiTestcaseInfoManager, ApiTestcaseMainManager
from atp.engine.api_chain import get_testcase_chain
from atp.engine.api_runner import ApiRunner
from atp.engine.exceptions import LoadCaseError, RunCaseError
# from atp.engine.api_run_test import api_run_test
# from atp.env import RUNNING_ENV
from atp.views.wrappers import timer, developer_check
from atp.utils.common import get_request_json, make_response
# from sqlalchemy.exc import IntegrityError
from atp.api.redis_api import RedisManager
from flask import request

redis = RedisManager()
api_run = Blueprint('api_run_interface', __name__)


class ApiRun(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))
        self.atim = ApiTestcaseInfoManager()
        self.arm = ApiTestReportManager()
        self.atmm = ApiTestcaseMainManager()

    @timer
    @developer_check
    def post(self):
        """
        请求报文示例：
        1、测试用例id列表（同一个测试集下）：
            {
                "env": "ALIUAT",
                "testcaseList": [
                    "1",
                    "2",
                    "3"
                ],
                "reportId": "666",
                "pubVariableChanges": [
                    {
                        "pvId": "",
                        "name": "",
                        "tmpValue": "",
                        "optionValue": "",
                        "type": ""
                    },
                    {
                        "pvId": "",
                        "name": "",
                        "tmpValue": "",
                        "optionValue": "",
                        "type": ""
                    }
                ]
            }
        """
        testcase_id_list = self.data.pop("testcaseList", None)
        testcase_main_id_list = self.data.pop("testcaseMainList", None)
        custom_flow_id = self.data.pop("customFlowId", None)
        if not testcase_id_list and not testcase_main_id_list:
            return make_response({"code": "100", "desc": "入参校验失败"})

        report_id = self.data.pop("reportId", None)
        pub_variable_changes = self.data.pop("pubVariableChanges", None)

        try:
            env_name = self.data["env"]
            project_id = self.data.pop("projectId", None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        kwargs = {
            "project_id": project_id,
            "env_name": env_name,
            "pub_variable_changes": pub_variable_changes,
            "custom_flow_id": custom_flow_id
        }
        # 按测试用例id列表运行
        if testcase_id_list:
            testcase_id_list = self.filter_case_by_status(testcase_id_list=testcase_id_list)
            if not testcase_id_list:
                return make_response({"code": "200", "desc": "没有可执行的用例"})
            kwargs["testcase_id_list"] = testcase_id_list
        elif testcase_main_id_list:
            testcase_main_id_list = self.filter_case_by_status(testcase_main_id_list=testcase_main_id_list)
            if not testcase_main_id_list:
                return make_response({"code": "200", "desc": "没有可执行的用例"})
            kwargs["testcase_main_id_list"] = testcase_main_id_list
        else:
            return make_response({"code": "101", "desc": "入参校验失败, 缺少testcaseList/testcase_main_id_list字段或值为空"})

        # 注册report_id并返回
        if not report_id:

            report_id = self.pre_register_report(self.username)
            # kwargs['report_id'] = report_idvi

            # p = Process(target=run_test, kwargs=kwargs)
            # p.start()
            total_progress = 0
            if testcase_id_list:
                for testcase_id in testcase_id_list:
                    total_progress += self.count_call_chain(testcase_id)
            elif testcase_main_id_list:
                for testcase_main_id in testcase_main_id_list:
                    total_progress += self.count_main_call_chain(testcase_main_id)

            # log_push_queue = LogPushQueue(RUNNING_ENV, report_id)
            return make_response(
                {"code": "000", "reportId": "{}".format(report_id), "totalProgress": total_progress,
                 "desc": "已注册report_id, 回调本接口开始运行"})
        # 运行用例，并等待返回测试报告
        else:
            kwargs['report_id'] = report_id
        # executor = concurrent.futures.ProcessPoolExecutor()
        # # with concurrent.futures.ProcessPoolExecutor() as executor:
        # executor.submit(run_test, **kwargs)

            try:
                # report_path = api_run_test(**kwargs)

                api_runner_kwargs = {
                    "executor": self.username
                }
                api_runner = ApiRunner(**api_runner_kwargs)
                api_runner.run_debug(**kwargs)

            except LoadCaseError:
                return make_response({"code": "200", "desc": "组装用例时出错"})
            except RunCaseError:
                return make_response({"code": "200", "desc": "执行用例时出错"})

            # return make_response({"code": "000", "desc": "{report_path}".format(report_path=report_path)})

            # log_push_queue = LogPushQueue(RUNNING_ENV, report_id)
            # log_push_queue.push_log()

            return make_response({"code": "000", "desc": "测试用例由celery异步运行中"})

    def filter_case_by_status(self, testcase_id_list=None, testcase_main_id_list=None, test_tree=None):
        """
        检查case状态，去掉case_status不为0的case
        :param testcase_id_list:
        :param testcase_main_id_list:
        :param test_tree:
        :return:
        """
        if testcase_id_list:
            objs = self.atim.get_testcases_in_id_list(testcase_id_list)
            for obj in objs:
                if obj.case_status != 0:
                    testcase_id_list.remove(str(obj.id))
            return testcase_id_list
        elif testcase_main_id_list:
            objs = self.atmm.get_testcases_in_id_list(testcase_main_id_list)
            for obj in objs:
                if obj.case_status != 0:
                    testcase_main_id_list.remove(str(obj.id))
            return testcase_main_id_list
        elif test_tree:
            return test_tree
        else:
            return None

    def pre_register_report(self, username):
        """
        预注册测试报告，返回report_id
        :return:
        """
        report_id = self.get_next_report_id()
        self.arm.insert_report(id=report_id, status='running', executor=username)

        return report_id

    def get_next_report_id(self):
        """
        获取test_report表下一个id
        :return:
        """
        return self.arm.get_next_report_id()

    def count_call_chain(self, testcase_id, previous_count=None):
        """
        根据testcase_id计算该用例的调用链长度
        :param previous_count:
        :param testcase_id:
        :return:
        """
        chain_list = get_testcase_chain(testcase_id, case_type=1)
        return len(chain_list)
        # if not previous_count:
        #     current_count = 1
        # else:
        #     current_count = previous_count
        # row = self.atim.query_testcase_belong(testcase_id)
        # if row[0]:
        #     setup_cases = eval(row[0])[1]['setup_cases']
        # else:
        #     setup_cases = []
        #
        # for setup_case_id in setup_cases:
        #     if str(testcase_id) != str(setup_case_id):
        #         current_count = self.count_call_chain(setup_case_id, current_count)
        #         current_count += 1
        #
        # return current_count

    def count_api_call_chain(self, testcase_id, previous_count=None):
        """
        根据testcase_id计算该接口用例的调用链长度（包含）
        :param previous_count:
        :param testcase_id:
        :return:
        """
        if not previous_count:
            current_count = 1
        else:
            current_count = previous_count
        row = self.atim.query_testcase_belong(testcase_id)
        if row[0]:
            setup_cases = eval(row[0])[1]['setup_cases']
        else:
            setup_cases = []

        for setup_case_id in setup_cases:
            if str(testcase_id) != str(setup_case_id):
                current_count = self.count_call_chain(setup_case_id, current_count)
                current_count += 1

        return current_count

    def count_main_call_chain(self, testcase_main_id):
        """
        testcase_main_id
        :param testcase_main_id:
        :return:
        """
        tm_obj = self.atmm.get_testcase_main(id=testcase_main_id)
        return len(json.loads(tm_obj.sub_list))
