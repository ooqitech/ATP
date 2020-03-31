# -*- coding:utf-8 -*-

import copy

from flask import Blueprint, request
from flask_restful import Resource

from atp.api.mysql_manager import (
    ApiProductLineManager, ApiTestcaseMainManager, ApiIntfInfoManager,
    ApiTestcaseSubManager, ApiTestcaseRequestQllManager, TestcaseTagManager, ApiTestcaseMainTagRelationManager,
    ApiTestcaseMainCustomFlowManager)
from atp.api.redis_api import RedisManager
from atp.engine.api_runner import get_full_product_line_name
from atp.engine.exceptions import LoadCaseError
from atp.engine.handle_testcase import handle_api_testcase_main, set_testcase_tag, save_flow
from atp.engine.return_code_desc import CODE_DESC_MAP
from atp.engine.testcase_detail import get_api_testcase_main_detail
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.utils.map_functions import map_number_to_case_status, map_number_to_last_run
from atp.utils.tools import json_loads, json_dumps
from atp.views.wrappers import timer, login_check, developer_check, developer_with_limit_check

redis = RedisManager()
api_testcase_main = Blueprint('api_testcase_main_interface', __name__)


class ApiTestcaseMain(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))
        self.atmtrm = ApiTestcaseMainTagRelationManager()
        self.aplm = ApiProductLineManager()
        self.atmm = ApiTestcaseMainManager()
        self.aiim = ApiIntfInfoManager()
        self.atsm = ApiTestcaseSubManager()
        self.atrqm = ApiTestcaseRequestQllManager()
        self.ttm = TestcaseTagManager()
        if self.username:
            self.data["userName"] = self.username

    @timer
    def post(self, action):
        if action == 'add':
            return self.add_testcase_main(action)

        elif action == 'edit':
            return self.edit_testcase_main(action)

        elif action == 'delete':
            return self.delete_testcase_main()

        elif action == 'queryByProductLine':
            return self.query_by_product_line()

        elif action == 'queryByIntfId':
            return self.query_by_intf_id()

        elif action == 'detail':
            return self.testcase_detail()

        elif action == 'changeStatus':
            return self.change_status()

        elif action == 'copy':
            return self.copy_testcase()

        elif action == 'setTag':
            return self.set_tag()

        elif action == 'changeParent':
            return self.change_parent()

        elif action == 'queryRelatedCasesBySubId':
            return self.query_related_cases_by_sub_id()

        elif action == 'getCustomFlows':
            return self.get_custom_flows()

        elif action == 'saveCustomFlows':
            return self.save_custom_flows()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def add_testcase_main(self, action):
        try:
            handle_api_testcase_main(action, **self.data)
        except LoadCaseError:
            return make_response({"code": "201", "desc": "新增用例时出错"})
        return make_response({"code": "000", "desc": "用例新增成功"})

    @developer_with_limit_check
    def edit_testcase_main(self, action):
        try:
            handle_api_testcase_main(action, **self.data)
        except LoadCaseError:
            return make_response({"code": "201", "desc": "保存用例时出错"})
        return make_response({"code": "000", "desc": "用例保存成功"})

    @developer_with_limit_check
    def delete_testcase_main(self):
        try:
            testcase_id = int(self.data.pop('testcaseId'))
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        tm_obj = self.atmm.get_testcase_main(id=testcase_id)
        if not tm_obj:
            return make_response({"code": "200", "desc": "用例id\"{}\"不存在, 请刷新后重试".format(testcase_id)})

        sub_list = json_loads(tm_obj.sub_list)
        if tm_obj.case_type == 2:
            for sub_id in sub_list:
                sub_obj = self.atsm.get_testcase_sub(id=sub_id)
                main_list = json_loads(sub_obj.main_list) if sub_obj.main_list else []
                if testcase_id in main_list:
                    main_list.remove(testcase_id)
                    self.atsm.update_testcase_sub(sub_id, main_list=json_dumps(main_list))
                # self.atsm.delete_testcase_sub(sub_id)
        else:
            for sub_id in sub_list:
                sub_obj = self.atsm.get_testcase_sub(id=sub_id)
                if sub_obj.api_intf_id == tm_obj.api_intf_id:
                    main_list = json_loads(sub_obj.main_list) if sub_obj.main_list else []
                    if testcase_id in main_list:
                        main_list.remove(testcase_id)
                        self.atsm.update_testcase_sub(sub_id, main_list=json_dumps(main_list))
                    # self.atsm.delete_testcase_sub(sub_id)

        self.atmm.delete_testcase_main(testcase_id)

        # 删除tag关系
        relation_objs = self.atmtrm.get_relations(api_testcase_id=testcase_id)
        for relation_obj in relation_objs:
            self.atmtrm.delete_relation(relation_obj.id)

        return make_response({"code": "000", "desc": "测试用例删除成功"})

    @login_check
    def query_by_product_line(self):
        """
        根据product_line查找该套件下的所有测试用例:
        分页展示，支持用例名称搜索
        """
        try:
            product_line_id = self.data.pop('productLineId')
            page_no = int(self.data.pop('pageNo'))
            page_size = int(self.data.pop('pageSize'))
            testcase_name = self.data.pop('testcaseName', None)
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        if not self.aplm.get_product_line(id=product_line_id):
            return make_response({"code": "201", "desc": "产品线id\"{}\"不存在, 请刷新后重试".format(product_line_id)})

        # 查询所有标签{类别-场景}MAP
        tag_base_map = self.get_tag_base_map()

        case_obj = self.atmm.paging_query_testcase_by_product_line_id(
            product_line_id, page_no, page_size, testcase_name=testcase_name)
        desc_list = []
        for i in case_obj.items:
            case_status = map_number_to_case_status(i.case_status)
            last_run = map_number_to_last_run(i.last_run)

            tag_relations = self.atmtrm.get_relations(api_testcase_id=i.id)
            tag_map = {}
            for base_category in tag_base_map:
                tag_map[base_category] = []
            for relation in tag_relations:
                for category, tag_list in tag_base_map.items():
                    for tag_dic in tag_list:
                        if tag_dic['tagId'] == relation.tag_id:
                            tag_map[category].append(tag_dic)

            testcases_dict = {
                "id": i.id,
                "testcase_name": "{0}__{1}".format(i.testcase_name, i.expect_result),
                "testcase_desc": i.simple_desc,
                "expectResult": i.expect_result,
                "status": case_status,
                "creator": username_to_nickname(i.creator),
                "last_modifier": username_to_nickname(i.last_modifier),
                "last_run": last_run,
                "tags": tag_map,
                "createTime": format(i.create_time) if i.create_time else '',
                "updateTime": format(i.update_time) if i.update_time else '',
                "lastRunTime": format(i.last_run_time) if i.last_run_time else '',
            }
            desc_list.append(testcases_dict)
        return make_response({"code": "000", "desc": desc_list, "totalNum": case_obj.total})

    @login_check
    def query_by_intf_id(self):
        """
        根据intf_id查找该套件下的所有测试用例:
        分页展示，支持用例名称搜索
        """
        try:
            intf_id = self.data.pop('intfId')
            page_no = int(self.data.pop('pageNo'))
            page_size = int(self.data.pop('pageSize'))
            testcase_name = self.data.pop('testcaseName', None)
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        if not self.aiim.get_intf(id=intf_id):
            return make_response({"code": "201", "desc": "接口id\"{}\"不存在, 请刷新后重试".format(intf_id)})

        # 查询所有标签{类别-场景}MAP
        tag_base_map = self.get_tag_base_map()

        case_obj = self.atmm.paging_query_testcase_by_intf_id(
            intf_id, page_no, page_size, testcase_name=testcase_name)
        desc_list = []
        for i in case_obj.items:
            case_status = map_number_to_case_status(i.case_status)
            last_run = map_number_to_last_run(i.last_run)

            tag_relations = self.atmtrm.get_relations(api_testcase_id=i.id)
            tag_map = {}
            for base_category in tag_base_map:
                tag_map[base_category] = []
            for relation in tag_relations:
                for category, tag_list in tag_base_map.items():
                    for tag_dic in tag_list:
                        if tag_dic['tagId'] == relation.tag_id:
                            tag_map[category].append(tag_dic)

            testcases_dict = {
                "id": i.id,
                "testcase_name": i.testcase_name,
                "testcase_desc": i.simple_desc,
                "expectResult": i.expect_result,
                "status": case_status,
                "creator": username_to_nickname(i.creator),
                "last_modifier": username_to_nickname(i.last_modifier),
                "last_run": last_run,
                "tags": tag_map,
                "createTime": format(i.create_time) if i.create_time else '',
                "updateTime": format(i.update_time) if i.update_time else '',
                "lastRunTime": format(i.last_run_time) if i.last_run_time else '',
            }
            desc_list.append(testcases_dict)
        return make_response({"code": "000", "desc": desc_list, "totalNum": case_obj.total})

    @developer_check
    def testcase_detail(self):
        try:
            testcase_id = self.data.pop("testcaseId")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})
        tm_obj = self.atmm.get_testcase_main(id=testcase_id)

        if not tm_obj:
            return make_response({"code": "101", "desc": "用例id\"{}\"不存在, 请刷新后重试".format(testcase_id)})

        testcase_detail = get_api_testcase_main_detail(tm_obj)
        return make_response({"code": "000", "data": testcase_detail})

    @developer_check
    def change_status(self):
        try:
            testcase_id = self.data.pop("id")
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        obj = self.atmm.get_testcase_main(id=testcase_id)

        case_status = 1 if obj.case_status == 0 else 0

        self.atmm.update_testcase_main(id_=testcase_id, case_status=case_status)
        return make_response({"code": "000", "desc": "操作成功"})

    @developer_check
    def copy_testcase(self):
        try:
            testcase_id = self.data.pop('id')
            copy_num = int(self.data.pop('copyNum'))
            copy_type = int(self.data.pop('copyType', 1))  # 1:复制主用例，引用子用例 2:复制主用例和子用例
        except (KeyError, ValueError):
            return make_response({"code": "100", "desc": "入参校验失败"})

        tm_obj = self.atmm.get_testcase_main(id=testcase_id)
        if tm_obj.case_type == 2:
            product_line_id = tm_obj.api_product_line_id
            pre_obj = self.atmm.get_last_obj_by_product_line(product_line_id)
        else:
            intf_id = tm_obj.api_intf_id
            pre_obj = self.atmm.get_last_obj_by_intf(intf_id)

        index = pre_obj.index + 1 if pre_obj else 0
        table_last_obj = self.atmm.get_last_obj()
        insert_id = table_last_obj.id + 1 if table_last_obj else 1

        if copy_type == 2:
            from_sub_list = json_loads(tm_obj.sub_list)
            sub_info_list = []
            for from_sub_id in from_sub_list:
                t_sub_obj = self.atsm.get_testcase_sub(id=from_sub_id)
                tr_obj = self.atrqm.get_request(api_testcase_id=from_sub_id)

                sub_info_list.append(
                    {
                        'request': tr_obj.request,
                        'sub_name': t_sub_obj.sub_name,
                        'request_type': t_sub_obj.request_type,
                        'include': t_sub_obj.include,
                        'simple_desc': t_sub_obj.simple_desc,
                        'case_type': t_sub_obj.case_type,
                        'api_intf_id': t_sub_obj.api_intf_id,
                        'creator': self.username,
                        'expect_result': t_sub_obj.expect_result,
                    }
                )

            testcase_insert_list = []
            testcase_id_list = []
            for i in range(copy_num):
                update_list = copy.deepcopy(sub_info_list)
                to_sub_list = ApiTestcaseSubManager.batch_update_testcase_sub(update_list)

                case_name = tm_obj.testcase_name + '_copy_{0}_{1}'.format(testcase_id, i + 1)
                testcase_insert_list.append(
                    {
                        'id': insert_id + i,
                        'testcase_name': case_name,
                        'simple_desc': tm_obj.simple_desc,
                        'case_type': tm_obj.case_type,
                        'case_status': tm_obj.case_status,
                        'api_intf_id': tm_obj.api_intf_id,
                        'api_product_line_id': tm_obj.api_product_line_id,
                        'sub_list': json_dumps(to_sub_list),
                        'creator': self.username,
                        'expect_result': tm_obj.expect_result,
                        'index': index + i,
                        'setup_flow_list': tm_obj.setup_flow_list,
                        'main_teardown_hooks': tm_obj.main_teardown_hooks,
                    }
                )
                testcase_id_list.append(insert_id + i)
            self.atmm.batch_insert_testcase_main(testcase_insert_list)

            # 复制tag
            tag_relation_objs = self.atmtrm.get_relations(api_testcase_id=testcase_id)
            tag_id_list = [str(obj.tag_id) for obj in tag_relation_objs]
            tag_relation_insert_list = []
            for i in range(copy_num):
                for tag_id in tag_id_list:
                    tag_relation_insert_list.append(
                        {
                            'api_testcase_id': testcase_id_list[i],
                            'tag_id': tag_id
                        }
                    )
            self.atmtrm.batch_insert_relation(tag_relation_insert_list)

        elif copy_type == 1:
            to_sub_list = json_loads(tm_obj.sub_list)
            testcase_insert_list = []
            testcase_id_list = []
            for i in range(copy_num):
                case_name = tm_obj.testcase_name + '_copy_{0}_{1}'.format(testcase_id, i + 1)
                testcase_insert_list.append(
                    {
                        'id': insert_id + i,
                        'testcase_name': case_name,
                        'simple_desc': tm_obj.simple_desc,
                        'case_type': tm_obj.case_type,
                        'case_status': tm_obj.case_status,
                        'api_intf_id': tm_obj.api_intf_id,
                        'api_product_line_id': tm_obj.api_product_line_id,
                        'sub_list': json_dumps(to_sub_list),
                        'creator': self.username,
                        'expect_result': tm_obj.expect_result,
                        'index': index + i,
                        'setup_flow_list': tm_obj.setup_flow_list,
                        'main_teardown_hooks': tm_obj.main_teardown_hooks,
                    }
                )
                testcase_id_list.append(insert_id + i)
            self.atmm.batch_insert_testcase_main(testcase_insert_list)

            # 复制tag
            tag_relation_objs = self.atmtrm.get_relations(api_testcase_id=testcase_id)
            tag_id_list = [str(obj.tag_id) for obj in tag_relation_objs]
            tag_relation_insert_list = []
            for i in range(copy_num):
                for tag_id in tag_id_list:
                    tag_relation_insert_list.append(
                        {
                            'api_testcase_id': testcase_id_list[i],
                            'tag_id': tag_id
                        }
                    )
            self.atmtrm.batch_insert_relation(tag_relation_insert_list)

        else:
            return make_response({"code": "101", "desc": "错误的copy_type:{0}".format(copy_type)})

        return make_response({"code": "000", "desc": "用例{0}复制成功, 数量{1}".format(testcase_id, copy_num)})

    @developer_with_limit_check
    def set_tag(self):
        try:
            testcase_id = self.data.pop("testcaseId")
            tag_id_list = self.data.pop("tagIdList")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})

        for tag_id in tag_id_list:
            if not self.ttm.get_testcase_tag(tag_id):
                return make_response({"code": "200", "desc": "标签id\"{}\"不存在, 请刷新后重试".format(tag_id)})

        set_testcase_tag(testcase_id, tag_id_list, is_main=True)

        return make_response({"code": "000", "desc": "设置标签成功"})

    @login_check
    def query_related_cases_by_sub_id(self):
        try:
            sub_id = self.data.pop("subId")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})

        sub_obj = ApiTestcaseSubManager.get_testcase_sub(id=sub_id)
        if not sub_obj or not sub_obj.main_list or not json_loads(sub_obj.main_list):
            return make_response({"code": "101", "desc": "没有关联的用例信息"})

        main_id_list = json_loads(sub_obj.main_list)
        main_objs = ApiTestcaseMainManager.get_testcases_in_id_list(main_id_list)
        data_list = []
        for main_obj in main_objs:
            p_obj = ApiProductLineManager.get_product_line(id=main_obj.api_product_line_id)
            data_dic = {
                "testcaseId": main_obj.id,
                "testcaseName": main_obj.testcase_name,
                "productLineDesc": get_full_product_line_name(p_obj)
            }
            data_list.append(data_dic)

        return make_response({"code": "000", "data": data_list})

    @login_check
    def get_custom_flows(self):
        try:
            testcase_id = self.data.pop('testcaseId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        flow_objs = ApiTestcaseMainCustomFlowManager.get_flows(testcase_id=testcase_id)
        data_list = [
            {
                'flowId': obj.id,
                'flowName': obj.flow_name,
                'flowIndexList': json_loads(obj.flow_index_list)
            }
            for obj in flow_objs
        ]
        return make_response({"code": "000", "flowList": data_list})

    @developer_check
    def save_custom_flows(self):
        try:
            testcase_id = self.data.pop('testcaseId')
            flow_list = self.data.pop('flowList')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        save_flow(testcase_id, flow_list)

        return make_response({"code": "000", "desc": "保存成功"})

    @developer_check
    def change_parent(self):
        try:
            testcase_id = self.data.pop('testcaseId')
            parent_id = self.data.pop('newParentId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        tm_obj = self.atmm.get_testcase_main(id=testcase_id)
        if tm_obj.case_type == 2:
            pl_obj = self.aplm.get_product_line(id=parent_id)
            if not pl_obj:
                return make_response({"code": "202", "desc": "不存在的目录id, 请刷新后重试"})
            sub_obj = self.aplm.get_product_line(parent_id=pl_obj.id)
            if sub_obj:
                return make_response({"code": "500", "desc": "移动失败，新目录下包含其他目录，请移动到最后一层目录中"})
            pre_tm_obj = self.atmm.get_last_obj_by_product_line(parent_id)
        else:
            intf_obj = self.aiim.get_intf(id=parent_id)
            if not intf_obj:
                return make_response({"code": "201", "desc": "不存在的接口id, 请刷新后重试"})
            pre_tm_obj = self.atmm.get_last_obj_by_intf(parent_id)

        # 更新原产品线/原接口其他用例的index
        self.atmm.index_update_while_remove_testcase(id_=testcase_id)

        # 获取新产品线/新接口的用例index
        index = pre_tm_obj.index + 1 if pre_tm_obj else 0

        # 更新
        if tm_obj.case_type == 2:
            self.atmm.update_testcase_main(
                id_=testcase_id,
                api_product_line_id=parent_id, index=index
            )
        else:
            self.atmm.update_testcase_main(
                id_=testcase_id,
                api_intf_id=parent_id, index=index
            )
        return make_response({"code": "000", "desc": "移动成功"})

    def get_tag_base_map(self):
        # 查询所有标签{类别-场景}MAP
        tag_objs = self.ttm.query_testcase_tag()
        tag_base_map = {}
        for tag_obj in tag_objs:
            if tag_obj.tag_category not in tag_base_map:
                tag_base_map[tag_obj.tag_category] = [{"tagId": tag_obj.id, "tagName": tag_obj.tag_name}]
            else:
                tag_base_map[tag_obj.tag_category].append({"tagId": tag_obj.id, "tagName": tag_obj.tag_name})
        return tag_base_map
