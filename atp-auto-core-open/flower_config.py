# -*- coding:utf-8 -*-


from atp.env import RUNNING_ENV

broker_api_map = {
    'DEV': 'http://a***:ad****@XX.XX.XX.XX:XXXX/atp_dev',
    'ALIUAT': 'http://a***n:1***@WSX@XX.XX.XX.XX:XXXX/atp_uat'
}

# RabbitMQ management api
broker_api = broker_api_map[RUNNING_ENV]

# Enable debug logging
logging = 'DEBUG'

# 端口号
port = 5555
