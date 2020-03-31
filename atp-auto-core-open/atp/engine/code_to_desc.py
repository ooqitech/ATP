# -*- coding:utf-8 -*-


def get_desc_by_case_type(case_type):
    if case_type == 1:
        return "接口用例"
    elif case_type == 2:
        return "全链路用例"


def get_case_type_by_desc(desc):
    if desc == "接口用例":
        return 1
    elif desc == "全链路用例":
        return 2


def get_desc_by_case_status(case_status):
    if case_status == 0:
        return "启用中"
    elif case_status == 1:
        return "已停用"
    else:
        return "已停用"


def get_desc_by_last_run(last_run):
    if last_run == 0:
        return "成功"
    elif last_run == 1:
        return "失败"
    else:
        return "未运行"
