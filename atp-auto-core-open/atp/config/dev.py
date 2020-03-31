# -*- coding:utf-8 -*-

import platform

from atp.config.default import Config


class DevConfig(Config):
    # redis
    REDIS_HOST = ''
    REDIS_PORT = 6379
    REDIS_DB_18 = 18
    REDIS_PASSWORD = ''

    # mysql
    if platform.system() == 'Linux':
        SQLALCHEMY_DATABASE_URI = ""
    elif platform.system() == 'Windows':
        SQLALCHEMY_DATABASE_URI = ""

    elif platform.system() == 'Darwin':
        SQLALCHEMY_DATABASE_URI = ""
    else:
        SQLALCHEMY_DATABASE_URI = ""

    # 基线用例需要解析的文件夹命名列表
    BASELINE_DIR_NAME_LIST = ['A', 'B']

    # gitlab相关配置
    GIT_URL = "http://"
    GIT_PRIVATE_TOKEN = ""
    GIT_API_VERSION = 3

    # celery任务相关配置
    BROKER_URL = 'amqp://'
    CELERY_RESULT_BACKEND = 'amqp://'

    # RabbitMQ
    RABBIT_HOST = ''
    RABBIT_USERNAME = ''  # 指定远程rabbitmq的用户名
    RABBIT_PWD = ''  # 密码
    RABBIT_PORT = 5672
    RABBIT_V_HOST = ''
