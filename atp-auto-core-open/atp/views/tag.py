# -*- coding:utf-8 -*-

from flask import Blueprint, request
from flask_restful import Resource
from atp.api.redis_api import RedisManager
from atp.api.mysql_manager import TestcaseTagManager
from atp.views.wrappers import timer, login_check, developer_check
from atp.utils.common import get_request_json, make_response

redis = RedisManager()
tag = Blueprint('tag_interface', __name__)


class Tag(Resource):

    def __init__(self):
        self.data = get_request_json()
        self.ttm = TestcaseTagManager()
        self.username = redis.get_username(request.headers.get('X-Token'))
        if self.username:
            self.data["userName"] = self.username

    @timer
    def post(self, action):
        if action == 'list':
            return self.list()

        elif action == 'listForTask':
            return self.list_for_task()

    @login_check
    def list(self):
        tag_objs = self.ttm.query_testcase_tag()
        tag_map = {}
        for tag_obj in tag_objs:
            if tag_obj.tag_category not in tag_map:
                tag_map[tag_obj.tag_category] = [{"tagId": tag_obj.id, "tagName": tag_obj.tag_name}]
            else:
                tag_map[tag_obj.tag_category].append({"tagId": tag_obj.id, "tagName": tag_obj.tag_name})

        return make_response({"code": "000", "tags": tag_map})

    @login_check
    def list_for_task(self):
        tag_objs = self.ttm.query_testcase_tags(is_for_task=1)
        tag_list = []
        for tag_obj in tag_objs:
            tag_list.append(
                {
                    "tagId": tag_obj.id,
                    "tagName": tag_obj.tag_name
                }
            )
        return make_response({"code": "000", "tags": tag_list})
