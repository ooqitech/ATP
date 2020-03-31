# -*- coding:utf-8 -*-


import os,xmind,time
from xmind.core.const import TOPIC_DETACHED
from xmind.core.markerref import MarkerId
import json
import zipfile
from atp import app
from collections import OrderedDict
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from atp.api.comm_log import logger
from atp.config.default import get_config

CONFIG = get_config()
basedir = os.path.abspath(os.path.join(os.getcwd(), ".."))


class XmindParser(object):
    def __init__(self, **kwargs):
        self.temp_dir = kwargs.pop('temp_dir', CONFIG.TEMP_DIR)
        self.target_xml_name = 'content.xml'
        self.xmind_file = kwargs.pop('xmind_file', None)
        self.xml_file = kwargs.pop('xml_file', None)
        self.xmlns = kwargs.pop('xmlns', '')

    def __del__(self):
        if self.xml_file:
            os.remove(self.xml_file)

    def _parse_topic(self, parent, topic):
        topic_children = topic.find(self.xmlns + 'children')
        if not topic_children:
            return
        sub_topic_list = topic_children.find(self.xmlns + 'topics').findall(self.xmlns + 'topic')
        for sub_topic in sub_topic_list:
            key = sub_topic.find(self.xmlns + 'title').text
            if key:
                parent[key] = OrderedDict()
                self._parse_topic(parent[key], sub_topic)

    def xml_to_dict(self):
        """
        解析xml，返回有序字典
        :return:
        """
        tree = ET.parse(self.xml_file)
        root = tree.getroot()
        try:
            sheet = root.find(self.xmlns+'sheet')
            topic = sheet.find(self.xmlns+'topic')
            first_topic = topic.find(self.xmlns+'title').text
        except AttributeError:
            logger.error("Incorrect XML")
            return {}
        orderd_dic = OrderedDict()
        orderd_dic[first_topic] = OrderedDict()
        self._parse_topic(orderd_dic[first_topic], topic)
        return orderd_dic

    def xmind_to_xml(self):
        """
        解压xmind，返回xml
        :return:
        """
        zfile = zipfile.ZipFile(self.xmind_file, 'r')
        #print(zfile, type(zfile))
        for filename in zfile.namelist():
            #print(filename, type(filename))
            if self.target_xml_name == filename:
                data = zfile.read(filename)
                with open(self.temp_dir + filename, 'w+b') as f:
                    f.write(data)

                self.xml_file = self.temp_dir + filename
                return





def export_xmind_api(xmind_dic):
    for projectName, json_value in xmind_dic.items():
        file_name = projectName
        unix_time = int(time.time())
        new_filename = str(unix_time)
        if not os.path.exists(CONFIG.DOWNLOADS_DIR):
            os.makedirs(CONFIG.DOWNLOADS_DIR)
        file_dir=CONFIG.DOWNLOADS_DIR + "{0}{1}.xmind".format(file_name,new_filename)
        workbook = xmind.load(file_dir)

        sheet1 = workbook.getPrimarySheet()
        sheet1.setTitle(projectName)
        rootTop1 = sheet1.getRootTopic()
        rootTop1.setTitle(projectName)
        for systemName, json_value in json_value.items():
            # system_topic = rootTop1.addSubTopic(topics_type = TOPIC_DETACHED)
            system_topic = rootTop1.addSubTopic()
            # system_topic.setTopicHyperlink(sheet1.getID())
            system_topic.setTitle(systemName)
            for moudleName, json_value in json_value.items():
                moudle_topic = system_topic.addSubTopic()
                moudle_topic.setTitle(moudleName)
                for typeName, json_value in json_value.items():
                    type_topic = moudle_topic.addSubTopic()
                    type_topic.setTitle(typeName)
                    for suiteName, json_value in json_value.items():
                        suite_topic = type_topic.addSubTopic()
                        suite_topic.setTitle(suiteName)
                        for sceneType, json_value in json_value.items():
                            scene_topic = suite_topic.addSubTopic()
                            scene_topic.setTitle(sceneType)
                            for testcaseName, json_value in json_value.items():
                                testcase_topic = scene_topic.addSubTopic()
                                testcase_topic.setTitle(testcaseName)
                                for expect, json_value in json_value.items():
                                    expect_topic = testcase_topic.addSubTopic()
                                    expect_topic.setTitle(expect)
                                    for expectResult, json_value in json_value.items():
                                        expectResult_topic = expect_topic.addSubTopic()
                                        expectResult_topic.setTitle(expectResult)
        xmind.save(workbook)
        return file_name+new_filename+'.xmind'


def Multi_layer_module(json_values,topic):
    '''1~n多层模块的递归方法'''
    for moudlelayerName, json_value in json_values.items():
        if '功能' in json_value.keys():
                moudle_last_topic = topic.addSubTopic()
                moudle_last_topic.setTitle(moudlelayerName)
                for typeName, json_value in json_value.items():
                    type_topic = moudle_last_topic.addSubTopic()
                    type_topic.setTitle(typeName)
                    '''用例名称'''
                    for caseName, json_value in json_value.items():
                        case_topic = type_topic.addSubTopic()
                        case_topic.setTitle(caseName)
                        '''操作步骤'''
                        for stepsName, json_value in json_value.items():
                            steps_topic = case_topic.addSubTopic()
                            steps_topic.setTitle(stepsName)
                            '''加上一列预期俩个字'''
                            expect_topic = steps_topic.addSubTopic()
                            expect_topic.setTitle("预期")
                            '''预期结果'''
                            for expect in json_value.values():
                                for expectedResult, json_value in expect.items():
                                    expectedResult_topic = expect_topic.addSubTopic()
                                    expectedResult_topic.setTitle(expectedResult)
        else:
            moudle_layer_topic = topic.addSubTopic()
            moudle_layer_topic.setTitle(moudlelayerName)
            Multi_layer_module(json_value,moudle_layer_topic)


def export_xmind_base(xmind_dic):
    for projectName, json_value in xmind_dic.items():
        file_name = projectName
        unix_time = int(time.time())
        new_filename = str(unix_time)
        if not os.path.exists(CONFIG.DOWNLOADS_DIR):
            os.makedirs(CONFIG.DOWNLOADS_DIR)
        file_dir = CONFIG.DOWNLOADS_DIR + "{0}{1}.xmind".format(file_name, new_filename)
        workbook = xmind.load(file_dir)
        sheet1 = workbook.getPrimarySheet()
        sheet1.setTitle(projectName)
        rootTop1 = sheet1.getRootTopic()
        rootTop1.setTitle(projectName)
        for systemName, json_value in json_value.items():
            system_topic = rootTop1.addSubTopic()
            system_topic.setTitle(systemName)
            for moudleName, json_value in json_value.items():
                moudle_topic = system_topic.addSubTopic()
                moudle_topic.setTitle(moudleName)
                '''模块最后一级'''
                Multi_layer_module(json_value,moudle_topic)
        xmind.save(workbook)
        return file_name + new_filename + '.xmind'

if __name__ == '__main__':
    kwargs = {
        "xmind_file": r"C:\Users\MIME\Desktop\xmind\功能测试用例模块test.xmind",
        "xmlns": '{urn:xmind:xmap:xmlns:content:2.0}',
    }
    xp = XmindParser(**kwargs)
    xp.xmind_to_xml()
    res = xp.xml_to_dict()
    json_ = json.dumps(res, ensure_ascii=False, indent=4)
    print(json_)








