# -*- coding:utf-8 -*-

import json
import time

from flask import Blueprint
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.api.mysql_manager import (ApiCompanyInfoManager, ApiSystemInfoManager, ApiIntfInfoManager,
                                   ApiProjectSystemRelationManager)
from atp.views.wrappers import timer, login_check, developer_check, master_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.redis_api import RedisManager
from flask import request
from atp.api.git_api import GitlabAPI

redis = RedisManager()
api_system = Blueprint('api_system_interface', __name__)


class ApiSystem(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))
        self.acim = ApiCompanyInfoManager()
        self.asim = ApiSystemInfoManager()
        self.aiim = ApiIntfInfoManager()
        self.apsrm = ApiProjectSystemRelationManager()

    @timer
    def post(self, action):
        if action == 'add':
            return self.add_system()

        elif action == 'edit':
            return self.edit_system()

        elif action == 'delete':
            return self.delete_system()

        elif action == 'queryByCompanyId':
            return self.query_by_company_id()

        elif action == 'getGitBranchNamesBySystemId':
            return self.get_git_branch_names_by_system_id()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @master_check
    def add_system(self):
        try:
            company_id = self.data.pop('companyId')
            system_name = self.data.pop('systemName')
            git_ssh_url = self.data.pop('gitSshURL')
            simple_desc = self.data.pop('simpleDesc', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        system_name = str(system_name).strip()
        git_ssh_url = str(git_ssh_url).strip()

        if not self.acim.get_company(id=company_id):
            return make_response({"code": "201", "desc": "公司id\"{}\"不存在".format(company_id)})

        if self.asim.get_system(system_name=system_name, api_company_id=company_id):
            return make_response({"code": "201", "desc": "公司下存在相同工程名称\"{}\", 无法新增".format(system_name)})

        self.asim.insert_system(system_name=system_name, simple_desc=simple_desc, api_company_id=company_id, git_url=git_ssh_url,
                                creator=self.username)
        return make_response({"code": "000", "desc": "工程\"{}\"增加成功".format(system_name)})

    @master_check
    def edit_system(self):
        try:
            system_id = self.data.pop('systemId')
            system_name = self.data.pop('systemName')
            git_ssh_url = self.data.pop('gitSshURL')
            simple_desc = self.data.pop('simpleDesc', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        system_obj = self.asim.get_system(id=system_id)
        if not system_obj:
            return make_response({"code": "202", "desc": "工程id\"{}\"不存在, 请刷新后重试".format(system_id)})

        exist_system_obj = self.asim.get_system(system_name=system_name, api_company_id=system_obj.api_company_id)
        if exist_system_obj and exist_system_obj.id != int(system_id):
            return make_response({"code": "201", "desc": "公司下存在相同工程名称\"{}\", 无法修改".format(system_name)})

        self.asim.update_system(system_id, system_name=system_name, git_url=git_ssh_url, simple_desc=simple_desc, last_modifier=self.username)
        return make_response({"code": "000", "desc": "工程\"{}\"修改成功".format(system_name)})

    @master_check
    def delete_system(self):
        try:
            system_id = self.data.pop('systemId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        if not self.asim.get_system(id=system_id):
            return make_response({"code": "202", "desc": "工程id\"{}\"不存在, 请刷新后重试".format(system_id)})

        intf_objs = self.aiim.get_intfs(api_system_id=system_id)
        if intf_objs:
            return make_response({"code": "300", "desc": "工程下已配置{}个接口，无法直接删除".format(len(intf_objs))})

        self.asim.delete_system(system_id)
        return make_response({"code": "000", "desc": "工程删除成功"})

    # @login_check
    def query_by_company_id(self):
        try:
            company_id = self.data.pop('companyId')
            project_id = self.data.pop('projectId', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        all_system_objs = self.asim.get_systems(api_company_id=company_id)
        all_system_list = []
        for obj in all_system_objs:
            all_system_list.append(
                {
                    'systemId': obj.id,
                    'label': obj.system_name,
                    'gitUrl': obj.git_url
                }
            )

        include_system_list = []
        system_list = []
        if project_id:
            relation_objs = self.apsrm.get_relations(api_project_id=project_id)
            for system_dic in all_system_list:
                is_include = False
                for relation_obj in relation_objs:
                    if relation_obj.api_system_id == system_dic['systemId']:
                        include_system_list.append(
                            {
                                'systemId': system_dic['systemId'],
                                'label': system_dic['label'],
                            }
                        )
                        is_include = True
                        break
                if not is_include:
                    system_list.append(
                        {
                            'systemId': system_dic['systemId'],
                            'label': system_dic['label'],
                        }
                    )
            return make_response({"code": "000", "systemList": system_list, "includeSystemList": include_system_list})
        else:
            return make_response({"code": "000", "allSystemList": all_system_list})

    def get_git_branch_names_by_system_id(self):
        try:
            git_url = self.data.pop('gitUrl')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        git_userspace_name = git_url.split(":")[1].strip('.git')

        try:
            git = GitlabAPI()
            git_branches_list = git.get_project_branches(git_userspace_name)
            return make_response({"code": "000", "data": {"gitUrl": git_url, "gitBranchList": git_branches_list}})
        except:
            return make_response({"code": "999", "desc": "系统内部错误"})
