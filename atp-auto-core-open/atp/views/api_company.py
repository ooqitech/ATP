# -*- coding:utf-8 -*-

import json

from datetime import datetime, timedelta
from flask import Blueprint, request
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.api.mysql_manager import (ApiCompanyInfoManager, ApiSystemInfoManager, ApiProductLineManager,
                                   ApiTestcaseMainManager, ApiTestcaseSubManager)
from atp.api.redis_api import RedisManager
from atp.engine.return_code_desc import CODE_DESC_MAP
from atp.utils.common import get_request_json, make_response, db_result_to_map
from atp.views.wrappers import timer, login_check, master_check, developer_check

redis = RedisManager()
api_company = Blueprint('api_company_interface', __name__)

subtree_filter_conditions = ['用例编号', '接口url', '接口中文名']
main_subtree_filter_conditions = ['用例编号', '接口url', '接口中文名']


class ApiCompany(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))
        self.acim = ApiCompanyInfoManager()
        self.asim = ApiSystemInfoManager()
        self.all_sub_objs = None

    @timer
    def post(self, action):
        if action == 'add':
            return self.add_company()

        elif action == 'edit':
            return self.edit_company()

        elif action == 'delete':
            return self.delete_company()

        elif action == 'list':
            return self.company_list()

        elif action == 'subtree':
            return self.subtree()

        elif action == 'projectSubtree':
            return self.project_subtree()

        elif action == 'productLineSubtree':
            return self.product_line_subtree()

        elif action == 'intfCaseSubtree':
            return self.intf_case_subtree()

        elif action == 'getFilterConditions':
            return make_response({"code": "000", "conditions": subtree_filter_conditions})

        elif action == 'subtreeFilter':
            return self.api_subtree_filter()

        elif action == 'mainSubtreeFilter':
            return self.api_main_subtree_filter()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @master_check
    def add_company(self):
        try:
            company_name = self.data.pop('companyName')
            simple_desc = self.data.pop('simpleDesc', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        company_name = str(company_name).strip()

        # 判断公司名是否已存在，存在无法添加
        if self.acim.get_company(company_name=company_name):
            return make_response({"code": "201", "desc": "公司名称\"{}\"已存在".format(company_name)})

        self.acim.insert_company(company_name=company_name, simple_desc=simple_desc, creator=self.username)
        return make_response({"code": "000", "desc": "公司\"{}\"增加成功".format(company_name)})

    @master_check
    def edit_company(self):
        try:
            company_id = self.data.pop('companyId')
            company_name = self.data.pop('companyName')
            simple_desc = self.data.pop('simpleDesc', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        if not self.acim.get_company(id=company_id):
            return make_response({"code": "202", "desc": "公司id\"{}\"不存在, 请刷新后重试".format(company_id)})
        elif self.acim.get_company(company_name=company_name):
            return make_response({"code": "201", "desc": "公司名称\"{}\"已存在, 无法修改".format(company_name)})

        self.acim.update_company(company_id, company_name=company_name, simple_desc=simple_desc,
                                 last_modifier=self.username)
        return make_response({"code": "000", "desc": "公司\"{}\"修改成功".format(company_name)})

    @login_check
    def company_list(self):
        res_list = []
        objs = self.acim.get_companies()
        for obj in objs:
            res_list.append(
                {
                    'companyId': obj.id,
                    'companyName': obj.company_name,
                    'simpleDesc': obj.simple_desc,
                    'creator': obj.creator,
                    'last_modifier': obj.last_modifier
                }
            )
        return make_response({"code": "000", "companyList": res_list})

    @master_check
    def delete_company(self):
        try:
            company_id = self.data.pop('companyId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        if not self.acim.get_company(id=company_id):
            return make_response({"code": "202", "desc": "公司id\"{}\"不存在, 请刷新后重试".format(company_id)})

        system_objs = self.asim.get_systems(api_company_id=company_id)
        if system_objs:
            return make_response({"code": "300", "desc": "公司下已配置{}个工程，无法直接删除公司".format(len(system_objs))})

        self.acim.delete_company(company_id)
        return make_response({"code": "000", "desc": "公司删除成功"})

    @login_check
    def subtree(self):
        """根据公司id查询配置在该公司下的系统-接口"""
        try:
            company_id = self.data.pop('companyId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        subtree = []
        index_id = 1

        result_list = self.acim.query_api_subtree(company_id)
        # logger.info('result_list:{}'.format(json.dumps(result_list)))

        system_id_exist_list = []
        intf_id_exist_list = []
        for row in result_list:
            if row[0] not in system_id_exist_list and row[2] is None:
                system_id_exist_list.append(row[0])
                subtree.append(
                    {
                        'id': index_id,
                        'label': row[1],
                        'systemId': row[0],
                        'gitSshURL': row[4],
                        'children': []
                    }
                )
                index_id += 1
            elif row[0] not in system_id_exist_list and row[2] not in intf_id_exist_list:
                system_id_exist_list.append(row[0])
                intf_id_exist_list.append(row[2])
                subtree.append(
                    {
                        'id': index_id,
                        'label': row[1],
                        'systemId': row[0],
                        'gitSshURL': row[4],
                        'children': [
                            {
                                'id': index_id + 1,
                                'label': row[3],
                                'intfId': row[2]
                            }
                        ]
                    }
                )
                index_id += 2
            elif row[0] in system_id_exist_list and row[2] not in intf_id_exist_list:
                intf_id_exist_list.append(row[2])
                for system in subtree:
                    if row[0] == system['systemId']:
                        system['children'].append(
                            {
                                'id': index_id,
                                'label': row[3],
                                'intfId': row[2]
                            }
                        )
                        break
                index_id += 1

        return make_response({"code": "000", "data": subtree})

    @login_check
    def project_subtree(self):
        """根据公司id查询配置在该公司下的项目-系统-接口-用例"""
        try:
            company_id = self.data.pop('companyId')
            recent_days = int(self.data.pop('recentDays', 0))
        except (KeyError, ValueError):
            return make_response({"code": "100", "desc": "入参校验失败"})

        if recent_days:
            today_date = datetime.date(datetime.now())
            start_day = today_date + timedelta(days=-int(recent_days))
            result_list = self.acim.query_api_project_subtree(company_id, start_day=start_day)
        else:
            result_list = self.acim.query_api_project_subtree(company_id)

        # logger.info('result_list:{}'.format(json.dumps(result_list)))
        patch_result_list = self.acim.query_api_project_subtree_patch(company_id)
        subtree = result_list_to_subtree(result_list, patch_result_list)

        return make_response({"code": "000", "data": subtree})

    @login_check
    def product_line_subtree_old(self):
        """根据公司id查询配置在该公司下的产品线-全链路用例"""
        try:
            company_id = self.data.pop('companyId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        subtree = []
        index_id = 0

        result_list = self.acim.query_api_product_line_subtree(company_id)
        logger.debug(result_list)

        result_dic = db_result_to_map(result_list)
        logger.debug(result_dic)
        for p_k, p_dic in result_dic.items():
            p_name = p_dic.pop('name')
            index_id += 1
            p_tree = {
                'id': index_id,
                'label': p_name,
                'productLineId': p_k,
                'children': []
            }
            for t_k, t_dic in p_dic.items():
                t_name = t_dic.pop('name')
                index_id += 1
                t_tree = {
                    'id': index_id,
                    'label': t_name,
                    'testcaseId': t_k,
                    'children': []
                }
                p_tree['children'].append(t_tree)
            subtree.append(p_tree)

        return make_response({"code": "000", "data": subtree})

    @login_check
    def product_line_subtree(self):
        """根据公司id查询配置在该公司下的产品线-目录-目录-...-全链路用例"""
        try:
            company_id = self.data.pop('companyId')
            with_sub = self.data.pop('withSub', None)
            tag_id_list = self.data.pop('tagIdList', None)
            without_testcase = self.data.pop('withoutTestcase', None)
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        if not (isinstance(tag_id_list, list) and len(tag_id_list) in [1, 2]):
            tag_id_list = None

        self.all_sub_objs = ApiTestcaseSubManager.get_testcase_subs()

        subtree = []
        index = 0

        pl_objs = ApiProductLineManager.get_product_lines(api_company_id=company_id)
        for pl_obj in pl_objs:
            index += 1
            top_tree = {
                'id': index,
                'label': pl_obj.product_line_name,
                'productLineId': pl_obj.id,
                'children': []
            }
            index = get_under_node(pl_obj.id, top_tree['children'], index, with_sub, tag_id_list, without_testcase,
                                   self.all_sub_objs)
            subtree.append(top_tree)

        if tag_id_list:
            # 过滤去除没有用例的节点
            remove_no_case_node(subtree)

        return make_response({"code": "000", "data": subtree})

    @login_check
    def intf_case_subtree(self):
        """根据公司id查询配置在该公司下的工程-接口-用例"""
        try:
            company_id = self.data.pop('companyId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        subtree = []
        index_id = 0

        result_list = self.acim.query_api_intf_case_subtree(company_id)

        result_dic = db_result_to_map(result_list)
        for s_k, s_dic in result_dic.items():
            p_name = s_dic.pop('name')
            index_id += 1
            s_tree = {
                'id': index_id,
                'label': p_name,
                'value': s_k,
                'children': []
            }
            for i_k, i_dic in s_dic.items():
                t_name = i_dic.pop('name')
                index_id += 1
                i_tree = {
                    'id': index_id,
                    'label': t_name,
                    'value': i_k
                }
                for t_k, t_dic in i_dic.items():
                    t_name = t_dic.pop('name')
                    index_id += 1
                    t_tree = {
                        'id': index_id,
                        'label': t_name,
                        'value': t_k
                    }
                    if 'children' not in i_tree:
                        i_tree['children'] = []
                    i_tree['children'].append(t_tree)
                s_tree['children'].append(i_tree)
            subtree.append(s_tree)

        return make_response({"code": "000", "data": subtree})

    @login_check
    def api_subtree_filter(self):
        try:
            company_id = self.data.pop('companyId')
            filter_ = self.data.pop('filter')
            keyword = self.data.pop('keyword').strip()
            if not keyword:
                raise ValueError
            if filter_ not in subtree_filter_conditions:
                raise ValueError
        except (KeyError, ValueError):
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        subtree = subtree_filter_by_keyword(company_id, filter_, keyword)

        return make_response({"code": "000", "data": subtree})

    @login_check
    def api_main_subtree_filter(self):
        try:
            company_id = self.data.pop('companyId')
            filter_ = self.data.pop('filter')
            keyword = self.data.pop('keyword').strip()
            if not keyword:
                raise ValueError
            if filter_ not in subtree_filter_conditions:
                raise ValueError
        except (KeyError, ValueError):
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        subtree = main_subtree_filter_by_keyword(company_id, filter_, keyword)

        return make_response({"code": "000", "data": subtree})


def get_under_node(parent_id, tree_list, index, with_sub, tag_id_list, without_testcase, all_sub_objs):
    pl_objs = ApiProductLineManager.get_product_lines(parent_id=parent_id)
    for pl_obj in pl_objs:
        index += 1
        tree = {
            'id': index,
            'label': pl_obj.product_line_name,
            'productLineId': pl_obj.id,
            'children': []
        }
        index = get_under_node(pl_obj.id, tree['children'], index, with_sub, tag_id_list, without_testcase,
                               all_sub_objs)
        tree_list.append(tree)

    if without_testcase:
        return index

    # tm_objs = ApiTestcaseMainManager.get_testcase_mains(api_product_line_id=parent_id)
    res = ApiTestcaseMainManager.get_testcase_mains_in_tag(api_product_line_id=parent_id, tag_id_list=tag_id_list)

    for row in res:
        index += 1
        tree = {
            'id': index,
            'label': str(row[0]) + '_' + row[1],
            'testcaseId': row[0],
            'children': []
        }
        # 是否需要添加到子用例层
        if with_sub:
            sub_list = json.loads(row[2])

            # sub_objs = ApiTestcaseSubManager.get_testcase_subs_in_id_list(sub_list)
            # for sub_obj in sub_objs:
            #     sub_tree = {
            #         'id': index,
            #         'label': sub_obj.sub_name,
            #         'subId': sub_obj.id,
            #     }
            #     tree['children'].append(sub_tree)

            # for sub_id in sub_list:
            #     sub_obj = ApiTestcaseSubManager.get_testcase_sub(id=sub_id)
            #     sub_tree = {
            #         'id': index,
            #         'label': sub_obj.sub_name,
            #         'subId': sub_id,
            #         'children': []
            #     }
            #     tree['children'].append(sub_tree)

            for sub_id in sub_list:
                for sub_obj in all_sub_objs:
                    if sub_id == sub_obj.id:
                        sub_tree = {
                            'id': index,
                            'label': sub_obj.sub_name,
                            'subId': sub_obj.id,
                        }
                        tree['children'].append(sub_tree)
                        break

        tree_list.append(tree)
    return index


def remove_no_case_node(subtree):
    delete_flag = False
    for i in range(len(subtree) - 1, -1, -1):
        if 'testcaseId' in subtree[i]:
            break
        if subtree[i]['children']:
            delete_flag = remove_no_case_node(subtree[i]['children'])
        else:
            delete_flag = True
        if delete_flag:
            subtree.pop(i)

    return delete_flag


def result_list_to_subtree(result_list, patch_result_list=None):
    subtree = []
    index_id = 1
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
    return subtree


def subtree_filter_by_keyword(company_id, filter_, keyword):
    result_list = []
    if filter_ == '用例编号':
        result_list = ApiCompanyInfoManager.query_api_project_subtree_by_testcase_id(company_id, testcase_id=keyword)
    elif filter_ == 'testcaseName':
        result_list = ApiCompanyInfoManager.query_api_project_subtree_like_testcase_name(company_id,
                                                                                         testcase_name=keyword)
    elif filter_ == 'testcaseCreator':
        result_list = ApiCompanyInfoManager.query_api_project_subtree_like_testcase_creator(company_id,
                                                                                            testcase_creator=keyword)
    elif filter_ == '接口url':
        result_list = ApiCompanyInfoManager.query_api_project_subtree_like_intf_url(company_id, intf_url=keyword)
    elif filter_ == '接口中文名':
        result_list = ApiCompanyInfoManager.query_api_project_subtree_like_intf_desc(company_id, intf_desc=keyword)
    # print(len(result_list))
    if not result_list:
        result_list = subtree_filter_by_keyword_not_belong_project(company_id, filter_, keyword)
    return result_list_to_subtree(result_list)


def subtree_filter_by_keyword_not_belong_project(company_id, filter_, keyword):
    # 补充查询
    result_list = []
    if filter_ == '用例编号':
        result_list = ApiCompanyInfoManager.query_api_subtree_by_testcase_id(company_id, testcase_id=keyword)
    elif filter_ == '接口url':
        result_list = ApiCompanyInfoManager.query_api_subtree_like_intf_url(company_id, intf_url=keyword)
    elif filter_ == '接口中文名':
        result_list = ApiCompanyInfoManager.query_api_subtree_like_intf_desc(company_id, intf_desc=keyword)

    if result_list:
        # 补齐特殊的项目id和项目名称
        new_result_list = []
        for row in result_list:
            row = list(row)
            row.insert(0, -1)
            row.insert(1, '未归属到任何项目')
            new_result_list.append(row)
        result_list = new_result_list

    return result_list


def main_subtree_filter_by_keyword(company_id, filter_, keyword):
    result_list = []
    if filter_ == '用例编号':
        result_list = ApiCompanyInfoManager.query_api_project_subtree_by_testcase_id(company_id, testcase_id=keyword)
    elif filter_ == '接口url':
        result_list = ApiCompanyInfoManager.query_api_project_subtree_like_intf_url(company_id, intf_url=keyword)
    elif filter_ == '接口中文名':
        result_list = ApiCompanyInfoManager.query_api_project_subtree_like_intf_desc(company_id, intf_desc=keyword)

    print(len(result_list))
    return result_list_to_subtree(result_list)
