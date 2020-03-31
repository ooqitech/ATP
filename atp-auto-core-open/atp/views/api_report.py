# -*- coding:utf-8 -*-

import json

from flask import Blueprint, request
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.views.wrappers import timer, login_check, developer_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.mysql_manager import ApiTestReportManager
from atp.api.redis_api import RedisManager

redis = RedisManager()
api_report = Blueprint('api_report_interface', __name__)


class ApiReport(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))

    @timer
    def post(self, action):
        if action == 'delete':
            return self.delete_report()

        elif action == 'queryReportById':
            return self.query_report_by_id()

        elif action == 'pagingQueryReportList':
            return self.paging_query_report_list()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def delete_report(self):
        """删除报告"""
        try:
            id_ = self.data.pop('reportId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        ApiTestReportManager.delete_report(id_)
        return make_response({"code": "000", "desc": "报告删除成功"})

    @login_check
    def query_report_by_id(self):
        """根据reportId查询报告"""
        try:
            report_id = self.data["reportId"]
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        obj = ApiTestReportManager.get_report(id=report_id)

        if not obj:
            return make_response({"code": "100", "desc": "不存在的reportId"})
        elif obj.status == 'running':
            return make_response({"code": "320", "desc": "用例正在运行中，报告未生成"})
        elif obj.status == 'error':
            return make_response({"code": "330", "desc": "用例运行时出错，请检查运行日志"})
        else:
            # url = obj.url.split('8899')[1]
            url = ''

            return make_response(
                {"code": "000", "reportUrl": url, "duration": obj.duration,
                 "desc": "用例运行完成！耗时：{duration}s".format(duration=obj.duration)})

    @login_check
    def paging_query_report_list(self):
        """根据条件分页查询报告列表"""
        try:
            page_no = int(self.data.pop('pageNo'))
            page_size = int(self.data.pop('pageSize'))
            project_id = self.data.pop('projectId')
            start_time = self.data.pop('startTime', None)
            end_time = self.data.pop('endTime', None)
            executor = self.data.pop('executor', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        p_obj = ApiTestReportManager.paging_query_reports(
            page_no, page_size, project_id=project_id, start_time=start_time, end_time=end_time,executor=executor)

        res_list = []
        for obj in p_obj.items:
            row = {
                "id": obj.id,
                "createTime": format(obj.create_time),
                "duration": str(obj.duration) + 's',
                "reportStatus": obj.status,
                "reportUrl": obj.url.split('8899')[1],
                "creator": username_to_nickname(obj.executor)

            }
            res_list.append(row)

        return make_response({'code': '000', 'tableData': res_list, "totalNum": p_obj.total})

