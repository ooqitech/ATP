# -*- coding:utf-8 -*-

from flask import Blueprint
from flask_restful import Resource

from atp.api.log_push_queue import LogPushQueue
from atp.api.mysql_manager import ApiRunTaskResultManager
from atp.engine.celery_tasks import celery_push_log, celery_push_task_log
from atp.engine.return_code_desc import CODE_DESC_MAP
from atp.env import RUNNING_ENV
from atp.views.wrappers import timer, login_check, developer_check, developer_with_limit_check
from atp.utils.common import get_request_json, make_response, username_to_nickname
from atp.api.redis_api import RedisManager
from atp.config.default import get_config
from flask import request

redis = RedisManager()
config = get_config()
api_push_log = Blueprint('api_push_log_interface', __name__)


class ApiPushLog(Resource):
    def __init__(self):
        self.data = get_request_json()
        self.username = redis.get_username(request.headers.get('X-Token'))

    @timer
    def post(self, action):
        if action == 'push':
            return self.push()
        elif action == 'pushTaskLog':
            return self.push_task_log()
        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    @developer_check
    def push(self):
        try:
            report_id = str(self.data.pop('reportId'))
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        log_push_queue = LogPushQueue(RUNNING_ENV, report_id=report_id)
        # log_push_queue.push_log()
        queue_name = log_push_queue.queue_name
        arguments = log_push_queue.arguments

        celery_push_log.delay(running_env=RUNNING_ENV, queue_name=queue_name, report_id=report_id)

        return make_response({"code": "000", "desc": "success", "queue": queue_name, "arguments": arguments})

    #@login_check
    def push_task_log(self):
        try:
            run_task_id = int(self.data.pop('taskRunId'))
            intf_id = int(self.data.pop('intfId', 0))
            testcase_id = int(self.data.pop('testcaseId'))
            is_main = self.data.pop('isMain', False)
            if not is_main and not intf_id:
                raise ValueError
        except (KeyError, ValueError):
            return make_response({"code": "100", "desc": CODE_DESC_MAP["100"]})

        run_date = format(ApiRunTaskResultManager.get_result(id=run_task_id).run_date)
        log_dir = '{0}{1}/task_run_{2}/'.format(config.RUN_TASK_LOG_DIR, run_date, run_task_id)

        kwargs = {
            'run_task_id': run_task_id,
            'intf_id': intf_id,
            'testcase_id': testcase_id,
            'is_main': is_main,
            'log_dir': log_dir
        }
        log_push_queue = LogPushQueue(RUNNING_ENV, **kwargs)
        queue_name = log_push_queue.queue_name
        arguments = log_push_queue.arguments
        celery_push_task_log.delay(running_env=RUNNING_ENV, queue_name=queue_name, **kwargs)

        return make_response({"code": "000", "desc": "success", "queue": queue_name, "arguments": arguments})
