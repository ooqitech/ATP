# -*- coding:utf-8 -*-

import json
import time

from flask import Blueprint
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.api.mysql_manager import (
    ApiCompanyInfoManager, ApiSystemInfoManager, ApiIntfInfoManager, ApiTestcaseInfoManager, ApiTestcaseRequestManager,
    ApiTestcaseTagRelationManager, TestcaseTagManager, ApiTestcaseMainManager, UserManager
)
from atp.engine.api_chain import parse_setup_case_str, get_testcase_chain, get_testcase_chain_objs, \
    get_setupped_case_id_list
from atp.engine.code_to_desc import get_desc_by_case_status, get_desc_by_last_run
from atp.engine.exceptions import LoadCaseError
from atp.engine.handle_testcase import handle_api_testcase, set_testcase_tag
from atp.engine.testcase_detail import get_api_testcase_detail, get_api_testcase_main_detail
from atp.views.wrappers import timer, login_check, developer_check, developer_with_limit_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.redis_api import RedisManager
from atp.utils.cache_data import CacheData
from flask import request

redis = RedisManager()
api_testcase = Blueprint('api_testcase_interface', __name__)


class ApiTestcase(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))
        self.acim = ApiCompanyInfoManager()
        self.asim = ApiSystemInfoManager()
        self.aiim = ApiIntfInfoManager()
        self.atim = ApiTestcaseInfoManager()
        self.atrm = ApiTestcaseRequestManager()
        self.attrm = ApiTestcaseTagRelationManager()
        self.ttm = TestcaseTagManager()
        self.atmm = ApiTestcaseMainManager()
        self.chain_list = []
        self.chain_no = 0
        if self.username:
            self.data["userName"] = self.username

        # self.USERNAME_NICKNAME_DIC = {row[0]: row[1] for row in UserManager.get_all_username_nickname()}

    @staticmethod
    def username2nickname_fast(username):
        if not username:
            return username

        cache = CacheData()
        if username in cache.USERNAME_NICKNAME_DIC:
            return cache.USERNAME_NICKNAME_DIC[username]
        else:
            return username

    @timer
    def post(self, action):
        if action == 'add':
            return self.add_testcase(action)

        elif action == 'edit':
            return self.edit_testcase(action)

        elif action == 'delete':
            return self.delete_testcase()

        # elif action == 'detailOld':
        #     return self.testcase_detail_old()

        elif action == 'detail':
            return self.testcase_detail()

        elif action == 'queryByIntfId':
            return self.query_by_intf_id()

        elif action == 'changeStatus':
            return self.change_status()

        elif action == 'copy':
            return self.copy_testcase()

        elif action == 'copyBytestcaseData':
            return self.copy_testcase_data()

        elif action == 'queryByCallchain':
            return self.query_callchain()

        elif action == 'setTag':
            return self.set_tag()

        elif action == 'changeParent':
            return self.change_parent()

        elif action == 'detailWithSetup':
            return self.testcase_detail_with_setup()

        elif action == 'queryListBySetupCase':
            return self.query_list_by_setup_case()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def add_testcase(self, action):
        try:
            handle_api_testcase(action, **self.data)
        except LoadCaseError:
            return make_response({"code": "200", "desc": "新增用例时出错"})
        return make_response({"code": "000", "desc": "用例新增成功"})

    @developer_with_limit_check
    def edit_testcase(self, action):
        try:
            handle_api_testcase(action, **self.data)
        except LoadCaseError:
            return make_response({"code": "200", "desc": "编辑用例时出错"})
        return make_response({"code": "000", "desc": "用例修改成功"})

    @developer_with_limit_check
    def delete_testcase(self):
        try:
            testcase_id = self.data.pop('testcaseId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        if not self.atim.get_testcase(id=testcase_id):
            return make_response({"code": "200", "desc": "用例id\"{}\"不存在, 请刷新后重试".format(testcase_id)})

        # 检查当前用例是否被其他用例作为前置，如果是无法删除
        setup_case_lists = self.atim.get_id_and_setup_case_list()

        is_setupped = False
        for setup_case_list in setup_case_lists:
            if is_setupped:
                break
            if setup_case_list[1]:
                setup_cases = eval(setup_case_list[1])
                for setup_case_id in setup_cases:
                    if int(setup_case_id.split('-')[1]) == testcase_id:
                        is_setupped = True
                        break

        if is_setupped:
            return make_response({"code": "300", "desc": "当前用例被其他用例引用为前置，无法直接删除"})

        self.atim.delete_testcase(testcase_id)
        r_obj = self.atrm.get_request(api_testcase_id=testcase_id)
        if r_obj:
            self.atrm.delete_request(r_obj.id)

        # 删除tag关系
        relation_objs = ApiTestcaseTagRelationManager.get_relations(api_testcase_id=testcase_id)
        for relation_obj in relation_objs:
            ApiTestcaseTagRelationManager.delete_relation(relation_obj.id)

        return make_response({"code": "000", "desc": "测试用例删除成功"})

    @developer_check
    def testcase_detail(self):
        try:
            testcase_id = self.data.pop("testcaseId")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})

        tc_obj = self.atim.get_testcase(id=testcase_id)

        if not tc_obj:
            return make_response({"code": "101", "desc": "用例id\"{}\"不存在, 请刷新后重试".format(testcase_id)})

        testcase_detail = get_api_testcase_detail(tc_obj)
        return make_response({"code": "000", "data": testcase_detail})

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
            return make_response({"code": "100", "desc": "入参校验失败"})

        if not self.aiim.get_intf(id=intf_id):
            return make_response({"code": "201", "desc": "接口id\"{}\"不存在, 请刷新后重试".format(intf_id)})

        # 查询所有标签{类别-场景}MAP
        tag_objs = self.ttm.query_testcase_tag()
        tag_base_map = {}
        for tag_obj in tag_objs:
            if tag_obj.tag_category not in tag_base_map:
                tag_base_map[tag_obj.tag_category] = [{"tagId": tag_obj.id, "tagName": tag_obj.tag_name}]
            else:
                tag_base_map[tag_obj.tag_category].append({"tagId": tag_obj.id, "tagName": tag_obj.tag_name})

        case_obj = self.atim.paging_query_testcase_by_intf_id(intf_id, page_no, page_size, testcase_name=testcase_name)
        desc_list = []
        for i in case_obj.items:
            case_status_desc = get_desc_by_case_status(i.case_status)
            last_run_desc = get_desc_by_last_run(i.last_run)

            tag_relations = self.attrm.get_relations(api_testcase_id=i.id)
            tag_map = {}
            for base_category in tag_base_map:
                tag_map[base_category] = []
            for relation in tag_relations:
                for category, tag_list in tag_base_map.items():
                    for tag_dic in tag_list:
                        if tag_dic['tagId'] == relation.tag_id:
                            tag_map[category].append(tag_dic)

            # tag_objs = self.attrm.query_tag_info_by_testcase(i.id)
            #
            # tag_id_list = [t_obj[0] for t_obj in tag_objs] if tag_objs else []
            # tag_name_list = [t_obj[1] for t_obj in tag_objs] if tag_objs else []

            testcases_dict = {
                "id": i.id,
                "testcase_name": "{0}__{1}".format(i.testcase_name, i.expect_result),
                "testcase_desc": i.simple_desc,
                "expectResult": i.expect_result,
                "status": case_status_desc,
                "creator": self.username2nickname_fast(i.creator),
                "last_modifier": self.username2nickname_fast(i.last_modifier),
                "last_run": last_run_desc,
                # "tags_id": tag_id_list,
                # "tags_name": tag_name_list,
                "tags": tag_map,
                "createTime": format(i.create_time) if i.create_time else '',
                "updateTime": format(i.update_time) if i.update_time else '',
                "lastRunTime": format(i.last_run_time) if i.last_run_time else '',
            }
            desc_list.append(testcases_dict)
        return make_response({"code": "000", "desc": desc_list, "totalNum": case_obj.total})

    @developer_check
    def change_status(self):
        try:
            testcase_id = self.data.pop("id")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})

        obj = self.atim.get_testcase(id=testcase_id)

        if obj.case_status == 0:
            case_status = 1
        else:
            case_status = 0

        self.atim.update_testcase(id_=testcase_id, case_status=case_status)
        return make_response({"code": "000", "desc": "操作成功"})

    @developer_check
    def query_callchain_old(self):
        """
        查询当前用例的调用链
        :return:
        """
        try:
            testcase_id = self.data.pop("testcaseId")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})
        if not self.atim.get_testcase(id=testcase_id):
            return make_response({"code": "200", "desc": "用例id\"{}\"不存在, 请刷新后重试".format(testcase_id)})
        res = self.traverse_setup_cases(testcase_id)
        res[-1]["chain_no"] += " 当前用例"
        return res

    def traverse_setup_cases(self, testcase_id):
        """
        遍历所有前置testcase_id
        :param testcase_id:
        :return:
        """
        row = self.atim.query_testcase_belong(testcase_id)
        if row[0]:
            setup_cases = eval(row[0])[1]['setup_cases']
        else:
            setup_cases = []
        for setup_case_id in setup_cases:
            if str(testcase_id) != str(setup_case_id):
                self.traverse_setup_cases(setup_case_id)

        extract_v_names = ''
        if row[4]:
            testset = json.loads(row[4])
            for extract_dic in testset['teststeps'][0]['extract']:
                for v_name in extract_dic:
                    extract_v_names += ', $' + v_name

        self.chain_no += 1
        self.chain_list.append({
            "chain_no": str(self.chain_no),
            "testcase_id": testcase_id,
            "testcase_name": row[1],
            "system_name": row[2],
            "intf_name": row[3],
            "extract_v_names": extract_v_names.strip(', ')
        })
        return self.chain_list

    @developer_check
    def query_callchain(self):
        """
        查询当前用例的调用链
        :return:
        """
        try:
            testcase_id = self.data.pop("testcaseId")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})
        tc_obj = self.atim.get_testcase(id=testcase_id)
        if not tc_obj:
            return make_response({"code": "200", "desc": "用例id\"{}\"不存在, 请刷新后重试".format(testcase_id)})
        res_list = get_testcase_chain(testcase_id, case_type=1, with_intf_system_name=True, with_extract=True)
        # res_list.reverse()
        return make_response({"code": "000", "data": res_list})

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

        set_testcase_tag(testcase_id, tag_id_list)

        # objs = self.attrm.get_relations(api_testcase_id=testcase_id)
        # to_delete_id_list = [str(obj.id) for obj in objs]
        #
        # for tag_id in tag_id_list:
        #     obj = self.attrm.get_relation(api_testcase_id=testcase_id, tag_id=tag_id)
        #     if obj and str(obj.id) in to_delete_id_list:
        #         to_delete_id_list.remove(str(obj.id))
        #     else:
        #         self.attrm.insert_relation(api_testcase_id=testcase_id, tag_id=tag_id)
        #
        # for id_ in to_delete_id_list:
        #     self.attrm.delete_relation(id_)

        return make_response({"code": "000", "desc": "设置标签成功"})

    @developer_check
    def copy_testcase(self):
        try:
            testcase_id = self.data.pop('id')
            count = int(self.data.pop('copyNum'))
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        obj = self.atim.get_testcase(id=testcase_id)
        intf_id = obj.api_intf_id
        pre_obj = self.atim.get_last_obj_by_intf(intf_id)
        index = pre_obj.index + 1 if pre_obj else 0
        table_last_obj = self.atim.get_last_obj()
        insert_id = table_last_obj.id + 1 if table_last_obj else 1

        testcase_insert_list = []
        testcase_id_list = []
        for i in range(count):
            case_name = obj.testcase_name + '_copy_{0}_{1}'.format(testcase_id, i + 1)
            testcase_insert_list.append(
                {
                    'id': insert_id + i,
                    'testcase_name': case_name,
                    'type': obj.type,
                    'include': obj.include,
                    'simple_desc': obj.simple_desc,
                    'case_status': obj.case_status,
                    'api_intf_id': obj.api_intf_id,
                    'creator': self.username,
                    'expect_result': obj.expect_result,
                    'index': index + i,
                    'setup_case_list': obj.setup_case_list,
                }
            )
            testcase_id_list.append(insert_id + i)

        self.atim.batch_insert_testcase(testcase_insert_list)

        request_obj = self.atrm.get_request(api_testcase_id=testcase_id)

        request_insert_list = []
        for i in range(count):
            request_insert_list.append(
                {
                    'api_testcase_id': testcase_id_list[i],
                    'request': request_obj.request
                }
            )
        self.atrm.batch_insert_request(request_insert_list)

        # 复制tag
        tag_relation_objs = ApiTestcaseTagRelationManager.get_relations(api_testcase_id=testcase_id)
        tag_id_list = [str(obj.tag_id) for obj in tag_relation_objs]
        tag_relation_insert_list = []
        for i in range(count):
            for tag_id in tag_id_list:
                tag_relation_insert_list.append(
                    {
                        'api_testcase_id': testcase_id_list[i],
                        'tag_id': tag_id
                    }
                )
        self.attrm.batch_insert_relation(tag_relation_insert_list)

        return make_response({"code": "000", "desc": "用例{0}复制成功, 数量{1}".format(testcase_id, count)})

    @developer_check
    def copy_testcase_data(self):
        """
        复制用例数据结构
        :return:
        """
        try:
            to_testcase_id_list = self.data.pop("copyIdList")
            from_testcase_id = self.data.pop("copiedId")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})

        from_obj = self.atim.get_testcase(id=from_testcase_id)
        from_request_obj = self.atrm.get_request(api_testcase_id=from_testcase_id)

        # 检查是否允许复制
        for testcase_id in to_testcase_id_list:
            to_obj = self.atim.get_testcase(id=testcase_id)
            if to_obj.api_intf_id != from_obj.api_intf_id:
                return make_response({"code": "201", "desc": "用例{}与被复制用例不属于同一接口，无法复制".format(testcase_id)})

        tag_relation_objs = ApiTestcaseTagRelationManager.get_relations(api_testcase_id=from_testcase_id)
        from_tag_id_list = [str(obj.tag_id) for obj in tag_relation_objs]

        for testcase_id in to_testcase_id_list:
            self.atim.update_testcase(testcase_id, include=from_obj.include, last_modifier=self.username,
                                      setup_case_list=from_obj.setup_case_list)
            self.atrm.update_request_by_testcase_id(testcase_id, request=from_request_obj.request)
            # 复制标签
            tag_relation_insert_list = []
            for tag_id in from_tag_id_list:
                tag_relation_insert_list.append(
                    {
                        'testcase_id': testcase_id,
                        'tag_id': tag_id
                    }
                )
            self.attrm.batch_insert_relation(tag_relation_insert_list)
        return make_response({"code": "000", "desc": "复制{}数据成功".format(from_testcase_id)})

    @developer_check
    def change_parent(self):
        try:
            id_ = self.data.pop('testcaseId')
            parent_id = self.data.pop('newParentId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        intf_obj = self.aiim.get_intf(id=parent_id)
        if not intf_obj:
            return make_response({"code": "200", "desc": "不存在的接口id, 请刷新后重试"})

        # 更新原用例集其他用例的index
        self.atim.index_update_while_remove_testcase(id_=id_)
        # 获取新用例集的index
        pre_obj = self.atim.get_last_obj_by_intf(parent_id)
        index = pre_obj.index + 1 if pre_obj else 0

        self.atim.update_testcase(
            id_=id_,
            api_intf_id=parent_id, index=index
        )
        return make_response({"code": "000", "desc": "ok"})

    @developer_check
    def testcase_detail_with_setup(self):
        """全链路引入接口用例时使用"""
        try:
            testcase_id = self.data.pop("testcaseId")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})

        detail_list = []

        chain_objs = get_testcase_chain_objs(testcase_id, case_type=1)
        for obj_info in chain_objs:
            if obj_info["case_type"] == 1:
                tc_obj = obj_info["obj"]
                detail_dic = get_api_testcase_detail(tc_obj=tc_obj, without_setup_cases=True)
                detail_dic.pop("include")
                detail_dic.pop("base")
                step = detail_dic.pop("steps")[0]
                intf_obj = self.aiim.get_intf(id=tc_obj.api_intf_id)
                step.update(
                    {
                        "base": {
                            "intfId": tc_obj.api_intf_id,
                            "intfName": intf_obj.intf_name,
                            "intfNameInChinese": intf_obj.intf_desc,
                            "requestType": intf_obj.intf_type,
                            "subName": tc_obj.testcase_name,
                            "subDesc": tc_obj.simple_desc if tc_obj.simple_desc else '',
                            "subExpectResult": tc_obj.expect_result if tc_obj.expect_result else ''
                        }
                    }
                )
                detail_dic.update(step)
                detail_list.append(detail_dic)
            elif obj_info["case_type"] == 2:
                tm_obj = obj_info["obj"]
                detail_dic = get_api_testcase_main_detail(tm_obj=tm_obj)
                detail_dic.pop("base")
                steps_list = detail_dic.pop("steps")
                for step in steps_list:
                    step["base"].pop("subId", None)
                    detail_list.append(step)

        return make_response({"code": "000", "dataList": detail_list})

    @login_check
    def query_list_by_setup_case(self):
        try:
            testcase_id = self.data.pop("testcaseId", 0)
            testcase_main_id = self.data.pop("testcaseMainId", 0)
            if testcase_id:
                testcase_id = int(testcase_id)
            elif testcase_main_id:
                testcase_main_id = int(testcase_main_id)
            else:
                raise KeyError
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验错误"})

        if testcase_id:
            setupped_case_id_list = get_setupped_case_id_list(testcase_id, 1)
        else:
            setupped_case_id_list = get_setupped_case_id_list(testcase_main_id, 2)

        # 获取{用例id:tag_map}
        cache = CacheData()
        tag_base_map = cache.get_tag_base_map()
        tag_relations = self.attrm.get_relations_in_case_ids(setupped_case_id_list)
        case_id_tag_map_tmp_dic = {}
        for case_id in setupped_case_id_list:
            tag_map = {base_category: [] for base_category in tag_base_map}
            for relation in tag_relations:
                if relation.api_testcase_id == case_id:
                    for category, tag_list in tag_base_map.items():
                        for tag_dic in tag_list:
                            if tag_dic['tagId'] == relation.tag_id:
                                tag_map[category].append(tag_dic)
            case_id_tag_map_tmp_dic[case_id] = tag_map

        data_list = []
        res = ApiTestcaseInfoManager.get_intf_and_case_info_in_case_ids(setupped_case_id_list)
        for row in res:
            data_list.append(
                {
                    'intfId': row[0],
                    'intfName': row[1],
                    'intfNameInChinese': row[2],
                    'intfType': row[3],
                    'id': row[4],
                    'testcaseName': row[5],
                    'testcaseCreator': self.username2nickname_fast(row[6]),
                    'testcaseLasModifier': self.username2nickname_fast(row[7]),
                    'status': get_desc_by_case_status(row[8]),
                    'testcaseLastRun': get_desc_by_last_run(row[9]),
                    'testcaseCreateTime': format(row[10]) if row[10] else '',
                    'testcaseUpdateTime': format(row[11]) if row[11] else '',
                    'testcaseLastRunTime': format(row[12]) if row[12] else '',
                    'tags': case_id_tag_map_tmp_dic[row[4]]
                }
            )
        return make_response({'code': '000', 'dataList': data_list})
