# -*- coding:utf-8 -*-

import functools
import time
import traceback
import importlib

from flask import jsonify, request

from atp.api.comm_log import logger
from atp.utils.common import make_response
from atp.utils.tools import get_host_port
from atp.config.default import get_config
from atp.api.redis_api import r
# from atp.api.mysql_manager import get_obj_from_model_by_id

config = get_config()

_class_map_to_model = {
    'ApiIntf': 'ApiIntfInfo',
    'ApiTestcase': 'ApiTestcaseInfo',
    'ApiTestcaseMain': 'ApiTestcaseMain',
}
_target_param_names = ['id', 'testcaseId', 'intfId']


def timer(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kw):
        who = 'Nobody'
        if hasattr(self, 'username'):
            who = self.username
        logger.info('<==================== {1} Begin call [{0}] ===================='.format(__get_full_class(self), who))
        start_time = time.time()
        try:
            c = func(self, *args, **kw)
        except Exception as err:
            text = '\n'.join(['an error occured on {}'.format(get_host_port()), str(err), traceback.format_exc()])
            logger.error('ATP: 接口发现未知错误 \n {traceback}'.format(traceback=text))
            # subject = 'ATP: 系统发现未知错误'
            # try:
            #     from atp.api.send_email import intf_send_mail
            #     from atp.config.default import get_config
            #     config = get_config()
            #     email_to = config.EMAIL_TO
            #     intf_send_mail(email_to, subject, text)
            #     logger.info("send mail {} {} {}".format(email_to, subject, text))
            # except Exception as e:
            #     logger.error("cannot send email: {} {} {}".format(str(e), subject, text))
            c = jsonify({"code": "999", "desc": "system error"})
        end_time = time.time()
        d_time = end_time - start_time
        logger.info("==================== End call [{0}], run {1:.3}s ====================>\n"
                    .format(__get_full_class(self), d_time))
        return c

    return wrapper


def __get_full_class(obj):
    return "{0}.{1}".format(obj.__module__, obj.__class__.__name__)


def __get_class_name(obj):
    return "{0}".format(obj.__class__.__name__)


def __get_func_name(obj):
    return "{0}".format(obj.__name__)


def custom_func_wrapper(func):
    # for custom
    @functools.wraps(func)
    def wrapper(*args, **kw):
        start_time = time.time()
        try:
            c = func(*args, **kw)
        except Exception as err:
            text = '\n'.join(['an error occured on {}'.format(get_host_port()), str(err), traceback.format_exc()])
            logger.error('ATP: 自定义方法发现未知错误 \n {traceback}'.format(traceback=text))
            c = "自定义方法调用失败"
            raise err
        end_time = time.time()
        d_time = end_time - start_time

        logger.info("==================== custom_func[{0}], run {1:.3}s ====================>\n"
                     .format(func.__name__, d_time))
        return c

    return wrapper


def login_check(func):
    """检查登录状态"""
    @functools.wraps(func)
    def wrapper(self, *args, **kw):
        if config.NON_AUTHENTICATION:
            return func(self, *args, **kw)

        token = request.headers.get('X-Token')

        # from atp.api.redis_api import RedisManager
        # r = RedisManager()

        if token and r.check_token_valid(token):
            c = func(self, *args, **kw)
        else:
            c = make_response({"code": "110", "desc": "用户未登录"})

        return c

    return wrapper


def master_check(func):
    """检查master权限"""
    @functools.wraps(func)
    def wrapper(self, *args, **kw):
        if config.NON_AUTHENTICATION:
            return func(self, *args, **kw)

        token = request.headers.get('X-Token')

        if token:
            # from atp.api.redis_api import RedisManager
            # r = RedisManager()
            # username = r.get_username(token)
            if self.username:
                level = r.get_user_info(self.username, key='level')
                if level and int(level) <= 10:
                    c = func(self, *args, **kw)
                else:
                    c = make_response({"code": "120", "desc": "Sorry, 当前用户没有此项操作权限"})
            else:
                c = make_response({"code": "110", "desc": "用户未登录"})
        else:
            c = make_response({"code": "110", "desc": "用户未登录"})

        return c

    return wrapper


