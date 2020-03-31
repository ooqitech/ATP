# -*- coding:utf-8 -*-

import pika
import time
import os
import platform

from datetime import datetime
from copy import copy

import re

from atp.config.load_config import load_config
from atp.utils.tools import get_current_timestamp

_YEAR = time.strftime('%Y', time.localtime(time.time()))

arguments_ex = {
    'x-message-ttl': 600000,  # message存活时间（毫秒）
    'x-expires': 600000,  # queue存活时间（毫秒）
}
arguments = {
    'durable': True, 'exclusive': False, 'auto_delete': False
}


class LogPushQueue(object):
    def __init__(self, env, queue_name=None, report_id=None, **kwargs):
        _config = load_config(env.upper())

        self.user_pwd = pika.PlainCredentials(_config.RABBIT_USERNAME, _config.RABBIT_PWD)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=_config.RABBIT_HOST, port=_config.RABBIT_PORT, credentials=self.user_pwd,
                virtual_host=_config.RABBIT_V_HOST))  # 创建连接
        self.channel = self.connection.channel()  # 连接上创建一个频道

        if report_id:
            # 调试用例日志
            self.report_id = report_id
            self.run_case_log_dir = _config.RUN_CASE_LOG_DIR
            if queue_name:
                self.queue_name = queue_name
            else:
                self.queue_name = 'report-id-{0}-{1}'.format(report_id, get_current_timestamp())
        else:
            # 任务运行用例日志
            self.is_task = True
            self.run_task_id = kwargs.get('run_task_id')
            self.intf_id = kwargs.get('intf_id')
            self.testcase_id = kwargs.get('testcase_id')
            self.is_main = kwargs.get('is_main')
            self.log_dir = kwargs.get('log_dir')
            if queue_name:
                self.queue_name = queue_name
            else:
                self.queue_name = 'task-run-log-{0}-{1}'.format(self.run_task_id, get_current_timestamp())

        # durable 表示是否持久化,
        # exclusive是否排他，如果为True则只允许创建这个队列的消费者使用,
        # auto_delete 表示消费完是否删除队列
        self.channel.queue_declare(
            queue=self.queue_name, durable=arguments['durable'], exclusive=arguments['exclusive'],
            auto_delete=arguments['auto_delete'], arguments=arguments_ex)
        self.arguments = copy(arguments_ex)
        self.arguments.update(copy(arguments))

    def send_single_message(self, data):
        self.channel.basic_publish(
            exchange='',  # 交换机
            routing_key=self.queue_name,  # 路由键，写明将消息发往哪个队列，本例是将消息发往队列queue_name
            body=data,  # 生产者要发送的消息
            properties=pika.BasicProperties(delivery_mode=2)  # 设置消息持久化，将要发送的消息的属性标记为2，表示该消息要持久化)
        )

    def push_debug_log(self):
        """推log"""
        print('进入push_log')
        count = 0

        today_str = datetime.now().strftime('%Y-%m-%d')
        if platform.system() == 'Windows':
            log_dir = '{0}{1}\\'.format(self.run_case_log_dir, today_str)
        else:
            log_dir = '{0}{1}/'.format(self.run_case_log_dir, today_str)

        g = self._create_generator('{dir}run_{report_id}.log'.format(dir=log_dir, report_id=self.report_id))
        # g = create_generator('{dir}run_1361.log'.format(dir=RUN_CASE_LOG_DIR, report_id=room))
        end_flag = False
        current_case = None
        for i in g:
            count += 1
            if end_flag:
                break
            # logger.debug('g生成器+1')
            time.sleep(0.5)

            if isinstance(i, list):
                p_list = []
                for p in i:
                    if p.startswith('[{}-'.format(_YEAR)):
                        # 去除linux log color
                        p = p[:33] + p[39:]

                    # logger.debug('推送内容：{}'.format(p))
                    p = p.replace(' ', '&nbsp')
                    res = color_log(p, current_case)
                    if not isinstance(res, str):
                        p = res[0]
                        current_case = res[1]
                    else:
                        p = res
                    p = font_log(p)

                    # self.send_single_message(p)
                    # logger.debug('本条p推送完成')
                    p_list.append(p)
                    if '【END】' in p:
                        end_flag = True

                if p_list:
                    ps = '<br/>'.join(p_list)
                    self.send_single_message(ps)

            else:
                print('i 是 {}'.format(type(i)))
                i = i.replace(' ', '&nbsp')
                count += 1
                self.send_single_message(i)
                if '【END】测试结束' in i:
                    break

    def _create_generator(self, file):
        """生成器"""
        print('新建了一个生成器')
        s = 0
        while s < 10:
            is_exist = os.path.exists(file)
            if is_exist:
                break
            else:
                time.sleep(1)
                s += 1
        with open(file, 'r') as t:
            t.seek(0, 0)
            has_read = False
            _return_in_line = False

            while True:
                # 首次读取，直接返回已存在的所有行，类型是list
                if not has_read:
                    exist_lines = t.readlines()
                    has_read = True
                    t.seek(0, 2)
                    line_num = len(exist_lines)
                    max_step = 500
                    if line_num > max_step:
                        i = 0
                        while (i + max_step) < line_num:
                            yield exist_lines[i:i + max_step]
                            i += max_step
                        yield exist_lines[i:]
                    else:
                        yield exist_lines

                # 按新增的行返回，类型是str
                elif _return_in_line:
                    line = t.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    yield line
                # 按新增的所有行返回，类型是list
                else:
                    exist_lines = t.readlines()
                    t.seek(0, 2)
                    yield exist_lines

    def push_task_run_log(self):
        if self.is_main:
            log_file_path = '{0}task_run_{1}_main_case_{2}.log'.format(self.log_dir, self.run_task_id, self.testcase_id)
            if not os.path.exists(log_file_path):
                main_ids_str_pattern = r'_main_case_list_\[([\d, ]+)\].log'
                ls_dir = os.listdir(self.log_dir)
                for log_name in ls_dir:
                    res_list = re.findall(main_ids_str_pattern, log_name)
                    if res_list:
                        main_id_list = [int(id_) for id_ in res_list[0].split(', ')]
                        if self.testcase_id in main_id_list:
                            log_file_path = '{0}{1}'.format(self.log_dir, log_name)
                            break
        else:
            log_file_path = '{0}task_run_{1}_intf_{2}.log'.format(self.log_dir, self.run_task_id, self.intf_id)

        g = self._create_generator_for_task(log_file_path)

        end_flag = False
        current_case = None
        for i in g:
            print('g生成器+1')
            if end_flag:
                print('push log over')
                break
            if not i:
                print('not i push log over')
                break
            time.sleep(0.5)

            if isinstance(i, list):
                p_list = []
                for p in i:
                    if p.startswith('[{}-'.format(_YEAR)):
                        # 去除linux log color
                        p = p[:33] + p[39:]

                    if '【END】' in p:
                        end_flag = True

                    p = p.replace(' ', '&nbsp')
                    res = color_log(p, current_case)
                    if not isinstance(res, str):
                        p = res[0]
                        current_case = res[1]
                    else:
                        p = res
                    p = font_log(p)
                    p_list.append(p)

                if p_list:
                    ps = '<br/>'.join(p_list)
                    self.send_single_message(ps)

            if end_flag:
                print('push log over, end')
                break

    def _create_generator_for_task(self, log_file_path):
        print('新建了一个生成器')
        is_exist = os.path.exists(log_file_path)
        if not is_exist:
            print('{}不存在'.format(log_file_path))
            yield []

        with open(log_file_path, 'r') as f:
            f.seek(0, 0)

            while True:
                # 首次读取，直接返回已存在的所有行，类型是list
                exist_lines = f.readlines()
                f.seek(0, 2)
                to_push_lines = []
                to_push = False
                print('exist_lines:{}'.format(len(exist_lines)))
                for i in range(len(exist_lines)):
                    if not to_push:
                        if '【准备运行测试用例】:' in exist_lines[i]:
                            print('find case start')
                            if exist_lines[i+1].endswith('【用例ID】: {}\n'.format(self.testcase_id)):
                                print('find case ID')
                                to_push = True
                    else:
                        if '【准备运行测试用例】:' in exist_lines[i] or '【结束调用HttpRunner】' in exist_lines[i]:
                            print('find case end')
                            break
                    if to_push:
                        to_push_lines.append(exist_lines[i])
                    # if '【结束执行用例】: ID_{},'.format(self.testcase_id) in exist_lines[i]:
                    #     print('find case normal end')
                    #     break
                    # if '【警告】: 因【' in exist_lines[i] and '】错误, 中断测试' in exist_lines[i]:
                    #     print('find case break end')
                    #     break

                if to_push_lines:
                    to_push_lines.append('【END】测试结束！')
                line_num = len(to_push_lines)
                print('to push line_num:{}'.format(line_num))
                max_step = 500
                if line_num > max_step:
                    i = 0
                    while (i + max_step) < line_num:
                        yield to_push_lines[i:i + max_step]
                        i += max_step
                    yield to_push_lines[i:]
                else:
                    yield to_push_lines


