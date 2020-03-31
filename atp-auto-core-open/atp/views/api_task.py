# -*- coding:utf-8 -*-

import functools
import json
import platform
import time
import traceback
from copy import copy, deepcopy
from datetime import datetime
from flask import Blueprint
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.api.disconf_executor import disconf_get_config, edit_disconf_value
from atp.api.excel_parser import ExcelParser
from atp.api.mysql_manager import (
    ApiSystemInfoManager, ApiTaskInfoManager, ApiTestcaseMainManager, ApiTestcaseInfoManager, GitDiffVersionManager,
    ApiProjectInfoManager, ApiRunTaskResultManager,
    CeleryTaskRecordManager, ApiIntfInfoManager, EnvInfoManager, TestcaseTagManager)
from atp.api.ssh_client import SSHClient
from atp.config.default import get_config
from atp.engine.api_chain import get_table_data, count_testcase_total
from atp.engine.api_runner import ApiRunner
from atp.engine.api_task_result_collector import TaskResultCollector
from atp.engine.return_code_desc import CODE_DESC_MAP
from atp.utils.tools import json_loads, json_dumps, get_current_timestamp, get_current_time
from atp.views.wrappers import timer, login_check, developer_check, master_check
from atp.utils.common import get_request_json, make_response, username_to_nickname, read_custom
from atp.api.redis_api import RedisManager
from flask import request
from atp.api.http_client import HttpClient
from atp.config.load_config import load_config

redis = RedisManager()
config = get_config()
custom = read_custom()
api_task = Blueprint('api_task_interface', __name__)
GL_CACHE_TESTCASE_CHAIN_DICT = {}


def func_timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        start_time = time.time()

        c = func(*args, **kw)
        end_time = time.time()
        d_time = end_time - start_time
        print("==== Finish [{0}], run {1:.3}s ====\n".format(func.__name__, d_time))
        return c

    return wrapper


