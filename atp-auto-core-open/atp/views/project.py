# -*- coding:utf-8 -*-

"""
File Name: `project`.py
Version:
Description:


增加接口：/project/add
入参格式：
    {
        "projectName":"XXX",
        "simpleDec:"xxx"(非必填)
    }

修改接口：/project/edit
入参格式：
    {
        "id":xx,
        "projectName":"xxx",
        "simpleDec:"xxx"(非必填)
    }

删除接口:/project/delete
入参格式：
    {
        “id":xxx
    }

查询接口:/project/list
入参格式：
    {
        "projectName":"xxx"(非必填)
    }

"""
import json

import time

from flask import Blueprint
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.api.mysql_manager import (
    # ProjectInfoManager, SystemInfoManager, ModuleInfoManager, TestsuiteInfoManager,
    #                                query_subtree, TestcaseInfoManager, query_subtree_with_case_id,
                                   BaseSystemInfoManager, BaseModuleInfoManager, BaseProjectInfoManager,
                                   UICasePageInfoManager, UiProjectInfoManager, UiSystemInfoManager, UiModuleInfoManager,
                                   BaseTestcaseInfoManager)
from atp.views.wrappers import timer, login_check, developer_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.redis_api import RedisManager
from flask import request

redis = RedisManager()
project = Blueprint('project_interface', __name__)


