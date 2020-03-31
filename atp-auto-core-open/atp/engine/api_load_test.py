# -*- coding:utf-8 -*-

import copy
import functools
import json
import re
import time

from atp.env import RUNNING_ENV
from atp.engine.api_chain import get_testcase_chain
from atp.engine.code_to_desc import get_case_type_by_desc
from atp.engine.exceptions import JSONDecodeError, LoadCaseError
from atp.api.mysql_manager import (
    EnvInfoManager as eim,
    ApiTestcaseInfoManager as atim,
    ApiIntfInfoManager as aiim,
    ApiTestcaseRequestManager as atrm,
    ApiPublicVariableInfoManager as avim,
    ApiTestcaseMainManager as atmm,
    ApiTestcaseSubManager as atsm,
    ApiTestcaseRequestQllManager as atrqm,
    ApiIntfDefaultRequestManager as aidrm,
    ApiPublicVariableInfoManager, ApiSystemInfoManager,
    ApiTestcaseMainCustomFlowManager as atmcfm)
from atp.api.comm_log import logger
from atp.utils.tools import json_loads, json_dumps

absolute_http_url_regexp = re.compile(r"^https?://", re.I)


_to_add_param_setup_function_map = {
    'setup_db_operation': '||$DB_CONNECT',
    'setup_wait_until_db_result_succeed': '||$DB_CONNECT',
    'setup_fund_order_conf': '||$DB_CONNECT',
    'setup_disconf_operation_merge': '||$DISCONF_HOST',
    'setup_zx_base_file_move': '||$SERVER_APP_MAP||$SERVER_DEFAULT_USER',
    'setup_zx_test_file_move': '||$SERVER_APP_MAP||$SERVER_DEFAULT_USER',
    'setup_qa_create_accounting_overdue': '||$ENV_NAME',
}

_to_add_param_teardown_function_map = {
    'teardown_db_operation': '||$DB_CONNECT',
    'teardown_wait_until_db_result_succeed': '||$DB_CONNECT',
    'teardown_disconf_operation_merge': '||$DISCONF_HOST',
    'teardown_compare_log_content': '||$SERVER_APP_MAP||$SERVER_DEFAULT_USER',
    'teardown_update_capital_no_list': '||$DB_CONNECT',
    'teardown_zx_base_file_move': '||$SERVER_APP_MAP||$SERVER_DEFAULT_USER',
}

_to_add_param_custom_function_map = {
    'get_access_token': '||$BASE_HOST||$REDIS_CONNECT||$DB_CONNECT',
    'encrypt_by_public_key': '||$REMOTE_HOST',
    'get_random_member_id': '$DB_CONNECT',
    'get_random_phone_no': '||$DB_CONNECT',
    'get_from_log_content': '||$SERVER_APP_MAP||$SERVER_DEFAULT_USER',
    'get_redis_value': '||$REDIS_CONNECT'
}


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


def _confirm_pub_variable_changes(pub_variable_changes):
    """
    确认公共变量的修改
    :param pub_variable_changes:
    :return:
    """
    confirmed_pv_changes = []

    if not pub_variable_changes or not isinstance(pub_variable_changes, list):
        return confirmed_pv_changes

    for pv_dic in pub_variable_changes:
        if pv_dic["optionValue"]:
            pv_dic['changedValue'] = pv_dic["optionValue"]
            pv_dic.pop("optionValue")
            pv_dic.pop("tmpValue")
            confirmed_pv_changes.append(pv_dic)
        elif pv_dic["tmpValue"]:
            pv_dic['changedValue'] = pv_dic["tmpValue"]
            pv_dic.pop("optionValue")
            pv_dic.pop("tmpValue")
            confirmed_pv_changes.append(pv_dic)
        else:
            continue
    return confirmed_pv_changes


