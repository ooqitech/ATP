# -*- coding:utf-8 -*-

import json
import re
import requests
import traceback
from urllib import parse
from atp.utils.common import make_response

from atp.api.comm_log import logger
from atp.models.atp_auto import EnvInfo


def disconf_session(disconf_host):
    url = disconf_host + '/api/account/session'
    cookie = None
    heard_info = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}  # 请求头
    try:
        response = requests.get(url=url, headers=heard_info)
        logger.debug("response.headers: {0}".format(response.headers))
        cookie = response.headers['Set-Cookie']  # 获取JSESSIONID
        logger.debug("cookie: {0}".format(cookie))
    except Exception as err:
        raise err
    return cookie


def disconf_signin(disconf_host, cookie):
    url = disconf_host + '/api/account/signin'
    heard_info = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Cookie': cookie}
    body = "name=admin&password=admin&remember=0"
    try:
        response = requests.post(url=url, headers=heard_info, data=body)
        logger.debug("response.text: {0}".format(response.text))
    except Exception as err:
        raise err
    return cookie


def disconf_get_config(disconf_host, cookie, config_id):
    url = disconf_host + '/api/web/config/' + str(config_id)
    heard_info = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Cookie': cookie}
    value = None
    try:
        response = requests.get(url=url, headers=heard_info)
        logger.debug("response.text: {0}".format(response.text))
        response_dict = json.loads(response.text)
        logger.info('response_dict: {}'.format(response_dict))
        value = response_dict['result']['value']
    except Exception as err:
        raise err
    return value


def disconf_put_config(disconf_host, cookie, config_id, body):
    url = disconf_host + '/api/web/config/filetext/' + str(config_id)
    heard_info = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Cookie': cookie}
    body = "fileContent=" + parse.quote(body.encode('utf-8'))  # urlencode
    str_response = None
    try:
        response = requests.put(url=url, headers=heard_info, data=body)
        logger.debug("上传disconf配置返回结果: {0}".format(response.text))
        str_response = json.loads(response.text)
        str_response = str_response['success']
    except Exception as err:
        raise err
    return str_response


def query_configId_value(disconf_name, value):
    # 判断第一个和最后一个配置是否符合
    # if value.split('=')[0] == disconf_name:
    #     disconf_List = re.findall(disconf_name + r"=(.+?)\n", value, re.S)
    # elif value.split('\n')[-1].split('=')[0] == disconf_name:
    #     disconf_List = []
    #     disconf_List.append(value.split('\n')[-1].split('=')[-1])
    # else:
    #     disconf_List = re.findall("\n" + disconf_name + r"=(.+?)\n", value, re.S)
    # return disconf_List

    tmp_value = value.split('\n')
    disconf_List = []
    for i in tmp_value:
        if i.split('=', 1)[0] == disconf_name:
            # disconf_List = re.findall(disconf_name + r"=(.+?)\n", value, re.S)
            # disconf_List = i.split('=', 1)[-1]
            disconf_List.append(i)
    return disconf_List

    # tmp_value_list = value.split('\n')
    # disconf_List = []
    # for i in tmp_value_list:
    #     if disconf_name == i.split('=', 1)[0]:
    #         # disconf_List = re.findall(disconf_name + r"=(.+?)\n", value, re.S)
    #         # disconf_List = i.split('=', 1)[-1]
    #         disconf_List.append(i)
    # return disconf_List




def disconf_execute(disconf_obj):
    '''
    操作disconf
    :param disconf_obj:
    :return:
    '''
    logger.debug("操作disconf入参为: {0}".format(disconf_obj))
    try:
        disconf_method = disconf_obj.pop("disconf_method")
        disconf_id = disconf_obj.pop("disconf_id")
        disconf_name = disconf_obj.pop("disconf_name")
        disconf_value = disconf_obj.pop("disconf_value")
        env_name = disconf_obj.pop("env_name")
    except KeyError:
        return make_response({"code": "100", "desc": "入参校验失败"})
    try:
        obj = EnvInfo.query.filter_by(env_name=env_name.upper()).first()
        disconf_host = obj.disconf_host
    except Exception as err:
        raise Exception('\n'.join([str(err), traceback.format_exc()]))
    if disconf_method == "edit":
        return edit_disconf_value(disconf_host, disconf_id, disconf_name, disconf_value)

    elif disconf_method == "add":
        return add_disconf_value(disconf_host, disconf_id, disconf_name, disconf_value)

    elif disconf_method == "delete":
        return del_disconf_value(disconf_host, disconf_id, disconf_name, disconf_value)

    elif disconf_method == "query":
        return query_disconf_value(disconf_host, disconf_id, disconf_name)
    else:
        return make_response({"code": "100", "desc": "入参校验失败"})


def disconf_execute_new(disconf_obj):
    '''
    操作disconf新版本
    :param disconf_obj:
    :return:
    '''
    logger.debug("操作disconf入参为: {0}".format(disconf_obj))
    try:
        disconf_method = disconf_obj.pop("disconf_method")
        disconf_id = disconf_obj.pop("disconf_id")
        disconf_name = disconf_obj.pop("disconf_name")
        disconf_value = disconf_obj.pop("disconf_value")
        disconf_host = disconf_obj.pop("disconf_host")
    except KeyError:
        return make_response({"code": "100", "desc": "入参校验失败"})

    if disconf_method == "edit":
        return edit_disconf_value(disconf_host, disconf_id, disconf_name, disconf_value)

    elif disconf_method == "add":
        return add_disconf_value(disconf_host, disconf_id, disconf_name, disconf_value)

    elif disconf_method == "delete":
        return del_disconf_value(disconf_host, disconf_id, disconf_name, disconf_value)

    elif disconf_method == "query":
        return query_disconf_value(disconf_host, disconf_id, disconf_name)
    else:
        return make_response({"code": "100", "desc": "入参校验失败"})


