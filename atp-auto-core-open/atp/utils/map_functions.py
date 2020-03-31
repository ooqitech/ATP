# -*- coding:utf-8 -*-


def map_testcase_type_to_number(intf_type):
    """
    接口类型映射关系
    :param intf_type:
    :return:
    """
    if intf_type == "HTTP":
        return 1
    elif intf_type == "DUBBO":
        return 2
    elif intf_type == "MQ":
        return 3


def map_number_to_testcase_type(number):
    """
    接口类型映射关系
    :param number:
    :return:
    """
    if number == 1:
        return "HTTP"
    elif number == 2:
        return "DUBBO"
    elif number == 3:
        return "MQ"


def map_number_to_case_status(number):
    if number == 0:
        return "启用中"
    elif number == 1:
        return "已停用"
    else:
        return "已停用"


def map_number_to_last_run(number):
    if number == 0:
        return "成功"
    elif number == 1:
        return "失败"
    else:
        return "未运行"