class ApiTestLoader(object):
    def __init__(self, **kwargs):
        self.env_name = kwargs.pop('env_name', None)
        self.env_id = kwargs.pop('env_id', None)
        self.testcase_id_list = kwargs.pop('testcase_id_list', None)
        self.testcase_main_id_list = kwargs.pop('testcase_main_id_list', None)
        self.test_tree = kwargs.pop('test_tree', None)
        self.pub_variable_changes = kwargs.pop('pub_variable_changes', None)
        self.confirmed_pv_changes = _confirm_pub_variable_changes(self.pub_variable_changes)
        self.custom_flow_id = kwargs.pop('custom_flow_id', None)

        if self.env_name:
            self.env_info = eim.get_env(env_name=self.env_name)
        else:
            self.env_info = eim.get_env(id=self.env_id)

        # 识别加载类型
        self.load_type = 0
        if self.testcase_id_list:
            self.load_type = 1
        elif self.testcase_main_id_list:
            self.load_type = 2

        self._testset_list = []
        self._test_meta_list = []
        self._project_id = None

        self.has_extract_variable_in_main_teardown = False

    @func_timer
    def get_testset_list(self):
        """
        获取testset_list
        """
        if not self._testset_list:
            self._load()
        return self._testset_list

    def get_test_meta_list(self):
        """
        获取test_meta_list
        """
        if not self._test_meta_list:
            self._load()
        return self._test_meta_list

    def _load(self):
        """
        识别加载类型，分别加载
        """
        # 接口用例--可能前置其他接口用例或者前置全流程用例
        if self.load_type == 1:
            for testcase_id in self.testcase_id_list:
                testset = self._load_testcase_mixed(testcase_id)
                self._testset_list.append(testset)
            # 增加调用链列表
            for test_dic in self._testset_list:
                chain_list = []
                i = 0
                last_case_id = None
                for teststep in test_dic['teststeps']:
                    if teststep['is_main']:
                        if last_case_id == teststep['case_id']:
                            i += 1
                        else:
                            i = 1
                        chain_list.append('{0}-{1}'.format(teststep['case_id'], i))
                    else:
                        chain_list.append(teststep['case_id'])
                    last_case_id = teststep['case_id']
                test_dic["config"]["chain_list"] = chain_list
        # 全流程用例
        elif self.load_type == 2:
            for testcase_main_id in self.testcase_main_id_list:
                self.has_extract_variable_in_main_teardown = False
                testset = self._load_main_testcase(testcase_main_id, custom_flow_id=self.custom_flow_id)
                self._testset_list.append(testset)
            # 增加调用链列表
            for test_dic in self._testset_list:
                chain_list = []
                i = 0
                for teststep in test_dic['teststeps']:
                    i += 1
                    chain_list.append('{0}-{1}'.format(teststep['case_id'], i))
                test_dic["config"]["chain_list"] = chain_list

        for testcase in self._testset_list:
            testcase['teststeps'][-1]['is_last'] = True

    def _load_testcase_mixed(self, testcase_id):
        """
        加载用例到testset,包含接口用例和全链路用例
        """
        case_chain_list = get_testcase_chain(testcase_id, case_type=1)
        """
        case_chain_list  EXAMPLE:
        [
            {
                'preSystemName': '',
                'customFlowId': 1,
                'preCaseType': '全链路用例',
                'preCaseName': '新户提交必填信息2',
                'preCaseId': 32,
                'preIntfName': ''
                'customFlowName': '32flow1'
            },
            {
                'preCaseType': '接口用例',
                'preCaseName': '随机获取身份证134佛挡杀佛水电费',
                'preCaseId': 5141
            }
        ]
        """
        print(json_dumps(case_chain_list))
        case_chain_list.reverse()
        testset = None
        for case_info in case_chain_list:
            if get_case_type_by_desc(case_info["preCaseType"]) == 1:
                testset = self._load_api_testcase_itself(testcase_id=case_info["preCaseId"], testset=testset)
            elif get_case_type_by_desc(case_info["preCaseType"]) == 2:
                self.has_extract_variable_in_main_teardown = False
                testset = self._load_main_testcase(testcase_main_id=case_info["preCaseId"], testset=testset,
                                                   custom_flow_id=case_info["customFlowId"])

        return testset

    def _load_api_testcase_itself(self, testcase_id, testset=None):
        """
        加载单个接口用例到testset
        """
        tc_obj = atim.get_testcase(id=testcase_id)
        tc_obj.testcase_name = '{0}__{1}'.format(tc_obj.testcase_name, tc_obj.expect_result)
        intf_obj = aiim.get_intf(id=tc_obj.api_intf_id)

        testset = self._add_to_testset(testset, tc_obj, intf_obj)

        return testset

    def _load_api_testcase(self, testcase_id, testset=None):
        """
        递归加载接口用例到testset
        """
        tc_obj = atim.get_testcase(id=testcase_id)
        tc_obj.testcase_name = '{0}__{1}'.format(tc_obj.testcase_name, tc_obj.expect_result)
        intf_obj = aiim.get_intf(id=tc_obj.api_intf_id)
        include_list = json_loads(tc_obj.include)
        setup_cases_list = include_list[1]["setup_cases"]

        testset = self._add_to_testset(testset, tc_obj, intf_obj)

        if setup_cases_list:
            """存在前置用例"""
            for setup_case_id in reversed(setup_cases_list):
                """前置用例id不能和自身用例id相同"""
                if str(setup_case_id) != str(testcase_id):
                    """加载前置用例到testset"""
                    testset = self._load_api_testcase(setup_case_id, testset)

        return testset

    def _load_main_testcase(self, testcase_main_id, testset=None, custom_flow_id=None):
        """
        循环加载子用例到testset
        """
        tm_obj = atmm.get_testcase_main(id=testcase_main_id)
        tm_obj.testcase_name = '{0}__{1}'.format(tm_obj.testcase_name, tm_obj.expect_result)
        sub_list = json_loads(tm_obj.sub_list)
        if custom_flow_id:
            # 存在指定自定义链路信息，按照链路切割sub_list
            flow_obj = atmcfm.get_flow(id=custom_flow_id)
            # sub_list = sub_list[flow_obj.start_sub_index:flow_obj.start_sub_index + 1]
            flow_index_list = json_loads(flow_obj.flow_index_list)
            new_sub_list = [sub_list[i] for i in flow_index_list]
            sub_list = new_sub_list

        sub_list.reverse()

        # 新加载方式，耗时减少60%
        union_list = split_list_to_union_list(sub_list)
        # print(union_list)
        sub_objs = []
        for part_list in union_list:
            part_sub_objs = atsm.get_testcase_subs_in_id_list(part_list)
            sorted_part_sub_objs = sort_objs_by_id_list(part_sub_objs, part_list)
            sub_objs.extend(sorted_part_sub_objs)

        intf_id_list = [sub_obj.api_intf_id for sub_obj in sub_objs]
        union_intf_id_list = split_list_to_union_list(intf_id_list)
        intf_objs = []
        for part_list in union_intf_id_list:
            part_intf_objs = aiim.get_intfs_in_id_list(part_list)
            sorted_part_intf_objs = sort_objs_by_id_list(part_intf_objs, part_list)
            intf_objs.extend(sorted_part_intf_objs)

        for i in range(len(sub_objs)):
            sub_obj = sub_objs[i]
            print('sub_id:{}'.format(sub_obj.id))
            ts_obj = sub_obj
            intf_obj = intf_objs[i]
            # print('intf_id:{}'.format(intf_obj.id))

            testset = self._add_to_testset(testset, tc_obj=ts_obj, intf_obj=intf_obj, tm_obj=tm_obj)

        # # 旧加载方式
        # for sub_id in sub_list:
        #     print('sub_id:{}'.format(sub_id))
        #     ts_obj = atsm.get_testcase_sub(id=sub_id)
        #     intf_obj = aiim.get_intf(id=ts_obj.api_intf_id)
        #
        #     testset = self._add_to_testset(testset, tc_obj=ts_obj, intf_obj=intf_obj, tm_obj=tm_obj)

        # 接口用例(case_type==1)可能存在前置全链路用例(目前还没有)
        if tm_obj.case_type == 1:
            setup_flow_list = json_loads(tm_obj.setup_flow_list)
            setup_flow_list.reverse()
            for flow_id in setup_flow_list:
                testset = self._load_main_testcase(flow_id, testset=testset, custom_flow_id=custom_flow_id)

        return testset

    def _add_to_testset(self, testset, tc_obj, intf_obj, tm_obj=None):
        """
        加载一个子用例到testset
        """
        if not testset:
            """首次加载,初始化整个testset"""
            testset = self._init_testset(tc_obj, intf_obj, tm_obj=tm_obj)
            meta_data = self._get_meta(testset, tc_obj, intf_obj, tm_obj=tm_obj)
            if not self._test_meta_list:
                self._test_meta_list.append({'intf_id': intf_obj.id})
            self._test_meta_list.append(meta_data)
            """根据接口类型添加接口信息"""
            testset = self._add_intf_info(testset, intf_obj, is_first=True)
        else:
            """ 前置用例加载，仅添加step到testset"""
            testset = self._add_step_to_testset(testset, tc_obj, intf_obj, tm_obj=tm_obj)
            """根据接口类型添加接口信息"""
            testset = self._add_intf_info(testset, intf_obj, is_first=False)

        """添加公共变量"""
        testset = self._add_pv(testset, tc_obj, intf_obj, tm_obj=tm_obj)

        # """根据接口类型添加接口信息"""
        # testset = self._add_intf_info(testset, ts_obj)

        # TODO json改json_str
        # json_dic = testset["teststeps"][0]["request"].get("json", None)
        # if json_dic:
        #     json_str = json_dumps(json_dic)
        #     json_str = json_str.replace("\"$current_timestamp\"", "$current_timestamp")
        #     testset["teststeps"][0]["request"]["json_str"] = json_str
        #     testset["teststeps"][0]["request"].pop("json")

        return testset

    def _add_public_env_to_config(self, testset):
        """
        给testset增加公共环境信息
        """
        if testset['config']['variables']:
            return testset

        env_info = self.env_info

        variables_list = testset['config']['variables']
        variables_list.append({"DUBBO_ZOOKEEPER": env_info.dubbo_zookeeper})
        variables_list.append({"ENV_NAME": env_info.env_name})
        variables_list.append({"DB_CONNECT": env_info.db_connect})
        variables_list.append({"BASE_HOST": env_info.base_host})
        variables_list.append({"REMOTE_HOST": env_info.remote_host})
        variables_list.append({"DISCONF_HOST": env_info.disconf_host})
        variables_list.append({"REDIS_CONNECT": env_info.redis_connect})
        variables_list.append({"SERVER_APP_MAP": env_info.server_app_map})
        variables_list.append({"SERVER_DEFAULT_USER": env_info.server_default_user})
        mq_key = json_loads(env_info.mq_key)
        variables_list.append({"MQ_AK": mq_key["ak"]})
        variables_list.append({"MQ_SK": mq_key["sk"]})

        return testset

    @staticmethod
    def _get_testset_from_obj(tc_obj, intf_obj, tm_obj=None):
        """
        从数据库对象obj中获取request值，并转成dict格式，并进行一些预处理，把缺少必要环境变量的地方加上环境变量
        e.g:
            change from
            "variables": [
                {
                    "encrypted_newPassword": "${encrypt_by_public_key(392843||$publicKey)}"
                }
            ],
            to
            "variables": [
                {
                    "encrypted_newPassword": "${encrypt_by_public_key(392843||$publicKey||$REMOTE_HOST)}"
                }
            ],
        更新：识别"入参字段校验用例"
        """
        if tm_obj:
            testset_str = atrqm.get_request(api_testcase_id=tc_obj.id).request
        else:
            testset_str = atrm.get_request(api_testcase_id=tc_obj.id).request

        try:
            testset = json.loads(testset_str)
        except JSONDecodeError:
            raise LoadCaseError('Json Load testcase_info.request Error')

        # for v_dic in testset["teststeps"][0]["variables"]:
        #     for v_name in v_dic:
        #         if isinstance(v_dic[v_name], str) and v_dic[v_name].startswith(
        #                 "${encrypt_by_public_key") and not v_dic[v_name].endswith(
        #                 "||$REMOTE_HOST)}"):
        #             v_dic[v_name] = v_dic[v_name][:-2] + "||$REMOTE_HOST)}"

        new_variables = []
        for variable_dic in testset["teststeps"][0]["variables"]:
            for variable_name, variable_str in variable_dic.items():
                if isinstance(variable_str, str):
                    parsed_variable_str = variable_string_add_param(variable_str)
                else:
                    parsed_variable_str = variable_str
                new_variables.append({variable_name: parsed_variable_str})
        testset["teststeps"][0]["variables"] = new_variables

        new_setup_hooks = []
        for setup_hook_str in testset["teststeps"][0]["setup_hooks"]:
            # if setup_hook_str.startswith("${setup_fund_order_conf") and not setup_hook_str.endswith(
            #         "||$DB_CONNECT)}"):
            #     setup_hook_str = setup_hook_str[:-2] + "||$DB_CONNECT)}"
            # if setup_hook_str.startswith("${setup_disconf_operation_merge") and not setup_hook_str.endswith(
            #         "||$DISCONF_HOST)}"):
            #     setup_hook_str = setup_hook_str[:-2] + "||$DISCONF_HOST)}"
            parsed_setup_hook_str = setup_or_teardown_string_add_param(setup_hook_str, is_setup=True)
            new_setup_hooks.append(parsed_setup_hook_str)
        testset["teststeps"][0]["setup_hooks"] = new_setup_hooks

        new_teardown_hooks = []
        for teardown_hook_str in testset["teststeps"][0]["teardown_hooks"]:
            # if teardown_hook_str.startswith("${teardown_disconf_operation_merge") and not teardown_hook_str.endswith(
            #         "||$DISCONF_HOST)}"):
            #     teardown_hook_str = teardown_hook_str[:-2] + "||$DISCONF_HOST)}"
            parsed_teardown_hook_str = setup_or_teardown_string_add_param(teardown_hook_str, is_setup=False)
            new_teardown_hooks.append(parsed_teardown_hook_str)
        testset["teststeps"][0]["teardown_hooks"] = new_teardown_hooks

        if "request_teardown_hooks" in testset["teststeps"][0]:
            new_request_teardown_hooks = []
            for teardown_hook_str in testset["teststeps"][0]["request_teardown_hooks"]:
                parsed_teardown_hook_str = setup_or_teardown_string_add_param(teardown_hook_str, is_setup=False)
                new_request_teardown_hooks.append(parsed_teardown_hook_str)
            testset["teststeps"][0]["request_teardown_hooks"] = new_request_teardown_hooks

        if tm_obj:
            testset["teststeps"][0]["case_id"] = tm_obj.id
            testset["teststeps"][0]["sub_case_id"] = tc_obj.id
            testset["teststeps"][0]["is_main"] = True
        else:
            testset["teststeps"][0]["case_id"] = tc_obj.id
            testset["teststeps"][0]["is_main"] = False

        # # 注释合并请求报文
        # intf_r_obj = aidrm.get_request(api_intf_id=tc_obj.api_intf_id)
        # if intf_r_obj and intf_r_obj.request:
        #     default_body_base = json_loads(intf_r_obj.request)
        #     default_body_detail = json_loads(intf_r_obj.request_detail)
        #     # 根据intf_r_obj.request_detail中首层字段的必填性，把非必填字段去除
        #     for key_dic in default_body_detail:
        #         if not key_dic["isRequired"]:
        #             if isinstance(default_body_base, list):
        #                 default_body_base = []
        #             else:
        #                 default_body_base.pop(key_dic["paramName"])
        #
        #     if default_body_base:
        #         request_type = tc_obj.request_type if tm_obj else tc_obj.type
        #
        #         # 合并请求报文
        #         # http
        #         if request_type == 1:
        #             tc_body = testset["teststeps"][0]["request"]["json"]
        #             testset["teststeps"][0]["request"]["json"] = merge_request_body(default_body_base, tc_body)
        #         # dubbo
        #         elif request_type == 2:
        #             tc_body = testset["teststeps"][0]["request"]["json"]["args"]
        #             testset["teststeps"][0]["request"]["json"]["args"] = merge_request_body(
        #                 default_body_base, tc_body, is_list=True
        #             )
        #         # mq
        #         elif request_type == 3:
        #             tc_body_str = testset["teststeps"][0]["request"]["json"]["msg"]
        #             tc_body = json_loads(tc_body_str)
        #             testset["teststeps"][0]["request"]["msg"] = json_dumps(
        #                 merge_request_body(default_body_base, tc_body)
        #             )
        testset["teststeps"][0]["request"].pop("isMerge", None)

        # 增加支持form表单类型接口
        # intf_obj = aiim.get_intf(id=tc_obj.api_intf_id)
        if intf_obj.intf_type == 'HTTP':
            intf_info_dic = json_loads(intf_obj.intf_info)
            headers_dic = json_loads(intf_info_dic["headers"].replace("'", "\""))
            if 'Content-Type' in headers_dic:
                if 'application/x-www-form-urlencoded' in headers_dic['Content-Type']:
                    testset["teststeps"][0]["request"]["data"] = testset["teststeps"][0]["request"]["json"]
                    testset["teststeps"][0]["request"].pop("json")
        return testset

    def _init_testset(self, tc_obj, intf_obj, tm_obj=None):
        """
        初始化testset
        """

        testset = self._get_testset_from_obj(tc_obj, intf_obj, tm_obj=tm_obj)
        testset = self._add_public_env_to_config(testset)
        testset = self._param_check_update(testset, tc_obj)

        # 主用例
        if tm_obj:
            main_case_id = tm_obj.id
            main_name = tm_obj.testcase_name
            testset['config']['is_main'] = True
            # testset增加主用例用例后置信息
            if tm_obj.main_teardown_hooks:
                main_teardown_hooks = json_loads(tm_obj.main_teardown_hooks)
                if main_teardown_hooks:
                    parsed_teardown_hooks = []
                    for teardown_hook_str in main_teardown_hooks:
                        parsed_teardown_hook_str = setup_or_teardown_string_add_param(teardown_hook_str, is_setup=False)
                        parsed_teardown_hooks.append(parsed_teardown_hook_str)
                    testset['config']['teardown_hooks'] = parsed_teardown_hooks
        # 接口用例
        else:
            main_case_id = tc_obj.id
            main_name = tc_obj.testcase_name
            testset['config']['is_main'] = False

        testset['name'] = main_name
        testset['config']['case_id'] = main_case_id
        # 给testset增加name信息
        testset['config']['name'] = testset['name']

        return testset

    @staticmethod
    def _param_check_update(testset, tc_obj):
        """
        识别是否"入参字段校验用例", 是:更新teststeps结构
        """
        include_list = json_loads(tc_obj.include)
        if include_list and isinstance(include_list, list) and len(include_list) >= 3:
            param_check_dict = include_list[2]["param_check"]
            original_step = copy.deepcopy(testset["teststeps"][0])
            step_name = original_step['name'][:-2] if original_step['name'].endswith('.1') else original_step['name']
            step_no = 1
            for item, check_key_list in param_check_dict.items():
                # 入参值为空字符串校验
                if item == 'empty':
                    testset["teststeps"] = []
                    for key in check_key_list:
                        copy_step = copy.deepcopy(original_step)
                        if key in copy_step['request']['json']:
                            copy_step['name'] = '{0}.{1}'.format(step_name, step_no)
                            copy_step['request']['json'][key] = ''
                            testset["teststeps"].append(copy_step)
                            step_no += 1
        return testset

    def _add_step_to_testset(self, testset, tc_obj, intf_obj, tm_obj=None):
        """
        添加tc_obj的step到testset
        """
        # testset增加主用例用例后置信息
        if tm_obj and tm_obj.main_teardown_hooks:
            main_teardown_hooks = json_loads(tm_obj.main_teardown_hooks)
            if main_teardown_hooks:
                parsed_teardown_hooks = []
                for teardown_hook_str in main_teardown_hooks:
                    parsed_teardown_hook_str = setup_or_teardown_string_add_param(teardown_hook_str, is_setup=False)
                    parsed_teardown_hooks.append(parsed_teardown_hook_str)
                if 'teardown_hooks' not in testset['config']:
                    testset['config']['teardown_hooks'] = parsed_teardown_hooks
                else:
                    testset['config']['teardown_hooks'].extend(parsed_teardown_hooks)
                    testset['config']['teardown_hooks'] = list(set(testset['config']['teardown_hooks']))

        setup_testset = self._get_testset_from_obj(tc_obj, intf_obj, tm_obj=tm_obj)
        setup_teststep = setup_testset['teststeps'][0]
        testset['teststeps'].insert(0, setup_teststep)
        return testset

    def _add_pv(self, testset, tc_obj, intf_obj, tm_obj=None):
        """
        添加公共变量到config
        """
        # testset增加主用例用例独立后置中的公共变量
        if not self.has_extract_variable_in_main_teardown and tm_obj and tm_obj.main_teardown_hooks:
            variable_regexp = r"\$([\w_]+)"
            # main_teardown_hooks = json_loads(tm_obj.main_teardown_hooks)
            main_teardown_variables = re.findall(variable_regexp, str(tm_obj.main_teardown_hooks))
            for target in main_teardown_variables:
                system_id = intf_obj.api_system_id
                s_var_obj = ApiPublicVariableInfoManager.get_variable(variable_name=target, api_system_id=system_id)

                if s_var_obj:
                    testset["config"]["variables"].append({
                        target: s_var_obj.value.split('##')[0]
                    })
                else:
                    company_id = ApiSystemInfoManager.get_system(id=system_id).api_company_id
                    c_var_obj = ApiPublicVariableInfoManager.get_variable(
                        variable_name=target, api_company_id=company_id)
                    if c_var_obj:
                        testset["config"]["variables"].append({
                            target: c_var_obj.value.split('##')[0]
                        })
            self.has_extract_variable_in_main_teardown = True

        teststep = testset["teststeps"][0]
        include_list = json_loads(tc_obj.include)
        pv_list = None
        for include in include_list:
            if "public_variables" in include:
                pv_list = include["public_variables"]
                break

        """用例存在引用公共变量"""
        if pv_list:
            """存在公共变量临时修改"""
            if self.confirmed_pv_changes:
                for pv_change_dic in self.confirmed_pv_changes:
                    if pv_change_dic['changedValue']:
                        if pv_change_dic['type'] == 'files':
                            continue  # 暂不支持文件类型公共变量临时修改
                        elif pv_change_dic['type'] in ['constant', 'function', 'db']:
                            if int(pv_change_dic['pvId']) in pv_list:
                                pv_list.remove(int(pv_change_dic['pvId']))
                                testset["config"]["variables"].append({
                                    pv_change_dic['name']: pv_change_dic['changedValue']
                                })

                        # if int(pv_change_dic['pvId']) in pv_list:
                        #     if pv_change_dic['type'] == 'files':
                        #         continue  # 暂不支持文件类型公共变量临时修改
                        #     pv_list.remove(int(pv_change_dic['pvId']))
                        #     testset["config"]["variables"].append({
                        #         pv_change_dic['name']: pv_change_dic['changedValue']
                        #     })

            pv_objs = avim.get_variables_in_id_list(pv_list)
            for obj in pv_objs:
                if obj.type == 'files':
                    """特殊处理files类型的公共变量"""
                    file_variable_name = obj.variable_name
                    try:
                        file_path_list = eval(obj.value)
                    except (SyntaxError, NameError):
                        file_path_list = None

                    if not isinstance(file_path_list, list):
                        continue

                    target_key = None
                    for key in teststep['request']['json']:
                        if teststep['request']['json'][key] == '$' + file_variable_name:
                            teststep['request']['files'] = []
                            for i in range(len(file_path_list)):
                                if 'f_name' in teststep['request']['json']:
                                    file_name = teststep['request']['json']['f_name'][i]
                                else:
                                    file_name = str(file_path_list[i]).split('/')[-1]
                                try:
                                    teststep['request']['files'].append(
                                        (key, (file_name, open(file_path_list[i], "rb"), "multipart/form-data"))
                                    )
                                except FileNotFoundError:
                                    # 公共变量指定的文件不存在
                                    pass
                            target_key = key
                            break
                    if target_key:
                        teststep['request']['json'].pop('f_name', 0)
                        teststep['request']['json'].pop(target_key)
                        teststep['request']['data'] = teststep['request']['json']
                        teststep['request'].pop('json')
                elif obj.type == 'function':
                    """处理自定义方法类型的公共变量"""
                    is_exist = False
                    for exist_pv_dic in testset["config"]["variables"]:
                        for key in exist_pv_dic:
                            if key == obj.variable_name:
                                is_exist = True
                        if is_exist:
                            break
                    if not is_exist:
                        variable_string = variable_string_add_param(str(obj.value))
                        testset["config"]["variables"].append({
                            obj.variable_name: variable_string
                        })
                elif obj.type == 'db':
                    """处理db类型的公共变量"""
                    is_exist = False
                    for exist_pv_dic in testset["config"]["variables"]:
                        for key in exist_pv_dic:
                            if key == obj.variable_name:
                                is_exist = True
                        if is_exist:
                            break
                    if not is_exist:
                        testset["config"]["variables"].append({
                            obj.variable_name: [v.strip() for v in str(obj.value).strip('##').split('##')][0]
                        })
                else:
                    """处理key-value类型的公共变量"""
                    is_exist = False
                    for exist_pv_dic in testset["config"]["variables"]:
                        for key in exist_pv_dic:
                            if key == obj.variable_name:
                                is_exist = True
                        if is_exist:
                            break
                    if not is_exist:
                        var_value = [v.strip() for v in str(obj.value).strip('##').split('##')][0]
                        save_as = obj.save_as if obj.save_as else 'str'
                        if save_as in ['num', 'bool', 'list', 'dict']:
                            try:
                                var_value = eval(var_value)
                            except SyntaxError:
                                var_value = var_value
                        testset["config"]["variables"].append({
                            obj.variable_name: var_value
                        })

        return testset

    def _add_intf_info(self, testset, intf_obj, is_first=False):
        """
        添加接口基本信息
        """
        intf_type = intf_obj.intf_type
        intf_info_dic = json_loads(intf_obj.intf_info)

        # teststep = testset["teststeps"][0]
        for teststep in testset["teststeps"]:

            if intf_type == "HTTP":
                base_url = self.env_info.base_host
                api_url = intf_info_dic["apiUrl"].strip()
                if absolute_http_url_regexp.match(api_url):
                    teststep["request"]["url"] = api_url
                elif api_url.startswith('/'):
                    teststep["request"]["url"] = base_url + api_url
                else:
                    teststep["request"]["url"] = base_url + '/' + api_url
                teststep["request"]["method"] = intf_info_dic["method"]
                teststep["request"]["headers"] = json_loads(intf_info_dic["headers"].replace("'", "\""))
                teststep["request"]["allow_redirects"] = False

            elif intf_type == "DUBBO":
                base_url = self.env_info.remote_host
                teststep["request"]["url"] = base_url + "/invokeDubbo"
                teststep["request"]["method"] = "POST"

                teststep["variables"].append({"DUBBO_METHOD": intf_info_dic["dubboMethod"]})
                teststep["variables"].append({"DUBBO_INTERFACE": intf_info_dic["dubboService"]})
                teststep["variables"].append({"DUBBO_VERSION": intf_info_dic["version"]})
                teststep["request"]["json"]["version"] = "$DUBBO_VERSION"
                teststep["request"]["json"]["interfaceName"] = "$DUBBO_INTERFACE"
                teststep["request"]["json"]["zkUrl"] = "$DUBBO_ZOOKEEPER"
                teststep["request"]["json"]["methodName"] = "$DUBBO_METHOD"
                teststep["request"]["json"]["parameterTypes"] = []

                parameter_type_count = 0
                try:
                    parameter_type_list = json_loads(intf_info_dic["parameterTypes"])
                except json.decoder.JSONDecodeError:
                    logger.error('ERROR parameterTypes: intf_id {}'.format(intf_obj.id))
                    parameter_type_list = []
                for parameter_type in parameter_type_list:
                    parameter_type_count += 1
                    teststep["variables"].append({
                        "DUBBO_PARAMETER_TYPE_{no}".format(no=parameter_type_count): parameter_type
                    })
                    teststep["request"]["json"]["parameterTypes"].append(
                        "$DUBBO_PARAMETER_TYPE_{no}".format(no=parameter_type_count)
                    )

            elif intf_type == "MQ":
                if self.env_info.env_name == "SIT":
                    default_env = self.env_info.env_name
                else:
                    default_env = "ALIUAT"  # MQ的env默认为定值'ALIUAT'
                base_url = self.env_info.remote_host
                teststep["request"]["url"] = base_url + "/sendMQ"
                teststep["request"]["method"] = "POST"

                teststep["variables"].append({"MQ_TOPIC": intf_info_dic["topic"]})
                teststep["variables"].append({"MQ_TAG": intf_info_dic["tag"]})
                teststep["variables"].append({"MQ_PID": "PID_{mid}_{env}".format(
                    mid=intf_info_dic["topic"][3:], env=default_env)})

                teststep["request"]["json"]["env"] = default_env
                teststep["request"]["json"]["topic"] = "$MQ_TOPIC"
                teststep["request"]["json"]["tag"] = "$MQ_TAG"
                teststep["request"]["json"]["pid"] = "$MQ_PID"
                teststep["request"]["json"]["onsSecretKey"] = "{{\"{env}\":\"$MQ_SK\"}}".format(env=default_env)
                teststep["request"]["json"]["onsAccessKey"] = "{{\"{env}\":\"$MQ_AK\"}}".format(env=default_env)
                if "appid" in intf_info_dic and intf_info_dic["appid"]:
                    teststep["request"]["json"]["appid"] = intf_info_dic["appid"]

            # 非首次加载接口信息的情况，只处理testset["teststeps"][0]
            if not is_first:
                break

        return testset

    @staticmethod
    def _get_meta(testset, tc_obj, intf_obj, tm_obj=None):
        """
        获取meta
        """
        if tm_obj:
            testcase_main_id = tm_obj.id
            testcase_main_name = tm_obj.testcase_name
            testcase_sub_name = tc_obj.sub_name
        else:
            testcase_main_id = tc_obj.id
            testcase_main_name = tc_obj.testcase_name
            testcase_sub_name = tc_obj.testcase_name

        meta_dict = {
            'id': testcase_main_id, 'testcase_name': testcase_main_name, 'step': [], "intf_type": intf_obj.intf_type
        }
        step = testset["teststeps"][0]
        meta_dict['step'].append({'testcase_name': testcase_sub_name, 'step_name': step['name']})

        return meta_dict


