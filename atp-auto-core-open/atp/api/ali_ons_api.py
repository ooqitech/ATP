#!/usr/bin/env python
# encoding: utf-8
'''
@time: 2019/12/20 16:27
@desc: 因阿里云有流控策略，改方法在并发操作时会有问题，故暂停使用
'''
import json
import base64
import time
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkons.request.v20190214.OnsMessagePageQueryByTopicRequest import OnsMessagePageQueryByTopicRequest


class AliOnsApi(object):
    """阿里云one消息查询接口"""

    def __init__(self, ak, sk, region='mq-internet-access'):
        self.ak = ak
        self.sk = sk
        self.region = region
        self.client = AcsClient(self.ak, self.sk, self.region)
        self.start_time = int(time.time() - 60) * 1000
        self.end_time = int(time.time() + 60) * 1000
        self.page_no = 1

    def get_msg_by_topic(self, topic, tag):
        """
        根据topic查询消息
        :param topic: 消息topic
        :param tag: 消息tag
        :return:
        """
        request = OnsMessagePageQueryByTopicRequest()
        request.set_accept_format('json')
        request.set_BeginTime(self.start_time)
        request.set_EndTime(self.end_time)
        request.set_CurrentPage(self.page_no)
        request.set_Topic(topic)

        response = self.client.do_action_with_exception(request)

        if response:
            try:
                msg_content = json.loads(str(response, encoding='utf-8'))

                # 如果返回体中无MaxPageCount，表示没有查询到消息
                if 'MaxPageCount' not in msg_content['MsgFoundDo']:
                    return None

                for i in range(msg_content['MsgFoundDo']['MaxPageCount']):
                    # 返回总页数大于1时，根据taskId依次获取后续消息记录
                    if i > 0:
                        request.set_TaskId(msg_content['MsgFoundDo']['TaskId'])
                        request.set_CurrentPage(i+1)
                        response = self.client.do_action_with_exception(request)
                        msg_content = json.loads(str(response, encoding='utf-8'))
                    for item in msg_content['MsgFoundDo']['MsgFoundList']['OnsRestMessageDo']:
                        if not list(filter(lambda x: x['Name'] == 'TAGS' and x['Value'] == tag,
                                           item['PropertyList']['MessageProperty'])):
                            continue
                        yield str(base64.b64decode(item['Body']), encoding='utf-8')
            except Exception as err:
                raise err

        return None