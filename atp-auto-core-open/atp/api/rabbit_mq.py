# -*- coding:utf-8 -*-

import os

import pika
import time
import string
import json
from atp.api.log_push_queue import color_log, font_log
host = '**.**.**.**'
username = '**'  # 指定远程rabbitmq的用户名
pwd = '**'  # 密码
queue_name = 'report-112'  # 队列名
user_pwd = pika.PlainCredentials(username, pwd)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=host, port=5672,
                              credentials=user_pwd, virtual_host='atp_dev'))  # 创建连接

channel = connection.channel()  # 连接上创建一个频道
arguments = {
    'x-message-ttl': 60000,  # message存活时间（毫秒）
    'x-expires': 60000,  # queue存活时间（毫秒）
}

# durable 表示是否持久化,
# exclusive是否排他，如果为True则只允许创建这个队列的消费者使用,
# auto_delete 表示消费完是否删除队列
channel.queue_declare(queue=queue_name, durable=True, exclusive=False,
                      auto_delete=False, arguments=arguments)
# 声明一个队列，生产者和消费者都要声明一个相同的队列，用来防止万一某一方挂了，另一方能正常运行


# 生产者，发送消息
def send_message(data):
    channel.basic_publish(exchange='',  # 交换机
                          routing_key=queue_name,  # 路由键，写明将消息发往哪个队列，本例是将消息发往队列queue_name
                          body=data,  # 生产者要发送的消息
                          properties=pika.BasicProperties(
                              delivery_mode=2, )  # 设置消息持久化，将要发送的消息的属性标记为2，表示该消息要持久化)
                          )


# 消费者，接收消息
def receive_message():
    # prefetch_count设置为3，表示同一时刻，只接受最多三个消息
    channel.basic_qos(prefetch_count=3)
    channel.basic_consume(callback, queue=queue_name)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.close()
        connection.close()


def callback(ch, method, properties, body):
    result = handle_data(body)
    if result == 1:
        print(" [消费者] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)  # 接收到消息后会给rabbitmq发送一个确认
    else:
        print(" [x] handle data error")
        ch.basic_reject(delivery_tag=method.delivery_tag)


# 代写接口,处理下一步的数据
def handle_data(body):
    try:
        data = json.loads(body)
        print(" [消费者] Received {}".format(data))
        time.sleep(10)
    except:
        return 0
    else:
        return 1


def create_generator(file):
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
                max_step = 200
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

if __name__ == '__main__':
    g = create_generator(r'D:\git\ATP\logs\run_case_logs\run_None.log')

    for i in g:
        if isinstance(i, list):
            for p in i:
                if p.startswith('[{}-'.format(_YEAR)):
                    # 去除linux log color
                    p = p[:25] + p[31:]

                # logger.debug('推送内容：{}'.format(p))
                p = p.replace(' ', '&nbsp&nbsp')
                res = color_log(p, current_case)
                if not isinstance(res, str):
                    p = res[0]
                    current_case = res[1]
                else:
                    p = res
                p = font_log(p)

                send_message(data=p)

                if '【END】' in p:
                    end_flag = True
