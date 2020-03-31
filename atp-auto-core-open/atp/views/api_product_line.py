# -*- coding:utf-8 -*-

import json
import time

from flask import Blueprint, request
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.api.mysql_manager import (
    ApiCompanyInfoManager, ApiSystemInfoManager, ApiIntfInfoManager, ApiTestcaseInfoManager,
    ApiProjectIntfRelationManager, ApiProductLineManager, ApiTestcaseMainManager
)
from atp.utils.tools import json_loads, json_dumps
from atp.views.wrappers import timer, login_check, developer_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.redis_api import RedisManager

redis = RedisManager()
api_product_line = Blueprint('api_product_line_interface', __name__)


class ApiProductLine(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))
        # self.acim = ApiCompanyInfoManager()
        # self.asim = ApiSystemInfoManager()
        # self.aiim = ApiIntfInfoManager()
        # self.atim = ApiTestcaseInfoManager()
        self.aplm = ApiProductLineManager()
        self.atmm = ApiTestcaseMainManager()

    @timer
    def post(self, action):
        if action == 'add':
            return self.add_product_line()

        elif action == 'edit':
            return self.edit_product_line()

        elif action == 'delete':
            return self.delete_product_line()

        elif action == 'changeParent':
            return self.change_folder_parent()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def add_product_line(self):
        try:
            product_line_name = self.data.pop('productLineName')
            company_id = self.data.pop('companyId', None)
            parent_id = self.data.pop('parentId', None)
            if not company_id and not parent_id:
                raise KeyError
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        product_line_name = str(product_line_name).strip()

        if company_id:
            # 判断产品线是否已存在，存在无法添加
            if self.aplm.get_product_line(product_line_name=product_line_name, api_company_id=company_id):
                return make_response({"code": "201", "desc": "产品线\"{}\"已存在".format(product_line_name)})

            self.aplm.insert_product_line(product_line_name=product_line_name, api_company_id=company_id,
                                          creator=self.username)
            return make_response({"code": "000", "desc": "产品线\"{}\"增加成功".format(product_line_name)})
        else:
            # 判断目录是否已存在，存在无法添加
            if self.aplm.get_product_line(product_line_name=product_line_name, parent_id=parent_id):
                return make_response({"code": "201", "desc": "目录\"{}\"已存在".format(product_line_name)})

            self.aplm.insert_folder(product_line_name=product_line_name, parent_id=parent_id, creator=self.username)
            return make_response({"code": "000", "desc": "目录\"{}\"增加成功".format(product_line_name)})

    @developer_check
    def edit_product_line(self):
        try:
            product_line_id = self.data.pop('productLineId')
            product_line_name = self.data.pop('productLineName')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        pl_obj = self.aplm.get_product_line(id=product_line_id)
        if pl_obj.api_company_id:
            if not pl_obj:
                return make_response({"code": "202", "desc": "产品线id\"{}\"不存在, 请刷新后重试".format(product_line_id)})
            elif self.aplm.get_product_line(product_line_name=product_line_name, api_company_id=pl_obj.api_company_id):
                return make_response({"code": "201", "desc": "产品线\"{}\"已存在, 无法修改".format(product_line_name)})

            self.aplm.update_product_line(product_line_id, product_line_name=product_line_name, last_modifier=self.username)
            return make_response({"code": "000", "desc": "产品线\"{}\"修改成功".format(product_line_name)})

        else:
            if not pl_obj:
                return make_response({"code": "202", "desc": "目录id\"{}\"不存在, 请刷新后重试".format(product_line_id)})
            elif self.aplm.get_product_line(product_line_name=product_line_name, parent_id=pl_obj.parent_id):
                return make_response({"code": "201", "desc": "目录\"{}\"已存在, 无法修改".format(product_line_name)})

            self.aplm.update_product_line(product_line_id, product_line_name=product_line_name, last_modifier=self.username)
            return make_response({"code": "000", "desc": "目录\"{}\"修改成功".format(product_line_name)})

    @developer_check
    def delete_product_line(self):
        try:
            product_line_id = self.data.pop('productLineId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        pl_obj = self.aplm.get_product_line(id=product_line_id)

        if pl_obj.api_company_id:
            if not pl_obj:
                return make_response({"code": "202", "desc": "产品线id\"{}\"不存在, 请刷新后重试".format(product_line_id)})

            sub_folder_objs = self.aplm.get_product_lines(parent_id=product_line_id)
            if sub_folder_objs:
                return make_response({"code": "300", "desc": "产品线下已配置{}个目录，无法直接删除".format(len(sub_folder_objs))})

            tm_objs = self.atmm.get_testcase_mains(api_product_line_id=product_line_id)
            if tm_objs:
                return make_response({"code": "300", "desc": "产品线下已配置{}个全链路用例，无法直接删除".format(len(tm_objs))})

            self.aplm.delete_product_line(product_line_id)
            return make_response({"code": "000", "desc": "产品线删除成功"})

        else:
            if not pl_obj:
                return make_response({"code": "202", "desc": "目录id\"{}\"不存在, 请刷新后重试".format(product_line_id)})

            sub_folder_objs = self.aplm.get_product_lines(parent_id=product_line_id)
            if sub_folder_objs:
                return make_response({"code": "300", "desc": "节点下已配置{}个目录，无法直接删除".format(len(sub_folder_objs))})

            tm_objs = self.atmm.get_testcase_mains(api_product_line_id=product_line_id)
            if tm_objs:
                return make_response({"code": "300", "desc": "节点下已配置{}个全链路用例，无法直接删除".format(len(tm_objs))})

            self.aplm.delete_folder(product_line_id)
            return make_response({"code": "000", "desc": "目录删除成功"})

    @developer_check
    def change_folder_parent(self):
        try:
            folder_id = self.data.pop('productLineId')
            new_parent_id = self.data.pop('newParentId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        folder_obj = self.aplm.get_product_line(id=folder_id)
        if not folder_obj:
            return make_response({"code": "202", "desc": "目录id\"{}\"不存在, 请刷新后重试".format(folder_id)})

        parent_obj = self.aplm.get_product_line(id=new_parent_id)
        if not parent_obj:
            return make_response({"code": "203", "desc": "目录id\"{}\"不存在, 请刷新后重试".format(new_parent_id)})

        kwargs = {
            'id': folder_obj.id,
            'product_line_name': folder_obj.product_line_name,
            'simple_desc': folder_obj.simple_desc,
            # 'api_company_id': folder_obj.api_company_id,
            'creator': folder_obj.creator,
            'last_modifier': self.username,
            'parent_id': new_parent_id,
        }
        self.aplm.delete_folder(folder_id)
        self.aplm.insert_folder(**kwargs)
        return make_response({"code": "000", "desc": "成功"})
