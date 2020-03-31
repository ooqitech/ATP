# -*- coding:utf-8 -*-

"""
File Name: `env`.py

增加接口：/env/add
入参格式：
    {
        "envName":"xxx",
        "baseHost":"xxx",
        "dubboZookeeper":"xxx",
        "mqKey":"xxx",
        "dbConnect":"xxx",
        "remoteHost":"xxxx",
        "disconfHost":"xxxx",
        "redisConnect":"xxxx",
        "simpleDesc":"xxxx"(非必填)
    }

修改接口：/env/edit
入参格式:

        {
        "env_Name":"xxx",
        "base_Host":"xxx",
        "dubboZookeeper":"xxx",
        "mqKey":"xxx",
        "dbConnect":"xxx",
        "remoteHost":"xxxx",
        "disconfHost":"xxxx",
        "redisConnect":"xxxx",
        "simpleDesc":"xxxx"(非必填)
    }


删除接口:/env/delete
入参格式：
    {
        “id":xxx
    }

查询接口:/env/list

入参格式:
    {
    }

"""

from flask import Blueprint
from flask_restful import Resource

# from atp.models.atp_auto import EnvInfo
# from atp.api.comm_log import logger
from atp.views.wrappers import timer, developer_check, login_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.mysql_manager import EnvInfoManager
from atp.api.redis_api import RedisManager
from flask import request
redis = RedisManager()
env = Blueprint('env_interface', __name__)


class Env(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))

    @timer
    def post(self, action):
        if action == 'add':
            return self.add_env()

        elif action == 'edit':
            return self.edit_env()

        elif action == 'delete':
            return self.delete_env()

        elif action == 'list':
            return self.env_list()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def add_env(self):
        try:
            env_name = self.data.pop('envName')
            base_host = self.data.pop('baseHost')
            dubbo_zookeeper = self.data.pop('dubboZookeeper')
            mq_key = self.data.pop('mqKey')
            db_connect = self.data.pop('dbConnect')
            remote_host = self.data.pop('remoteHost')
            disconf_host = self.data.pop('disconfHost')
            redis_connect = self.data.pop('redisConnect')
            simple_desc = self.data.pop('simpleDesc', None)
            server_app_map = self.data.pop('serverAppMap', None)
            server_default_user = self.data.pop('serverDefaultUser', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        pim = EnvInfoManager()

        # 判断env_name是否存在
        if pim.is_env_name_exist(env_name):
            return make_response({"code": "201", "desc": "环境配置已存在"})

            # 针对入参进行入库
        pim.insert_env(env_name=env_name, base_host=base_host, dubbo_zookeeper=dubbo_zookeeper, mq_key=mq_key,
                       db_connect=db_connect, remote_host=remote_host, disconf_host=disconf_host,
                       redis_connect=redis_connect, simple_desc=simple_desc, creator=self.username,
                       server_app_map=server_app_map, server_default_user=server_default_user)
        return make_response({"code": "000", "desc": "环境配置添加成功"})

    @developer_check
    def edit_env(self):
        try:
            id_ = self.data.pop('id')
            env_name = self.data.pop('envName')
            base_host = self.data.pop('baseHost')
            dubbo_zookeeper = self.data.pop('dubboZookeeper')
            mq_key = self.data.pop('mqKey')
            db_connect = self.data.pop('dbConnect')
            remote_host = self.data.pop('remoteHost')
            disconf_host = self.data.pop('disconfHost')
            redis_connect = self.data.pop('redisConnect')
            simple_desc = self.data.pop('simpleDesc')
            server_app_map = self.data.pop('serverAppMap', None)
            server_default_user = self.data.pop('serverDefaultUser', None)
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        pim = EnvInfoManager()

        # 判断修改数据是否存在

        if not pim.is_env_id_exist(id_):
            return make_response({"code": "200", "desc": "环境ID不存在,无法修改"})

            # 根据入参进行数据修改

        pim.update_env(id_, env_name=env_name, base_host=base_host, dubbo_zookeeper=dubbo_zookeeper, mq_key=mq_key,
                       db_connect=db_connect, remote_host=remote_host, disconf_host=disconf_host,
                       redis_connect=redis_connect, simple_desc=simple_desc, server_app_map=server_app_map,
                       server_default_user=server_default_user)
        return make_response({"code": "000", "desc": "环境配置修改成功"})

    @developer_check
    def delete_env(self):
        try:
            id_ = self.data.pop('id')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        pim = EnvInfoManager()

        # 判断修改数据是否存在

        if not pim.is_env_id_exist(id_):
            return make_response({"code": "200", "desc": "环境不存在,无法删除"})

        # 根据入参进行数据修改

        pim.delete_env(id_)
        return make_response({"code": "000", "desc": "环境配置删除成功"})

    @developer_check
    def env_list(self):
        # 查询列表入参可以为空或者输入项目名称
        try:
            env_name = self.data.pop('envName', None)
            pim = EnvInfoManager()

            # 判断入参有环境名时，是否可以查询
            if env_name:
                if not pim.is_env_name_exist(env_name):
                    return make_response({"code": "000", "desc": []})

            result1 = pim.env_info(env_name)
            desc_list = []
            envs = []

            # 循环查询env返回所有的env数据，并将其加入list 方便遍历
            for i in result1:
                envs.append([i.id, i.env_name, i.base_host, i.dubbo_zookeeper, i.mq_key, i.db_connect, i.remote_host,
                             i.disconf_host, i.redis_connect, i.simple_desc,i.creator, i.server_app_map,
                             i.server_default_user])

            print(envs)
            # 遍历project_list 并将其添加到字典中，并对字段赋值
            for j in envs:
                env_dict = {
                    "id": j[0],
                    "envName": j[1],
                    "baseHost": j[2],
                    "dubboZookeeper": j[3],
                    "mqKey": j[4],
                    "dbConnect": j[5],
                    "remoteHost": j[6],
                    "disconfHost": j[7],
                    "redisConnect": j[8],
                    "simpleDesc": j[9],
                    "creator": username_to_nickname(j[10]),
                    "serverAppMap": j[11],
                    "serverDefaultUser": j[12]
                }
                desc_list.append(env_dict)
            # 将desc_list 根据项目名进行排序
            desc_list.sort(key=lambda desc_sort: (desc_sort.get("envName", 0)))
            return make_response({"code": "000", "desc": desc_list})
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