def merge_request_body(template_body, to_merge_body, is_list=False):
    """
    将template_body与to_merge_body合并，返回合并后的body
    eg:
    接口默认报文 =
    {
        "a": 1,
        "b": False,
        "c": [{"cc": "kk"}, 2],
        "d": "DD",
        "e": None,
        "f": "F",
        "h": {"h1": "H1", "h2": "H2"},
        "i": {}
    }
    用例内报文 =
    {
        "a": 33,
        "b": True,
        "c": [4],
        "d": "DD",
        "e": {"e1": "", "e2": None},
        "g": "G",
        "h": {"h1": "1", "h3": "3"},
        "i": {"I1": "", "I2": 2, "I3": ""}
    }

    合并报文结果 =>
    {   "a": 33,
        "b": True,
        "c": [4],
        "d": "DD",
        "e": {"e1": "", "e2": None},
        "f": "F",
        "g": "G",
        "h": {"h1": "1", "h3": "3"},
        "i": {"I1": "", "I2": 2, "I3": ""}
    }
    """
    if is_list:
        merge_res_list = []
        if len(template_body) == len(to_merge_body):
            for i in range(len(template_body)):
                if isinstance(template_body[i], dict) and isinstance(to_merge_body[i], dict):
                    merge_res_list.append(merge_request_body(template_body[i], to_merge_body[i]))
                else:
                    merge_res_list.append(to_merge_body[i])
        else:
            # dubbo列表参数个数不一致的情况
            merge_res_list = to_merge_body
        return merge_res_list

    else:
        if isinstance(template_body, dict) and isinstance(to_merge_body, dict):
            template_body.update(to_merge_body)
            return template_body
        else:
            # 请求报文整理类型不一致的情况
            return to_merge_body

    # for key in template_body:
    #     if key in to_merge_body:
    #         if isinstance(template_body[key], dict) and isinstance(to_merge_body[key], dict):
    #             template_body[key] = merge_request_body(template_body[key], to_merge_body[key])
    #         else:
    #             template_body[key] = to_merge_body[key]
    # return template_body