class Project(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.ucpim = UICasePageInfoManager()
        self.username = redis.get_username(request.headers.get('X-Token'))

    @timer
    def post(self, action):
        # if action == 'add':
        #     return self.add_project()
        #
        # elif action == 'edit':
        #     return self.edit_project()
        #
        # elif action == 'delete':
        #     return self.delete_project()
        #
        # elif action == 'detail':
        #     return self.detail()
        #
        # elif action == 'list':
        #     return self.project_list()
        #
        # elif action == 'subtree':
        #     return self.project_subtree()
        #
        # elif action == 'subtreeWithCase':
        #     return self.project_subtree_with_case()

        if action == 'baseList':
            return self.base_project_list()

        elif action == 'baseSubtree':
            return self.base_project_subtree()

        elif action == 'uiSubtree':
            return self.ui_project_subtree()

        elif action == 'pageSubtree':
            return self.page_tree()

        elif action == 'uiList':
            return self.ui_project_list()
        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @login_check
    def base_project_list(self):
        try:
            project_name = self.data.pop('projectName', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        if project_name:
            if not BaseProjectInfoManager.get_project(project_name=project_name):
                return make_response({"code": "200", "desc": "项目名不存在,无法查询"})
        result = BaseProjectInfoManager.base_project_info(project_name)
        project_list = []
        for obj in result:
            project_list.append({
                "id": obj.id,
                "projectName": obj.project_name
            })
        return make_response({"code": "000", "desc": project_list})

    @login_check
    def ui_project_list(self):
        try:
            project_name = self.data.pop('projectName', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        result = UiProjectInfoManager.ui_project_info(project_name)
        project_list = []
        for obj in result:
            project_list.append({
                "id": obj.id,
                "projectName": obj.project_name
            })
        return make_response({"code": "000", "desc": project_list})

    @login_check
    def base_project_subtree(self):
        """根据业务用例的项目id查询配置在该项目下的系统-模块...-业务功能"""
        try:
            project_id = self.data.pop('id')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        system_list = BaseSystemInfoManager.get_all_system(project_id)
        subtree = []
        for system_obj in system_list:
            system_tree = []
            res_all_modules = BaseModuleInfoManager.get_modules(system_id=system_obj.id)
            if res_all_modules:
                for module_obj in res_all_modules:
                    response = query_parent_module_id(module_obj.id)
                    if response:
                        system_tree.append({
                            "children": response,
                            "id": module_obj.id,
                            "label": module_obj.module_name,
                            "moduleId": module_obj.id
                        })
                    else:
                        system_tree.append({
                            "id": module_obj.id,
                            "label": module_obj.module_name,
                            "moduleId_last": module_obj.id
                        })
                subtree.append({
                    "children": system_tree,
                    "id": system_obj.id,
                    "label": system_obj.system_name,
                    "systemId": system_obj.id
                })
            else:
                subtree.append({
                    "id": system_obj.id,
                    "label": system_obj.system_name,
                    "systemId": system_obj.id
                })

        subtree = count_base_subtree(subtree)
        return make_response({"code": "000", "data": subtree})



    @login_check
    def ui_project_subtree(self):
        """根据UI用例的项目id查询配置在该项目下的系统-模块"""
        try:
            project_id = self.data.pop('id')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        system_list = UiSystemInfoManager.get_all_system(project_id)
        subtree = []
        for system_obj in system_list:
            system_tree = []
            res_all_modules = UiModuleInfoManager.get_modules(system_id=system_obj.id)
            print(res_all_modules)
            if res_all_modules:
                for module_obj in res_all_modules:
                        system_tree.append({
                            "id": module_obj.id,
                            "label": module_obj.module_name,
                            "moduleId": module_obj.id
                        })
                subtree.append({
                    "children": system_tree,
                    "id": system_obj.id,
                    "label": system_obj.system_name,
                    "systemId": system_obj.id
                })
            else:
                subtree.append({
                    "id": system_obj.id,
                    "label": system_obj.system_name,
                    "systemId": system_obj.id
                })

        return make_response({"code": "000", "data": subtree})

    @login_check
    def page_tree(self):
        """根据业务用例的项目id查询配置在该项目下的系统-模块...-业务功能"""
        try:
            project_id = self.data.pop('id')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        project_list = UiSystemInfoManager.get_all_system(project_id)
        response = []
        for project_obj in project_list:
            system_obj = UiSystemInfoManager.query_system(id=project_obj.id)
            if not system_obj:
                return make_response({"code": "200", "desc": "系统不存在"})
            page_list = []
            page_info_list = self.ucpim.query_ui_pages(system_id=project_obj.id)
            for page_info in page_info_list:
                page_list.append({
                    "id": page_info.id,
                    "label": page_info.page_name,
                    "pageId": page_info.id
                })
            response.append({
                "children": page_list,
                "id": project_obj.id,
                "label": system_obj.system_name,
                "systemId": project_obj.id
            })
        return make_response({"code": "000", "data": response})


def query_parent_module_id(module_id):
    module_id_list = []
    objs = BaseModuleInfoManager.get_modules(parent_module_id=module_id)
    if objs:
        for obj in objs:
            res = query_parent_module_id(obj.id)
            if res:
                module_id_list.append({
                    "children": res,
                    "id": obj.id,
                    "label": obj.module_name,
                    "moduleId": obj.id
                })
            else:
                module_id_list.append({
                    "id": obj.id,
                    "label": obj.module_name,
                    "moduleId_last": obj.id
                })
        return module_id_list
    else:
        return None


def append_system(subtree, row, index_id):
    system_dict = dict()
    index_id += 1
    system_dict['id'] = index_id
    system_dict['label'] = row.system_name
    system_dict['systemId'] = row[0]
    system_dict['children'] = []

    if row[2]:
        index_id = append_module(system_dict, row, index_id)

    subtree.append(system_dict)

    return index_id


def append_testsuite(module, row, index_id):
    index_id += 1
    testsuite_dict = dict()
    testsuite_dict['id'] = index_id
    testsuite_dict['label'] = row.testsuite_name
    testsuite_dict['testsuiteId'] = row[4]

    module['children'].append(testsuite_dict)

    return index_id


def append_module(system_dict, row, index_id):
    index_id += 1
    module_dict = dict()
    module_dict['id'] = index_id
    module_dict['label'] = row.module_name
    module_dict['moduleId'] = row[2]
    module_dict['children'] = []

    if row[4]:
        index_id = append_testsuite(module_dict, row, index_id)

    system_dict['children'].append(module_dict)

    return index_id


def append_system_with_case(subtree, row, index_id):
    system_dict = dict()
    index_id += 1
    system_dict['id'] = index_id
    system_dict['label'] = row.system_name
    system_dict['systemId'] = row[0]
    system_dict['children'] = []

    if row[2]:
        index_id = append_module_with_case(system_dict, row, index_id)

    subtree.append(system_dict)

    return index_id


def append_testsuite_with_case(module, row, index_id):
    index_id += 1
    testsuite_dict = dict()
    testsuite_dict['id'] = index_id
    testsuite_dict['label'] = row.testsuite_name
    testsuite_dict['testsuiteId'] = row[4]
    testsuite_dict['children'] = []

    if row[6]:
        index_id = append_testcase_with_case(testsuite_dict, row, index_id)

    module['children'].append(testsuite_dict)

    return index_id


def append_module_with_case(system_dict, row, index_id):
    index_id += 1
    module_dict = dict()
    module_dict['id'] = index_id
    module_dict['label'] = row.module_name
    module_dict['moduleId'] = row[2]
    module_dict['children'] = []

    if row[4]:
        index_id = append_testsuite_with_case(module_dict, row, index_id)

    system_dict['children'].append(module_dict)

    return index_id


def append_testcase_with_case(testsuite, row, index_id):
    index_id += 1
    testcase_dict = dict()
    testcase_dict['id'] = index_id
    testcase_dict['label'] = str(row[6]) + '_' + row[7]
    testcase_dict['testcaseId'] = row[6]

    testsuite['children'].append(testcase_dict)

    return index_id


def count_subtree(subtree):
    for s_dic in subtree:
        s_case_count = 0
        for m_dic in s_dic['children']:
            m_case_count = 0
            for ts_dic in m_dic['children']:
                ts_case_count = len(ts_dic['children'])
                ts_dic['label'] += ' ({})'.format(ts_case_count)
                m_case_count += ts_case_count
            m_dic['label'] += ' ({})'.format(m_case_count)
            s_case_count += m_case_count
        s_dic['label'] += ' ({})'.format(s_case_count)

    return subtree


def count_base_subtree(subtree):
    grouped_case_data = BaseTestcaseInfoManager.group_testcases_by_module_id()

    def count_base_case_by_node(node_dic):
        current_node_count = 0
        if 'children' in node_dic:
            for sub_node_dic in node_dic['children']:
                current_node_count += count_base_case_by_node(sub_node_dic)
            node_dic['label'] += ' ({})'.format(current_node_count)
        else:
            if 'moduleId_last' in node_dic:
                for row in grouped_case_data:
                    if row[0] == node_dic['moduleId_last']:
                        current_node_count = row[1]
                        break
            node_dic['label'] += ' ({})'.format(current_node_count)
        return current_node_count

    for s_dic in subtree:
        count_base_case_by_node(s_dic)

    return subtree
