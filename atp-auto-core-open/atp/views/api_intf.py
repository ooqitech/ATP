# -*- coding:utf-8 -*-

import json
import time
import re

from flask import Blueprint
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.api.mysql_manager import (
    ApiCompanyInfoManager, ApiSystemInfoManager, ApiIntfInfoManager, ApiTestcaseInfoManager,
    ApiProjectIntfRelationManager, ApiIntfDefaultRequestManager, ApiPublicVariableInfoManager, ApiTestcaseSubManager
)
from atp.utils.tools import json_loads, json_dumps
from atp.views.wrappers import timer, login_check, developer_check, developer_with_limit_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.redis_api import RedisManager
from flask import request

redis = RedisManager()
api_intf = Blueprint('api_intf_interface', __name__)


class ApiIntf(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))
        self.acim = ApiCompanyInfoManager()
        self.asim = ApiSystemInfoManager()
        self.aiim = ApiIntfInfoManager()
        self.atim = ApiTestcaseInfoManager()
        self.apirm = ApiProjectIntfRelationManager()
        self.aidrm = ApiIntfDefaultRequestManager()

    @timer
    def post(self, action):
        if action == 'add':
            return self.add_intf()

        elif action == 'edit':
            return self.edit_intf()

        elif action == 'delete':
            return self.delete_intf()

        elif action == 'detail':
            return self.intf_detail()

        elif action == 'queryBySystemId':
            return self.query_by_system_id()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def add_intf(self):
        try:
            system_id = self.data.pop('systemId')
            intf_desc = self.data.pop('intfNameInChinese')
            intf_type = self.data.pop('type')
            intf_info = self.data.pop('info')
            request_dic = self.data.pop('request', {})
            request_detail_dic = self.data.pop('requestDetail', [])
            intf_relation = self.data.pop('intfRelation')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        intf_desc = str(intf_desc).strip()

        if not self.asim.get_system(id=system_id):
            return make_response({"code": "201", "desc": "工程id\"{}\"不存在".format(system_id)})

        if intf_type != 'MQ':
            if intf_type == 'HTTP':
                intf_info['apiUrl'] = intf_info['apiUrl'].strip()
                intf_name = intf_info['apiUrl']
            elif intf_type == 'DUBBO':
                intf_info['dubboService'] = intf_info['dubboService'].strip()
                intf_info['dubboMethod'] = intf_info['dubboMethod'].strip()
                intf_name = '{0}.{1}'.format(intf_info['dubboService'], intf_info['dubboMethod'])

            company_id = self.asim.get_system(id=system_id).api_company_id
            system_id_list = [row.id for row in self.asim.get_systems(api_company_id=company_id)]
            intf_name_list = [row.intf_name for row in self.aiim.get_intfs_in_system_id_list(system_id_list)]
            if intf_name in intf_name_list:
                company_name = self.acim.get_company(id=company_id).company_name
                return make_response({"code": "201", "desc": "\"{0}\"公司下存在相同接口\"{1}\", 请使用已存在的接口".format(
                    company_name, intf_name)})

        else:
            intf_info['topic'] = intf_info['topic'].strip()
            intf_info['tag'] = intf_info['tag'].strip()
            intf_name = '{0}.{1}'.format(intf_info['topic'], intf_info['tag'])
            obj = self.aiim.get_intf(intf_name=intf_name, api_system_id=system_id)
            if obj:
                return make_response({"code": "201", "desc": "工程下存在相同MQ接口\"{}\", 请使用已存在的MQ接口".format(intf_name)})

        # 增加依赖接口列表属性
        if intf_relation:
            intf_relation = [i[1] for i in intf_relation]
            self.aiim.insert_intf(intf_name=intf_name, intf_desc=intf_desc, api_system_id=system_id,
                                  intf_type=intf_type, intf_info=json_dumps(intf_info), creator=self.username,
                                  intf_relation=json_dumps(intf_relation))
        else:
            self.aiim.insert_intf(intf_name=intf_name, intf_desc=intf_desc, api_system_id=system_id,
                                  intf_type=intf_type, intf_info=json_dumps(intf_info), creator=self.username)
        intf_obj = self.aiim.get_intf(intf_name=intf_name, intf_desc=intf_desc, api_system_id=system_id,
                                      intf_type=intf_type, intf_info=json_dumps(intf_info), creator=self.username)
        self.aidrm.insert_request(api_intf_id=intf_obj.id, request=json_dumps(request_dic),
                                  request_detail=json_dumps(request_detail_dic))
        return make_response({"code": "000", "desc": "接口\"{}\"增加成功".format(intf_name)})

    @developer_with_limit_check
    def edit_intf(self):
        try:
            intf_id = self.data.pop('intfId')
            intf_desc = self.data.pop('intfNameInChinese')
            intf_type = self.data.pop('type')
            intf_info = self.data.pop('info')
            request_dic = self.data.pop('request', {})
            request_detail_dic = self.data.pop('requestDetail', [])
            intf_relation = self.data.pop('intfRelation')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        intf_obj = self.aiim.get_intf(id=intf_id)
        if not intf_obj:
            return make_response({"code": "202", "desc": "接口id\"{}\"不存在, 请刷新后重试".format(intf_id)})

        if intf_type != 'MQ':
            header_variables = []
            if intf_type == 'HTTP':
                intf_info['apiUrl'] = intf_info['apiUrl'].strip()
                intf_name = intf_info['apiUrl']
                header = intf_info['headers']
                variable_regexp = r"\$([\w_]+)"
                header_variables = re.findall(variable_regexp, header)
            elif intf_type == 'DUBBO':
                intf_info['dubboService'] = intf_info['dubboService'].strip()
                intf_info['dubboMethod'] = intf_info['dubboMethod'].strip()
                intf_name = '{0}.{1}'.format(intf_info['dubboService'], intf_info['dubboMethod'])

            company_id = self.asim.get_system(id=intf_obj.api_system_id).api_company_id
            system_id_list = [row.id for row in self.asim.get_systems(api_company_id=company_id)]
            for obj in self.aiim.get_intfs_in_system_id_list(system_id_list):
                if obj.intf_name == intf_name and int(obj.id) != int(intf_id):
                    company_name = self.acim.get_company(id=company_id).company_name
                    return make_response({"code": "201", "desc": "\"{0}\"公司下存在相同接口\"{1}\", 无法将当前接口修改为\"{1}\"".format(
                        company_name, intf_name)})

        else:
            intf_info['topic'] = intf_info['topic'].strip()
            intf_info['tag'] = intf_info['tag'].strip()
            intf_name = '{0}.{1}'.format(intf_info['topic'], intf_info['tag'])

            obj = self.aiim.get_intf(intf_name=intf_name, api_system_id=intf_obj.api_system_id)
            if obj and obj.id != intf_id:
                return make_response({"code": "201", "desc": "工程下存在相同MQ接口\"{}\", 请使用已存在的MQ接口".format(intf_name)})

        if intf_relation:
            intf_relation = [i[1] for i in intf_relation]
            self.aiim.update_intf(intf_id, intf_name=intf_name, intf_desc=intf_desc, intf_type=intf_type,
                                  intf_info=json_dumps(intf_info), last_modifier=self.username,
                                  intf_relation=json_dumps(intf_relation))
        else:
            self.aiim.update_intf(intf_id, intf_name=intf_name, intf_desc=intf_desc, intf_type=intf_type,
                                  intf_info=json_dumps(intf_info), last_modifier=self.username)
        self.aidrm.update_request_by_intf_id(intf_id, request=json_dumps(request_dic),
                                             request_detail=json_dumps(request_detail_dic))

        # 保存接口headers中的公共变量到接口下的所有用例
        if intf_type == 'HTTP' and header_variables:
            to_add_pv_id_list = []
            pv_objs = ApiPublicVariableInfoManager.get_variables(api_company_id=company_id)
            for pv_obj in pv_objs:
                for header_variable in header_variables:
                    if header_variable == pv_obj.variable_name:
                        to_add_pv_id_list.append(pv_obj.id)
                        break
            # 如果存在需添加的公共变量id
            if to_add_pv_id_list:
                tc_objs = ApiTestcaseInfoManager.get_testcases(api_intf_id=intf_id)
                for tc_obj in tc_objs:
                    try:
                        pv_id_list = json_loads(tc_obj.include)[0]['public_variables']
                    except (json.decoder.JSONDecodeError, IndexError, KeyError):
                        pv_id_list = []
                    merge_pv_id_list = pv_id_list + to_add_pv_id_list
                    merge_pv_id_list = list(set(merge_pv_id_list))
                    if set(merge_pv_id_list) != set(pv_id_list):
                        include = json_dumps([{"public_variables": merge_pv_id_list}])
                        ApiTestcaseInfoManager.update_testcase(id_=tc_obj.id, include=include)
                ts_objs = ApiTestcaseSubManager.get_testcase_subs(api_intf_id=intf_id)
                for ts_obj in ts_objs:
                    try:
                        pv_id_list = json_loads(ts_obj.include)[0]['public_variables']
                    except (json.decoder.JSONDecodeError, IndexError, KeyError):
                        pv_id_list = []
                    merge_pv_id_list = pv_id_list + to_add_pv_id_list
                    merge_pv_id_list = list(set(merge_pv_id_list))
                    if set(merge_pv_id_list) != set(pv_id_list):
                        include = json_dumps([{"public_variables": merge_pv_id_list}])
                        ApiTestcaseSubManager.update_testcase_sub(id_=ts_obj.id, include=include)

        return make_response({"code": "000", "desc": "接口\"{}\"修改成功".format(intf_name)})

    @developer_with_limit_check
    def delete_intf(self):
        try:
            intf_id = self.data.pop('intfId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        if not self.aiim.get_intf(id=intf_id):
            return make_response({"code": "202", "desc": "接口id\"{}\"不存在, 请刷新后重试".format(intf_id)})

        testcase_objs = self.atim.get_testcases(api_intf_id=intf_id)
        if testcase_objs:
            return make_response({"code": "300", "desc": "接口下已编写{}个用例，无法直接删除".format(len(testcase_objs))})

        self.aiim.delete_intf(intf_id)
        self.aidrm.delete_request_by_intf_id(intf_id)
        relation_objs = self.apirm.get_relations(api_intf_id=intf_id)
        for relation_obj in relation_objs:
            self.apirm.delete_relation(relation_obj.id)
        return make_response({"code": "000", "desc": "接口删除成功"})

    @login_check
    def intf_detail(self):
        try:
            intf_id = self.data.pop('intfId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        intf_obj = self.aiim.get_intf(id=intf_id)
        if not intf_obj:
            return make_response({"code": "202", "desc": "接口id\"{}\"不存在, 请刷新后重试".format(intf_id)})

        try:
            info = json.loads(intf_obj.intf_info)
        except json.decoder.JSONDecodeError:
            return make_response({"code": "301", "desc": "intf_info字段解析异常"})

        intf_r_obj = self.aidrm.get_request(api_intf_id=intf_id)
        if intf_r_obj:
            request_dic = json.loads(intf_r_obj.request)
            request_detail_dic = json.loads(intf_r_obj.request_detail)
        else:
            request_dic = {}
            request_detail_dic = []

        # 处理依赖列表数据
        if intf_obj.intf_relation:
            relation_intf_objs = self.aiim.get_intfs_in_id_list(json.loads(intf_obj.intf_relation))
            intf_relation = [[i.api_system_id, i.id] for i in relation_intf_objs]
        else:
            intf_relation = []
        data = {
            'intfChineseName': intf_obj.intf_desc,
            'type': intf_obj.intf_type,
            'systemId': intf_obj.api_system_id,
            'info': info,
            'request': request_dic,
            'requestDetail': request_detail_dic,
            'intfRelation': intf_relation
        }
        return make_response({"code": "000", "data": data})

    @login_check
    def query_by_system_id(self):
        try:
            system_id = self.data.pop('systemId')
            project_id = self.data.pop('projectId', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        all_intf_objs = self.aiim.get_intfs(api_system_id=system_id)
        # print(len(all_intf_objs))
        all_intf_list = []
        for obj in all_intf_objs:
            all_intf_list.append(
                {
                    'intfId': obj.id,
                    'label': obj.intf_name,
                }
            )

        include_intf_list = []
        intf_list = []
        if project_id:
            relation_objs = self.apirm.get_relations(api_project_id=project_id)
            for intf_dic in all_intf_list:
                is_include = False
                for relation_obj in relation_objs:
                    if relation_obj.api_intf_id == intf_dic['intfId']:
                        include_intf_list.append(
                            {
                                'intfId': intf_dic['intfId'],
                                'label': intf_dic['label'],
                            }
                        )
                        is_include = True
                        break
                if not is_include:
                    intf_list.append(
                        {
                            'intfId': intf_dic['intfId'],
                            'label': intf_dic['label'],
                        }
                    )
            return make_response({"code": "000", "intfList": intf_list, "includeIntfList": include_intf_list})
        else:
            return make_response({"code": "000", "intfList": all_intf_list, "includeIntfList": include_intf_list})