def developer_check(func):
    """检查developer权限"""
    @functools.wraps(func)
    def wrapper(self, *args, **kw):
        if config.NON_AUTHENTICATION:
            return func(self, *args, **kw)

        token = request.headers.get('X-Token')

        if token:
            # from atp.api.redis_api import RedisManager
            # r = RedisManager()
            # username = r.get_username(token)
            if self.username:
                level = r.get_user_info(self.username, key='level')
                if level and int(level) <= 25:
                    r.conn.expire('token:%s' % token, config.LOGIN_EXPIRE_TIME)
                    c = func(self, *args, **kw)
                else:
                    c = make_response({"code": "120", "desc": "Sorry, 当前用户没有此项操作权限"})
            else:
                c = make_response({"code": "110", "desc": "用户未登录"})
        else:
            c = make_response({"code": "110", "desc": "用户未登录"})

        return c

    return wrapper


def developer_with_limit_check(func):
    """检查有限制的developer权限"""
    @functools.wraps(func)
    def wrapper(self, *args, **kw):
        if config.NON_AUTHENTICATION:
            return func(self, *args, **kw)

        token = request.headers.get('X-Token')

        if token:
            if self.username:
                level = r.get_user_info(self.username, key='level')
                if level and int(level) <= 25:
                    if 20 < int(level):
                        class_name = __get_class_name(self)
                        if class_name in _class_map_to_model:
                            creator = get_creator(self)
                            if creator != 'no creator column' and creator != self.username:
                                c = make_response({"code": "130", "desc": "Sorry, 当前用户角色只能修改/删除自己创建的记录"})
                                return c
                    r.conn.expire('token:%s' % token, config.LOGIN_EXPIRE_TIME)
                    c = func(self, *args, **kw)
                else:
                    c = make_response({"code": "120", "desc": "Sorry, 当前用户没有此项操作权限"})
            else:
                c = make_response({"code": "110", "desc": "用户未登录"})
        else:
            c = make_response({"code": "110", "desc": "用户未登录"})

        return c

    return wrapper


def reporter_check(func):
    """检查reporter权限"""
    @functools.wraps(func)
    def wrapper(self, *args, **kw):
        if config.NON_AUTHENTICATION:
            return func(self, *args, **kw)

        token = request.headers.get('X-Token')

        if token:
            # from atp.api.redis_api import RedisManager
            # r = RedisManager()
            # username = r.get_username(token)
            if self.username:
                level = r.get_user_info(self.username, key='level')

                if level and int(level) <= 35:
                    c = func(self, *args, **kw)
                else:
                    c = make_response({"code": "120", "desc": "Sorry, 当前用户没有此项操作权限"})
            else:
                c = make_response({"code": "110", "desc": "用户未登录"})
        else:
            c = make_response({"code": "110", "desc": "用户未登录"})

        return c

    return wrapper


def get_creator(self):
    class_name = __get_class_name(self)
    model_name = _class_map_to_model[class_name]

    id_ = -1
    for param_name in _target_param_names:
        if param_name in self.data:
            id_ = self.data.get(param_name)
            break
        elif 'base' in self.data:
            if param_name in self.data['base']:
                id_ = self.data['base'].get(param_name)
                break

    obj = get_obj_from_model_by_id(model_name, id_)
    if hasattr(obj, 'creator'):
        return obj.creator
    else:
        return 'no creator column'


def get_obj_from_model_by_id(model_name, id_):
    """根据model名称和id查询对应表的记录"""
    # with SessionHandler() as sh:
    import_module = importlib.import_module('atp.models.atp_auto')
    api_class = getattr(import_module, model_name)
    api_instance = api_class()
    obj = api_instance.query.filter_by(id=id_).first()
    return obj
