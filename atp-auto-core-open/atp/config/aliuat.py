# -*- coding:utf-8 -*-

import platform

from atp.config.default import Config


class AliuatConfig(Config):
    # redis
    REDIS_HOST = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    REDIS_PORT = 232
    REDIS_DB_18 = 23
    REDIS_PASSWORD = 'XXXXXXXXXXXXXX'

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


    BROKER_URL = ''
    CELERY_RESULT_BACKEND = ''

    # apt-monitor
    ATP_MONITOR_SYSTEMS = []
    ATP_MONITOR_LIST = ''
    ATP_MONITOR_REBOOT = ''

    # RabbitMQ
    RABBIT_HOST = 'XX.XX.XX.XX'
    RABBIT_USERNAME = ''  # 指定远程rabbitmq的用户名
    RABBIT_PWD = ''  # 密码
    RABBIT_PORT = 5672
    RABBIT_V_HOST = ''
