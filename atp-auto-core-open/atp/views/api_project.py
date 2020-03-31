# -*- coding:utf-8 -*-

import json

from flask import Blueprint
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.api.mysql_manager import (
    ApiCompanyInfoManager, ApiSystemInfoManager, ApiIntfInfoManager, ApiProjectInfoManager,
    ApiProjectIntfRelationManager, ApiProjectSystemRelationManager
)
from atp.views.wrappers import timer, login_check, developer_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.redis_api import RedisManager
from flask import request

redis = RedisManager()
api_project = Blueprint('api_project_interface', __name__)


class ApiProject(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))
        self.acim = ApiCompanyInfoManager()
        self.asim = ApiSystemInfoManager()
        self.aiim = ApiIntfInfoManager()
        self.apim = ApiProjectInfoManager()
        self.apsrm = ApiProjectSystemRelationManager()
        self.apirm = ApiProjectIntfRelationManager()

    @timer
    def post(self, action):
        if action == 'add':
            return self.add_project()

        elif action == 'edit':
            return self.edit_project()

        elif action == 'delete':
            return self.delete_project()

        elif action == 'list':
            return self.project_list_by_company_id()

        elif action == 'includeSystem':
            return self.include_system()

        elif action == 'includeIntf':
            return self.include_intf()

        elif action == 'excludeSystem':
            return self.exclude_system()

        elif action == 'excludeIntf':
            return self.exclude_intf()

        elif action == 'getIncludeIntfList':
            return self.get_include_intf_list()

        elif action == 'subtree':
            return self.subtree()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def add_project(self):
        try:
            company_id = self.data.pop('companyId')
            project_name = self.data.pop('projectName')
            simple_desc = self.data.pop('simpleDesc', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        project_name = str(project_name).strip()

        if self.apim.get_project(project_name=project_name, api_company_id=company_id):
            return make_response({"code": "201", "desc": "公司下存在相同项目名称\"{}\", 无法新增".format(project_name)})

        self.apim.insert_project(project_name=project_name, simple_desc=simple_desc, api_company_id=company_id,
                                 creator=self.username)
        return make_response({"code": "000", "desc": "项目\"{}\"增加成功".format(project_name)})

    @developer_check
    def edit_project(self):
        try:
            project_id = self.data.pop('projectId')
            project_name = self.data.pop('projectName')
            simple_desc = self.data.pop('simpleDesc', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        project_obj = self.apim.get_project(id=project_id)
        if not project_obj:
            return make_response({"code": "202", "desc": "项目id\"{}\"不存在, 请刷新后重试".format(project_id)})

        exist_project_obj = self.apim.get_project(project_name=project_name, api_company_id=project_obj.api_company_id)
        if exist_project_obj and exist_project_obj.id != int(project_id):
            return make_response({"code": "201", "desc": "公司下存在相同工项目\"{}\", 无法修改".format(project_name)})

        self.apim.update_project(project_id, project_name=project_name, simple_desc=simple_desc,
                                 last_modifier=self.username)
        return make_response({"code": "000", "desc": "公司\"{}\"修改成功".format(project_name)})

    @developer_check
    def delete_project(self):
        try:
            project_id = self.data.pop('projectId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        if not self.apim.get_project(id=project_id):
            return make_response({"code": "202", "desc": "项目id\"{}\"不存在, 请刷新后重试".format(project_id)})

        relation_objs = self.apirm.get_relations(api_project_id=project_id)
        if relation_objs:
            return make_response({"code": "300", "desc": "项目下已引入{}个接口，无法直接删除".format(len(relation_objs))})

        self.apim.delete_project(project_id)
        return make_response({"code": "000", "desc": "项目删除成功"})

    @login_check
    def project_list_by_company_id(self):
        try:
            company_id = int(self.data.pop('companyId', 0))
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        if company_id:
            p_objs = self.apim.get_projects_reverse(api_company_id=company_id)
        else:
            p_objs = self.apim.get_projects()

        # 根据项目分组查询项目中的用例总数
        count_res = self.apim.count_api_project_subtree_group_by_project_id(company_id)

        res_list = []
        for p_obj in p_objs:
            testcase_num = [row[1] for row in count_res if row[0] == p_obj.id][0]
            if testcase_num:
                has_children = True
            else:
                r_obj = ApiProjectSystemRelationManager.get_relation(api_project_id=p_obj.id)
                has_children = True if r_obj else False
            res_list.append(
                {
                    'projectId': p_obj.id,
                    'projectName': p_obj.project_name,
                    'simpleDesc': p_obj.simple_desc,
                    'creator': p_obj.creator,
                    'last_modifier': p_obj.last_modifier,
                    'hasChildren': has_children,
                    'testcaseNum': testcase_num,
                }
            )
        return make_response({"code": "000", "projectList": res_list})

    @developer_check
    def include_system(self):
        try:
            project_id = self.data.pop('projectId')
            system_id_list = self.data.pop('systemIdList')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        if not system_id_list:
            return make_response({"code": "200", "desc": "未选择工程，无法引入"})

        if len(system_id_list) != len(set(system_id_list)):
            return make_response({"code": "101", "desc": "入参校验失败, systemIdList包含重复元素"})

        exist_relation_objs = self.apsrm.get_relations(api_project_id=project_id)
        for exist_relation_obj in exist_relation_objs:
            if exist_relation_obj.api_system_id in system_id_list:
                system_id_list.remove(exist_relation_obj.api_system_id)

        insert_list = []
        for system_id in system_id_list:
            insert_list.append(
                {
                    'api_project_id': project_id,
                    'api_system_id': system_id
                }
            )
        self.apsrm.batch_insert_relation(insert_list)
        return make_response({"code": "000", "desc": "{}个工程引入成功".format(len(system_id_list))})

    @developer_check
    def include_intf(self):
        try:
            project_id = self.data.pop('projectId')
            intf_id_list = self.data.pop('intfIdList')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        if not intf_id_list:
            return make_response({"code": "200", "desc": "未选择接口，无法引入"})

        if len(intf_id_list) != len(set(intf_id_list)):
            return make_response({"code": "101", "desc": "入参校验失败, intf_id_list包含重复元素"})

        exist_relation_objs = self.apirm.get_relations(api_project_id=project_id)
        for exist_relation_obj in exist_relation_objs:
            if exist_relation_obj.api_intf_id in intf_id_list:
                intf_id_list.remove(exist_relation_obj.api_intf_id)

        insert_list = []
        for intf_id in intf_id_list:
            insert_list.append(
                {
                    'api_project_id': project_id,
                    'api_intf_id': intf_id
                }
            )
        self.apirm.batch_insert_relation(insert_list)
        return make_response({"code": "000", "desc": "{}个接口引入成功".format(len(intf_id_list))})

    @developer_check
    def exclude_system(self):
        try:
            project_id = self.data.pop('projectId')
            system_id = self.data.pop('systemId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        obj = self.apsrm.get_relation(api_project_id=project_id, api_system_id=system_id)
        if not obj:
            return make_response({"code": "200", "desc": "此工程未被引入，请刷新后重试"})

        p_i_relation_objs = self.apirm.get_relations(api_project_id=project_id)
        intf_id_list = [p_i_relation_obj.api_intf_id for p_i_relation_obj in p_i_relation_objs]

        intf_objs = self.aiim.get_intfs_in_id_list(intf_id_list)
        for intf_obj in intf_objs:
            if intf_obj.api_system_id == int(system_id):
                return make_response({"code": "300", "desc": "此工程下已引入接口，无法直接去除"})

        self.apsrm.delete_relation(id_=obj.id)
        return make_response({"code": "000", "desc": "工程去除成功"})

    @developer_check
    def exclude_intf(self):
        try:
            project_id = self.data.pop('projectId')
            intf_id = self.data.pop('intfId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        obj = self.apirm.get_relation(api_project_id=project_id, api_intf_id=intf_id)
        if not obj:
            return make_response({"code": "200", "desc": "此接口未被引入，请刷新后重试"})

        self.apirm.delete_relation(id_=obj.id)
        return make_response({"code": "000", "desc": "接口去除成功"})

    @developer_check
    def get_include_intf_list(self):
        """
            Input:
            {"projectId":"7"}
            Return:
            {
                "code": "000",
                "includeIntfList": [
                    441,
                    457,
                    653,
                    658,
                    679,
                    737,
                    680,
                    765
                ]
            }
        """
        try:
            project_id = self.data.pop('projectId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        objs = self.apirm.get_relations(api_project_id=project_id)
        intf_id_list = [obj.api_intf_id for obj in objs]
        return make_response({"code": "000", "includeIntfList": intf_id_list})

    def subtree(self):
        try:
            project_id = int(self.data.pop('projectId'))
        except (KeyError, ValueError):
            return make_response({"code": "100", "desc": "入参校验失败"})

        subtree = []
        index_id = 0

        result_list = self.apim.query_api_project_subtree(project_id)
        patch_result_list = self.apim.query_api_project_subtree_patch(project_id)

        result_dic = db_result_to_map(result_list, patch_result_list)
        for p_k, p_dic in result_dic.items():
            p_name = p_dic.pop('name')
            index_id += 1
            p_tree = {
                'id': index_id,
                'label': p_name,
                'projectId': p_k,
                'children': []
            }
            for s_k, s_dic in p_dic.items():
                s_name = s_dic.pop('name')
                index_id += 1
                s_tree = {
                    'id': index_id,
                    'label': s_name,
                    'systemId': s_k,
                    'children': []
                }
                for i_k, i_dic in s_dic.items():
                    i_name = i_dic.pop('name')
                    index_id += 1
                    i_tree = {
                        'id': index_id,
                        'label': i_name,
                        'intfId': i_k,
                        'children': []
                    }
                    for t_k, t_dic in i_dic.items():
                        index_id += 1
                        t_tree = {
                            'id': index_id,
                            'label': '{0}_{1}'.format(t_k, t_dic['name']),
                            'testcaseId': t_k,
                        }
                        i_tree['children'].append(t_tree)
                    s_tree['children'].append(i_tree)
                p_tree['children'].append(s_tree)
            subtree.append(p_tree)

        return make_response({"code": "000", "data": subtree[0]['children']})


def db_result_to_map(query_res, patch_res=None):
    mapped_dic = {}
    if not patch_res:
        patch_res = []
    for row in query_res:
        width = len(row)
        # print(row)
        if row[0] not in mapped_dic:
            mapped_dic[row[0]] = {'name': row[1]}
            if width >= 4 and row[2]:
                mapped_dic[row[0]][row[2]] = {'name': row[3]}
                if width >= 6 and row[4]:
                    mapped_dic[row[0]][row[2]][row[4]] = {'name': row[5]}
                    if width >= 8 and row[6]:
                        mapped_dic[row[0]][row[2]][row[4]][row[6]] = {'name': row[7]}
        else:
            if width >= 4 and row[2] not in mapped_dic[row[0]]:
                mapped_dic[row[0]][row[2]] = {'name': row[3]}
                if width >= 6 and row[4]:
                    mapped_dic[row[0]][row[2]][row[4]] = {'name': row[5]}
                    if width >= 8 and row[6]:
                        mapped_dic[row[0]][row[2]][row[4]][row[6]] = {'name': row[7]}
            else:
                if width >= 6 and row[4] not in mapped_dic[row[0]][row[2]]:
                    mapped_dic[row[0]][row[2]][row[4]] = {'name': row[5]}
                    if width >= 8 and row[6]:
                        mapped_dic[row[0]][row[2]][row[4]][row[6]] = {'name': row[7]}
                else:
                    if width >= 8 and row[6] not in mapped_dic[row[0]][row[2]][row[4]]:
                        mapped_dic[row[0]][row[2]][row[4]][row[6]] = {'name': row[7]}

    for row in patch_res:
        if row[0] in mapped_dic:
            if row[2] and row[2] not in mapped_dic[row[0]]:
                mapped_dic[row[0]][row[2]] = {'name': row[3]}

    # print(json_dumps(mapped_dic))
    # print(mapped_dic)
    return mapped_dic
