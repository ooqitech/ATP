# -*- coding:utf-8 -*-

import random
import time

from flask import Blueprint, request
from flask_restful import Resource

from atp.api.comm_log import logger
from atp.api.md5 import md5
from atp.api.redis_api import r as redis
from atp.views.wrappers import timer, master_check, developer_check, reporter_check, login_check
from atp.utils.common import get_request_json, make_response
from atp.api.mysql_manager import UserManager
from atp.config.default import get_config

user = Blueprint('user_interface', __name__)

# redis = RedisManager()
config = get_config()


class User(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))

    @timer
    def post(self, action):
        if action == 'login':
            return self.login()

        elif action == 'logout':
            return self.logout()

        elif action == 'add':
            return self.add_user()

        elif action == 'delete':
            return self.delete_user()

        elif action == 'resetPassword':
            return self.reset_password()

        elif action == 'changePassword':
            return self.change_password()

        elif action == 'detail':
            return self.user_detail()

        elif action == 'list':
            return self.user_list()

        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    def login(self):
        """用户登录"""
        try:
            username = self.data["username"]
            plain_password = self.data["password"]
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        user_obj = UserManager.get_user_by_username(username)
        if not user_obj:
            user_obj = UserManager.get_user_by_nickname(username)

        password = md5(plain_password)

        if not user_obj or user_obj.password != password:
            return make_response({"code": "100", "desc": "用户名或密码错误"})

        username = user_obj.username
        nickname = user_obj.nickname
        level = user_obj.level

        old_token = redis.get_user_info(username, key='token')

        # token不存在，或者，token存在但已失效
        if (not old_token) or (not redis.check_token_valid(old_token)):
            token = gen_token(username, password)

            user_map = {'token': token, 'nickname': nickname, 'online': 1, 'level': level}
            redis.set_user_map(username, user_map)
            redis.set_token(token, username, expire_time=config.LOGIN_EXPIRE_TIME)
        else:
            token = old_token
            redis.set_token(token, username, expire_time=config.LOGIN_EXPIRE_TIME)

        return make_response({"code": "000", "desc": "登录成功", "token": token, "username": username,
                              "nickname": nickname})

    def logout(self):
        """用户注销"""
        token = request.headers.get('X-Token')
        if not token:
            return make_response({"code": "100", "desc": "请求头没有token信息"})

        username = redis.get_username(token)
        if not username:
            return make_response({"code": "000", "desc": "注销成功"})

        redis.delete_token(token)
        redis.set_user_map(username, {'online': 0})

        return make_response({"code": "000", "desc": "注销成功"})

    @master_check
    def add_user(self):
        """新增用户"""
        try:
            username = str(self.data.pop('username')).strip()
            nickname = str(self.data.pop('nickname')).strip()
            role = self.data.pop('role')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        obj = UserManager.get_user_by_username(username)
        if obj:
            return make_response({"code": "200", "desc": "用户<{}>已存在".format(username)})

        if role == 'tester':
            level = 30
        else:
            level = 35
        UserManager.insert_user(username=username, nickname=nickname, password=md5(config.DEFAULT_USER_PWD),
                                level=level, user_status=1)
        return make_response({"code": "000", "desc": "用户<{}>新增成功".format(username)})

    @master_check
    def delete_user(self):
        """删除用户"""
        try:
            user_id = self.data.pop('userId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        obj = UserManager.get_user(user_id)
        if not obj:
            return make_response({"code": "200", "desc": "userId不存在"})

        UserManager.delete_user(user_id)
        # 清除redis的token和user
        token = redis.get_user_info(obj.username, key='token')
        redis.delete_token(token)
        redis.delete_user(obj.username)

        return make_response({"code": "000", "desc": "用户已删除"})

    @master_check
    def reset_password(self):
        """重置密码"""
        try:
            user_id = self.data.pop('userId')
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        obj = UserManager.get_user(user_id)
        if not obj:
            return make_response({"code": "200", "desc": "userId不存在"})

        if obj.username in ['admin', 'guest']:
            return make_response({"code": "300", "desc": "特殊账号不能重置密码"})

        user_obj = UserManager.get_user(user_id)
        if user_obj.level in [25, 35]:
            reset_level = 35
        else:
            reset_level = 30

        UserManager.update_user(user_id, password=md5(config.DEFAULT_USER_PWD), level=reset_level, user_status=1)
        # 清除redis的token和user
        token = redis.get_user_info(obj.username, key='token')
        redis.delete_token(token)
        redis.delete_user(obj.username)

        return make_response({"code": "000", "desc": "用户密码已重置为[{}]".format(config.DEFAULT_USER_PWD)})

    @reporter_check
    def change_password(self):
        """修改密码"""
        try:
            old_pwd = str(self.data.pop('oldPassword'))
            new_pwd = str(self.data.pop('newPassword'))
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        default_pwd = str(config.DEFAULT_USER_PWD)

        if new_pwd == default_pwd:
            return make_response({"code": "400", "desc": "不能设定为初始密码[{}]".format(default_pwd)})

        token = request.headers.get('X-Token')
        username = redis.get_username(token)

        user_obj = UserManager.get_user_by_username(username)
        if not user_obj:
            return make_response({"code": "200", "desc": "userId不存在"})

        if user_obj.password != md5(old_pwd):
            return make_response({"code": "300", "desc": "原密码错误"})

        if new_pwd == old_pwd:
            return make_response({"code": "500", "desc": "新旧密码不能相同"})

        # 是否修改初始密码
        if old_pwd == default_pwd:
            # 判断原权限决定升级后的新权限
            if user_obj.level == 35:
                upgrade_level = 25
            else:
                upgrade_level = 20
            kw = {'password': md5(new_pwd), 'level': upgrade_level, 'user_status': 0}
        else:
            kw = {'password': md5(new_pwd)}

        UserManager.update_user(user_obj.id, **kw)

        # 清除redis的token和user
        redis.delete_token(token)
        redis.delete_user(username)

        return make_response({"code": "000", "desc": "密码已修改"})

    @login_check
    def user_detail(self):
        """查询用户详情"""
        token = request.headers.get('X-Token')
        username = redis.get_username(token)

        obj = UserManager.get_user_by_username(username)
        if not obj:
            return make_response({"code": "200", "desc": "userId不存在"})

        status_desc = '已认证' if obj.user_status == 0 else '未认证'
        return make_response({"code": "000", "username": obj.username, "nickname": obj.nickname,
                              "statusDesc": status_desc})

    @login_check
    def user_list(self):
        """分页查询用户列表"""
        try:
            page_no = int(self.data.pop('pageNo'))
            page_size = int(self.data.pop('pageSize'))
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        p_obj = UserManager.paging_query_users(page_no, page_size)

        res_list = []
        for obj in p_obj.items:
            row = {
                "id": obj.id,
                "createTime": format(obj.create_time),
                "username": obj.username,
                "nickname": obj.nickname,
                "userStatus": "已认证" if obj.user_status == 0 else "未认证"
            }
            res_list.append(row)

        return make_response({'code': '000', 'tableData': res_list, "totalNum": p_obj.total})


def gen_token(username, password):
    """生成token"""
    token = md5(username, password, str(int(time.time())))
    return token
