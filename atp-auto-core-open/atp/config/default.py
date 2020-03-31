# -*- coding:utf-8 -*-

import os
import platform

from atp.utils.tools import get_host


class Config(object):
    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(Config, "_instance"):  # 反射
            Config._instance = object.__new__(cls)
        return Config._instance

    # 获取文件目录相对路径
    BASE_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '\..')

    JSON_AS_ASCII = False
    # SECRET_KEY = os.urandom (24)

    # mysql
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_POOL_TIMEOUT = 40
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_POOL_RECYCLE = 3600

    # linux atp dir path
    LINUX_BASE_PATH = '/usr/local/src/atp'

    # log
    LINUX_LOG = '/usr/local/src/logs/atp-auto-core/atp-auto-core.log'
    # WINDOWS_LOG = r'E:\git_mime\atp-platform-core\atp\logs\flask.log'
    WINDOWS_LOG =BASE_PATH + r'\logs' + r'\flask.log'
    MAC_LOG = '/Users/wangyongjun/git_work/atp-platform-core/atp/logs/flask.log'

    # report TEMPLATE path
    LINUX_REPORT_TEMPLATE = LINUX_BASE_PATH + '/atp-auto-core/atp/engine/templates/default_report_template_v_1.5.11.html'
    # WINDOWS_REPORT_TEMPLATE = r"E:\git_mime\atp-platform-core\atp\engine\templates\default_report_template.html"
    WINDOWS_REPORT_TEMPLATE = BASE_PATH + r'\engine\templates\default_report_template_v_1.5.11.html'
    MAC_REPORT_TEMPLATE = '/Users/wangyongjun/git_work/atp-platform-core/atp/engine/templates/default_report_template_v_1.5.11.html'

    # reports dir
    LINUX_REPORT_DIR = LINUX_BASE_PATH + '/reports/'
    # WINDOWS_REPORT_TEMPLATE = r"E:\git_mime\atp-platform-core\atp\engine\templates\default_report_template.html"
    WINDOWS_REPORT_DIR = BASE_PATH + r'\reports'
    MAC_REPORT_DIR = '/Users/wangyongjun/git_work/atp-platform-core/reports/'

    # reports dir
    LINUX_UI_REPORT_DIR = LINUX_BASE_PATH + '/reports/'
    # WINDOWS_REPORT_TEMPLATE = r"E:\git_mime\atp-platform-core\atp\engine\templates\default_report_template.html"
    WINDOWS_UI_REPORT_DIR = BASE_PATH + r'\reports'

    # tmp dir
    LINUX_TEMP_DIR = LINUX_BASE_PATH + '/atp-auto-core/atp/api/tmp/'
    # WINDOWS_TEMP_DIR = "E:\\git_mime\\atp-platform-core\\atp\\api\\tmp\\"
    WINDOWS_TEMP_DIR = BASE_PATH + r'\api\tmp'
    MAC_TEMP_DIR = '/Users/wangyongjun/git_work/atp-platform-core/atp/api/tmp/'

    # custom file path
    LINUX_CUSTOM_FILE = LINUX_BASE_PATH + '/atp-auto-core/atp/utils/custom.py'
    WINDOWS_CUSTOM_FILE = BASE_PATH + r'\utils\custom.py'
    MAC_CUSTOM_FILE = '/Users/wangyongjun/git_work/atp-platform-core/atp/utils/custom.py'

    # run case log dir
    LINUX_RUN_CASE_LOG_DIR = LINUX_BASE_PATH + '/run_case_logs/'
    WINDOWS_RUN_CASE_LOG_DIR = BASE_PATH + '\\logs\\run_case_logs\\'
    MAC_RUN_CASE_LOG_DIR = '/Users/wangyongjun/git_work/atp-platform-core/atp/logs/run_case_logs/'

    # run task log dir
    LINUX_RUN_TASK_LOG_DIR = LINUX_BASE_PATH + '/run_task_logs/'
    WINDOWS_RUN_TASK_LOG_DIR = BASE_PATH + '\\logs\\run_task_logs\\'

    # downloads dir
    LINUX_DOWNLOADS_DIR = LINUX_BASE_PATH + '/downloads/'
    WINDOWS_DOWNLOADS_DIR = BASE_PATH + '\\logs\\downloads\\'

    # baseline git dir
    LINUX_BASELINE_GIT_DIR = '/usr/local/src/git_folder/baseline-testcase'
    WINDOWS_BASELINE_GIT_DIR = r"E:\git_mime\baseline-testcase"

    if platform.system() == 'Linux':
        LOG_PATH = LINUX_LOG
        REPORT_TEMPLATE_PATH = LINUX_REPORT_TEMPLATE
        TEMP_DIR = LINUX_TEMP_DIR
        CUSTOM_FILE = LINUX_CUSTOM_FILE
        RUN_CASE_LOG_DIR = LINUX_RUN_CASE_LOG_DIR
        RUN_TASK_LOG_DIR = LINUX_RUN_TASK_LOG_DIR
        REPORT_DIR = LINUX_REPORT_DIR
        UI_REPORT_DIR = LINUX_UI_REPORT_DIR
        DOWNLOADS_DIR = LINUX_DOWNLOADS_DIR
        BASELINE_GIT_DIR = LINUX_BASELINE_GIT_DIR

    elif platform.system() == 'Windows':
        LOG_PATH = WINDOWS_LOG
        REPORT_TEMPLATE_PATH = WINDOWS_REPORT_TEMPLATE
        TEMP_DIR = WINDOWS_TEMP_DIR
        CUSTOM_FILE = WINDOWS_CUSTOM_FILE
        RUN_CASE_LOG_DIR = WINDOWS_RUN_CASE_LOG_DIR
        RUN_TASK_LOG_DIR = WINDOWS_RUN_TASK_LOG_DIR
        REPORT_DIR = WINDOWS_REPORT_DIR
        UI_REPORT_DIR = WINDOWS_UI_REPORT_DIR
        DOWNLOADS_DIR = WINDOWS_DOWNLOADS_DIR
        BASELINE_GIT_DIR = WINDOWS_BASELINE_GIT_DIR

    elif platform.system() == 'Darwin':
        LOG_PATH = MAC_LOG
        REPORT_TEMPLATE_PATH = MAC_REPORT_TEMPLATE
        TEMP_DIR = MAC_TEMP_DIR
        CUSTOM_FILE = MAC_CUSTOM_FILE
        RUN_CASE_LOG_DIR = MAC_RUN_CASE_LOG_DIR
        REPORT_DIR = MAC_REPORT_DIR

    else:
        LOG_PATH = LINUX_LOG
        REPORT_TEMPLATE_PATH = LINUX_REPORT_TEMPLATE
        TEMP_DIR = LINUX_TEMP_DIR
        CUSTOM_FILE = LINUX_CUSTOM_FILE
        RUN_CASE_LOG_DIR = LINUX_RUN_CASE_LOG_DIR
        REPORT_DIR = LINUX_REPORT_DIR
        DOWNLOADS_DIR = LINUX_DOWNLOADS_DIR
        BASELINE_GIT_DIR = LINUX_BASELINE_GIT_DIR

    # email to
    EMAIL_TO = []

    # default user password
    DEFAULT_USER_PWD = '123456'

    # login_expire_time
    LOGIN_EXPIRE_TIME = 28800  # 8 hours

    # run without authentication，DO NOT change to True
    NON_AUTHENTICATION = False

    CELERY_TIMEZONE = 'Asia/Shanghai',
    CELERY_ENABLE_UTC = True,
    CELERY_ACCEPT_CONTENT = ['json'],
    CELERY_TASK_SERIALIZER = 'json',
    CELERY_RESULT_SERIALIZER = 'json',
    CELERYD_FORCE_EXECV = True,  # 非常重要,有些情况下可以防止死锁
    # CELERYD_CONCURRENCY = 20,  # 并发worker数
    CELERY_DISABLE_RATE_LIMITS = True,  # 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
    CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker执行了多少任务就会死掉，死掉后会新建一个worker


def get_config():
    return Config


if __name__ == '__main__':
    print(os.path.split(os.path.realpath(__file__))[0])
