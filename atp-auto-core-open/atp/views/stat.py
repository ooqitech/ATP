# -*- coding:utf-8 -*-

import json

from datetime import datetime, timedelta
from flask import Blueprint, request
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.engine.return_code_desc import CODE_DESC_MAP
from atp.utils.tools import json_dumps, json_loads
from atp.views.wrappers import timer, login_check, developer_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.mysql_manager import stat_api_testcase, ApiTestcaseInfoManager, \
    get_reuse_group_by_testcase_id, ApiCompanyInfoManager, ApiSystemInfoManager, get_reuse_group_by_intf_id, \
    get_reuse_group_by_system_id, get_reuse_group_by_day, get_reuse_group_by_month, get_reuse_group_by_week
from atp.api.redis_api import RedisManager

redis = RedisManager()
stat = Blueprint('stat_interface', __name__)


class Stat(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))

    @timer
    def post(self, action):
        if action == 'testcaseSummary':
            return self.testcase_summary()

        elif action == 'getReuseSummary':
            return self.get_reuse_summary()

        elif action == 'getReuseTrend':
            return self.get_reuse_trend()

        elif action == 'getStatistics':
            return self.get_statistics()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    # @login_check
    def testcase_summary(self):
        """
        统计测试用例总数
        output:
        {
            "code": "000",
            "values": {
                "projects": ["米么", "宝生", "汇鑫"],
                "tags": [
                    {
                        "dataList": [2714, 369, 646],
                        "showName": "无标签"
                    }
                ]
            }
        }

        """
        objs = stat_api_testcase()
        values = {
            "projects": [],
            "tags": []
        }
        tag_dic = {"showName": "无标签", "dataList": []}

        for obj in objs:
            tag_dic["dataList"].append(obj[1])
            values["projects"].append(obj[0])

        values["tags"].append(tag_dic)

        return make_response({"code": "000", "values": values})

    def get_reuse_summary(self):
        """
        查询用例复用记录汇总
        Input:
            {   #三选一必填
                "companyId": 1,
                "systemId": 1,
                "intfId": 1,
                "recentDays": 30  #非必填
            }
        Return:
            {
                "code": "000",
                "valueList": [
                    {
                        "labelName": "",
                        "totalReuseNum": 0,
                        "succReuseNum": 0,
                        "failReuseNum": 0,
                        "succRate": "100%"
                    }
                ]
            }

        """
        try:
            company_id = self.data.pop('companyId', None)
            system_id = self.data.pop('systemId', None)
            intf_id = self.data.pop('intfId', None)
            recent_days = self.data.pop('recentDays', None)
            if not (company_id or intf_id or system_id):
                raise KeyError
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        today_date = datetime.date(datetime.now())
        if recent_days:
            start_day = today_date + timedelta(days=-int(recent_days))
        else:
            start_day = datetime.fromtimestamp(1555516800)  # 2019-04-18
            # start_day = today_date + timedelta(days=-30)

        value_list = []
        res_list = []

        if intf_id:
            res_list = get_reuse_group_by_testcase_id(start_day, today_date, intf_id)
        elif system_id:
            res_list = get_reuse_group_by_intf_id(start_day, today_date, system_id)
        elif company_id:
            res_list = get_reuse_group_by_system_id(start_day, today_date, company_id)

        for row in res_list:
            value_list.append(
                {
                    "labelName": row[1],
                    "totalReuseNum": int(row[2]),
                    "succReuseNum": int(row[3]),
                    "failReuseNum": int(row[4]),
                    "succRate": calc_success_rate(int(row[3]), int(row[2]))
                }
            )
        bubble_sort_by_total(value_list)
        return make_response({"code": "000", "valueList": value_list})

    def get_reuse_trend(self):
        """
        查询用例复用记录变化趋势
        Input:
            {   #三选一必填
                "companyId": 1,
                "systemId": 1,
                "intfId": 1,
                "period": "day"/"week"/"month",
                "startTimestamp": 1555689600,
                "endTimestamp": 1557476277,
            }
        Return:
            {
                "code": "000",
                "valueList": [
                    {
                        "labelName": "",
                        "totalReuseNum": 0,
                        "succReuseNum": 0,
                        "failReuseNum": 0,
                        "succRate": "100%"
                    }
                ]
            }
        """
        try:
            company_id = self.data.pop('companyId', None)
            system_id = self.data.pop('systemId', None)
            intf_id = self.data.pop('intfId', None)
            period = self.data.pop('period')
            start_timestamp = self.data.pop('startTimestamp')
            end_timestamp = self.data.pop('endTimestamp')
            if not (company_id or intf_id or system_id):
                raise KeyError
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        start_day = datetime.fromtimestamp(start_timestamp)
        end_day = datetime.fromtimestamp(end_timestamp)
        res_list = []
        value_list = []

        if period == 'day':
            res_list = get_reuse_group_by_day(start_day, end_day,
                                              intf_id=intf_id, system_id=system_id, company_id=company_id)
        elif period == 'week':
            res_list = get_reuse_group_by_week(start_day, end_day,
                                               intf_id=intf_id, system_id=system_id, company_id=company_id)
        elif period == 'month':
            res_list = get_reuse_group_by_month(start_day, end_day,
                                                intf_id=intf_id, system_id=system_id, company_id=company_id)

        for row in res_list:
            value_list.append(
                {
                    "labelName": format(row[0]),
                    "totalReuseNum": int(row[1]),
                    "succReuseNum": int(row[2]),
                    "failReuseNum": int(row[3]),
                    "succRate": calc_success_rate(int(row[2]), int(row[1]))
                }
            )
        # bubble_sort_by_total(value_list)
        return make_response({"code": "000", "valueList": value_list})

    def get_statistics(self):
        try:
            company_id = self.data.pop('companyId')
        except KeyError:
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        data_dic = {'intfTotalNum': 0}
        res = ApiTestcaseInfoManager.count_intf_in_company_id(company_id)
        for row in res:
            data_dic['intfTotalNum'] += row[1]
            if row[0] == 'HTTP':
                data_dic['intfHttpNum'] = row[1]
            elif row[0] == 'DUBBO':
                data_dic['intfDubboNum'] = row[1]
            elif row[0] == 'MQ':
                data_dic['intfMqNum'] = row[1]
        res = ApiSystemInfoManager.count_system_with_intf_in_company_id(company_id)
        data_dic['systemTotalNum'] = res[0]

        res = ApiTestcaseInfoManager.get_testcase_id_in_company_id(company_id)
        testcase_id_list = [row[0] for row in res]
        data_dic['caseTotalNum'] = len(testcase_id_list)
        can_auto_tag_id = 12
        res = ApiTestcaseInfoManager.count_testcase_in_tag_id(testcase_id_list, can_auto_tag_id)
        data_dic['caseAutoNum'] = res[0]

        return make_response({"code": "000", "data": data_dic})


def calc_success_rate(success, total):
    """计算成功率"""
    return "{}%".format(int(success * 100 / total))


def bubble_sort_by_total(alist):
    for j in range(len(alist) - 1, 0, -1):
        # j表示每次遍历需要比较的次数，是逐渐减小的
        for i in range(j):
            if alist[i]["totalReuseNum"] > alist[i + 1]["totalReuseNum"]:
                alist[i], alist[i + 1] = alist[i + 1], alist[i]