def setup_or_teardown_string_add_param(hook_str, is_setup):
    """前后置操作方法统一增加环境信息"""
    if is_setup:
        for func_name, to_add_param in _to_add_param_setup_function_map.items():
            if func_name in hook_str and to_add_param not in hook_str:
                return hook_str[:-2] + "{})}}".format(to_add_param)
        return hook_str
    else:
        for func_name, to_add_param in _to_add_param_teardown_function_map.items():
            if func_name in hook_str and to_add_param not in hook_str:
                return hook_str[:-2] + "{})}}".format(to_add_param)
        return hook_str


def variable_string_add_param(variable_str):
    """自定义方法统一增加环境信息"""
    for func_name, to_add_param in _to_add_param_custom_function_map.items():
        if func_name in variable_str and to_add_param not in variable_str:
            return variable_str[:-2] + "{})}}".format(to_add_param)
    return variable_str


def split_list_to_union_list(num_list):
    """
    分割一个list，使之成为多个没有重复元素的列表
    num_list: [1,2,3,4,5,3,4,2,3,3,1,7]
    union_list : [[1,2,3,4,5], [3,4,2], [3], [3,1,7]]
    """
    union_list = []
    part_list = []
    for num in num_list:
        if num not in part_list:
            part_list.append(num)
        else:
            union_list.append(copy.copy(part_list))
            part_list = [num]
    if part_list:
        union_list.append(copy.copy(part_list))
    return union_list


def sort_objs_by_id_list(objs, id_list):
    """
    对数据库对象列表按照id_list顺序进行排序
    """
    sorted_objs = []
    for id_ in id_list:
        for obj in objs:
            if id_ == obj.id:
                sorted_objs.append(obj)
                break
    return sorted_objs

if __name__ == '__main__':
    kwargs_ = {
        "testcase_id_list": [6393],  # http demo
        # "testcase_main_id_list": [183],  # http demo
        # "env_name": "MOCK",
        # "test_tree": {"5": {"66": ["140", "142"]}, "68": {"71": ["141"]}}
        "env_id": "1",
        # "testsuite_id_list": ["1"],
    }
    from atp.app import create_app
    app = create_app()
    with app.app_context():
        loader = ApiTestLoader(**kwargs_)
        print(json_dumps(loader.get_testset_list()))
        print(json_dumps(loader.get_test_meta_list()))