def edit_disconf_value(disconf_host, disconf_id, disconf_name, disconf_value):
    """
    根据传入的配置文件唯一标识id修改某个配置的值（Disconf）
    :param disconf_id: 配置文件唯一标识
    :param disconf_name: 配置文件的变量名
    :param disconf_value: 配置文件的变量名的值
    :return:
    """
    cookie = disconf_session(disconf_host)
    cookie = disconf_signin(disconf_host, cookie)
    value = disconf_get_config(disconf_host, cookie, disconf_id)
    # if value:
    #     disconf_List = query_configId_value(disconf_name, value)
    #     try:
    #         join_disconf_value = disconf_name + "=" + disconf_List
    #         tmp_list = value.split(join_disconf_value)
    #         # disconf_List[0] = disconf_value
    #         disconf_edit_value = disconf_name + "=" + disconf_value
    #         return disconf_put_config(disconf_host, cookie, disconf_id, disconf_edit_value.join(tmp_list))
    #     except IndexError:
    #         return -2
    # else:
    #     return -1

    # 如果value存在，以换行符分割为list
    if value:
        tmp_value_list = value.split('\n')

     #
     # 轮询list，如果disconf_name，则改变value值
        try:
            for i in range(len(tmp_value_list)):
                if tmp_value_list[i].split('=', 1)[0] == disconf_name:
                    tmp_value_list[i] = disconf_name + "=" + disconf_value
            # return tmp_value_list
            return disconf_put_config(disconf_host, cookie, disconf_id, "\n".join(tmp_value_list))
        except IndexError:
            return -2
    else:
        return -1


def query_disconf_value(disconf_host, disconf_id, disconf_name):
    """
    根据传入的配置文件唯一标识id查询某个配置的值（Disconf）
    :param disconf_id:配置文件唯一标识
    :param disconf_name:配置文件的变量名
    :return:
    """
    cookie = disconf_session(disconf_host)
    cookie = disconf_signin(disconf_host, cookie)
    value = disconf_get_config(disconf_host, cookie, disconf_id)
    if value:
        disconf_List = query_configId_value(disconf_name, value)
        logger.info("查询disconf结果为: {0}".format(disconf_List[0]))
        return str(disconf_List[0]).split('=', 1)[1]
    else:
        return -1


def add_disconf_value(disconf_host, disconf_id, disconf_name, disconf_value):
    """
    根据传入的配置文件唯一标识id增加某个配置的值（Disconf）
    :param disconf_id: 配置文件唯一标识
    :param disconf_name: 配置文件的变量名
    :param disconf_value: 配置文件的变量名的值
    :return:
    """
    cookie = disconf_session(disconf_host)
    cookie = disconf_signin(disconf_host, cookie)
    value = disconf_get_config(disconf_host, cookie, disconf_id)
    if value:
        disconf_List = query_configId_value(disconf_name, value)
        try:
            join_disconf_value = disconf_name + "=" + disconf_List[0]
            tmp_list = value.split(join_disconf_value)
            # disconf_List[0] = disconf_List[0] + ',' + disconf_value
            disconf_edit_value = disconf_name + "=" + disconf_List[0] + ',' + disconf_value
            return disconf_put_config(disconf_host, cookie, disconf_id, disconf_edit_value.join(tmp_list))
        except IndexError:
            return -2
    else:
        return -1


def del_disconf_value(disconf_host, disconf_id, disconf_name, disconf_value):
    """
    根据传入的配置文件唯一标识id删除某个配置的值（Disconf）
    :param disconf_id: 配置文件唯一标识
    :param disconf_name: 配置文件的变量名
    :param disconf_value: 需要删除的配置文件变量名的值
    :return:
    """
    cookie = disconf_session(disconf_host)
    cookie = disconf_signin(disconf_host, cookie)
    value = disconf_get_config(disconf_host, cookie, disconf_id)
    if value:
        disconf_List = query_configId_value(disconf_name, value)
        try:
            join_disconf_value = disconf_name + "=" + disconf_List[0]
            tmp_list = value.split(join_disconf_value)
            if disconf_value not in disconf_List[0]:
                return "{0}配置的值没有发现您要删除的{1}".format(disconf_name, disconf_value)
            if disconf_value + ',' in disconf_List[0]:
                disconf_List[0] = disconf_List[0].replace(disconf_value + ',', '')
            elif ',' + disconf_value in disconf_List[0]:
                disconf_List[0] = disconf_List[0].replace(',' + disconf_value, '')
            else:
                disconf_List[0] = disconf_List[0].replace(disconf_value, '')
            disconf_edit_value = disconf_name + "=" + disconf_List[0]
            return disconf_put_config(disconf_host, cookie, disconf_id, disconf_edit_value.join(tmp_list))
        except IndexError:
            return -2
    else:
        return -1


if __name__ == '__main__':
    pass
