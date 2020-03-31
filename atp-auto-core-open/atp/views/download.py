# -*- coding:utf-8 -*-

from flask import Blueprint, request, send_from_directory
from flask_restful import Resource
from atp.api.redis_api import RedisManager
from atp.api.mysql_manager import (BaseTestcaseInfoManager, BaseModuleInfoManager,
                                   BaseSystemInfoManager, BaseProjectInfoManager,
                                   TestcaseTagManager)
from atp.api.mysql_manager import ApiCompanyInfoManager, ApiTestcaseTagRelationManager
from atp.api.xmind_parser import export_xmind_api, export_xmind_base
from atp.config.default import get_config
from atp.utils.export_recent_case_to_excel import export_by_time
from atp.views.wrappers import timer, developer_check
from atp.utils.common import get_request_json, make_response
from atp.api.excel_parser import ExcelParser
import json
from atp.api.comm_log import logger

CONFIG = get_config()
redis = RedisManager()
download = Blueprint('download_interface', __name__)
module_list = []


class Download(Resource):
    def __init__(self):
        self.data = get_request_json()
        # self.pim = ProjectInfoManager()
        # self.sim = SystemInfoManager()
        # self.mim = ModuleInfoManager()
        self.acim = ApiCompanyInfoManager()
        self.attrm = ApiTestcaseTagRelationManager()
        # self.tsim = TestsuiteInfoManager()
        # self.tcim = TestcaseInfoManager()
        self.btim = BaseTestcaseInfoManager()
        self.bsim = BaseSystemInfoManager()
        self.bpim = BaseProjectInfoManager()
        self.bmim = BaseModuleInfoManager()
        self.username = redis.get_username(request.headers.get('X-Token'))
        self.header_func = ["编号", "模块", "用例标题", "前置条件", "操作步骤", "预期结果", "执行结果", "备注"]  # 业务用例excel表格标题

        # if self.username:
        #     self.data["userName"] = self.username

    @timer
    def get(self, action):
        if action.endswith("xmind") or action.endswith("xlsx"):
            return send_from_directory(CONFIG.DOWNLOADS_DIR, action, mimetype='application/octet-stream')
        elif action.endswith("zip"):
            filename = 'run.zip'
            logger.info('zip_path', CONFIG.DOWNLOADS_DIR)
            return send_from_directory(CONFIG.DOWNLOADS_DIR, filename, mimetype='application/octet-stream')
        elif action == 'recentTestcasesToExcel':
            # print(action)
            from_ = request.args.get('from', type=str)
            # print(from_)
            excel_name = export_by_time(from_)
            return send_from_directory(CONFIG.DOWNLOADS_DIR, excel_name, mimetype='application/octet-stream')

    @timer
    def post(self, action):
        if action == 'xmindApi':
            return self.download_xmind_api()

        elif action == 'xmindBase':
            return self.download_xmind_base()

        elif action == 'excel':
            return self.download_excel()

        elif action == 'excelModules':
            return self.download_modules_excel()
        else:
            return make_response({"code": "100", "desc": "url错误，不存在的接口动作<{action}>".format(action=action)})

    def Multi_layer_module(self, module_id_Subsets, dict):
        '''包含多级模块的递归'''
        for module_id_Subset in module_id_Subsets:
            id_ = module_id_Subset.id  # 二级模块  769
            module_second_name = module_id_Subset.module_name
            dict[module_second_name] = {}
            new_dict = dict[module_second_name]
            module_id_Subsets_tests = self.bmim.get_modules(parent_module_id=id_)
            if not module_id_Subsets_tests:
                new_dict["功能"] = {}
                '''获取所有用例'''
                testcases = self.btim.get_all_testcase(module_id=id_)
                for testcase in testcases:
                    case_name = testcase.testcase_name
                    case_detail = json.loads(testcase.detail)
                    new_dict["功能"][case_name] = case_detail
            else:
                self.Multi_layer_module(module_id_Subsets_tests, new_dict)

    @developer_check
    def download_xmind_base(self):
        try:
            system_id = self.data.pop("systemId", None)
            project_id = self.data.pop("projectId", None)

        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        xmind_dict = {}
        """处理项目名称和系统名称"""
        project_name = self.bpim.get_project(id=project_id).project_name
        system_name = self.bsim.query_system(id=system_id).system_name

        module_list = self.bmim.get_modules(system_id=system_id)
        xmind_dict[project_name] = {
            system_name: {
            }
        }
        # '''系统下所有的模块'''
        # for module_names  in module_name_list:
        #     module_name=module_names.module_name  #一级模块名称
        #     xmind_dict[project_name][system_name][module_name]={}
        #     module_id = module_names.id           #一级模块id
        #     parent_module_id=module_names.parent_module_id
        #     if not parent_module_id:
        #         module_id_lasts = self.bmim.get_modules(parent_module_id=module_id)
        #         for  module_id_last in  module_id_lasts:
        #              id_= module_id_last.id       #最后一级模块id
        #              last_module_name = module_id_last.module_name  #最后一级模块名称
        #              xmind_dict[project_name][system_name][module_name][last_module_name]={"功能":{}}
        #              '''获取所有用例'''
        #              testcases = self.btim.get_all_testcase(module_id=id_)
        #              for  testcase  in  testcases:
        #                  case_name = testcase.testcase_name
        #                  case_detail = json.loads(testcase.detail)
        #                  xmind_dict[project_name][system_name][module_name][last_module_name]["功能"][case_name]=case_detail
        '''系统下所有的模块'''
        for module in module_list:
            module_first_name = module.module_name
            xmind_dict[project_name][system_name][module_first_name] = {}
            dict = xmind_dict[project_name][system_name][module_first_name]
            module_first_id = module.id
            module_id_Subsets = self.bmim.get_modules(parent_module_id=module_first_id)
            self.Multi_layer_module(module_id_Subsets, dict)
        filename = export_xmind_base(xmind_dict)
        return make_response({"code": "000", "desc": filename})

    # @developer_check
    # def download_xmind_api_old(self):
    #     try:
    #         module_id = self.data.pop("moduleId", None)
    #         system_id = self.data.pop("systemId", None)
    #     except KeyError:
    #         return make_response({"code": "100", "desc": "入参校验失败"})
    #
    #     xmind_dic = {}
    #     if module_id:
    #         m_obj = self.mim.query_module_id(module_id)[0]
    #         s_obj = self.sim.query_systeminfo_by_id(m_obj.system_id)
    #         p_obj = self.pim.get_project_info(s_obj.project_id)
    #         xmind_dic[p_obj.project_name] = {
    #             s_obj.system_name: {
    #                 m_obj.module_name: {}
    #             }
    #         }
    #         module_dic = deal_testcase_by_module(module_id)
    #         xmind_dic[p_obj.project_name][s_obj.system_name][m_obj.module_name] = module_dic
    #         filename = export_xmind_api(xmind_dic)
    #         return make_response({"code": "000", "desc": filename})
    #     elif system_id:
    #         s_obj = self.sim.query_systeminfo_by_id(system_id)
    #         p_obj = self.pim.get_project_info(s_obj.project_id)
    #         m_list = self.mim.query_all_module(system_id)
    #         xmind_dic[p_obj.project_name] = {
    #             s_obj.system_name: {}
    #         }
    #         for m_obj in m_list:
    #             module_dic = deal_testcase_by_module(m_obj.id)
    #             xmind_dic[p_obj.project_name][s_obj.system_name][m_obj.module_name] = module_dic
    #         filename = export_xmind_api(xmind_dic)
    #         return make_response({"code": "000", "desc": filename})
    #     else:
    #         return make_response({"code": "200", "desc": "未识别到有效节点导出"})

    @developer_check
    def download_xmind_api(self):
        try:
            project_id = self.data.pop("projectId", None)
            system_id = self.data.pop("systemId", None)
            if not project_id and not system_id:
                raise KeyError
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})

        res_list = []
        if project_id:
            res_list = self.acim.query_api_subtree_for_xmind(project_id)
        elif system_id:
            res = self.acim.query_api_subtree_for_xmind_by_system_id(system_id)
            if res:
                system_name = res[0][0]
                for row in res:
                    temp_row = ['默认_{}'.format(system_name)]
                    temp_row.extend(list(row))
                    res_list.append(temp_row)

        xmind_dic = {}
        for row in res_list:
            if row[0] not in xmind_dic:
                xmind_dic[row[0]] = {}
            if row[1] and row[1] not in xmind_dic[row[0]]:
                xmind_dic[row[0]][row[1]] = {}
            if row[2] and row[2] not in xmind_dic[row[0]][row[1]]:
                xmind_dic[row[0]][row[1]][row[2]] = {}
            if row[3] and row[3] not in xmind_dic[row[0]][row[1]][row[2]]:
                xmind_dic[row[0]][row[1]][row[2]][row[3]] = {}
            if row[4]:
                tag_objs = self.attrm.query_tag_info_by_testcase(row[4])
                tag_name_list = [t_obj[1] for t_obj in tag_objs] if tag_objs else []
                tag = '异常场景' if '异常场景' in tag_name_list else '正常场景'
                if tag not in xmind_dic[row[0]][row[1]][row[2]][row[3]]:
                    xmind_dic[row[0]][row[1]][row[2]][row[3]].update({tag: {}})

                expect = row[6] if row[6] else ''
                xmind_dic[row[0]][row[1]][row[2]][row[3]][tag].update({row[5]: {'预期': {expect: {}}}})

        filename = export_xmind_api(xmind_dic)
        return make_response({"code": "000", "desc": filename})

    @developer_check
    def download_excel(self):
        try:
            system_id = self.data.pop("systemId")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        value_list = []
        value_list.append(self.header_func)
        """查询系统名称和项目id"""
        s_obj = self.bsim.query_system(id=system_id)
        if not s_obj:
            return make_response({"code": "100", "desc": "系统不存在"})
        project_id = s_obj.project_id
        system_name = s_obj.system_name
        """处理项目名称"""
        p_obj = self.bpim.get_project(id=project_id)
        if not p_obj:
            return make_response({"code": "100", "desc": "项目不存在"})
        project_name = p_obj.project_name
        """查询系统下模块"""
        parent_module_list = self.bmim.get_modules(system_id=system_id)
        testcase_objs = {}
        for module_obj in parent_module_list:
            module_name = module_obj.module_name
            module_name = remove_spaces(module_name)
            sub_module_list = self.bmim.get_modules(parent_module_id=module_obj.id)
            module_list = []
            module_list.append(self.header_func)
            idx = 1
            for sub_module_obj in sub_module_list:
                sub_module_name = sub_module_obj.module_name
                case_objs = self.btim.get_all_testcase(module_id=sub_module_obj.id)
                for case_obj in case_objs:
                    '''处理操作步骤和预期结果'''
                    detail = eval(case_obj.detail)
                    setup_list = []
                    step_list = []
                    expect_list = []
                    remark_list = []
                    actualResult_list = []
                    for i in range(0, len(detail)):
                        setup_list.append(detail[i]["前置条件"])
                        step_list.append(detail[i]["操作步骤"])
                        expect_list.append(detail[i]["预期结果"])
                        remark_list.append(detail[i]["备注"])
                        actualResult_list.append('')
                    """封装写入Excel的数据"""
                    case_list = []
                    case_list.append(idx)
                    case_list.append(sub_module_name)
                    case_list.append(case_obj.testcase_name)
                    case_list.append(setup_list)
                    case_list.append(step_list)
                    case_list.append(expect_list)
                    case_list.append(actualResult_list)
                    case_list.append(remark_list)
                    module_list.append(case_list)
                    idx += 1
            testcase_objs[module_name] = module_list
        ep = ExcelParser(project_name + '_' + system_name)

        file_name = ep.writeExcel(values=testcase_objs)
        return make_response({"code": "000", "desc": file_name})

    @developer_check
    def download_modules_excel(self):
        try:
            system_id = self.data.pop("systemId")
            sub_module_list = self.data.pop("moduleList")
        except KeyError:
            return make_response({"code": "100", "desc": "入参校验失败"})
        value_list = []
        value_list.append(self.header_func)
        """查询系统名称和项目id"""
        s_obj = self.bsim.query_system(id=system_id)
        if not s_obj:
            return make_response({"code": "100", "desc": "系统不存在"})
        project_id = s_obj.project_id
        system_name = s_obj.system_name
        """处理项目名称"""
        p_obj = self.bpim.get_project(id=project_id)
        if not p_obj:
            return make_response({"code": "100", "desc": "项目不存在"})
        project_name = p_obj.project_name
        """查询系统下模块"""

        sub_module_object = {}
        for sub_module_id in sub_module_list:
            parent_module_obj = self.bmim.get_module(id=(self.bmim.get_module(id=sub_module_id).parent_module_id))
            if parent_module_obj.id not in sub_module_object.keys():
                sub_module_object[parent_module_obj.id] = [sub_module_id]
            else:
                sub_module_object[parent_module_obj.id].append(sub_module_id)

        testcase_objs = {}
        for module_id, sub_module_id_list in sub_module_object.items():
            module_name = self.bmim.get_module(id=module_id).module_name
            module_name = remove_spaces(module_name)
            sub_module_list = self.bmim.get_modules_by_module_ids(sub_module_id_list)
            module_list = []
            module_list.append(self.header_func)
            idx = 1
            for sub_module_obj in sub_module_list:
                sub_module_name = sub_module_obj.module_name
                case_objs = self.btim.get_all_testcase(module_id=sub_module_obj.id)
                for case_obj in case_objs:
                    '''处理操作步骤和预期结果'''
                    detail = eval(case_obj.detail)
                    setup_list = []
                    step_list = []
                    expect_list = []
                    remark_list = []
                    actualResult_list = []
                    for i in range(0, len(detail)):
                        setup_list.append(detail[i]["前置条件"])
                        step_list.append(detail[i]["操作步骤"])
                        expect_list.append(detail[i]["预期结果"])
                        remark_list.append(detail[i]["备注"])
                        actualResult_list.append('')
                    """封装写入Excel的数据"""
                    case_list = []
                    case_list.append(idx)
                    case_list.append(sub_module_name)
                    case_list.append(case_obj.testcase_name)
                    case_list.append(setup_list)
                    case_list.append(step_list)
                    case_list.append(expect_list)
                    case_list.append(actualResult_list)
                    case_list.append(remark_list)
                    module_list.append(case_list)
                    idx += 1
            testcase_objs[module_name] = module_list
        ep = ExcelParser(project_name + '_' + system_name)
        file_name = ep.writeExcel(values=testcase_objs)
        return make_response({"code": "000", "desc": file_name})


def remove_spaces(name):
    if '\r\n' in name:
        nameList = name.split('\r\n')
        name = nameList[0] + nameList[1]
        if '/' in name:
            name = name.replace('/', '-')
        return name
    elif '/' in name:
        name = name.replace('/', '-')
        return name
    else:
        return name




def traverse_module(module_id, module_name):
    """返回最底层子模块id和所有module_name的拼接"""
    module_id_list = []
    sub_module_list = BaseModuleInfoManager.get_modules(parent_module_id=module_id)
    if sub_module_list:
        last_sub_module_list = None
        for obj in sub_module_list:
            deal_module_name = module_name + "-" + obj.module_name
            last_sub_module_list = traverse_module(obj.id, deal_module_name)
        return last_sub_module_list
    else:
        module_id_list.append(module_id)
        module_id_list.append(module_name)
        module_list.append(module_id_list)
        return module_list