def color_log(p, current_case):
    """
    日志增加字体颜色和背景颜色
    :param current_case:
    :param p:
    :return:
    """
    bg_color_grey_keys = ['【START】']
    for key in bg_color_grey_keys:
        if key in p:
            # p = p.replace(key, '<span style="font-weight:bold;background-color:LightGray">' + key) + '</span>'
            p = p.replace(key, '<span id="start" style="font-weight:bold;background-color:Green;color:White">' + key) + '</span>'
            return p

    bg_color_grey_keys = ['【END】']
    for key in bg_color_grey_keys:
        if key in p:
            p = p.replace(key, '<span id="end" style="font-weight:bold;background-color:Green;color:White">' + key) + '</span>'
            return p

    # bg_color_red_keys = ['【ERROR】', '【警告】']
    # for key in bg_color_red_keys:
    #     if key in p:
    #         p = p.replace(key, '<span style="font-weight:bold;background-color:Crimson;color:White">' + key) + '</span>'
    #         return p

    bg_color_blue_keys = ['【环境】', '【准备运行测试用例】', '【用例ID】', '【用例名称】', '【使用Html报告模板】',
                          '【开始生成Html报告】', '【渲染报告数据】', '【已生成Html报告】', '【开始执行用例】',
                          '【结束执行用例】', '【存在前置用例】', '【根据前置用例组成调用链(ID)】']
    for key in bg_color_blue_keys:
        if key in p:
            if '【开始执行用例】' == key:
                # case_id = p.split('ID_')[1].split(',')[0]
                case_id = p.split('ID_')[1].replace('&nbsp', '').strip('\n')
                case_id = current_case + '-' + case_id
                p = p.replace(key, '<span id="' + case_id + '" style="background-color:#D2E9FF">' + key) + '</span>'
            elif '【用例ID】' == key:
                new_case_id = p.split('&nbsp')[-1].strip('\n')
                current_case = new_case_id
                p = p.replace(key, '<span id="newCase' + new_case_id + '" style="background-color:#D2E9FF">' + key) + '</span>'
            else:
                p = p.replace(key, '<span style="background-color:#D2E9FF">' + key) + '</span>'
            return p, current_case

    bg_color_orange_keys = ['【使用Html报告模板】', '【开始生成Html报告】', '【渲染报告数据】', '【已生成Html报告】']
    for key in bg_color_orange_keys:
        if key in p:
            p = p.replace(key, '<span style="background-color:OldLace">' + key) + '</span>'
            return p

    # 红色报错信息
    color_red_keys = ['[ERROR]']
    for key in color_red_keys:
        if key in p:
            if 'extract!' in p:
                p = p.replace(key,
                              '<span id="extractError" style="font-weight:bold;color:Crimson">' + key) + '</span>'
                # p = '<span id="extractError" style="font-weight:bold;color:Crimson">' + p + '</span>'
            else:
                p = p.replace(key,
                              '<span id="otherError" style="font-weight:bold;color:Crimson">' + key) + '</span>'
                # p = '<span id="otherError" style="font-weight:bold;color:Crimson">' + p + '</span>'
            return p

    # 橙色警告信息
    color_coral_keys = ['[WARN&nbsp]']
    for key in color_coral_keys:
        if key in p:
            p = p.replace(key, '<span id="otherError" style="font-weight:bold;color:Coral">' + key) + '</span>'
            # p = '<span id="otherError" style="font-weight:bold;color:Crimson">' + p + '</span>'
            return p

    color_green_keys = ['【验证点】']
    for key in color_green_keys:
        if key in p:
            if '.........PASS' in p:
                p = p.replace(key, '<span style="font-weight:bold;color:Green">' + key) + '</span>'
            # else:
            #     p = p.replace(key, '<span id="checkError" style="font-weight:bold;color:Crimson">' + key) + '</span>'
            return p

    color_blue_keys = ['【请求内容&nbsp详情】', '【响应内容&nbsp详情】', '【状态码】', '【响应耗时】']
    for key in color_blue_keys:
        if key in p:
            p = p.replace(key, '<span style="color:DodgerBlue">' + key + '</span>')
            return p

    # 特殊节点标签颜色区分
    color_orange_keys = ['【变量替换-开始】', '【变量替换-结束】',
                         '【请求前置-开始】', '【请求前置-结束】',
                         '【接口请求-开始】', '【接口请求-结束】',
                         '【请求后置-开始】', '【请求后置-结束】',
                         '【提取变量-开始】', '【提取变量-结束】',
                         '【结果校验-开始】', '【结果校验-结束】',
                         '【全局后置-开始】', '【全局后置-结束】']
    for key in color_orange_keys:
        if key in p:
            p = p.replace(key, '<span style="color:Orange">' + key + '</span>')
            return p

    return p


def font_log(p):
    """
    日志改变字体
    :param p:
    :return:
    """
    return '<span style="font-family: sansserif">' + p + '</span>'
    # return '<span style="font-family: Microsoft YaHei">' + p + '</span>'

if __name__ == '__main__':
    log_push_queue = LogPushQueue('DEV', '3278')
    log_push_queue.push_log()
