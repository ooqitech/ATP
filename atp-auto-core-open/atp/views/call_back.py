# -*- coding:utf-8 -*-


from flask import Blueprint
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.api.mysql_manager import (
    ApiCompanyInfoManager, ApiSystemInfoManager, ApiIntfInfoManager, ApiProjectSystemRelationManager, ApiTaskInfoManager, GitDiffVersionManager, ApiTestcaseInfoManager
)
from atp.engine.return_code_desc import CODE_DESC_MAP
from atp.utils.tools import json_dumps, json_loads
from atp.views.wrappers import timer, login_check, developer_check, master_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.redis_api import RedisManager
from flask import request

redis = RedisManager()
call_back = Blueprint('call_back_interface', __name__)


class CallBack(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.gdvm = GitDiffVersionManager()
        self.aiif = ApiIntfInfoManager()
        self.atim = ApiTaskInfoManager()
        self.atcm = ApiTestcaseInfoManager()

    @timer
    def post(self, action):
        if action == 'getChangesBySeqNo':
            return self.get_changes_by_seq_no()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    def get_changes_by_seq_no(self):
        """
        根据流水号获取变更内容
        :return:
        """
        try:
            seq_no = self.data.pop('seq_no')
            application = self.data.pop('application')
        except KeyError:
            return make_response({"code": "100", "mes": CODE_DESC_MAP["100"]})

        git_diffs = self.gdvm.get_git_diff_versions(seq_no=seq_no)
        if not git_diffs:
            return make_response({"code": "100", "desc": "seq_no不存在"})
        elif len(git_diffs) > 1:
            return make_response({"code": "100", "desc": "seq_no不唯一"})
        else:
            changes = application['changes']
            api_task_id = git_diffs[0].api_task_id
            self.gdvm.update_git_diff_version_by_seq_no(seq_no_=seq_no, detail=json_dumps(changes))
            self.update_task_info(api_task_id, changes, seq_no)

            return make_response({"code": "0000", "msg": "成功"})

    def update_task_info(self, api_task_id, changes, seq_no):
        """
        解析回调接口返回的变更内容
        :param api_task_id:
        :param changes:
        :param seq_no:
        :return:
        """
        affect_http = set()
        affect_dubbo = set()
        affect_mq = set()
        affect_elasticJob = set()
        for affects in [change['affects'] for change in changes]:
            for methods in [affect['methods'] for affect in affects]:
                for method in methods:
                    if method.get('http'):
                        method_http = method.get('http').get('url')
                        affect_http.add(method_http)
                    if method.get('dubbo'):
                        role = method.get('dubbo').get('role')
                        method_dubbo = method.get('dubbo').get('service').get('interface') + '.' + method.get('method') \
                            if role == 'service' else method.get('dubbo').get('reference').get(
                            'interface') + '.' + method.get('method')
                        affect_dubbo.add(method_dubbo)
                    if method.get('mq'):
                        role = method.get('mq').get('role')
                        method_mq = method.get('mq').get('producer').get('topic') \
                            if role == 'producer' else method.get('mq').get('consumer').get(
                            'topic') + '.' + method.get('mq').get('consumer').get(
                            'tag')
                        affect_mq.add(method_mq)
                    if method.get('elasticJob'):
                        method_elasticJob = method.get('elasticJob').get('class') + '.' + method.get('method')
                        affect_elasticJob.add(method_elasticJob)
        affects = {
            "http": list(affect_http), "dubbo": list(affect_dubbo), "mq": list(affect_mq),
            "elasticJob": list(affect_elasticJob)}

        # 查询atp平台是否存在对应接口，如有则将接口id填入effect_intf_id_list，如无则将接口数据填入uncovered_info
        task_info = self.atim.get_task(id=api_task_id)
        effect_intf_id_list = set(json_loads(task_info.effect_intf_id_list)) if task_info.effect_intf_id_list else set()
        uncovered_info = json_loads(task_info.uncovered_info) if task_info.uncovered_info else {}
        uncovered_info_http = set(uncovered_info.get('http')) if uncovered_info.get('http') else set()
        uncovered_info_dubbo = set(uncovered_info.get('dubbo')) if uncovered_info.get('dubbo') else set()
        uncovered_info_mq = set(uncovered_info.get('mq')) if uncovered_info.get('mq') else set()
        uncovered_info_elasticJob = set(uncovered_info.get('elasticJob')) if uncovered_info.get('elasticJob') else set()
        for intf_name in affects['http']:
            if intf_name:
                intf_info = self.aiif.get_intf(intf_name=intf_name)
                if intf_info:
                    testcase_info = self.atcm.get_testcase(api_intf_id=intf_info.id)
                    if testcase_info:
                        affects['http'] = affects['http'].remove(intf_name)
                        effect_intf_id_list.add(intf_info.id)
                    else:
                        uncovered_info_http.add(intf_name)
                else:
                    uncovered_info_http.add(intf_name)

        for intf_name in affects['dubbo']:
            if intf_name:
                intf_info = self.aiif.get_intf(intf_name=intf_name)
                if intf_info:
                    testcase_info = self.atcm.get_testcase(api_intf_id=intf_info.id)
                    if testcase_info:
                        affects['dubbo'] = affects['dubbo'].remove(intf_name)
                        effect_intf_id_list.add(intf_info.id)
                    else:
                        uncovered_info_dubbo.add(intf_name)
                else:
                    uncovered_info_dubbo.add(intf_name)

        for intf_name in affects['mq']:
            if intf_name:
                intf_info = self.aiif.get_intf(intf_name=intf_name)
                if intf_info:
                    testcase_info = self.atcm.get_testcase(api_intf_id=intf_info.id)
                    if testcase_info:
                        affects['mq'] = affects['mq'].remove(intf_name)
                        effect_intf_id_list.add(intf_info.id)
                    else:
                        uncovered_info_mq.add(intf_name)
                else:
                    uncovered_info_mq.add(intf_name)

        for intf_name in affects['elasticJob']:
            if intf_name:
                intf_info = self.aiif.get_intf(intf_name=intf_name)
                if intf_info:
                    testcase_info = self.atcm.get_testcase(api_intf_id=intf_info.id)
                    if testcase_info:
                        affects['elasticJob'] = affects['elasticJob'].remove(intf_name)
                        effect_intf_id_list.add(intf_info.id)
                    else:
                        uncovered_info_elasticJob.add(intf_name)
                else:
                    uncovered_info_elasticJob.add(intf_name)

        effect_intf_id_list = list(effect_intf_id_list)
        uncovered_info['http'] = list(uncovered_info_http)
        uncovered_info['dubbo'] = list(uncovered_info_dubbo)
        uncovered_info['mq'] = list(uncovered_info_mq)
        uncovered_info['elasticJob'] = list(uncovered_info_elasticJob)

        # 判断当前是否是同一个api_task下的最后一个回调，如果是则更新api_task_info表里面对应记录的task_status为1（启动）
        git_diffs = self.gdvm.get_git_diff_versions_special(seq_no, api_task_id)
        if not git_diffs:
            self.atim.update_task(api_task_id, effect_intf_id_list=json_dumps(effect_intf_id_list),
                                  uncovered_info=json_dumps(uncovered_info),
                                  task_status=1)
        else:
            flag = 0
            for row in git_diffs:
                if not row.detail:
                    flag = 1
                    break
            if flag == 1:
                self.atim.update_task(api_task_id, effect_intf_id_list=json_dumps(effect_intf_id_list),
                                      uncovered_info=json_dumps(uncovered_info))
            if flag == 0:
                self.atim.update_task(api_task_id, effect_intf_id_list=json_dumps(effect_intf_id_list),
                                      uncovered_info=json_dumps(uncovered_info),
                                      task_status=1)