class ApiTask(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))

    @timer
    def post(self, action):
        if action == 'add':
            return self.add_task()

        elif action == 'edit':
            return self.edit_task()

        elif action == 'delete':
            return self.delete_task()

        elif action == 'detail':
            return self.task_detail()

        elif action == 'runHistory':
            return self.query_run_history()

        elif action == 'list':
            return self.task_list()

        elif action == 'listSmokingTask':
            return self.list_smoking_task()

        elif action == 'listRegressionTask':
            return self.list_regression_task()

        elif action == 'getProgress':
            return self.get_task_running_progress()

        elif action == 'getUncoveredInfo':
            return self.get_uncovered_info()

        elif action == 'getSummary':
            return self.get_summary()

        elif action == 'getRunDataByTestcase':
            return self.get_run_data_by_testcase()

        elif action == 'getRunResults':
            return self.get_run_results()

        elif action == 'getRunResultBySingleDay':
            return self.get_run_result_by_single_day()

        elif action == 'exportSummaryToExcel':
            return self.export_summary_to_excel()

        elif action == 'exportSmokingTestLogToExcel':
            return self.export_smoking_test_log_to_excel()

        elif action == 'reCollectTaskResult':
            return self.re_collect_task_result()

        elif action == 'run':
            return self.run_task()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def add_task(self):
        """
        Input:
        手工指定
        {
            "companyId": 1,  # 2019.6.19 新增
            "projectId": 1,
            "taskName": "",
            "taskType": 1,
            "tagIdList": [1,2,3],
            "selectIntfTree": [1,2,3],
            "selectFullTree":[54]
        }
        基于代码变更
        {
            "companyId": 1,  # 2019.6.19 新增
            "projectId": 1,
            "taskName": "",
            "taskType": 2,
            "tagIdList": [1,2,3],
            "gitDiff": [
                {
                    "changeSystemId": 1,
                    "changeBranchName": "",
                    "commitStartId": "",
                    "commitEndId": "",
                    "gitUrl": "",
                }
            ]
        }
        Return:
        {
            "code": "000",
            "desc": "保存成功"
        }

        """

        try:
            company_id = self.data.pop('companyId')
            project_id = self.data.pop('projectId')
            task_name = self.data.pop('taskName')
            task_type = int(self.data.pop('taskType'))
            intf_id_list = self.data.pop('selectIntfTree', [])
            product_line_id_list = self.data.pop('selectFullTree', [])
            git_diff_list = self.data.pop('gitDiff', [])
            tag_id_list = self.data.pop('tagIdList')
            if not isinstance(tag_id_list, list):
                raise KeyError
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        exist_obj = ApiTaskInfoManager.get_task(
            task_name=task_name, api_project_id=project_id, api_company_id=company_id)
        if exist_obj:
            return make_response({"code": "301", "desc": "测试任务名称已存在"})

        if task_type in (1,3):
            case_tree = {'intf_id_list': intf_id_list, 'product_line_id_list': product_line_id_list}
            ApiTaskInfoManager.insert_task(
                task_name=task_name, api_project_id=project_id, task_type=task_type, case_tree=json_dumps(case_tree),
                creator=self.username, task_status=1, api_company_id=company_id,
                related_tag_id_list=json_dumps(tag_id_list))
        else:
            ApiTaskInfoManager.insert_task(
                task_name=task_name, api_project_id=project_id, task_type=task_type, creator=self.username,
                task_status=0, api_company_id=company_id, related_tag_id_list=json_dumps(tag_id_list))
            task_obj = ApiTaskInfoManager.get_task(
                task_name=task_name, api_project_id=project_id, api_company_id=company_id)
            for git_diff_dic in git_diff_list:
                GitDiffVersionManager.insert_git_diff_version(
                    api_task_id=task_obj.id, api_system_id=git_diff_dic['changeSystemId'],
                    git_branch_name=git_diff_dic['changeBranchName'], old_commit_id=git_diff_dic['commitStartId'],
                    new_commit_id=git_diff_dic['commitEndId'], creator=self.username
                )
                system_obj = ApiSystemInfoManager.get_system(id=git_diff_dic['changeSystemId'])
                if not system_obj.git_url:
                    ApiSystemInfoManager.update_system(system_obj.id, git_url=git_diff_dic['gitUrl'])

                # TODO 调用获取git差异接口

        return make_response({"code": "000", "desc": "保存成功"})

    @developer_check
    def edit_task(self):
        """
        Input:
        手工指定
        {
            "taskId": 1,
            "companyId": 1,  # 2019.6.19 新增
            "projectId": 1,
            "taskName": "",
            "taskType": 1,
            "tagIdList": [1,2,3],
            "selectIntfTree": [1,2,3],
            "selectFullTree":[54]
        }
        基于代码变更
        {
            "taskId": 2,
            "companyId": 1,  # 2019.6.19 新增
            "projectId": 1,
            "taskName": "",
            "taskType": 2,
            "tagIdList": [1,2,3],
            "gitDiff": [
                {
                    "changeSystemId": 1,
                    "changeBranchName": "",
                    "commitStartId": "",
                    "commitEndId": "",
                    "gitUrl": "",
                }
            ]
        }
        Return:
        {
            "code": "000",
            "desc": "保存成功"
        }

        """

        try:
            company_id = self.data.pop('companyId')
            task_id = self.data.pop('taskId')
            project_id = self.data.pop('projectId')
            task_name = self.data.pop('taskName')
            task_type = int(self.data.pop('taskType'))
            intf_id_list = self.data.pop('selectIntfTree', [])
            product_line_id_list = self.data.pop('selectFullTree', [])
            git_list = self.data.pop('gitDiff', [])
            tag_id_list = self.data.pop('tagIdList')
            if not isinstance(tag_id_list, list):
                raise KeyError
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        task_obj = ApiTaskInfoManager.get_task(id=task_id)
        if not task_obj:
            return make_response({"code": "301", "desc": "taskId不存在"})

        if task_obj.task_name != task_name:
            exist_obj = ApiTaskInfoManager.get_task(
                task_name=task_name, api_company_id=company_id)
            if exist_obj:
                return make_response({"code": "301", "desc": "测试任务名称已存在"})

        if task_type in (1, 3):
            case_tree = {'intf_id_list': intf_id_list, 'product_line_id_list': product_line_id_list}
            ApiTaskInfoManager.update_task(
                task_id,
                task_name=task_name, api_project_id=project_id, task_type=task_type, case_tree=json_dumps(case_tree),
                last_modifier=self.username, related_tag_id_list=json_dumps(tag_id_list))
        else:
            ApiTaskInfoManager.update_task(
                task_id,
                task_name=task_name, api_project_id=project_id, task_type=task_type, last_modifier=self.username,
                task_status=0, related_tag_id_list=json_dumps(tag_id_list))
            db_git_objs = GitDiffVersionManager.get_git_diff_versions(api_task_id=task_id)
            still_alive_git_objs = []
            for git_dic in git_list:
                # 是否已经在数据库存在
                is_exist = False
                for db_git_obj in db_git_objs:
                    if db_git_obj.api_system_id == int(git_dic['changeSystemId']) and db_git_obj.git_branch_name == \
                            git_dic['changeBranchName'] and db_git_obj.old_commit_id == git_dic['commitStartId'] \
                            and db_git_obj.new_commit_id == git_dic['commitEndId']:
                        still_alive_git_objs.append(db_git_obj)
                        is_exist = True
                        break
                if not is_exist:
                    GitDiffVersionManager.insert_git_diff_version(
                        api_task_id=task_obj.id, api_system_id=git_dic['changeSystemId'],
                        git_branch_name=git_dic['changeBranchName'], old_commit_id=git_dic['commitStartId'],
                        new_commit_id=git_dic['commitEndId'], creator=self.username
                    )
                    system_obj = ApiSystemInfoManager.get_system(id=git_dic['changeSystemId'])
                    if not system_obj.git_url:
                        ApiSystemInfoManager.update_system(system_obj.id, git_url=git_dic['gitUrl'])

                    # TODO 调用获取git差异接口

            to_delete_git_objs = list(set(db_git_objs) ^ set(still_alive_git_objs))
            for to_delete_obj in to_delete_git_objs:
                GitDiffVersionManager.delete_git_diff_version_by_obj(to_delete_obj)

        return make_response({"code": "000", "desc": "保存成功"})

    @master_check
    def delete_task(self):
        """
        Input:
        {
            "taskId": 1,
        }
        Return:
        {
            "code": "000",
            "desc": "删除成功"
        }
        """
        try:
            task_id = self.data.pop('taskId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        ApiTaskInfoManager.delete_task(id_=task_id)
        git_objs = GitDiffVersionManager.get_git_diff_versions(api_task_id=task_id)
        for git_obj in git_objs:
            GitDiffVersionManager.delete_git_diff_version(git_obj.id)

        return make_response({"code": "000", "desc": "删除成功"})

    @developer_check
    def task_detail(self):
        """
        Input:
        {
            "taskId": 1,
        }
        Return:
        {
            "code": "000",
            "projectId": 1,
            "taskName": "",
            "taskType": 2,
            "gitDiff": [
                {
                    "changeSystemId": 1,
                    "changeBranchName": "",
                    "commitStartId": "",
                    "commitEndId": "",
                    "gitUrl": "",
                }
            ],
            "selectIntfTree": [1,2,3],
            "selectFullTree":[54]
            "tags": [
                {
                    "tagId": 6,
                    "tagName": "正常场景"
                }
            ],
        }
        """
        try:
            task_id = self.data.pop('taskId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        task_obj = ApiTaskInfoManager.get_task(id=task_id)
        if not task_obj:
            return make_response({"code": "301", "desc": "taskId不存在"})

        if task_obj.task_type in (1, 3):
            intf_tree, full_tree = parse_case_tree(task_obj.case_tree)
            git_diff_list = []
        else:
            intf_tree = []
            full_tree = []
            git_diff_list = []
            git_diff_objs = GitDiffVersionManager.get_git_diff_versions(api_task_id=task_obj.id)
            for git_diff_obj in git_diff_objs:
                system_obj = ApiSystemInfoManager.get_system(id=git_diff_obj.api_system_id)
                git_diff_list.append({
                    "changeSystemId": system_obj.id,
                    "changeBranchName": git_diff_obj.git_branch_name,
                    "commitStartId": git_diff_obj.old_commit_id,
                    "commitEndId": git_diff_obj.new_commit_id,
                    "gitUrl": system_obj.git_url,
                })

        tag_list = []
        try:
            related_tag_id_list = json_loads(task_obj.related_tag_id_list)
        except Exception:
            related_tag_id_list = []
        for tag_id in related_tag_id_list:
            tag_obj = TestcaseTagManager.get_testcase_tag(tag_id)
            tag_list.append(
                {
                    "tagId": tag_id,
                    "tagName": tag_obj.tag_name
                }
            )

        return make_response({
            "code": "000",
            "projectId": task_obj.api_project_id, "taskName": task_obj.task_name, "taskType": task_obj.task_type,
            "selectIntfTree": intf_tree, "selectFullTree": full_tree, "gitDiff": git_diff_list, "tags": tag_list
        })

    @developer_check
    def query_run_history(self):
        """
        Input:
        {
            "taskId": 1,
        }
        Return:
        {
            "code": "000",
            "runHistoryList": [
                {
                    "startTime": "2019-04-23 16:00:33",
                    "duration": "10分钟",
                    # "coveredIntfIdList": [],
                    # "unCoveredIntfIdList": [],
                    "totalCaseNum": 120,
                    "notRunCaseNum": 20,
                    "runCaseNum": 100,
                    "successCaseNum": 90,
                    "failCaseNum": 10,
                    "successRate": "90%",
                    "lastExecutor": "查道庆",
                    "runPercent": '',
                    "runProgress": '',
                    "envId": 14,
                    "runStatus": "运行完成",
                    "taskRunId": 88
                }
            ]
        }
        """
        try:
            task_id = self.data.pop('taskId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        task_obj = ApiTaskInfoManager.get_task(id=task_id)
        if not task_obj:
            return make_response({"code": "301", "desc": "taskId不存在"})

        run_history_list = []
        run_objs = ApiRunTaskResultManager.get_results_order_by_id_desc(api_task_id=task_id)
        for run_obj in run_objs:
            callback_obj = CeleryTaskRecordManager.get_callback_celery(api_run_task_result_id=run_obj.id)
            percent, progress, status_desc = get_task_running_progress(task_obj, run_obj)
            run_history_dic = {
                "taskRunId": run_obj.id,
                "startTime": format(run_obj.start_time),
                "totalCaseNum": run_obj.total_cases,
                "lastExecutor": get_last_executor(run_obj.creator),
                "runPercent": percent,
                "runProgress": progress,
                "runStatus": status_desc,
                "envId": run_obj.run_env_id,
            }
            # 回调任务成功
            if callback_obj.celery_task_status == 'SUCCESS':
                run_history_dic.update(
                    {
                        "duration": get_duration_msg(run_obj.start_time, run_obj.end_time),
                        # "coveredIntfIdList": json_loads(run_obj.covered_intf_id_list),
                        # "unCoveredIntfIdList": json_loads(run_obj.uncovered_intf_id_list),
                        "notRunCaseNum": run_obj.not_run_cases,
                        "runCaseNum": run_obj.run_cases,
                        "successCaseNum": run_obj.success_cases,
                        "failCaseNum": run_obj.fail_cases,
                        "successRate": calc_success_rate(run_obj.success_cases, run_obj.run_cases),
                    }
                )
            # 回调任务失败
            elif callback_obj.celery_task_status == 'ERROR':
                run_history_dic.update(
                    {
                        "duration": get_duration_msg(run_obj.start_time, run_obj.end_time),
                        "notRunCaseNum": None,
                        "runCaseNum": None,
                        "successCaseNum": None,
                        "failCaseNum": None,
                        "successRate": None,
                    }
                )
            # 回调任务等待/运行中，即测试任务运行中
            else:
                run_history_dic.update(
                    {
                        "duration": get_duration_msg(run_obj.start_time),
                        "notRunCaseNum": None,
                        "runCaseNum": None,
                        "successCaseNum": None,
                        "failCaseNum": None,
                        "successRate": None,
                    }
                )
            run_history_list.append(run_history_dic)

        return make_response({"code": "000", "runHistoryList": run_history_list})

    @developer_check
    def task_list(self):
        """
        Input:
        {
            "companyId": 1,
            "pageNo": 1,
            "pageSize": 10
        }
        Return:
        {
            "code": "000",
            "taskList": [
                {
                    "envId": 1,
                    "taskId": 1,
                    "taskName": "",
                    "taskType": 1,
                    "taskStatus": 0,
                    "projectId": 1,
                    "runCaseNum": 100,
                    "successCaseNum": 90,
                    "failCaseNum": 10,
                    "successRate": "90%",
                    "lastDuration": "10分钟",
                    "lastRunTime": "2019-04-23 16:00:33",
                    "lastExecutor": "查道庆",
                    "creator": "何剑豪",
                    "totalCaseNum": 100,
                    "runPercent": '',
                    "runProgress": '',
                    "envId": 14,
                    "lastRunStatus": "运行中"
                }
            ]
        }
        """
        try:
            company_id = self.data.pop('companyId')
            page_no = self.data.pop('pageNo', None)
            page_size = self.data.pop('pageSize', None)
            keywords = self.data.pop('keyWords', None)
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})
        # start_time = time.time()

        task_list = []
        task_not_run_list = []
        # project_objs = ApiProjectInfoManager.get_projects(api_company_id=company_id)
        # project_id_list = [project_obj.id for project_obj in project_objs]
        # task_objs = ApiTaskInfoManager.get_tasks_in_project_id_list(project_id_list)
        task_objs = ApiTaskInfoManager.get_tasks_paginate(page_no, page_size, company_id, keywords=keywords)
        total_num = task_objs.total
        # t1 = time.time()
        # d1 = t1 - start_time
        # print("==== Finish [t1], run {:.3}s ====\n".format(d1))

        table_data = get_table_data()
        global GL_CACHE_TESTCASE_CHAIN_DICT
        # 用例-调用链dict缓存重置
        GL_CACHE_TESTCASE_CHAIN_DICT = {}
        for task_obj in task_objs.items:
            task_dic = {
                "taskId": task_obj.id,
                "taskName": task_obj.task_name,
                "taskType": task_obj.task_type,
                "taskStatus": task_obj.task_status,
                "projectId": task_obj.api_project_id,
                "runCaseNum": 0,
                "successCaseNum": 0,
                "failCaseNum": 0,
                "successRate": "",
                "lastDuration": "",
                "lastRunTime": "",
                "lastExecutor": "",
                "lastRunStatus": "未运行",
                "envId": None,
                "creator": username_to_nickname(task_obj.creator),
                "totalCaseNum": 0,
                "runPercent": '',
                "runProgress": '',
            }

            # 仅在任务状态为可运行时计算总用例数
            if task_obj.task_status == 1:
                total = count_testcase_total(task_obj, table_data, GL_CACHE_TESTCASE_CHAIN_DICT)
                print(GL_CACHE_TESTCASE_CHAIN_DICT)
                # total = 0
                # intf_testcases_map = {}
                # if task_obj.task_type == 1:
                #     intf_id_list, product_line_id_list = parse_case_tree(task_obj.case_tree)
                #     for intf_id in intf_id_list:
                #         # total += len(get_testcase_id_list_filter_by_tag(task_obj.related_tag_id_list, intf_id=intf_id))
                #         testcase_id_list = get_testcase_id_list_filter_by_tag(task_obj.related_tag_id_list, intf_id=intf_id)
                #         intf_testcases_map[intf_id] = testcase_id_list
                #     for product_line_id in product_line_id_list:
                #         total += len(get_testcase_id_list_filter_by_tag(
                #             task_obj.related_tag_id_list, product_line_id=product_line_id))
                # else:
                #     intf_id_list = json_loads(task_obj.effect_intf_id_list)
                #     for intf_id in intf_id_list:
                #         # total += len(get_testcase_id_list_filter_by_tag(task_obj.related_tag_id_list, intf_id=intf_id))
                #         testcase_id_list = get_testcase_id_list_filter_by_tag(task_obj.related_tag_id_list, intf_id=intf_id)
                #         intf_testcases_map[intf_id] = testcase_id_list
                #
                # # 接口用例智能去重
                # filtered_intf_testcases_map = smart_filter_testcase(
                #     intf_testcases_map, table_data=testcase_id_map_to_setup_case_data)
                # for testcase_list in filtered_intf_testcases_map.values():
                #     total += len(testcase_list)

                task_dic["totalCaseNum"] = total

            # 是否有运行记录
            last_run_obj = ApiRunTaskResultManager.get_last_result_by_task_id(task_obj.id)
            if last_run_obj:
                percent, progress, last_run_status = get_task_running_progress(task_obj, last_run_obj)
                task_dic["lastRunTime"] = format(last_run_obj.start_time)
                task_dic["lastExecutor"] = get_last_executor(last_run_obj.creator)
                task_dic["lastRunStatus"] = last_run_status
                task_dic["runPercent"] = percent
                task_dic["runProgress"] = progress
                task_dic["envId"] = last_run_obj.run_env_id
                if last_run_obj.end_time:
                    task_dic["runCaseNum"] = last_run_obj.run_cases
                    task_dic["successCaseNum"] = last_run_obj.success_cases
                    task_dic["failCaseNum"] = last_run_obj.fail_cases
                    task_dic["successRate"] = calc_success_rate(last_run_obj.success_cases, last_run_obj.run_cases)
                    task_dic["lastDuration"] = get_duration_msg(last_run_obj.start_time, last_run_obj.end_time)
                    task_dic["lastRunStatus"] = last_run_status
            task_list.append(task_dic)

        # t2 = time.time()
        # d2 = t2 - t1
        # print("==== Finish [t2], run {:.3}s ====\n".format(d2))

        # bubble_sort_by_last_run_time(task_list)
        # task_list.extend(task_not_run_list)

        # t3 = time.time()
        # d3 = t3 - t2
        # print("==== Finish [t23], run {:.3}s ====\n".format(d3))

        return make_response({"code": "000", "total": total_num, "taskList": task_list})

    @developer_check
    def list_smoking_task(self):
        """
        返回冒烟测试任务列表
        Input:
        {
            "companyId": 1,
            "pageNo": 1,
            "pageSize": 10,
            "keyWords": "loan-web"
        }
        Return:
        {
            "code": "000",
            "taskList": [
                {
                    "envId": 1,
                    "taskId": 1,
                    "taskName": "",
                    "taskType": 1,
                    "taskStatus": 0,
                    "projectId": 1,
                    "runCaseNum": 100,
                    "successCaseNum": 90,
                    "failCaseNum": 10,
                    "successRate": "90%",
                    "lastDuration": "10分钟",
                    "lastRunTime": "2019-04-23 16:00:33",
                    "lastExecutor": "查道庆",
                    "creator": "何剑豪",
                    "totalCaseNum": 100,
                    "runPercent": '',
                    "runProgress": '',
                    "envId": 14,
                    "lastRunStatus": "运行中",
                    "createTime": "2019-04-23 16:00:33",
                    "updateTime": "2019-04-23 16:00:33",
                }
            ]
        }
        """
        try:
            company_id = self.data.pop('companyId')
            page_no = self.data.pop('pageNo', 1)
            page_size = self.data.pop('pageSize', 10)
            keywords = self.data.pop('keyWords', None)
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        task_list = []
        task_objs = ApiTaskInfoManager.get_smoking_tasks_paginate(page_no, page_size, company_id, keywords=keywords)
        total_num = task_objs.total
        table_data = get_table_data()
        global GL_CACHE_TESTCASE_CHAIN_DICT
        # 用例-调用链dict缓存重置
        GL_CACHE_TESTCASE_CHAIN_DICT = {}
        for task_obj in task_objs.items:
            task_dic = {
                "taskId": task_obj.id,
                "taskName": task_obj.task_name,
                "taskType": task_obj.task_type,
                "taskStatus": task_obj.task_status,
                "projectId": task_obj.api_project_id,
                "runCaseNum": 0,
                "successCaseNum": 0,
                "failCaseNum": 0,
                "successRate": "",
                "lastDuration": "",
                "lastRunTime": "",
                "lastExecutor": "",
                "lastRunStatus": "未运行",
                "envId": None,
                "creator": username_to_nickname(task_obj.creator),
                "totalCaseNum": 0,
                "runPercent": '',
                "runProgress": '',
                "createTime": format(task_obj.create_time),
                "updateTime": format(task_obj.update_time) if task_obj.update_time else ""
            }

            # 是否有运行记录
            last_run_obj = ApiRunTaskResultManager.get_last_result_by_task_id(task_obj.id)
            if last_run_obj:
                percent, progress, last_run_status = get_task_running_progress(task_obj, last_run_obj)
                task_dic["lastRunTime"] = format(last_run_obj.start_time)
                task_dic["lastExecutor"] = get_last_executor(last_run_obj.creator)
                task_dic["lastRunStatus"] = last_run_status
                task_dic["runPercent"] = percent
                task_dic["runProgress"] = progress
                task_dic["envId"] = last_run_obj.run_env_id
                if last_run_obj.end_time:
                    task_dic["runCaseNum"] = last_run_obj.run_cases
                    task_dic["successCaseNum"] = last_run_obj.success_cases
                    task_dic["failCaseNum"] = last_run_obj.fail_cases
                    task_dic["successRate"] = calc_success_rate(last_run_obj.success_cases, last_run_obj.run_cases)
                    task_dic["lastDuration"] = get_duration_msg(last_run_obj.start_time, last_run_obj.end_time)
                    task_dic["lastRunStatus"] = last_run_status

            # 仅在任务状态为可运行时计算总用例数
            if task_obj.task_status == 1:
                # 任务运行状态为未运行时，按用例表和标签表进行计算, 其他状态直接从任务运行记录表中获取
                if not last_run_obj:
                    total = count_testcase_total(task_obj, table_data, GL_CACHE_TESTCASE_CHAIN_DICT)
                    print(GL_CACHE_TESTCASE_CHAIN_DICT)
                else:
                    total = last_run_obj.total_cases

                task_dic["totalCaseNum"] = total

            task_list.append(task_dic)

        return make_response({"code": "000", "total": total_num, "taskList": task_list})

    @developer_check
    def list_regression_task(self):
        """
        返回回归测试任务列表
        Input:
        {
            "companyId": 1,
            "pageNo": 1,
            "pageSize": 10,
            "keyWords": "loan-web"
        }
        Return:
        {
            "code": "000",
            "taskList": [
                {
                    "envId": 1,
                    "taskId": 1,
                    "taskName": "",
                    "taskType": 1,
                    "taskStatus": 0,
                    "projectId": 1,
                    "runCaseNum": 100,
                    "successCaseNum": 90,
                    "failCaseNum": 10,
                    "successRate": "90%",
                    "lastDuration": "10分钟",
                    "lastRunTime": "2019-04-23 16:00:33",
                    "lastExecutor": "查道庆",
                    "creator": "何剑豪",
                    "totalCaseNum": 100,
                    "runPercent": '',
                    "runProgress": '',
                    "envId": 14,
                    "lastRunStatus": "运行中",
                    "createTime": "2019-04-23 16:00:33",
                    "updateTime": "2019-04-23 16:00:33",
                }
            ]
        }
        """
        try:
            company_id = self.data.pop('companyId')
            page_no = self.data.pop('pageNo', 1)
            page_size = self.data.pop('pageSize', 10)
            keywords = self.data.pop('keyWords', None)
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        task_list = []
        task_objs = ApiTaskInfoManager.get_regression_tasks_paginate(page_no, page_size, company_id, keywords=keywords)
        total_num = task_objs.total
        table_data = get_table_data()
        global GL_CACHE_TESTCASE_CHAIN_DICT
        # 用例-调用链dict缓存重置
        GL_CACHE_TESTCASE_CHAIN_DICT = {}
        for task_obj in task_objs.items:
            task_dic = {
                "taskId": task_obj.id,
                "taskName": task_obj.task_name,
                "taskType": task_obj.task_type,
                "taskStatus": task_obj.task_status,
                "projectId": task_obj.api_project_id,
                "runCaseNum": 0,
                "successCaseNum": 0,
                "failCaseNum": 0,
                "successRate": "",
                "lastDuration": "",
                "lastRunTime": "",
                "lastExecutor": "",
                "lastRunStatus": "未运行",
                "envId": None,
                "creator": username_to_nickname(task_obj.creator),
                "totalCaseNum": 0,
                "runPercent": '',
                "runProgress": '',
                "createTime": format(task_obj.create_time),
                "updateTime": format(task_obj.update_time) if task_obj.update_time else ""
            }

            # 是否有运行记录
            last_run_obj = ApiRunTaskResultManager.get_last_result_by_task_id(task_obj.id)
            if last_run_obj:
                percent, progress, last_run_status = get_task_running_progress(task_obj, last_run_obj)
                task_dic["lastRunTime"] = format(last_run_obj.start_time)
                task_dic["lastExecutor"] = get_last_executor(last_run_obj.creator)
                task_dic["lastRunStatus"] = last_run_status
                task_dic["runPercent"] = percent
                task_dic["runProgress"] = progress
                task_dic["envId"] = last_run_obj.run_env_id
                if last_run_obj.end_time:
                    task_dic["runCaseNum"] = last_run_obj.run_cases
                    task_dic["successCaseNum"] = last_run_obj.success_cases
                    task_dic["failCaseNum"] = last_run_obj.fail_cases
                    task_dic["successRate"] = calc_success_rate(last_run_obj.success_cases, last_run_obj.run_cases)
                    task_dic["lastDuration"] = get_duration_msg(last_run_obj.start_time, last_run_obj.end_time)
                    task_dic["lastRunStatus"] = last_run_status

            # 仅在任务状态为可运行时计算总用例数
            if task_obj.task_status == 1:
                # 任务运行状态为未运行时，按用例表和标签表进行计算, 其他状态直接从任务运行记录表中获取
                if not last_run_obj:
                    total = count_testcase_total(task_obj, table_data, GL_CACHE_TESTCASE_CHAIN_DICT)
                    print(GL_CACHE_TESTCASE_CHAIN_DICT)
                else:
                    total = last_run_obj.total_cases

                task_dic["totalCaseNum"] = total

            task_list.append(task_dic)

        return make_response({"code": "000", "total": total_num, "taskList": task_list})

    @developer_check
    def get_task_running_progress(self):
        """
            Input:
            {
                "taskId": 1,
            }
            Return:
            {
                "code": "000",
                "percent": "50%"/"0%"/"100%"
                "progress": "5/10"/"0/10"/"10/10"
                "desc": "运行中"/"未运行"/"运行完成"
            }
        """
        try:
            task_id = self.data.pop('taskId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        task_obj = ApiTaskInfoManager.get_task(id=task_id)
        if not task_obj:
            return make_response({"code": "301", "desc": "taskId不存在"})

        last_run_obj = ApiRunTaskResultManager.get_last_result_by_task_id(task_id)

        percent, progress, desc = get_task_running_progress(task_obj, last_run_obj)

        return make_response({"code": "000", "desc": desc, "percent": percent, "progress": progress})

    @login_check
    def get_uncovered_info(self):
        """
            Input:
            {
                "taskId": 1,
            }
            Return:
            {
                "code": "000",
                "uncoveredList": [
                    {
                        "intfName": "***.",
                        "type": "mq"
                    },
                    {
                        "intfName": ".方法名称",
                        "type": "dubbo"
                    },
                    {
                        "intfName": "/user/submit",
                        "type": "http"
                    },
                    {
                        "intfName": ".方法名称",
                        "type": "elasticJob"
                    }
                ]
            }
        """
        try:
            task_id = self.data.pop('taskId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        task_obj = ApiTaskInfoManager.get_task(id=task_id)
        if not task_obj:
            return make_response({"code": "301", "desc": "taskId不存在"})

        uncovered_list = []

        uncovered_info_dic = json_loads(task_obj.uncovered_info) if task_obj.uncovered_info else {}
        for type_, intf_name_list in uncovered_info_dic.items():
            for intf_name in intf_name_list:
                uncovered_list.append({"intfName": intf_name, 'type': type_})

        return make_response({"code": "000", "uncoveredList": uncovered_list})

    # @login_check
    def get_summary(self):
        """
            Input:
            {
                "taskRunId": 88,
            }
            Return:
            {
                "code": "000",
                "base": {
                    "succCaseNum": 3,
                    "succRate": "75%",
                    "taskName": "测试回归任务人工指定1",
                    "testDuration": "32秒",
                    "testEndTime": "2019-05-09 10:39:49",
                    "testStartTime": "2019-05-09 10:39:17",
                    "totalCaseNum": 4
                },
                "fullLinkSummary": [
                    {
                        "failCaseNum": 0,
                        "productLineId": 17,
                        "productLineName": "钱包",
                        "runCaseNum": 1,
                        "succCaseNum": 1,
                        "succRate": "100%",
                        "tableData": [
                            {
                                "caseId": 53,
                                "caseName": "手机验证码登录",
                                "failReason": "",
                                "testResult": "成功"
                            }
                        ]
                    }
                ],
                "intfSummary": [
                    {
                        "children": [
                            {
                                "failCaseNum": 1,
                                "intfId": 814,
                                "intfName": "ATP接口querySignFunctions-/atp/auto/support/querySignFunctions",
                                "runCaseNum": 2,
                                "succCaseNum": 1,
                                "succRate": "50%",
                                "tableData": [
                                    {
                                        "caseId": 5143,
                                        "caseName": "获取sign方法2",
                                        "failReason": "结果验证失败",
                                        "testResult": "失败"
                                    }
                                ]
                            }
                        ],
                        "failCaseNum": 1,
                        "runCaseNum": 4,
                        "succCaseNum": 3,
                        "succRate": "75%",
                        "systemId": 31,
                        "systemName": ""
                    }
                ]
            }
        """
        try:
            task_run_id = self.data.pop('taskRunId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        run_obj = ApiRunTaskResultManager.get_result(id=task_run_id)
        if not run_obj:
            return make_response({"code": "301", "desc": "taskRunId不存在"})

        summary_file_path = from_run_id_to_summary_file_path(task_run_id)
        res = parse_summary_file(summary_file_path)

        if res == "summary文件不存在":
            return make_response({"code": "401", "desc": "summary文件不存在"})
        intf_summary_list, full_summary_list = res

        # 增加base信息
        task_obj = ApiTaskInfoManager.get_task(id=run_obj.api_task_id)
        base = {
            'taskName': task_obj.task_name if task_obj else '<任务已删除>',
            'totalCaseNum': run_obj.run_cases,
            'succCaseNum': run_obj.success_cases,
            'failCaseNum': run_obj.fail_cases,
            'succRate': calc_success_rate(run_obj.success_cases, run_obj.run_cases),
            'testStartTime': format(run_obj.start_time),
            'testEndTime': format(run_obj.end_time),
            'testDuration': get_duration_msg(run_obj.start_time, run_obj.end_time)
        }
        return make_response({"code": "000",
                              "intfSummary": intf_summary_list, "fullLinkSummary": full_summary_list, 'base': base})

    # @login_check
    def get_run_data_by_testcase(self):
        """
        Input:
        {
            "taskRunId": 98,
            "testcaseId": 5143,
            "testcaseMainId": null
        }
        Return:
        {
            "code": "000",
            "runData": [
                {
                    "name": "标题1",
                    "request": {},
                    "response": {},
                    "validators": [
                        {}
                    ],
                    "failReason": "",
                    "failDetail": ""
                }
            ]
        }
        """

        try:
            task_run_id = self.data.pop('taskRunId')
            testcase_id = self.data.pop('testcaseId', None)
            testcase_main_id = self.data.pop('testcaseMainId', None)
            if not testcase_id and not testcase_main_id:
                raise KeyError
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        summary_file_path = from_run_id_to_summary_file_path(task_run_id)

        try:
            with open(summary_file_path, 'r') as f:
                summary_list_str = f.readline()
                summary_list = json_loads(summary_list_str)
        except FileNotFoundError:
            return make_response({"code": "401", "desc": "summary文件不存在"})

        run_data_list = []
        if testcase_id:
            for summary in summary_list:
                if 'summary' not in summary:
                    continue
                if 'product_line_id' in summary['summary']:
                    continue
                for detail in summary['summary']['details']:
                    if detail['case_id'] == testcase_id:
                        for record in detail['records']:
                            filtered_request = filter_request_or_response(request=record['meta_data']['request'])
                            filtered_response = filter_request_or_response(response=record['meta_data']['response'])
                            filtered_validators = filter_validators(validators=record['meta_data']['validators'])
                            run_data_list.append(
                                {
                                    "name": record['name'],
                                    "request": filtered_request,
                                    "response": filtered_response,
                                    "validators": filtered_validators,
                                    "failReason": record['error_type'],
                                    "failDetail": record['attachment']
                                }
                            )
                        break
        else:
            for summary in summary_list:
                if 'summary' not in summary:
                    continue
                if 'product_line_id' not in summary['summary']:
                    continue
                for detail in summary['summary']['details']:
                    if detail['case_id'] == testcase_main_id:
                        for record in detail['records']:
                            filtered_request = filter_request_or_response(request=record['meta_data']['request'])
                            filtered_response = filter_request_or_response(response=record['meta_data']['response'])
                            filtered_validators = filter_validators(validators=record['meta_data']['validators'])
                            run_data_list.append(
                                {
                                    "name": record['name'],
                                    "request": filtered_request,
                                    "response": filtered_response,
                                    "validators": filtered_validators,
                                    "failReason": record['error_type'],
                                    "failDetail": record['attachment']
                                }
                            )
                        break

        return make_response({"code": "000", "runData": run_data_list})

    @login_check
    def get_run_results(self):
        """
            Input:
            {
                "companyId": 1,
            }
            Return:
            {
                "code": "000",
                "dataList": [
                    {
                        "runDate": "2019-05-13",
                        "runTaskNum": 5,
                        "totalCaseNum": 40,
                        "notRunCaseNum": 0,
                        "runCaseNum": 40,
                        "failCaseNum": 10,
                        "succCaseNum": 30,
                        "succRate": "75%",
                        "runStatusDesc": "通过"/"失败",
                    }
                ]
            }
        """
        try:
            company_id = self.data.pop('companyId')
            recent_days = self.data.pop('recentDays', None)
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        if not recent_days:
            res_list = ApiRunTaskResultManager.get_results_group_by_run_date_in_company_ignore_project(
                company_id, recent_days=30)
        else:
            res_list = ApiRunTaskResultManager.get_results_group_by_run_date_in_company_ignore_project(
                company_id, recent_days=recent_days)

        date_list = []
        for row in res_list:
            total_cases = int(row[2]) if row[2] else 0
            not_run_cases = int(row[3]) if row[3] else 0
            run_cases = int(row[4]) if row[4] else 0
            success_cases = int(row[5]) if row[5] else 0
            fail_cases = int(row[6]) if row[6] else 0
            succ_rate = calc_success_rate(success_cases, run_cases)
            date_list.append(
                {
                    "runDate": format(row[0]),
                    "runTaskNum": row[1],
                    "totalCaseNum": total_cases,
                    "notRunCaseNum": not_run_cases,
                    "runCaseNum": run_cases,
                    "succCaseNum": success_cases,
                    "failCaseNum": fail_cases,
                    "succRate": succ_rate,
                    "runStatusDesc": "通过" if succ_rate == '100%' else '失败'
                }
            )
        return make_response({"code": "000", "dataList": date_list})

    @login_check
    def get_run_result_by_single_day(self):
        """
            Input:
            {
                "companyId": 1,
                "runDate": "2019-05-13",
            }
            Return:
            {
                "code": "000",
                "dataList": [
                    {
                        "taskRunId": 1,
                        "envName": "ALIUAT",
                        "taskName": "",
                        "taskType": 1,
                        "projectName": "项目1",
                        "totalCaseNum": 100,
                        "runCaseNum": 100,
                        "succCaseNum": 90,
                        "failCaseNum": 10,
                        "successRate": "90%",
                        "duration": "10分钟",
                        "runTime": "2019-04-23 16:00:33",
                        "executor": "查道庆",
                    }
                ]
            }
        """
        try:
            company_id = self.data.pop('companyId')
            run_date_str = self.data.pop('runDate')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        run_date = datetime.strptime(run_date_str, "%Y-%m-%d")

        res_list = ApiRunTaskResultManager.get_results_by_run_date_in_company(company_id, run_date=run_date)
        res_list_without_project = ApiRunTaskResultManager.get_results_by_run_date_in_company_ignore_project(
            company_id, run_date=run_date)
        res_list.extend(res_list_without_project)

        date_list = []
        for row in res_list:
            date_list.append(
                {
                    "taskRunId": row[0],
                    "taskName": row[1],
                    "taskType": row[2],
                    "projectName": row[3] if row[3] else '',
                    "totalCaseNum": row[4],
                    "notRunCaseNum": row[5],
                    "runCaseNum": row[6],
                    "succCaseNum": row[7],
                    "failCaseNum": row[8],
                    "successRate": calc_success_rate(row[7], row[6]),
                    "duration": get_duration_msg(row[9], row[10]),
                    "runTime": format(row[9]),
                    "executor": row[11],
                    "envName": row[12],
                }
            )
        return make_response({"code": "000", "dataList": date_list})

    @login_check
    def export_summary_to_excel(self):
        """
            Input:
            {
                "runDate": "2019-05-13",
                "taskRunIdList": [1, 2, 3]
            }
            Return:
            {
                "code": "000",
                "fileName": ""
            }
            """
        try:
            run_date = self.data.pop('runDate')
            run_id_list = self.data.pop('taskRunIdList')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        value_lists = [[
            '测试任务名称',
            '系统',
            '接口',
            '产品线',
            '用例ID',
            '用例标题',
            '测试结果',
            '错误分类',
            '错误详情'
        ]]
        for run_id in run_id_list:
            run_obj = ApiRunTaskResultManager.get_result(id=run_id)
            task_obj = ApiTaskInfoManager.get_task(id=run_obj.api_task_id)

            summary_file_path = from_run_id_to_summary_file_path(run_id)
            res = parse_summary_file(summary_file_path, with_attachment=True)
            if res == 'summary文件不存在':
                continue
            intf_summary_list, full_summary_list = res
            for intf_summary in intf_summary_list:
                for intf_dic in intf_summary['children']:
                    for case_dic in intf_dic['tableData']:
                        value_lists.append(
                            [
                                task_obj.task_name,
                                intf_summary['systemName'],
                                intf_dic['intfName'],
                                '',
                                case_dic['caseId'],
                                case_dic['caseName'],
                                case_dic['testResult'],
                                case_dic['failReason'],
                                case_dic['failDetail']
                            ]
                        )
            for product_line_summary in full_summary_list:
                for case_dic in product_line_summary['tableData']:
                    value_lists.append(
                        [
                            task_obj.task_name,
                            '',
                            '',
                            product_line_summary['productLineName'],
                            case_dic['caseId'],
                            case_dic['caseName'],
                            case_dic['testResult'],
                            case_dic['failReason'],
                            case_dic['failDetail']
                        ]
                    )

        ep = ExcelParser(run_date)
        file_name = ep.write_summary_to_excel(run_date=run_date, value_lists=value_lists)
        print(file_name)
        return make_response({"code": "000", "fileName": file_name})

    @login_check
    def export_smoking_test_log_to_excel(self):
        """
        导出冒烟测试列表数据
            Input:
            {
                "companyId": 1,
                "pageNo": 1,
                "pageSize": 10,
                "keyWords": "loan-web"
            }
            Return:
            {
                "code": "000",
                "fileName": ""
            }
            """
        resp = self.list_smoking_task()
        res = json.loads(resp.data)
        if res['code'] != '000':
            return make_response({"code": res['code'], "desc": res['desc']})

        if not res['total']:
            return make_response({"code": "100", "desc": "查询不到可供导出的内容"})

        value_list = [[
            '任务ID',
            '任务名称',
            '测试范围',
            '总用例数',
            '最近一次成功率',
            '运行环境',
            '运行耗时',
            '任务状态',
            '运行开始时间',
            '创建时间',
            '更新时间'
        ]]
        for task_info in res['taskList']:
            value_list.append([
                task_info['taskId'],
                task_info['taskName'],
                '冒烟用例',
                task_info['totalCaseNum'],
                task_info['successRate'],
                'SIT',
                task_info['lastDuration'],
                task_info['lastRunStatus'],
                task_info['lastRunTime'],
                task_info['createTime'],
                task_info['updateTime']
            ])

        ep = ExcelParser("smoking")
        file_name = ep.write_smoking_test_log_to_excel("smoking", value_list)
        print(file_name)
        return make_response({"code": "000", "fileName": file_name})

    @developer_check
    def re_collect_task_result(self):
        try:
            run_task_id = self.data.pop('taskRunId')
        except (KeyError, ValueError):
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        collector = TaskResultCollector(run_task_id=run_task_id)
        res = collector.re_save_task_results()
        if res[0]:
            return make_response({"code": "20{}".format(res[0]), "desc": res[1]})

        return make_response({"code": "000", "desc": res[1]})

    # @developer_check
    def run_task(self):
        """
        Input:
        {
            "taskId": 1,
            "envId": 1,
            "times": 1,       #运行次数, 非必填, 正整数, 默认1
            "runMainCaseInParallel": true,   #全链路用例是否按单条用例并发运行, 非必填, 默认false
            "preCheckServerTime": true,  #是否检查服务器时间, 非必填, 默认true
            "preCorrectServerTime": true,  #是否自动修正服务器时间, 非必填, 仅preCheckServerTime为true时值生效, 默认false
            "preClearRecentData": true,  #是否清理最近生成的自动化数据, 非必填, 默认true
            "failedRetry": true, 是否为失败用例重试运行, 非必填, 默认false
            "taskRunId": 333,  任务运行id, 当failedRetry为true时必填
        }
        Return:
        {
            "code": "000",
            "desc": "测试任务正在运行..."
        }
        """
        try:
            task_id = self.data.pop('taskId')
            env_id = self.data.pop('envId')
            times = int(self.data.pop('times', 1))
            run_main_case_in_parallel = self.data.pop('runMainCaseInParallel', False)
            pre_check_server_time = self.data.pop('preCheckServerTime', True)
            pre_correct_server_time = self.data.pop('preCorrectServerTime', False)
            pre_clear_recent_data = self.data.pop('preClearRecentData', True)
            failed_retry = self.data.pop('failedRetry', False)
            if failed_retry:
                times = 1
                run_task_id = self.data.pop('taskRunId')
        except (KeyError, ValueError):
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        if times > 100:
            return make_response({"code": "402", "desc": "循环次数过多(大于100)"})

        task_obj = ApiTaskInfoManager.get_task(id=task_id)
        if not task_obj:
            return make_response({"code": "301", "desc": "不存在的taskId"})

        if not task_obj.task_status:
            return make_response({"code": "401", "desc": "测试任务状态为不可执行"})

        env_obj = EnvInfoManager.get_env(id=env_id)
        if not env_obj:
            return make_response({"code": "302", "desc": "不存在的envId"})

        # 更新短信配置至关闭状态
        disconf_map = {"ALIUAT": 588, "SIT": 588}

        disconf_id = None
        for key,value in disconf_map.items():
            if env_obj.env_name == key:
                disconf_id = value
                break
        if disconf_id:
            edit_disconf_value(env_obj.disconf_host,disconf_id,"sms.switch","0")


        # 检查服务器时间是否当前时间
        if pre_check_server_time:
            # 获取待检查的服务器列表和默认用户
            env_obj = EnvInfoManager.get_env(id=env_id)
            if not env_obj:
                return make_response({"code": "302", "desc": "不存在的envId"})

            if not env_obj.server_app_map:
                server_app_map_dic = {}
                server_default_user_dic = {}
            else:
                try:
                    server_app_map_dic = json_loads(env_obj.server_app_map)
                    server_default_user_dic = json_loads(env_obj.server_default_user)
                except (TypeError, json.decoder.JSONDecodeError):
                    return make_response({"code": "303", "desc": "环境配置信息（server_app_map/server_default_user）存在错误"})

            wrong_server_time_dic = {}
            for server_ip in server_app_map_dic:
                server_info_list = [server_ip, 22, server_default_user_dic['user'], server_default_user_dic['password']]

                cmd_get_current_timestamp = 'date +%s'
                try:
                    with SSHClient(server_info_list) as sc:
                        server_timestamp = int(sc.exec_cmd(cmd_get_current_timestamp))
                except Exception as e:
                    logger.error(traceback.format_exc())
                    return make_response({"code": "403", "desc": repr(e)})

                local_timestamp = get_current_timestamp()
                if server_timestamp > local_timestamp:
                    difference_second = server_timestamp - local_timestamp
                else:
                    difference_second = local_timestamp - server_timestamp
                if difference_second > 120:
                    time_str = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(server_timestamp)))
                    wrong_server_time_dic[server_ip] = time_str

            if wrong_server_time_dic:
                if pre_correct_server_time is True:
                    for server_ip in wrong_server_time_dic:
                        server_info_list = [
                            server_ip, 22, server_default_user_dic['user'], server_default_user_dic['password']
                        ]
                        time_str = get_current_time(time_format='%H:%M:%S %Y-%m-%d')
                        cmd_correct_time = 'sudo date -s "{}"'.format(time_str)

                        try:
                            with SSHClient(server_info_list) as sc:
                                out_log = sc.run_cmd(cmd_correct_time)
                        except Exception as e:
                            logger.error(traceback.format_exc())
                            return make_response({"code": "403", "desc": repr(e)})
                        logger.debug('已自动修改服务器{0}时间，修改为:{1}, 服务器返回:{2}'.format(server_ip, time_str, out_log))
                else:
                    desc = "存在下列应用服务器与ATP服务器时间相差超过2分钟:"
                    for server_ip, time_str in wrong_server_time_dic.items():
                        desc += "\n【服务器ip:{0}, 时间:{1}】".format(server_ip, time_str)
                    return make_response({"code": "403", "desc": desc})

        kwargs = {
            "env_id": env_id,
            "executor": self.username,
            "times": times,
            "run_main_case_in_parallel": run_main_case_in_parallel,
            # "reboot_sleep": reboot_sleep
        }
        api_runner = ApiRunner(**kwargs)
        try:
            if not failed_retry:
                callback_celery_no = api_runner.run_task(task_id)
            else:
                # 最新一次运行的失败用例重新运行
                summary_file_path = from_run_id_to_summary_file_path(run_task_id)
                res = parse_summary_file(summary_file_path, with_attachment=False)
                if res == 'summary文件不存在':
                    return make_response({"code": "202", "desc": res})

                failed_intf_dic, failed_full_dic = get_failed_info(res)
                if not (failed_intf_dic or failed_full_dic):
                    return make_response({"code": "701", "desc": "没有失败的用例，任务未运行"})

                callback_celery_no = api_runner.run_task_failed_retry(task_id, failed_intf_dic, failed_full_dic)
        except Exception as err:
            logger.error(traceback.format_exc())
            return make_response({"code": "601", "desc": "拆分测试任务时发生异常，请检查日志"})

        if not callback_celery_no:
            return make_response({"code": "501", "desc": "测试任务没有可执行用例, 任务未运行"})

        return make_response({"code": "000", "desc": "测试任务正在运行...", "callbackCeleryNo": callback_celery_no})


def get_duration_msg(start_time, end_time=None):
    """获取时长文字"""
    if not end_time:
        end_time = datetime.now()
    duration_seconds = (end_time - start_time).seconds
    if duration_seconds >= 60:
        duration_minutes = int(duration_seconds / 60)
        if duration_minutes >= 720:
            return "超过12小时未收集到结果"
        delta_seconds = duration_seconds % 60
        return "{0}分钟{1}秒".format(duration_minutes, delta_seconds)
    else:
        return "{}秒".format(duration_seconds)


def calc_success_rate(success, total):
    """计算成功率"""
    if not total:
        return None
    if not success:
        success = 0
    return "{}%".format(int(success * 100 / total))


def parse_case_tree(case_tree):
    tree_dic = json_loads(case_tree)
    intf_id_list = tree_dic.get('intf_id_list', [])
    product_line_id_list = tree_dic.get('product_line_id_list', [])
    return intf_id_list, product_line_id_list


def get_task_running_progress(task_obj, run_obj):
    """获取测试任务某次运行进度信息"""

    if not run_obj:
        percent = '0%'
        progress = '0/0'
        desc = '未运行'
    else:
        if run_obj.worker_num:
            total = run_obj.worker_num
        else:
            total = 0

        if run_obj.end_time:
            percent = '100%'
            progress = '{0}/{0}'.format(total)
            desc = '运行完成'
        else:
            celery_success_objs = CeleryTaskRecordManager.get_celeries(
                api_run_task_result_id=run_obj.id, celery_task_status='_success')
            celery_error_objs = CeleryTaskRecordManager.get_celeries(
                api_run_task_result_id=run_obj.id, celery_task_status='_error')
            success_num = len(celery_success_objs)
            error_num = len(celery_error_objs)
            finish_num = success_num + error_num
            if total:
                percent = '{}%'.format(int(finish_num * 100 / total))
            else:
                percent = '0%'
            progress = '{0}({1})/{2}'.format(finish_num, error_num, total)
            desc = '运行中(有任务异常退出)' if error_num else '运行中'

    return percent, progress, desc


def parse_summary_file(summary_file_path, with_attachment=False):
    """处理summary_file，返回intf_summary_list, full_summary_list"""
    # 接口用例summary
    intf_summary_list = []
    # 全链路用例summary
    full_summary_list = []
    try:
        with open(summary_file_path, 'r') as f:
            summary_list_str = f.readline()
            summary_list = json_loads(summary_list_str)
    except FileNotFoundError:
        return "summary文件不存在"

    for summary_dic in summary_list:
        if 'summary' not in summary_dic:
            continue
        # 接口用例
        if 'system_id' in summary_dic['summary']:
            system_id = summary_dic['summary']['system_id']
            system_name = summary_dic['summary']['system_name']
            intf_id = summary_dic['summary']['intf_id']
            intf_name = summary_dic['summary']['intf_name']
            table_data = []
            for detail in summary_dic['summary']['details']:
                if detail['stat']['failures']:
                    test_result = '失败'
                    fail_reason = ''
                    fail_detail = []
                    for record in detail['records']:
                        error_type = record.get('error_type', None)
                        attachment = record.get('attachment', None)
                        if error_type:
                            fail_reason = fail_reason + error_type + ', '
                            fail_detail.append(attachment)
                    fail_reason = fail_reason.strip().strip(',')
                    fail_detail = json_dumps(fail_detail)
                else:
                    test_result = '成功' if len(detail['records'][-1]['meta_data']['validators']) != 0 else '成功-无断言'
                    fail_reason = ''
                    fail_detail = ''
                table_data_dic = {
                    'caseId': detail['case_id'],
                    'caseName': detail['name'],
                    'testResult': test_result,
                    'failReason': fail_reason,
                }
                if with_attachment:
                    table_data_dic['failDetail'] = fail_detail
                table_data.append(table_data_dic)
            intf_dic = {
                'intfId': intf_id,
                'intfName': intf_name,
                'runCaseNum': summary_dic['summary']['stat']['testsRun'],
                'succCaseNum': summary_dic['summary']['stat']['successes'],
                'failCaseNum': summary_dic['summary']['stat']['failures'],
                'succRate': calc_success_rate(summary_dic['summary']['stat']['successes'],
                                              summary_dic['summary']['stat']['testsRun']),
                'tableData': table_data
            }
            is_system_exist = False
            for simple_summary in intf_summary_list:
                if simple_summary['systemId'] == system_id:
                    is_system_exist = True
                    simple_summary['children'].append(intf_dic)
                    break
            if not is_system_exist:
                intf_summary_list.append(
                    {
                        'systemId': system_id,
                        'systemName': system_name,
                        'children': [
                            intf_dic
                        ]
                    }
                )
        # 全链路用例
        else:
            product_line_id = summary_dic['summary']['product_line_id']
            product_line_name = summary_dic['summary']['product_line_name']
            # testcase_main_id = summary_dic['summary']['testcase_main_id']
            # testcase_main_name = summary_dic['summary']['testcase_main_name']
            table_data = []
            for detail in summary_dic['summary']['details']:
                if detail['stat']['failures']:
                    test_result = '失败'
                    fail_reason = ''
                    fail_detail = []
                    for record in detail['records']:
                        error_type = record.get('error_type', None)
                        attachment = record.get('attachment', None)
                        if error_type:
                            fail_reason = fail_reason + error_type + ', '
                            fail_detail.append(attachment)
                    fail_reason = fail_reason.strip().strip(',')
                    fail_detail = json_dumps(fail_detail)
                else:
                    test_result = '成功' if len(detail['records'][-1]['meta_data']['validators']) != 0 else '成功-无断言'
                    fail_reason = ''
                    fail_detail = ''
                table_data_dic = {
                    'caseId': detail['case_id'],
                    'caseName': detail['name'],
                    'testResult': test_result,
                    'failReason': fail_reason,
                }
                if with_attachment:
                    table_data_dic['failDetail'] = fail_detail
                table_data.append(table_data_dic)
            is_product_line_exist = False
            for simple_summary in full_summary_list:
                if simple_summary['productLineId'] == product_line_id:
                    is_product_line_exist = True
                    simple_summary['tableData'].append(
                        # 每条全链路用例一个worker，所以只取第一个元素
                        table_data[0]
                    )
                    break
            if not is_product_line_exist:
                full_summary_list.append(
                    {
                        'productLineId': product_line_id,
                        'productLineName': product_line_name,
                        'tableData': table_data
                    }
                )
    for simple_summary in intf_summary_list:
        case_total = 0
        case_success = 0
        case_fail = 0
        for child in simple_summary['children']:
            case_total += child['runCaseNum']
            case_success += child['succCaseNum']
            case_fail += child['failCaseNum']

        simple_summary['runCaseNum'] = case_total
        simple_summary['succCaseNum'] = case_success
        simple_summary['failCaseNum'] = case_fail
        simple_summary['succRate'] = calc_success_rate(case_success, case_total)

    for simple_summary in full_summary_list:
        case_total = 0
        case_success = 0
        case_fail = 0
        for case_dic in simple_summary['tableData']:
            case_total += 1
            if case_dic['testResult'] in ['成功', '成功-无断言']:
                case_success += 1
            else:
                case_fail += 1
        simple_summary['runCaseNum'] = case_total
        simple_summary['succCaseNum'] = case_success
        simple_summary['failCaseNum'] = case_fail
        simple_summary['succRate'] = calc_success_rate(case_success, case_total)

    return intf_summary_list, full_summary_list


def from_run_id_to_summary_file_path(task_run_id):
    """获取summary文件路径"""
    base_run_task_log_dir = config.RUN_TASK_LOG_DIR
    run_obj = ApiRunTaskResultManager.get_result(id=task_run_id)
    run_date = format(run_obj.run_date)
    if platform.system() == 'Windows':
        dir_ = '{0}{1}\\task_run_{2}\\'.format(base_run_task_log_dir, run_date, task_run_id)
    else:
        dir_ = '{0}{1}/task_run_{2}/'.format(base_run_task_log_dir, run_date, task_run_id)
    return '{0}task_run_{1}_summary.log'.format(dir_, task_run_id)


def filter_request_or_response(request=None, response=None):
    """过滤请求和返回信息"""
    if request:
        url = request.get('url', None)
        # 识别是否dubbo请求
        if url and '/invokeDubbo' in url:
            return {
                'json': request['json']
            }
        else:
            request.pop('body', None)
            return request
    elif response:
        url = response.get('url', None)
        # 识别是否dubbo请求
        if url and '/invokeDubbo' in url:
            return {
                'json': response['json'],
                'status_code': response['status_code'],
                'elapsed_ms': response['elapsed_ms']
            }
        else:
            response.pop('ok', None)
            response.pop('url', None)
            # response.pop('reason', None)
            # response.pop('cookies', None)
            # response.pop('content', None)
            response.pop('text', None)
            return response


def filter_validators(validators):
    """过滤验证信息"""
    comparators = custom['comparators']
    for validator in validators:
        for comparator in comparators:
            if isinstance(validator['check_value'], dict):
                validator['check_value'] = json_dumps(validator['check_value'])
            if validator['comparator'] == comparator['name']:
                validator['comparator'] = comparator['description']
                break
    return validators


def bubble_sort_by_last_run_time(alist):
    """按最新运行时间冒泡排序"""
    for j in range(len(alist) - 1, 0, -1):
        # j表示每次遍历需要比较的次数，是逐渐减小的
        for i in range(j):
            if alist[i]["lastRunTime"] < alist[i + 1]["lastRunTime"]:
                alist[i], alist[i + 1] = alist[i + 1], alist[i]


def get_testcase_id_list_filter_by_tag(related_tag_id_list, intf_id=None, product_line_id=None):
    """ 根据任务配置的测试标签，过滤接口用例和全链路用例"""
    try:
        related_tag_id_list = json_loads(related_tag_id_list)
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


def get_last_executor(creator):
    if creator:
        return username_to_nickname(creator)
    else:
        return "定时任务"


def get_failed_info(res):
    """获取失败用例信息"""
    intf_summary_list, full_summary_list = res

    failed_intf_dic = {}
    for system_dic in intf_summary_list:
        if system_dic['failCaseNum'] == 0:
            continue
        for intf_dic in system_dic['children']:
            if intf_dic['failCaseNum'] == 0:
                continue
            failed_intf_id = intf_dic['intfId']
            failed_intf_dic[failed_intf_id] = []
            for case_dic in intf_dic['tableData']:
                if case_dic['testResult'] == '失败':
                    failed_intf_dic[failed_intf_id].append(case_dic['caseId'])

    failed_full_dic = {}
    for product_line_dic in full_summary_list:
        if product_line_dic['failCaseNum'] == 0:
            continue
        failed_product_line_id = product_line_dic['productLineId']
        failed_full_dic[failed_product_line_id] = []
        for case_dic in product_line_dic['tableData']:
            if case_dic['testResult'] == '失败':
                failed_full_dic[failed_product_line_id].append(case_dic['caseId'])

    return failed_intf_dic, failed_full_dic
