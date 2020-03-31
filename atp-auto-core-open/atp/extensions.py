# -*- coding:utf-8 -*-

import flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from kombu import Exchange, Queue

from atp.config.load_config import load_config
from atp.env import RUNNING_ENV

current_config = load_config(RUNNING_ENV)


class FlaskCelery(Celery):

    def __init__(self, *args, **kwargs):

        super(FlaskCelery, self).__init__(*args, **kwargs)
        self.patch_task()

        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def patch_task(self):
        TaskBase = self.Task
        _celery = self

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
                else:
                    with _celery.app.app_context():
                        return TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app):

        self.app = app
        self.app.config['CELERY_BROKER_URL'] = current_config.BROKER_URL
        self.app.config['CELERY_RESULT_BACKEND'] = current_config.CELERY_RESULT_BACKEND
        self.conf.update(
            CELERY_TIMEZONE='Asia/Shanghai',
            CELERY_ENABLE_UTC=True,
            CELERY_ACCEPT_CONTENT=['json'],
            CELERY_TASK_SERIALIZER='json',
            CELERY_RESULT_SERIALIZER='json',
            CELERYD_FORCE_EXECV=True,  # 非常重要,有些情况下可以防止死锁
            # CELERYD_CONCURRENCY=10,  # 并发worker数
            CELERY_DISABLE_RATE_LIMITS=True,   # 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
            CELERYD_MAX_TASKS_PER_CHILD=2,  # 每个worker执行了多少任务就会死掉，死掉后会新建一个worker
            # CELERY_IMPORTS=['atp.engine.api_tasks'],
            CELERY_QUEUES=(
                Queue("default", Exchange("default"), routing_key="default"),
                Queue("for_task", Exchange("for_task"), routing_key="for_task"),
            ),
            # 路由
            CELERY_ROUTES={
                'tasks.collect': {"queue": "for_task", "routing_key": "for_task"},
                'tasks.intf_or_main': {"queue": "for_task", "routing_key": "for_task"},
                'tasks.main': {"queue": "for_task", "routing_key": "for_task"},
                'celery.chord_unlock': {"queue": "for_task", "routing_key": "for_task"},
            },
            # 如果不指定QUEUE 那么就用default
            CELERY_DEFAULT_QUEUE='default',
            CELERY_DEFAULT_EXCHANGE='default',
            CELERY_DEFAULT_ROUTING_KEY='default',

            CELERY_IMPORTS=('atp.engine.celery_tasks',)
        )
        self.config_from_object(current_config)


celery = FlaskCelery()
db = SQLAlchemy()
