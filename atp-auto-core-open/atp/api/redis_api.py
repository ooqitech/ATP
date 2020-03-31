# -*- coding:utf-8 -*-

import json

import redis

from atp.config.load_config import load_config
from atp.env import RUNNING_ENV

_config = load_config(RUNNING_ENV)


class RedisManager(object):
    """for ATP"""
    def __init__(self):
        pool = redis.ConnectionPool(
            host=_config.REDIS_HOST,
            port=_config.REDIS_PORT,
            db=_config.REDIS_DB_18,
            password=_config.REDIS_PASSWORD,
            decode_responses=True)
        self.conn = redis.Redis(connection_pool=pool)

    def __new__(cls, *args, **kwargs):
        if not hasattr(RedisManager, "_instance"):  # 反射
            RedisManager._instance = object.__new__(cls)
        return RedisManager._instance

    def set_user_map(self, username, user_map):
        self.conn.hmset('user:%s' % username, user_map)

    def set_token(self, token, username, expire_time=3600):
        self.conn.set('token:%s' % token, username)
        self.conn.expire('token:%s' % token, expire_time)

    def get_user_info(self, username, key):
        token = self.conn.hget('user:%s' % username, key)

        if not token:
            return None

        return token

    def check_token_valid(self, token):
        res = self.conn.get('token:%s' % token)

        if res:
            return True
        else:
            return False

    def get_username(self, token):
        username = self.conn.get('token:%s' % token)
        if not username:
            return None

        return username

    def delete_token(self, token):
        self.conn.delete('token:%s' % token)

    def delete_user(self, user):
        self.conn.delete('user:%s' % user)

    def set_project_subtree(self, company_id, project_subtree, expire_time=3600):
        self.conn.set('project_subtree:%s' % company_id, project_subtree)
        self.conn.expire('project_subtree:%s' % company_id, expire_time)

    def get_project_subtree(self, company_id):
        project_subtree = self.conn.get('project_subtree:%s' % company_id)

        if not project_subtree:
            return None
        return project_subtree


class RedisUtils(object):
    """Redis工具类"""
    def __init__(self, host, port, password, db_num):
        self.host = host
        self.port = port
        self.password = password
        self.db_num = db_num
        self.conn = None

    def __enter__(self):
        """初始化连接对象"""
        pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db_num,
            password=self.password,
            decode_responses=True)
        self.conn = redis.Redis(connection_pool=pool)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """调用结束处理"""
        if self.conn:
            self.conn.connection_pool.disconnect()

    def get_str_value(self, key):
        """根据key获取value"""
        res = self.conn.get(key)
        try:
            _res = json.loads(res)
            if isinstance(_res, dict):
                return _res
        except Exception as err:
            return res
        return res

r = RedisManager()

if __name__ == '__main__':
    pass
