
import os,time,json
from flask import Blueprint
from atp.api.xmind_parser import XmindParser
from werkzeug.utils import secure_filename
# from atp.api.mysql_manager import SystemInfoManager,ModuleInfoManager,TestsuiteInfoManager,TestcaseInfoManager,ProjectInfoManager
from atp.extensions import db
# from atp.engine.handle_testcase import map_testcase_type_to_number

import logging
logging.basicConfig(level=logging.DEBUG)

'''文件上传支持类型：目前仅支持.xmind. 
    例如：test.xmind'''
ALLOWED_EXTENSIONS = set(['xmind','jpg','png','pdf','doc','docx','xls','xlsx','mp4'])
file = Blueprint('file_interface',  __name__)


def allowed_file(filename):
        '''根据文件后缀名判断上传文件类型'''
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_file(f,file_dir):
        '''上传文件过程，
            如果5s内上传失败，跳出循环
        '''
        if f and allowed_file(f.filename):
            #fname = secure_filename(f.filename)
            ext = f.filename.rsplit('.', 1)[1]  # 获取文件后缀
            unix_time = int(time.time())
            new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
            f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
            upload_file_path=file_dir+ r'/{}'.format(new_filename)
            is_file_exits = False
            start = time.clock()
            while 1:
                if os.path.exists(upload_file_path):
                    is_file_exits = True
                    break
                else:
                    end = time.clock()
                    upload_time = int(end - start)
                    if upload_time > 5:
                        break
            return (upload_file_path,is_file_exits,f.filename)
        else:
            return  False

def xmind_parser(path):
        '''将上传好的xmind转为测试用例字典列表'''
        kwargs = {
            "xmind_file": path,
            "xmlns": '{urn:xmind:xmap:xmlns:content:2.0}',
        }
        xp = XmindParser(**kwargs)
        xp.xmind_to_xml()
        res = xp.xml_to_dict()
        testcase_dict = json.loads(json.dumps(res, ensure_ascii=False))
        return testcase_dict

if __name__=="__main__":
    xmind_path = os.path.abspath(os.path.join(os.getcwd(), "../.."))+r'\upload\{}'
    print(xmind_path)
    testcase_dic={
                "项目名称_xmind导入": {
                    "系统名称_xmind导入": {
                        "模块名称_xmind导入": {
                            "测试集名称_xmind导入": {
                                "正常场景": {
                                    "用例名称001_xmind导入": {
                                        "预期：接口返回成功，且数据库存入照片": {}
                                    }
                                },
                                "异常场景": {
                                    "用例名称002_xmind导入": {},
                                    "用例名称003_xmind导入": {
                                        "预期：接口返回成功，但数据不入库": {}
                                    }
                                }
                            }
                        }
                    }
                }
            }
