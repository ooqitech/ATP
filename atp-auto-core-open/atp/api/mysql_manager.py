# -*- coding:utf-8 -*-

from atp.extensions import db
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy import or_, distinct, case

from atp.models.atp_auto import (
    EnvInfo, User, TestcaseTag, BaseProjectInfo, BaseSystemInfo, BaseModuleInfo, BaseTestcaseInfo,
    BaseJobHistory, UiProjectInfo, UiSystemInfo, UiModuleInfo, UICasePageInfo, UICasePageObjectInfo, UiTestcaseInfo,
    ApiTestcaseRequestQll, ApiIntfDefaultRequest, BaseModuleInfoBak, BaseTestcaseInfoBak, CeleryTaskRecord,
    ApiRunTaskResult, GenerateDataRecord, ApiTestcaseMainTagRelation, ApiTestcaseMainCustomFlow)
from atp.models.atp_auto import (
    ApiCompanyInfo, ApiIntfInfo, ApiProjectInfo, ApiProjectIntfRelation, ApiProjectSystemRelation,
    ApiPublicVariableInfo, ApiSystemInfo, ApiTestcaseInfo, ApiTestcaseRequest, ApiTestcaseTagRelation, ApiTestReport,
    ApiProductLine, ApiTestcaseMain, ApiTestcaseSub, ApiTestcaseReuseRecord, ApiTaskInfo, GitDiffVersion
)
import logging

from sqlalchemy.exc import IntegrityError

logging.basicConfig(level=logging.DEBUG)


class SessionHandler(object):
    def __init__(self):
        self.db = db
        self.session = None

    def __enter__(self):
        self.session = self.db.session
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()

class ApiCompanyInfoManager(object):
    @staticmethod
    def insert_company(**kwargs):
        with SessionHandler() as sh:
            obj = ApiCompanyInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_company(insert_list):
        with SessionHandler() as sh:
            objs = [ApiCompanyInfo(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_company(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiCompanyInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_company(id_):
        with SessionHandler() as session_handler:
            obj = ApiCompanyInfo.query.filter_by(id=id_).first()
            if obj:
                session_handler.session.delete(obj)
                session_handler.session.commit()

    @staticmethod
    def get_company(**kwargs):
        with SessionHandler() as session_handler:
            obj = ApiCompanyInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_companies(**kwargs):
        with SessionHandler() as session_handler:
            objs = ApiCompanyInfo.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def query_api_subtree(company_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiSystemInfo.git_url
            ).outerjoin(
                ApiIntfInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).filter(
                ApiSystemInfo.api_company_id == company_id
            ).order_by(db.asc(ApiSystemInfo.system_name), db.asc(ApiIntfInfo.intf_name)).all()

    @staticmethod
    def query_api_project_subtree(company_id, start_day=None):
        with SessionHandler() as sh:
            if start_day:
                return sh.session.query(
                    ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
                    ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseInfo.id,
                    ApiTestcaseInfo.testcase_name,
                ).outerjoin(
                    ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
                ).outerjoin(
                    ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
                ).outerjoin(
                    ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
                ).outerjoin(
                    ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
                ).filter(
                    ApiProjectInfo.api_company_id == company_id,
                    ApiProjectInfo.create_time > start_day
                ).order_by(
                    db.asc(ApiProjectInfo.id),
                    db.asc(ApiSystemInfo.system_name),
                    db.asc(ApiIntfInfo.intf_name),
                    db.asc(ApiTestcaseInfo.index),
                ).all()
            else:
                return sh.session.query(
                    ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
                    ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseInfo.id,
                    ApiTestcaseInfo.testcase_name,
                ).outerjoin(
                    ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
                ).outerjoin(
                    ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
                ).outerjoin(
                    ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
                ).outerjoin(
                    ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
                ).filter(
                    ApiProjectInfo.api_company_id == company_id
                ).order_by(
                    db.asc(ApiProjectInfo.id),
                    db.asc(ApiSystemInfo.system_name),
                    db.asc(ApiIntfInfo.intf_name),
                    db.asc(ApiTestcaseInfo.index),
                ).all()

    @staticmethod
    def query_api_project_subtree_for_main_case(company_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseMain.id,
                ApiTestcaseMain.testcase_name,
            ).outerjoin(
                ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseMain, ApiTestcaseMain.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiProjectInfo.api_company_id == company_id
            ).order_by(
                db.asc(ApiProjectInfo.id),
                db.asc(ApiSystemInfo.system_name),
                db.asc(ApiIntfInfo.intf_name),
                db.asc(ApiTestcaseMain.index),
            ).all()

    @staticmethod
    def query_api_product_line_subtree(company_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProductLine.id, ApiProductLine.product_line_name,
                ApiTestcaseMain.id, func.concat(ApiTestcaseMain.id, '_', ApiTestcaseMain.testcase_name)
            ).outerjoin(
                ApiTestcaseMain, ApiProductLine.id == ApiTestcaseMain.api_product_line_id
            ).filter(
                ApiProductLine.api_company_id == company_id,
                # ApiTestcaseMain.case_type == 2
            ).order_by(
                db.asc(ApiProductLine.index),
                db.asc(ApiTestcaseMain.index),
            ).all()

    @staticmethod
    def query_api_intf_case_subtree(company_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name),
                ApiTestcaseInfo.id,
                func.concat(ApiTestcaseInfo.id, '_', ApiTestcaseInfo.testcase_name, '__', ApiTestcaseInfo.expect_result)
            ).join(
                ApiIntfInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
            ).filter(
                ApiSystemInfo.api_company_id == company_id
            ).order_by(
                db.asc(ApiSystemInfo.system_name),
                db.asc(ApiIntfInfo.intf_name),
                db.asc(ApiTestcaseInfo.index),
            ).all()

    @staticmethod
    def query_api_project_subtree_patch(company_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
            ).outerjoin(
                ApiProjectSystemRelation, ApiProjectSystemRelation.api_project_id == ApiProjectInfo.id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiProjectSystemRelation.api_system_id
            ).filter(
                ApiProjectInfo.api_company_id == company_id
            ).order_by(
                db.asc(ApiProjectInfo.id), db.asc(ApiSystemInfo.system_name)).all()

    @staticmethod
    def query_api_subtree_for_xmind(project_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.project_name, ApiSystemInfo.system_name, ApiIntfInfo.intf_type, ApiIntfInfo.intf_name,
                ApiTestcaseInfo.id, ApiTestcaseInfo.testcase_name, ApiTestcaseInfo.expect_result
            ).outerjoin(
                ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiProjectInfo.id == project_id).all()

    @staticmethod
    def query_api_subtree_for_xmind_by_system_id(system_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiSystemInfo.system_name, ApiIntfInfo.intf_type, ApiIntfInfo.intf_name,
                ApiTestcaseInfo.id, ApiTestcaseInfo.testcase_name, ApiTestcaseInfo.expect_result
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.api_system_id == ApiSystemInfo.id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiSystemInfo.id == system_id).all()

    @staticmethod
    def query_api_project_subtree_by_testcase_id(company_id, testcase_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseInfo.id,
                ApiTestcaseInfo.testcase_name,
            ).outerjoin(
                ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiProjectInfo.api_company_id == company_id,
                ApiTestcaseInfo.id == testcase_id
            ).order_by(
                db.desc(ApiProjectInfo.id)
            ).all()

    @staticmethod
    def query_api_subtree_by_testcase_id(company_id, testcase_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseInfo.id,
                ApiTestcaseInfo.testcase_name,
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.api_system_id == ApiSystemInfo.id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiSystemInfo.api_company_id == company_id,
                ApiTestcaseInfo.id == testcase_id
            ).order_by(
                db.desc(ApiSystemInfo.id)
            ).all()

    @staticmethod
    def query_api_project_subtree_like_intf_url(company_id, intf_url):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseInfo.id,
                ApiTestcaseInfo.testcase_name,
            ).outerjoin(
                ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiProjectInfo.api_company_id == company_id,
                ApiIntfInfo.intf_name.ilike('%{}%'.format(intf_url))
            ).order_by(
                db.desc(ApiProjectInfo.id),
                db.asc(ApiSystemInfo.system_name),
                db.asc(ApiIntfInfo.intf_name),
            ).all()

    @staticmethod
    def query_api_subtree_like_intf_url(company_id, intf_url):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseInfo.id,
                ApiTestcaseInfo.testcase_name,
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.api_system_id == ApiSystemInfo.id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiSystemInfo.api_company_id == company_id,
                ApiIntfInfo.intf_name.ilike('%{}%'.format(intf_url))
            ).order_by(
                db.asc(ApiSystemInfo.system_name),
                db.asc(ApiIntfInfo.intf_name),
                db.asc(ApiTestcaseInfo.index),
            ).all()

    @staticmethod
    def query_api_project_subtree_like_intf_desc(company_id, intf_desc):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseInfo.id,
                ApiTestcaseInfo.testcase_name,
            ).outerjoin(
                ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiProjectInfo.api_company_id == company_id,
                ApiIntfInfo.intf_desc.ilike('%{}%'.format(intf_desc))
            ).order_by(
                db.desc(ApiProjectInfo.id),
                db.asc(ApiSystemInfo.system_name),
                db.asc(ApiIntfInfo.intf_name),
            ).all()

    @staticmethod
    def query_api_subtree_like_intf_desc(company_id, intf_desc):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseInfo.id,
                ApiTestcaseInfo.testcase_name,
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.api_system_id == ApiSystemInfo.id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiSystemInfo.api_company_id == company_id,
                ApiIntfInfo.intf_desc.ilike('%{}%'.format(intf_desc))
            ).order_by(
                db.asc(ApiSystemInfo.system_name),
                db.asc(ApiIntfInfo.intf_name),
                db.asc(ApiTestcaseInfo.index),
            ).all()

    @staticmethod
    def query_api_project_subtree_like_testcase_name(company_id, testcase_name):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseInfo.id,
                ApiTestcaseInfo.testcase_name,
            ).outerjoin(
                ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiProjectInfo.api_company_id == company_id,
                ApiTestcaseInfo.testcase_name.ilike('%{}%'.format(testcase_name))
            ).order_by(
                db.desc(ApiProjectInfo.id),
                db.asc(ApiSystemInfo.system_name),
                db.asc(ApiIntfInfo.intf_name),
            ).all()

    @staticmethod
    def query_api_project_subtree_like_testcase_creator(company_id, testcase_creator):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name), ApiTestcaseInfo.id,
                ApiTestcaseInfo.testcase_name,
            ).outerjoin(
                ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiProjectInfo.api_company_id == company_id,
                ApiTestcaseInfo.creator.ilike('%{}%'.format(testcase_creator))
            ).order_by(
                db.desc(ApiProjectInfo.id),
                db.asc(ApiSystemInfo.system_name),
                db.asc(ApiIntfInfo.intf_name),
            ).all()


class ApiIntfInfoManager(object):
    @staticmethod
    def insert_intf(**kwargs):
        with SessionHandler() as sh:
            obj = ApiIntfInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_intf(insert_list):
        with SessionHandler() as sh:
            objs = [ApiIntfInfo(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_intf(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiIntfInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_intf(id_):
        with SessionHandler() as sh:
            obj = ApiIntfInfo.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_intf(**kwargs):
        with SessionHandler() as sh:
            obj = ApiIntfInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_intfs(**kwargs):
        with SessionHandler() as sh:
            objs = ApiIntfInfo.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_intfs_in_id_list(id_list):
        with SessionHandler() as sh:
            objs = ApiIntfInfo.query.filter(ApiIntfInfo.id.in_(id_list)).all()
            return objs

    @staticmethod
    def get_intfs_in_system_id_list(system_id_list):
        with SessionHandler() as sh:
            objs = ApiIntfInfo.query.filter(ApiIntfInfo.api_system_id.in_(system_id_list)).all()
            return objs


class ApiProjectInfoManager(object):
    @staticmethod
    def insert_project(**kwargs):
        with SessionHandler() as sh:
            obj = ApiProjectInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_project(insert_list):
        with SessionHandler() as sh:
            objs = [ApiProjectInfo(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_project(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiProjectInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_project(id_):
        with SessionHandler() as sh:
            obj = ApiProjectInfo.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_project(**kwargs):
        with SessionHandler() as sh:
            obj = ApiProjectInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_projects(**kwargs):
        with SessionHandler() as sh:
            objs = ApiProjectInfo.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_projects_reverse(**kwargs):
        with SessionHandler() as sh:
            objs = ApiProjectInfo.query.filter_by(**kwargs).order_by(db.desc(ApiProjectInfo.id)).all()
            return objs

    @staticmethod
    def query_api_project_subtree(project_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
                ApiIntfInfo.id, func.concat(ApiIntfInfo.intf_desc, '-', ApiIntfInfo.intf_name),
                ApiTestcaseInfo.id, func.concat(ApiTestcaseInfo.testcase_name, '_', ApiTestcaseInfo.expect_result),
            ).outerjoin(
                ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiProjectInfo.id == project_id
            ).order_by(
                db.asc(ApiSystemInfo.system_name),
                db.asc(ApiIntfInfo.intf_name),
                db.asc(ApiTestcaseInfo.index),
            ).all()

    @staticmethod
    def count_api_project_subtree(project_id):
        with SessionHandler() as sh:
            return sh.session.query(
                func.count(ApiTestcaseInfo.id)
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
            ).outerjoin(
                ApiProjectIntfRelation, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
                # ).outerjoin(
                #     ApiProjectInfo, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
                # ).
            ).filter(
                ApiProjectIntfRelation.api_project_id == project_id
            ).first()

    @staticmethod
    def count_api_project_subtree_group_by_project_id(company_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.id, func.count(ApiTestcaseInfo.id)
            ).outerjoin(
                ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id
            ).filter(
                ApiProjectInfo.api_company_id == company_id
            ).group_by(
                ApiProjectInfo.id
            ).all()

    @staticmethod
    def query_api_project_subtree_patch(project_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.id, ApiProjectInfo.project_name, ApiSystemInfo.id, ApiSystemInfo.system_name,
            ).outerjoin(
                ApiProjectSystemRelation, ApiProjectSystemRelation.api_project_id == ApiProjectInfo.id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiProjectSystemRelation.api_system_id
            ).filter(
                ApiProjectInfo.id == project_id
            ).order_by(
                db.asc(ApiProjectInfo.id), db.asc(ApiSystemInfo.system_name)).all()


class ApiProjectIntfRelationManager(object):
    @staticmethod
    def insert_relation(**kwargs):
        with SessionHandler() as sh:
            obj = ApiProjectIntfRelation(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_relation(insert_list):
        with SessionHandler() as sh:
            objs = [ApiProjectIntfRelation(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_relation(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiProjectIntfRelation.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_relation(id_):
        with SessionHandler() as sh:
            obj = ApiProjectIntfRelation.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_relation(**kwargs):
        with SessionHandler() as sh:
            obj = ApiProjectIntfRelation.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_relations(**kwargs):
        with SessionHandler() as sh:
            objs = ApiProjectIntfRelation.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_distinct_intf_ids():
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectIntfRelation.api_intf_id
            ).filter().distinct().all()


class ApiProjectSystemRelationManager(object):
    @staticmethod
    def insert_relation(**kwargs):
        with SessionHandler() as sh:
            obj = ApiProjectSystemRelation(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_relation(insert_list):
        with SessionHandler() as sh:
            objs = [ApiProjectSystemRelation(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_relation(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiProjectSystemRelation.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_relation(id_):
        with SessionHandler() as sh:
            obj = ApiProjectSystemRelation.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_relation(**kwargs):
        with SessionHandler() as sh:
            obj = ApiProjectSystemRelation.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_relations(**kwargs):
        with SessionHandler() as sh:
            objs = ApiProjectSystemRelation.query.filter_by(**kwargs).all()
            return objs


class ApiPublicVariableInfoManager(object):
    @staticmethod
    def insert_variable(**kwargs):
        with SessionHandler() as sh:
            obj = ApiPublicVariableInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_variable(insert_list):
        with SessionHandler() as sh:
            objs = [ApiPublicVariableInfo(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_variable(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiPublicVariableInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_variable(id_):
        with SessionHandler() as sh:
            obj = ApiPublicVariableInfo.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_variable(**kwargs):
        with SessionHandler() as sh:
            obj = ApiPublicVariableInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_variables(**kwargs):
        with SessionHandler() as sh:
            objs = ApiPublicVariableInfo.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_variables_in_id_list(id_list):
        with SessionHandler() as sh:
            objs = ApiPublicVariableInfo.query.filter(ApiPublicVariableInfo.id.in_(id_list)).all()
            return objs

    @staticmethod
    def public_variable_paginate(page, num, keywords=None):
        with SessionHandler() as sh:
            if keywords:
                value = '%{0}%'.format(keywords)
                data = ApiPublicVariableInfo.query.order_by(db.desc(ApiPublicVariableInfo.create_time)).filter(
                    or_(ApiPublicVariableInfo.variable_name.ilike(value),
                        ApiPublicVariableInfo.value.ilike(value),
                        ApiPublicVariableInfo.type.ilike(value),
                        ApiPublicVariableInfo.api_system_id.ilike(value))
                ).paginate(page=page, per_page=num, error_out=False)
            else:
                data = ApiPublicVariableInfo.query.order_by(
                    db.desc(ApiPublicVariableInfo.create_time)).filter().paginate(
                    page=page, per_page=num, error_out=False)
            return data

    @staticmethod
    def whether_variable_name_canbeupdated(variable_name, id_, api_system_id):
        """判断更改变量名称时,是否被其它变量名称使用"""
        with SessionHandler() as sh:
            obj = ApiPublicVariableInfo.query.filter(ApiPublicVariableInfo.id != id_,
                                                     ApiPublicVariableInfo.variable_name == variable_name,
                                                     ApiPublicVariableInfo.api_system_id == api_system_id).first()
            if obj:
                return True
            else:
                return False

    @staticmethod
    def whether_variable_name_canbeupdated_in_company_id(variable_name, id_, api_company_id):
        """判断更改变量名称时,是否被其它变量名称使用"""
        with SessionHandler() as sh:
            obj = ApiPublicVariableInfo.query.filter(ApiPublicVariableInfo.id != id_,
                                                     ApiPublicVariableInfo.variable_name == variable_name,
                                                     ApiPublicVariableInfo.api_company_id == api_company_id).first()
            if obj:
                return True
            else:
                return False


class ApiSystemInfoManager(object):
    @staticmethod
    def insert_system(**kwargs):
        with SessionHandler() as sh:
            obj = ApiSystemInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_system(insert_list):
        with SessionHandler() as sh:
            objs = [ApiSystemInfo(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_system(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiSystemInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_system(id_):
        with SessionHandler() as sh:
            obj = ApiSystemInfo.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_system(**kwargs):
        with SessionHandler() as sh:
            obj = ApiSystemInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_systems(**kwargs):
        with SessionHandler() as sh:
            objs = ApiSystemInfo.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def count_system_with_intf_in_company_id(company_id):
        with SessionHandler() as sh:
            return sh.session.query(
                func.count(distinct(ApiSystemInfo.id))
            ).join(
                ApiIntfInfo, ApiIntfInfo.api_system_id == ApiSystemInfo.id
            ).filter(ApiSystemInfo.api_company_id == company_id).first()


class ApiTestcaseInfoManager(object):
    @staticmethod
    def insert_testcase(**kwargs):
        with SessionHandler() as sh:
            api_intf_id = kwargs.get('api_intf_id')
            pre_obj = ApiTestcaseInfo.query.filter_by(api_intf_id=api_intf_id).order_by(
                db.desc(ApiTestcaseInfo.index)).first()
            index = pre_obj.index + 1 if pre_obj else 0
            kwargs.update({'index': index})
            obj = ApiTestcaseInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_testcase(insert_list):
        with SessionHandler() as sh:
            objs = [ApiTestcaseInfo(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_testcase(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_testcase(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseInfo.query.filter_by(id=id_).first()
            if obj:
                to_update_objs = ApiTestcaseInfo.query.filter(
                    ApiTestcaseInfo.api_intf_id == obj.api_intf_id, ApiTestcaseInfo.index > obj.index
                ).all()
                for to_update_obj in to_update_objs:
                    to_update_obj = obj_set_value(to_update_obj, 'index', to_update_obj.index - 1)
                    sh.session.add(to_update_obj)
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_testcases(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTestcaseInfo.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def count_testcases_in_intf_id_list(intf_id_list):
        with SessionHandler() as sh:
            # return sh.session.query(func.count(ApiTestcaseInfo.id)).filter_by(**kwargs).first()
            return sh.session.query(
                func.count(ApiTestcaseInfo.id)
            ).filter(
                ApiTestcaseInfo.api_intf_id.in_(intf_id_list), ApiTestcaseInfo.case_status == 0
            ).first()

    @staticmethod
    def get_testcases_order_by_create_time_desc(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTestcaseInfo.query.filter_by(**kwargs).order_by(db.desc(ApiTestcaseInfo.create_time)).all()
            return objs

    @staticmethod
    def query_all_testcases_include():
        with SessionHandler() as sh:
            return sh.session.query(ApiTestcaseInfo.include).filter().all()

    @staticmethod
    def paging_query_testcase_by_intf_id(intf_id, page_no, page_size, testcase_name=None):
        """分页查询某一接口下的testcase"""
        with SessionHandler() as sh:
            if testcase_name:
                value = '%{0}%'.format(testcase_name)
                pagination_obj = ApiTestcaseInfo.query.order_by(db.asc(ApiTestcaseInfo.index)).filter(
                    ApiTestcaseInfo.api_intf_id == intf_id, ApiTestcaseInfo.testcase_name.ilike(value)).paginate(
                    page=page_no, per_page=page_size, error_out=False)
            else:
                pagination_obj = ApiTestcaseInfo.query.order_by(db.asc(ApiTestcaseInfo.index)).filter(
                    ApiTestcaseInfo.api_intf_id == intf_id).paginate(page=page_no, per_page=page_size, error_out=False)
            return pagination_obj

    @staticmethod
    def query_testcase_belong(testcase_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiTestcaseInfo.include, ApiTestcaseInfo.testcase_name, ApiSystemInfo.system_name,
                ApiIntfInfo.intf_name, ApiTestcaseRequest.request
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).outerjoin(
                ApiTestcaseRequest, ApiTestcaseRequest.api_testcase_id == ApiTestcaseInfo.id
            ).filter(ApiTestcaseInfo.id == testcase_id).first()

    @staticmethod
    def get_testcases_in_id_list(id_list):
        with SessionHandler() as sh:
            objs = ApiTestcaseInfo.query.filter(ApiTestcaseInfo.id.in_(id_list)).all()
            return objs

    @staticmethod
    def get_testcases_in_intf_id_list(intf_id_list):
        with SessionHandler() as sh:
            objs = ApiTestcaseInfo.query.filter(ApiTestcaseInfo.api_intf_id.in_(intf_id_list)).all()
            return objs

    @staticmethod
    def get_last_obj_by_intf(intf_id):
        with SessionHandler() as sh:
            return ApiTestcaseInfo.query.filter_by(api_intf_id=intf_id).order_by(db.desc(ApiTestcaseInfo.index)).first()

    @staticmethod
    def get_last_obj():
        with SessionHandler() as sh:
            return ApiTestcaseInfo.query.order_by(db.desc(ApiTestcaseInfo.id)).first()

    @staticmethod
    def index_update_while_remove_testcase(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseInfo.query.filter_by(id=id_).first()
            if obj:
                to_update_objs = ApiTestcaseInfo.query.filter(
                    ApiTestcaseInfo.api_intf_id == obj.api_intf_id, ApiTestcaseInfo.index > obj.index
                ).all()
                for to_update_obj in to_update_objs:
                    to_update_obj = obj_set_value(to_update_obj, 'index', to_update_obj.index - 1)
                    sh.session.add(to_update_obj)
                sh.session.commit()

    @staticmethod
    def filter_task_testcase_ids(intf_id, tag_id_list):
        with SessionHandler() as sh:
            # # 可自动化标签默认添加
            # if 12 not in tag_id_list:
            #     tag_id_list.append(12)
            return sh.session.query(
                ApiTestcaseInfo.id
            ).join(
                ApiTestcaseTagRelation, ApiTestcaseInfo.id == ApiTestcaseTagRelation.api_testcase_id
            ).filter(
                ApiTestcaseInfo.api_intf_id == intf_id,
                ApiTestcaseTagRelation.tag_id.in_(tag_id_list),
                ApiTestcaseInfo.case_status == 0
            ).distinct().all()

    @staticmethod
    def filter_task_testcase_ids_(intf_ids, tag_id_list):
        with SessionHandler() as sh:
            # # 可自动化标签默认添加
            # if 12 not in tag_id_list:
            #     tag_id_list.append(12)
            return sh.session.query(
                ApiTestcaseInfo.id,
                ApiTestcaseInfo.api_intf_id
            ).join(
                ApiTestcaseTagRelation, ApiTestcaseInfo.id == ApiTestcaseTagRelation.api_testcase_id
            ).filter(
                ApiTestcaseInfo.api_intf_id.in_(intf_ids),
                ApiTestcaseTagRelation.tag_id.in_(tag_id_list),
                ApiTestcaseInfo.case_status == 0
            ).distinct().all()

    @staticmethod
    def get_id_and_setup_case_list():
        with SessionHandler() as sh:
            return sh.session.query(
                ApiTestcaseInfo.id, ApiTestcaseInfo.setup_case_list
            ).filter().all()

    @staticmethod
    def get_intf_and_case_info_in_case_ids(case_ids):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiIntfInfo.id, ApiIntfInfo.intf_name, ApiIntfInfo.intf_desc, ApiIntfInfo.intf_type,
                ApiTestcaseInfo.id, ApiTestcaseInfo.testcase_name, ApiTestcaseInfo.creator,
                ApiTestcaseInfo.last_modifier, ApiTestcaseInfo.case_status, ApiTestcaseInfo.last_run,
                ApiTestcaseInfo.create_time, ApiTestcaseInfo.update_time, ApiTestcaseInfo.last_run_time
            ).join(
                ApiTestcaseInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id,
            ).filter(
                ApiTestcaseInfo.id.in_(case_ids),
            ).order_by(
                ApiIntfInfo.api_system_id, ApiIntfInfo.intf_name, ApiTestcaseInfo.id
            ).all()

    @staticmethod
    def get_recent_testcases_by_time(time_):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiProjectInfo.project_name, ApiSystemInfo.system_name, ApiTestcaseInfo.id,
                ApiTestcaseInfo.create_time, ApiTestcaseInfo.last_modify_time, ApiTestcaseInfo.creator,
                ApiTestcaseInfo.last_modifier, ApiProjectInfo.id,
            ).join(
                ApiProjectIntfRelation, ApiProjectInfo.id == ApiProjectIntfRelation.api_project_id,
            ).join(
                ApiIntfInfo, ApiIntfInfo.id == ApiProjectIntfRelation.api_intf_id,
            ).join(
                ApiTestcaseInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id,
            ).join(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id,
            ).filter(
                or_(ApiTestcaseInfo.create_time > time_, ApiTestcaseInfo.last_modify_time > time_),
                ApiSystemInfo.id.notin_([448, 450, 451]), ApiTestcaseInfo.case_status == 0
            ).order_by(
                ApiProjectInfo.project_name, ApiSystemInfo.id, ApiTestcaseInfo.id
            ).all()

    @staticmethod
    def get_recent_testcases_by_time_not_belong_project(time_, intf_id_list):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiSystemInfo.system_name, ApiTestcaseInfo.id,
                ApiTestcaseInfo.create_time, ApiTestcaseInfo.last_modify_time, ApiTestcaseInfo.creator,
                ApiTestcaseInfo.last_modifier
            ).join(
                ApiIntfInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id,
            ).join(
                ApiTestcaseInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id,
            ).filter(
                or_(ApiTestcaseInfo.create_time > time_, ApiTestcaseInfo.last_modify_time > time_),
                ApiIntfInfo.id.notin_(intf_id_list), ApiSystemInfo.id.notin_([448, 450, 451]),
                ApiTestcaseInfo.case_status == 0
            ).order_by(
                ApiSystemInfo.id, ApiTestcaseInfo.id
            ).all()

    @staticmethod
    def get_testcase_id_in_company_id(company_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiTestcaseInfo.id
            ).join(
                ApiIntfInfo, ApiTestcaseInfo.api_intf_id == ApiIntfInfo.id,
            ).join(
                ApiSystemInfo, ApiIntfInfo.api_system_id == ApiSystemInfo.id,
            ).filter(
                ApiSystemInfo.api_company_id == company_id,
                ApiTestcaseInfo.case_status == 0
            ).all()

    @staticmethod
    def count_testcase_in_tag_id(testcase_id_list, tag_id):
        with SessionHandler() as sh:
            return sh.session.query(
                func.count(ApiTestcaseTagRelation.id)
            ).join(
                ApiTestcaseInfo, ApiTestcaseInfo.id == ApiTestcaseTagRelation.api_testcase_id,
            ).filter(
                ApiTestcaseTagRelation.tag_id == tag_id,
                ApiTestcaseInfo.id.in_(testcase_id_list)
            ).first()

    @staticmethod
    def count_intf_in_company_id(company_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiIntfInfo.intf_type, func.count(distinct(ApiIntfInfo.id)),
            ).join(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id,
            ).filter(
                ApiSystemInfo.api_company_id == company_id,
            ).group_by(
                ApiIntfInfo.intf_type
            ).all()


class ApiTestcaseRequestManager(object):
    @staticmethod
    def insert_request(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseRequest(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_request(insert_list):
        with SessionHandler() as sh:
            objs = [ApiTestcaseRequest(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def delete_request(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseRequest.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def update_request(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseRequest.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def get_request(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseRequest.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def update_request_by_testcase_id(testcase_id, **kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseRequest.query.filter_by(api_testcase_id=testcase_id).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()


class ApiTestcaseTagRelationManager(object):
    @staticmethod
    def insert_relation(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseTagRelation(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_relation(insert_list):
        with SessionHandler() as sh:
            objs = [ApiTestcaseTagRelation(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def delete_relation(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseTagRelation.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_relation(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseTagRelation.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_relations(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTestcaseTagRelation.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def query_tag_info_by_testcase(testcase_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiTestcaseTagRelation.tag_id, TestcaseTag.tag_name,
            ).outerjoin(
                TestcaseTag, ApiTestcaseTagRelation.tag_id == TestcaseTag.id
            ).filter(
                ApiTestcaseTagRelation.api_testcase_id == testcase_id).all()

    @staticmethod
    def get_relations_in_case_ids(case_ids):
        with SessionHandler() as sh:
            objs = ApiTestcaseTagRelation.query.filter(ApiTestcaseTagRelation.api_testcase_id.in_(case_ids)).all()
            return objs


class ApiTestcaseMainTagRelationManager(object):
    @staticmethod
    def insert_relation(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseMainTagRelation(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_relation(insert_list):
        with SessionHandler() as sh:
            objs = [ApiTestcaseMainTagRelation(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def delete_relation(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseMainTagRelation.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_relation(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseMainTagRelation.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_relations(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTestcaseMainTagRelation.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def query_tag_info_by_testcase(testcase_id):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiTestcaseMainTagRelation.tag_id, TestcaseTag.tag_name,
            ).outerjoin(
                TestcaseTag, ApiTestcaseMainTagRelation.tag_id == TestcaseTag.id
            ).filter(
                ApiTestcaseMainTagRelation.api_testcase_id == testcase_id).all()


class ApiTestReportManager(object):
    @staticmethod
    def insert_report(**kwargs):
        with SessionHandler() as sh:
            kwargs.pop('report', None)
            obj = ApiTestReport(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_report(insert_list):
        with SessionHandler() as sh:
            objs = [ApiTestReport(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_report(id_, **kwargs):
        with SessionHandler() as sh:
            kwargs.pop('report', None)
            obj = ApiTestReport.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_report(id_):
        with SessionHandler() as sh:
            obj = ApiTestReport.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_report(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestReport.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_reports(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTestReport.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_next_report_id():
        """获取api_test_report表下一个id"""
        with SessionHandler() as sh:
            obj = sh.session.query(func.max(ApiTestReport.id)).first()
            if not obj[0]:
                return 1
            return obj[0] + 1

    @staticmethod
    def paging_query_reports(page_no, page_size, project_id=None, start_time=None, end_time=None, executor=None):
        with SessionHandler() as sh:
            if project_id and start_time and end_time and executor:
                pagination_obj = ApiTestReport.query.filter(ApiTestReport.create_time.between(start_time, end_time),
                                                            ApiTestReport.api_project_id == project_id,
                                                            ApiTestReport.executor == executor,
                                                            ApiTestReport.status.in_(('success', 'fail'))).order_by(
                    db.desc(ApiTestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)

            elif project_id and start_time and end_time:
                pagination_obj = ApiTestReport.query.filter(ApiTestReport.create_time.between(start_time, end_time),
                                                            ApiTestReport.api_project_id == project_id,
                                                            ApiTestReport.status.in_(('success', 'fail'))).order_by(
                    db.desc(ApiTestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)

            elif project_id and executor:
                pagination_obj = ApiTestReport.query.filter(ApiTestReport.api_project_id == project_id,
                                                            ApiTestReport.executor == executor,
                                                            ApiTestReport.status.in_(('success', 'fail'))).order_by(
                    db.desc(ApiTestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)

            elif start_time and end_time and executor:
                pagination_obj = ApiTestReport.query.filter(ApiTestReport.create_time.between(start_time, end_time),
                                                            ApiTestReport.executor == executor,
                                                            ApiTestReport.status.in_(('success', 'fail'))).order_by(
                    db.desc(ApiTestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)

            elif project_id:
                pagination_obj = ApiTestReport.query.filter(ApiTestReport.api_project_id == project_id,
                                                            ApiTestReport.status.in_(('success', 'fail'))).order_by(
                    db.desc(ApiTestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)

            elif start_time and end_time:
                pagination_obj = ApiTestReport.query.filter(ApiTestReport.create_time.between(start_time, end_time),
                                                            ApiTestReport.status.in_(('success', 'fail'))).order_by(
                    db.desc(ApiTestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)

            elif executor:
                pagination_obj = ApiTestReport.query.filter(ApiTestReport.executor == executor,
                                                            ApiTestReport.status.in_(('success', 'fail'))).order_by(
                    db.desc(ApiTestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)

            else:
                pagination_obj = ApiTestReport.query.filter(ApiTestReport.status.in_(('success', 'fail'))).order_by(
                    db.desc(ApiTestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)
            return pagination_obj


class ApiProductLineManager(object):
    @staticmethod
    def insert_product_line(**kwargs):
        with SessionHandler() as sh:
            api_company_id = kwargs.get('api_company_id')
            pre_obj = ApiProductLine.query.filter_by(api_company_id=api_company_id).order_by(
                db.desc(ApiProductLine.index)).first()
            index = pre_obj.index + 1 if pre_obj else 0
            kwargs.update({'index': index})
            obj = ApiProductLine(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def insert_folder(**kwargs):
        with SessionHandler() as sh:
            parent_id = kwargs.get('parent_id')
            pre_obj = ApiProductLine.query.filter_by(parent_id=parent_id).order_by(
                db.desc(ApiProductLine.index)).first()
            index = pre_obj.index + 1 if pre_obj else 0
            kwargs.update({'index': index})
            obj = ApiProductLine(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_product_line(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiProductLine.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_product_line(id_):
        with SessionHandler() as sh:
            obj = ApiProductLine.query.filter_by(id=id_).first()
            if obj:
                to_update_objs = ApiProductLine.query.filter(
                    ApiProductLine.api_company_id == obj.api_company_id, ApiProductLine.index > obj.index
                ).all()
                for to_update_obj in to_update_objs:
                    to_update_obj = obj_set_value(to_update_obj, 'index', to_update_obj.index - 1)
                    sh.session.add(to_update_obj)
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def delete_folder(id_):
        with SessionHandler() as sh:
            obj = ApiProductLine.query.filter_by(id=id_).first()
            if obj:
                to_update_objs = ApiProductLine.query.filter(
                    ApiProductLine.parent_id == obj.parent_id, ApiProductLine.index > obj.index
                ).all()
                for to_update_obj in to_update_objs:
                    to_update_obj = obj_set_value(to_update_obj, 'index', to_update_obj.index - 1)
                    sh.session.add(to_update_obj)
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_product_line(**kwargs):
        with SessionHandler() as sh:
            obj = ApiProductLine.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    # @custom_func_wrapper
    def get_product_lines(**kwargs):
        with SessionHandler() as sh:
            objs = ApiProductLine.query.filter_by(**kwargs).all()
            return objs


class ApiTestcaseMainManager(object):
    @staticmethod
    def insert_testcase_main(**kwargs):
        with SessionHandler() as sh:
            api_intf_id = kwargs.get('api_intf_id', None)
            api_product_line_id = kwargs.get('api_product_line_id', None)
            if api_product_line_id:
                pre_obj = ApiTestcaseMain.query.filter_by(api_product_line_id=api_product_line_id).order_by(
                    db.desc(ApiTestcaseMain.index)).first()
            else:
                pre_obj = ApiTestcaseMain.query.filter_by(api_intf_id=api_intf_id).order_by(
                    db.desc(ApiTestcaseMain.index)).first()
            index = pre_obj.index + 1 if pre_obj else 0
            kwargs.update({'index': index})
            obj = ApiTestcaseMain(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_testcase_main(insert_list):
        with SessionHandler() as sh:
            objs = [ApiTestcaseMain(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_testcase_main(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseMain.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_testcase_main(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseMain.query.filter_by(id=id_).first()
            if obj:
                if obj.case_type == 2:
                    to_update_objs = ApiTestcaseMain.query.filter(
                        ApiTestcaseMain.api_product_line_id == obj.api_product_line_id,
                        ApiTestcaseMain.index > obj.index
                    ).all()
                else:
                    to_update_objs = ApiTestcaseMain.query.filter(
                        ApiTestcaseMain.api_intf_id == obj.api_intf_id, ApiTestcaseMain.index > obj.index
                    ).all()
                for to_update_obj in to_update_objs:
                    to_update_obj = obj_set_value(to_update_obj, 'index', to_update_obj.index - 1)
                    sh.session.add(to_update_obj)
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_testcase_main(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseMain.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_testcase_mains(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTestcaseMain.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def count_testcases_in_id_list(id_list):
        with SessionHandler() as sh:
            return sh.session.query(
                func.count(ApiTestcaseMain.id)
            ).filter(
                ApiTestcaseMain.id.in_(id_list), ApiTestcaseMain.case_status == 0
            ).first()

    @staticmethod
    def paging_query_testcase_by_intf_id(intf_id, page_no, page_size, testcase_name=None):
        """分页查询某一接口下的testcase"""
        with SessionHandler() as sh:
            if testcase_name:
                value = '%{0}%'.format(testcase_name)
                pagination_obj = ApiTestcaseMain.query.order_by(db.asc(ApiTestcaseMain.index)).filter(
                    ApiTestcaseMain.api_intf_id == intf_id, ApiTestcaseMain.testcase_name.ilike(value)).paginate(
                    page=page_no, per_page=page_size, error_out=False)
            else:
                pagination_obj = ApiTestcaseMain.query.order_by(db.asc(ApiTestcaseMain.index)).filter(
                    ApiTestcaseMain.api_intf_id == intf_id).paginate(page=page_no, per_page=page_size, error_out=False)
            return pagination_obj

    @staticmethod
    def paging_query_testcase_by_product_line_id(product_line_id, page_no, page_size, testcase_name=None):
        """分页查询某一产品线下的testcase"""
        with SessionHandler() as sh:
            if testcase_name:
                value = '%{0}%'.format(testcase_name)
                pagination_obj = ApiTestcaseMain.query.order_by(db.asc(ApiTestcaseMain.index)).filter(
                    ApiTestcaseMain.api_product_line_id == product_line_id,
                    ApiTestcaseMain.testcase_name.ilike(value)).paginate(
                    page=page_no, per_page=page_size, error_out=False)
            else:
                pagination_obj = ApiTestcaseMain.query.order_by(db.asc(ApiTestcaseMain.index)).filter(
                    ApiTestcaseMain.api_product_line_id == product_line_id).paginate(page=page_no, per_page=page_size,
                                                                                     error_out=False)
            return pagination_obj

    @staticmethod
    def index_update_while_remove_testcase(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseMain.query.filter_by(id=id_).first()
            if obj:
                if obj.case_type == 2:
                    to_update_objs = ApiTestcaseMain.query.filter(
                        ApiTestcaseMain.api_product_line_id == obj.api_product_line_id,
                        ApiTestcaseMain.index > obj.index
                    ).all()
                else:
                    to_update_objs = ApiTestcaseMain.query.filter(
                        ApiTestcaseMain.api_intf_id == obj.api_intf_id, ApiTestcaseMain.index > obj.index
                    ).all()
                for to_update_obj in to_update_objs:
                    to_update_obj = obj_set_value(to_update_obj, 'index', to_update_obj.index - 1)
                    sh.session.add(to_update_obj)
                sh.session.commit()

    @staticmethod
    def get_last_obj_by_intf(intf_id):
        with SessionHandler() as sh:
            return ApiTestcaseMain.query.filter_by(api_intf_id=intf_id).order_by(db.desc(ApiTestcaseMain.index)).first()

    @staticmethod
    def get_last_obj_by_product_line(product_line_id):
        with SessionHandler() as sh:
            return ApiTestcaseMain.query.filter_by(api_product_line_id=product_line_id).order_by(
                db.desc(ApiTestcaseMain.index)).first()

    @staticmethod
    def get_last_obj():
        with SessionHandler() as sh:
            return ApiTestcaseMain.query.order_by(db.desc(ApiTestcaseMain.id)).first()

    @staticmethod
    def get_testcases_in_id_list(id_list):
        with SessionHandler() as sh:
            objs = ApiTestcaseMain.query.filter(ApiTestcaseMain.id.in_(id_list)).all()
            return objs

    @staticmethod
    def get_valid_testcases_in_id_list(id_list):
        with SessionHandler() as sh:
            objs = ApiTestcaseMain.query.filter(ApiTestcaseMain.id.in_(id_list), ApiTestcaseMain.case_status == 0).all()
            return objs

    @staticmethod
    def get_testcase_mains_in_tag(api_product_line_id, tag_id_list=None):
        with SessionHandler() as sh:
            if not tag_id_list:
                return sh.session.query(
                    ApiTestcaseMain.id, func.concat(ApiTestcaseMain.testcase_name, '__', ApiTestcaseMain.expect_result),
                    ApiTestcaseMain.sub_list
                ).filter(
                    ApiTestcaseMain.api_product_line_id == api_product_line_id
                ).order_by(db.asc(ApiTestcaseMain.id)).all()

            elif 1 == len(tag_id_list):
                return sh.session.query(
                    ApiTestcaseMain.id, func.concat(ApiTestcaseMain.testcase_name, '__', ApiTestcaseMain.expect_result),
                    ApiTestcaseMain.sub_list
                ).join(
                    ApiTestcaseMainTagRelation, ApiTestcaseMain.id == ApiTestcaseMainTagRelation.api_testcase_id
                ).filter(
                    ApiTestcaseMain.api_product_line_id == api_product_line_id,
                    ApiTestcaseMainTagRelation.tag_id == tag_id_list[0]
                ).order_by(db.asc(ApiTestcaseMain.id)).all()
            elif 2 == len(tag_id_list):
                main_tag_relation1 = aliased(ApiTestcaseMainTagRelation)
                main_tag_relation2 = aliased(ApiTestcaseMainTagRelation)
                return sh.session.query(
                    ApiTestcaseMain.id, func.concat(ApiTestcaseMain.testcase_name, '__', ApiTestcaseMain.expect_result),
                    ApiTestcaseMain.sub_list
                ).join(
                    main_tag_relation1, ApiTestcaseMain.id == main_tag_relation1.api_testcase_id
                ).join(
                    main_tag_relation2, ApiTestcaseMain.id == main_tag_relation2.api_testcase_id
                ).filter(
                    ApiTestcaseMain.api_product_line_id == api_product_line_id,
                    main_tag_relation1.tag_id == tag_id_list[0],
                    main_tag_relation2.tag_id == tag_id_list[1]
                ).order_by(db.asc(ApiTestcaseMain.id)).all()
            else:
                return []

    @staticmethod
    def filter_task_testcase_ids(product_line_id, tag_id_list):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiTestcaseMain.id
            ).join(
                ApiTestcaseMainTagRelation, ApiTestcaseMain.id == ApiTestcaseMainTagRelation.api_testcase_id
            ).filter(
                ApiTestcaseMain.api_product_line_id == product_line_id,
                ApiTestcaseMainTagRelation.tag_id.in_(tag_id_list),
                ApiTestcaseMain.case_status == 0
            ).distinct().all()

    @staticmethod
    def filter_task_testcase_ids_(product_line_ids, tag_id_list):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiTestcaseMain.id
            ).join(
                ApiTestcaseMainTagRelation, ApiTestcaseMain.id == ApiTestcaseMainTagRelation.api_testcase_id
            ).filter(
                ApiTestcaseMain.api_product_line_id.in_(product_line_ids),
                ApiTestcaseMainTagRelation.tag_id.in_(tag_id_list),
                ApiTestcaseMain.case_status == 0
            ).distinct().all()


class ApiTestcaseSubManager(object):
    @staticmethod
    def insert_testcase_sub(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseSub(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_testcase_sub(insert_list):
        with SessionHandler() as sh:
            objs = [ApiTestcaseSub(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_testcase_sub(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseSub.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_update_testcase_sub(update_list):
        with SessionHandler() as sh:
            from atp.utils.tools import json_dumps
            sub_id_list = []
            for sub in update_list:
                sub_id = sub.pop('sub_id', None)

                if not sub:
                    # 引入的子用例，不更新直接跳过
                    sub_id_list.append(sub_id)
                    continue

                hr_request = sub.pop('request')
                if isinstance(hr_request, dict):
                    hr_request = json_dumps(hr_request)

                '''插入或更新ApiTestcaseSub和ApiTestcaseRequestQll'''
                # insert
                if not sub_id:
                    last_sub_obj = sh.session.query(func.max(ApiTestcaseSub.id)).first()
                    next_sub_id = last_sub_obj[0] + 1 if last_sub_obj[0] else 1
                    sub['id'] = next_sub_id
                    sub_id_list.append(next_sub_id)
                    obj = ApiTestcaseSub(**sub)
                    sh.session.add(obj)
                    sh.session.commit()

                    ApiTestcaseRequestQllManager.insert_request(
                        api_testcase_id=next_sub_id,
                        request=hr_request,
                    )

                # update
                else:
                    sub_id_list.append(sub_id)
                    obj = ApiTestcaseSub.query.filter_by(id=sub_id).first()
                    for column in sub:
                        obj = obj_set_value(obj, column, sub[column])
                    sh.session.add(obj)
                    sh.session.commit()

                    ApiTestcaseRequestQllManager.update_request_by_testcase_id(
                        testcase_id=sub_id,
                        request=hr_request,
                    )

            return sub_id_list

    @staticmethod
    def delete_testcase_sub(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseSub.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()
                ApiTestcaseRequestQllManager.delete_request_by_testcase_id(testcase_id=id_)

    @staticmethod
    def get_testcase_sub(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseSub.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    # @custom_func_wrapper
    def get_testcase_subs(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTestcaseSub.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_testcase_subs_in_id_list(id_list):
        with SessionHandler() as sh:
            objs = ApiTestcaseSub.query.filter(ApiTestcaseSub.id.in_(id_list)).all()
            return objs


class ApiTestcaseRequestQllManager(object):
    @staticmethod
    def insert_request(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseRequestQll(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_request(insert_list):
        with SessionHandler() as sh:
            objs = [ApiTestcaseRequestQll(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def delete_request(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseRequestQll.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def delete_request_by_testcase_id(testcase_id):
        with SessionHandler() as sh:
            obj = ApiTestcaseRequestQll.query.filter_by(api_testcase_id=testcase_id).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def update_request(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseRequestQll.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def get_request(**kwargs):
        with SessionHandler() as sh:
            return ApiTestcaseRequestQll.query.filter_by(**kwargs).first()

    @staticmethod
    def get_requests(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTestcaseRequestQll.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_redundant_requests():
        with SessionHandler() as sh:
            return sh.session.query(
                ApiTestcaseRequestQll.request
            ).group_by(
                ApiTestcaseRequestQll.request
            ).having(
                func.count(ApiTestcaseRequestQll.id) > 1
            ).all()

    @staticmethod
    def update_request_by_testcase_id(testcase_id, **kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseRequestQll.query.filter_by(api_testcase_id=testcase_id).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def get_requests_in_case_id_list(case_id_list):
        with SessionHandler() as sh:
            objs = ApiTestcaseRequestQll.query.filter(ApiTestcaseRequestQll.api_testcase_id.in_(case_id_list)).all()
            return objs


class EnvInfoManager(object):
    @staticmethod
    def insert_env(**kwargs):
        with SessionHandler() as sh:
            obj = EnvInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_env(id_, **kwargs):
        with SessionHandler() as sh:
            obj = EnvInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_env(id_):
        with SessionHandler() as sh:
            obj = EnvInfo.query.filter_by(id=id_).first()
            sh.session.delete(obj)
            sh.session.commit()

    @staticmethod
    def env_info(env_name=None):
        with SessionHandler() as sh:
            if env_name:
                obj = EnvInfo.query.filter_by(env_name=env_name)
            else:
                obj = EnvInfo.query.all()

            return obj

    @staticmethod
    def is_env_id_exist(id):
        with SessionHandler() as sh:
            obj = EnvInfo.query.filter_by(id=id).first()
            if obj:
                return True
            else:
                return False

    @staticmethod
    def is_env_name_exist(name):
        with SessionHandler() as sh:
            obj = EnvInfo.query.filter_by(env_name=name).first()
            if obj:
                return True
            else:
                return False

    @staticmethod
    def get_env_info(id_):
        with SessionHandler() as sh:
            obj = EnvInfo.query.filter_by(id=id_).first()
            return obj

    @staticmethod
    def get_env(**kwargs):
        with SessionHandler() as sh:
            obj = EnvInfo.query.filter_by(**kwargs).first()
            return obj


# class ProjectInfoManager(object):
#     @staticmethod
#     def insert_project(**kwargs):
#         obj = ProjectInfo(**kwargs)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def update_project(id_, **kwargs):
#         obj = ProjectInfo.query.filter_by(id=id_).first()
#         for column in kwargs:
#             obj = obj_set_value(obj, column, kwargs[column])
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def delete_project(id_):
#         obj = ProjectInfo.query.filter_by(id=id_).first()
#         sh.session.delete(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def is_project_name_exist(project_name):
#         project_name = '%' + project_name + '%'
#         obj = ProjectInfo.query.filter(ProjectInfo.project_name.like(project_name)).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def is_project_name_exist_for_update(project_name):
#         obj = ProjectInfo.query.filter_by(project_name=project_name).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def is_project_name_exist_union(id, project_name):
#         obj = ProjectInfo.query.filter_by(project_name=project_name, id=id).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def is_project_id_exist(id):
#         obj = ProjectInfo.query.filter_by(id=id).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def project_info(project_name):
#         if project_name == "":
#             obj = ProjectInfo.query.all()
#         else:
#             project_name = '%' + project_name + '%'
#             obj = ProjectInfo.query.filter(ProjectInfo.project_name.like(project_name)).all()
#
#         return obj
#
#     @staticmethod
#     def system_info(id_):
#
#         obj = SystemInfo.query.filter_by(project_id=id_).all()
#
#         return obj
#
#     @staticmethod
#     def select_id_by(project_name):
#         obj = ProjectInfo.query.filter_by(project_name=project_name).first()
#
#         return obj.id
#
#     @staticmethod
#     def get_project_info(id_):
#         obj = ProjectInfo.query.filter_by(id=id_).first()
#         return obj
#
#
# class SystemInfoManager(object):
#     @staticmethod
#     def insert_system(**kwargs):
#         project_id = kwargs.get('project_id')
#         pre_obj = SystemInfo.query.filter_by(project_id=project_id).order_by(db.desc(SystemInfo.index)).first()
#         index = pre_obj.index + 1 if (pre_obj and pre_obj.index is not None) else 0
#         kwargs.update({'index': index})
#         obj = SystemInfo(**kwargs)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def update_system(id_, **kwargs):
#         obj = SystemInfo.query.filter_by(id=id_).first()
#         for column in kwargs:
#             obj = obj_set_value(obj, column, kwargs[column])
#         # obj.system_name = kwargs.pop('system_name')
#         # obj.test_user = kwargs.pop('test_user', None)
#         # obj.dev_user = kwargs.pop('dev_user', None)
#         # obj.publish_app = kwargs.pop('publish_app', None)
#         # obj.simple_desc = kwargs.pop('simple_desc', None)
#         # obj.project_id = kwargs.pop('project_id', None)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def delete_system(id_):
#         obj = SystemInfo.query.filter_by(id=id_).first()
#         if obj:
#             to_update_objs = SystemInfo.query.filter(
#                 SystemInfo.project_id == obj.project_id, SystemInfo.index > obj.index
#             ).all()
#             for to_update_obj in to_update_objs:
#                 to_update_obj = obj_set_value(to_update_obj, 'index', to_update_obj.index - 1)
#                 sh.session.add(to_update_obj)
#             sh.session.delete(obj)
#             sh.session.commit()
#
#     @staticmethod
#     def is_system_name_exist(system_name, project_id=None):
#         if project_id:
#             obj = SystemInfo.query.filter_by(system_name=system_name, project_id=project_id).first()
#         else:
#             obj = SystemInfo.query.filter_by(system_name=system_name).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def query_systeminfo_by_id(_id):
#         obj = SystemInfo.query.filter_by(id=_id).first()
#         return obj
#
#     @staticmethod
#     def is_system_exist(system_name, project_id):
#         obj = SystemInfo.query.filter_by(system_name=system_name, project_id=project_id).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def is_project_id_exist(project_id):
#         obj = ProjectInfo.query.filter_by(id=project_id).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def is_system_id_exist(id):
#         obj = SystemInfo.query.filter_by(id=id).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def system_info(system_name):
#         if system_name == "":
#             obj = SystemInfo.query.all()
#         else:
#             system_name = '%' + system_name + '%'
#             obj = SystemInfo.query.filter(SystemInfo.system_name.like(system_name)).all()
#
#         return obj
#
#     @staticmethod
#     def project_info(id_):
#         obj = ProjectInfo.query.filter_by(id=id_).all()
#         return obj
#
#     @staticmethod
#     def select_by_project_id(project_id):
#         obj = SystemInfo.query.filter_by(project_id=project_id).all()
#         return obj
#
#     @staticmethod
#     def query_id_by_projectid(project_id, system_name):
#         obj = SystemInfo.query.filter_by(system_name=system_name, project_id=project_id).first()
#         return obj.id
#
#     @staticmethod
#     def get_max_index(project_id):
#         obj = SystemInfo.query.filter_by(project_id=project_id).order_by(db.desc(SystemInfo.index)).first()
#         return obj.id
#
#     @staticmethod
#     def up_system(id_):
#         obj = SystemInfo.query.filter_by(id=id_).first()
#         if obj and obj.index != 0:
#             pre_obj = SystemInfo.query.filter_by(project_id=obj.project_id, index=obj.index - 1).first()
#             pre_obj = obj_set_value(pre_obj, 'index', obj.index)
#             sh.session.add(pre_obj)
#             obj = obj_set_value(obj, 'index', obj.index - 1)
#             sh.session.add(obj)
#             sh.session.commit()
#
#     @staticmethod
#     def down_system(id_):
#         obj = SystemInfo.query.filter_by(id=id_).first()
#         if obj:
#             next_obj = SystemInfo.query.filter_by(project_id=obj.project_id, index=obj.index + 1).first()
#             if next_obj:
#                 next_obj = obj_set_value(next_obj, 'index', obj.index)
#                 sh.session.add(next_obj)
#                 obj = obj_set_value(obj, 'index', obj.index + 1)
#                 sh.session.add(obj)
#                 sh.session.commit()
#
#
# class ModuleInfoManager(object):
#     @staticmethod
#     def insert_module(**kwargs):
#         obj = ModuleInfo(**kwargs)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def update_module(id_, **kwargs):
#         obj = ModuleInfo.query.filter_by(id=id_).first()
#         for column in kwargs:
#             obj = obj_set_value(obj, column, kwargs[column])
#         # obj.module_name = kwargs.pop('module_name')
#         # obj.test_user = kwargs.pop('test_user', None)
#         # obj.simple_desc = kwargs.pop('simple_desc', None)
#         # obj.system_id = kwargs.pop('system_id', None)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def delete_module(id_):
#         obj = ModuleInfo.query.filter_by(id=id_).first()
#         if obj:
#             sh.session.delete(obj)
#             sh.session.commit()
#
#     @staticmethod
#     def query_module(system_id, module_name):
#         obj = ModuleInfo.query.filter_by(system_id=system_id, module_name=module_name).all()
#         return obj
#
#     @staticmethod
#     def query_module_id(id):
#         obj = ModuleInfo.query.filter_by(id=id).all()
#         return obj
#
#     @staticmethod
#     def query_module_by_id(id_):
#         obj = ModuleInfo.query.filter_by(id=id_).first()
#         return obj
#
#     @staticmethod
#     def query_module_name(name, system_id):
#         obj = ModuleInfo.query.order_by(db.desc(ModuleInfo.create_time)).filter_by(module_name=name, system_id=system_id).first()
#         return obj.id
#
#     @staticmethod
#     def query_all_module(system_id):
#         obj = ModuleInfo.query.filter_by(system_id=system_id).all()
#         return obj
#
#     @staticmethod
#     def is_module_exits(module_name, system_id):
#         obj = ModuleInfo.query.filter_by(module_name=module_name, system_id=system_id).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def delete_module_by_system_id(system_id):
#         """根据system_id删除对应模块"""
#         objs = ModuleInfo.query.filter_by(system_id=system_id).all()
#         if objs:
#             [sh.session.delete(obj) for obj in objs]
#             sh.session.commit()
#
#
# class TestsuiteInfoManager(object):
#     @staticmethod
#     def insert_testsuite(**kwargs):
#         obj = TestsuiteInfo(**kwargs)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def update_testsuite(id_, **kwargs):
#         obj = TestsuiteInfo.query.filter_by(id=id_).first()
#         for column in kwargs:
#             obj = obj_set_value(obj, column, kwargs[column])
#         # obj.testsuite_name = kwargs.pop('testsuite_name')
#         # obj.simple_desc = kwargs.pop('simple_desc', None)
#         # obj.module_id = kwargs.pop('module_id', None)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def delete_testsuite(id_):
#         obj = TestsuiteInfo.query.filter_by(id=id_).first()
#         if obj:
#             sh.session.delete(obj)
#             sh.session.commit()
#
#     @staticmethod
#     def query_all_testsuite(module_id):
#         obj = TestsuiteInfo.query.filter_by(module_id=module_id).all()
#         return obj
#
#     @staticmethod
#     def query_testsuiteid(testsuite_name, module_id):
#         '''导入时：根据用例集名称，模块名称查询是否存在重复的用例集'''
#         obj = TestsuiteInfo.query.filter_by(testsuite_name=testsuite_name, module_id=module_id).first()
#         return obj.id
#
#     @staticmethod
#     def query_testsuite_by_id(id_):
#         obj = TestsuiteInfo.query.filter_by(id=id_).first()
#         return obj
#
#     @staticmethod
#     def is_testsuite_exits(testsuite_name, module_id):
#         obj = TestsuiteInfo.query.filter_by(testsuite_name=testsuite_name, module_id=module_id).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def delete_testsuite_by_module_id(module_id):
#         """根据module_id删除对应测试集"""
#         objs = TestsuiteInfo.query.filter_by(module_id=module_id).all()
#         if objs:
#             [sh.session.delete(obj) for obj in objs]
#             sh.session.commit()
#
#     @staticmethod
#     def query_testsuite_by_projectid(id_):
#         testsuite_list = []
#         system_objs = SystemInfo.query.filter_by(project_id=id_).all()
#         for obj in system_objs:
#             module_objs = ModuleInfo.query.filter_by(system_id=obj.id).all()
#             for obj in module_objs:
#                 testsuites = TestsuiteInfo.query.filter_by(module_id=obj.id).all()
#                 for testsuite in testsuites:
#                     testsuite_list.append(testsuite.id)
#         return testsuite_list
#
#     @staticmethod
#     def get_all_testsuites():
#         return TestsuiteInfo.query.filter_by().all()
#
#
# class TestcaseInfoManager(object):
#     @staticmethod
#     def insert_testcase(**kwargs):
#         testsuite_id = kwargs.get('testsuite_id')
#         pre_obj = TestcaseInfo.query.filter_by(testsuite_id=testsuite_id).order_by(db.desc(TestcaseInfo.index)).first()
#         index = pre_obj.index + 1 if pre_obj else 0
#         kwargs.update({'index': index})
#         obj = TestcaseInfo(**kwargs)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     '''一次commit插入批量case'''
#
#     @staticmethod
#     def insert_testcases(testcases):
#         sh.session.add_all(testcases)
#         sh.session.commit()
#
#     @staticmethod
#     def update_testcase(id_, **kwargs):
#         obj = TestcaseInfo.query.filter_by(id=id_).first()
#         for column in kwargs:
#             obj = obj_set_value(obj, column, kwargs[column])
#         # obj.testcase_name = kwargs.pop('testcase_name')
#         # obj.type = kwargs.pop('type')
#         # obj.include = kwargs.pop('include', None)
#         # obj.request = kwargs.pop('request')
#         # obj.testsuite_id = kwargs.pop('testsuite_id', None)
#         # obj.module_id = kwargs.pop('module_id', None)
#         # obj.system_id = kwargs.pop('system_id', None)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def delete_testcase(id_):
#         obj = TestcaseInfo.query.filter_by(id=id_).first()
#         if obj:
#             to_update_objs = TestcaseInfo.query.filter(
#                 TestcaseInfo.testsuite_id == obj.testsuite_id, TestcaseInfo.index > obj.index
#             ).all()
#             for to_update_obj in to_update_objs:
#                 to_update_obj = obj_set_value(to_update_obj, 'index', to_update_obj.index - 1)
#                 sh.session.add(to_update_obj)
#             sh.session.delete(obj)
#             sh.session.commit()
#
#     @staticmethod
#     def get_testcase(id_):
#         obj = TestcaseInfo.query.filter_by(id=id_).first()
#         return obj
#
#     @staticmethod
#     def get_all_testcases():
#         objs = TestcaseInfo.query.filter_by().all()
#         return objs
#
#     @staticmethod
#     def query_all_testcases_include():
#         return sh.session.query(TestcaseInfo.include).filter().all()
#
#     @staticmethod
#     def is_testcase_id_exist(id_):
#         """判断查询或删除用例时,id是否存在"""
#         if isinstance(id_, list):
#             objs = TestcaseInfo.query.filter(TestcaseInfo.id.in_(id_)).all()
#             if len(id_) == len(objs):
#                 return True
#             else:
#                 return False
#         else:
#             obj = TestcaseInfo.query.filter_by(id=id_).first()
#             if obj:
#                 return True
#             else:
#                 return False
#
#     @staticmethod
#     def query_suite_testcase(testsuite_id, page_no, page_size, testcase_name=None):
#         """获取某一测试用例集下的testcase"""
#
#         if testcase_name:
#             value = '%{0}%'.format(testcase_name)
#             pagination_obj = TestcaseInfo.query.order_by(db.asc(TestcaseInfo.index)).filter \
#                 (TestcaseInfo.testsuite_id == testsuite_id, TestcaseInfo.testcase_name.ilike(value)). \
#                 paginate(page=page_no, per_page=page_size, error_out=False)
#         else:
#             pagination_obj = TestcaseInfo.query.order_by(db.asc(TestcaseInfo.index)).filter \
#                 (TestcaseInfo.testsuite_id == testsuite_id). \
#                 paginate(page=page_no, per_page=page_size, error_out=False)
#         return pagination_obj
#
#     @staticmethod
#     def is_case_exists_by_testsuiteid(testsuite_id):
#         """获取某一测试用例集下的testcase"""
#         obj = TestcaseInfo.query.filter_by(testsuite_id=testsuite_id).order_by(TestcaseInfo.index.asc(), TestcaseInfo.id.asc()).all()
#         return obj
#
#     @staticmethod
#     def is_case_exists_by_moduleid(module_id):
#         """获取某一模块下的testcase"""
#         objs = TestcaseInfo.query.filter_by(module_id=module_id).all()
#         return objs
#
#     @staticmethod
#     def is_case_exists_by_systemid(system_id):
#         """获取某一系统下的testcase"""
#         objs = TestcaseInfo.query.filter_by(system_id=system_id).all()
#         return objs
#
#     @staticmethod
#     def get_no_index_testcases():
#         """获取未index的用例"""
#         objs = TestcaseInfo.query.filter_by(index=None).all()
#         return objs
#
#     @staticmethod
#     def get_testcases_by(**kwargs):
#         """根据条件获取用例s"""
#         objs = TestcaseInfo.query.filter_by(**kwargs).all()
#         return objs
#
#     @staticmethod
#     def get_case_status(id_list):
#         objs = TestcaseInfo.query.filter(TestcaseInfo.id.in_(id_list)).all()
#         return objs
#
#     @staticmethod
#     def get_system_testcases(system_id):
#         """获取某一系统下的所有testcase"""
#         objs = TestcaseInfo.query.filter_by(system_id=system_id).all()
#         return objs
#
#     @staticmethod
#     def get_last_obj_by_testsuite(testsuite_id):
#         return TestcaseInfo.query.filter_by(testsuite_id=testsuite_id).order_by(db.desc(TestcaseInfo.index)).first()
#
#     @staticmethod
#     def up_testcase(id_):
#         obj = TestcaseInfo.query.filter_by(id=id_).first()
#         if obj and obj.index != 0:
#             pre_obj = TestcaseInfo.query.filter_by(testsuite_id=obj.testsuite_id, index=obj.index - 1).first()
#             pre_obj = obj_set_value(pre_obj, 'index', obj.index)
#             sh.session.add(pre_obj)
#             obj = obj_set_value(obj, 'index', obj.index - 1)
#             sh.session.add(obj)
#             sh.session.commit()
#
#     @staticmethod
#     def down_testcase(id_):
#         obj = TestcaseInfo.query.filter_by(id=id_).first()
#         if obj:
#             next_obj = TestcaseInfo.query.filter_by(testsuite_id=obj.testsuite_id, index=obj.index + 1).first()
#             if next_obj:
#                 next_obj = obj_set_value(next_obj, 'index', obj.index)
#                 sh.session.add(next_obj)
#                 obj = obj_set_value(obj, 'index', obj.index + 1)
#                 sh.session.add(obj)
#                 sh.session.commit()
#
#     @staticmethod
#     def index_update_while_remove_testcase(id_):
#         obj = TestcaseInfo.query.filter_by(id=id_).first()
#         if obj:
#             to_update_objs = TestcaseInfo.query.filter(
#                 TestcaseInfo.testsuite_id == obj.testsuite_id, TestcaseInfo.index > obj.index
#             ).all()
#             for to_update_obj in to_update_objs:
#                 to_update_obj = obj_set_value(to_update_obj, 'index', to_update_obj.index - 1)
#                 sh.session.add(to_update_obj)
#             sh.session.commit()
#
#
# class TestReportManager(object):
#     @staticmethod
#     def insert_testreport(**kwargs):
#         obj = TestReport(**kwargs)
#         sh.session.add(obj)
#         try:
#             sh.session.commit()
#             return True
#         except IntegrityError:
#             sh.session.rollback()
#             return False
#
#     @staticmethod
#     def delete_testreport(id_):
#         obj = TestReport.query.filter_by(id=id_).first()
#         if obj:
#             sh.session.delete(obj)
#             sh.session.commit()
#
#     @staticmethod
#     def query_testreport(system_id):
#         obj = TestReport.query.filter_by(system_id=system_id).all()
#         return obj
#
#     @staticmethod
#     def get_next_report_id():
#         """获取test_report表下一个id"""
#         obj = sh.session.query(func.max(TestReport.id)).first()
#         if not obj[0]:
#             return 1
#         return obj[0] + 1
#
#     @staticmethod
#     def update_testreport(id_, **kwargs):
#         obj = TestReport.query.filter_by(id=id_).first()
#         for column in kwargs:
#             obj = obj_set_value(obj, column, kwargs[column])
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def query_testreport_by_id(id_):
#         obj = TestReport.query.filter_by(id=id_).first()
#         return obj
#
#     @staticmethod
#     def query_report_by_executor(executor):
#         obj = TestReport.query.filter_by(executor=executor).order_by(db.desc(TestReport.id)).first()
#         return obj
#
#     @staticmethod
#     def paging_query_reports(page_no, page_size, project_id=None, start_time=None, end_time=None, executor=None):
#         if project_id and start_time and end_time and executor:
#             pagination_obj = TestReport.query.filter(TestReport.create_time.between(start_time, end_time),
#                                                      TestReport.project_id == project_id,
#                                                      TestReport.executor == executor,
#                                                      TestReport.status.in_(('success', 'fail'))).order_by(
#                 db.desc(TestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)
#
#         elif project_id and start_time and end_time:
#             pagination_obj = TestReport.query.filter(TestReport.create_time.between(start_time, end_time),
#                                                      TestReport.project_id == project_id,
#                                                      TestReport.status.in_(('success', 'fail'))).order_by(
#                 db.desc(TestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)
#
#         elif project_id and executor:
#             pagination_obj = TestReport.query.filter(TestReport.project_id == project_id,
#                                                      TestReport.executor == executor,
#                                                      TestReport.status.in_(('success', 'fail'))).order_by(
#                 db.desc(TestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)
#
#         elif start_time and end_time and executor:
#             pagination_obj = TestReport.query.filter(TestReport.create_time.between(start_time, end_time),
#                                                      TestReport.executor == executor,
#                                                      TestReport.status.in_(('success', 'fail'))).order_by(
#                 db.desc(TestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)
#
#         elif project_id:
#             pagination_obj = TestReport.query.filter(TestReport.project_id == project_id,
#                                                      TestReport.status.in_(('success', 'fail'))).order_by(
#                 db.desc(TestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)
#
#         elif start_time and end_time:
#             pagination_obj = TestReport.query.filter(TestReport.create_time.between(start_time, end_time),
#                                                      TestReport.status.in_(('success', 'fail'))).order_by(
#                 db.desc(TestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)
#
#         elif executor:
#             pagination_obj = TestReport.query.filter(TestReport.executor == executor,
#                                                      TestReport.status.in_(('success', 'fail'))).order_by(
#                 db.desc(TestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)
#
#         else:
#             pagination_obj = TestReport.query.filter(TestReport.status.in_(('success', 'fail'))).order_by(
#                 db.desc(TestReport.id)).paginate(page=page_no, per_page=page_size, error_out=False)
#         return pagination_obj
#
#
# class PublicVariableInfoManage(object):
#     @staticmethod
#     def insert_public_variable(**kwargs):
#         """新增变量"""
#         obj = PublicVariableInfo(**kwargs)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def is_variable_name_exist(system_id, variable_name):
#         """判断查询或删除变量时,是否存在"""
#         obj = PublicVariableInfo.query.filter_by(system_id=system_id, variable_name=variable_name).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def public_variable_paginate(page, num, keywords=None):
#         if keywords:
#             value = '%{0}%'.format(keywords)
#             data = PublicVariableInfo.query.order_by(db.desc(PublicVariableInfo.create_time)).filter(
#                 or_(PublicVariableInfo.variable_name.ilike(value),
#                     PublicVariableInfo.vaule.ilike(value),
#                     PublicVariableInfo.type.ilike(value),
#                     PublicVariableInfo.system_id.ilike(value)), ).paginate(page=page, per_page=num, error_out=False)
#         else:
#             data = PublicVariableInfo.query.order_by(db.desc(PublicVariableInfo.create_time)).filter().paginate(
#                 page=page, per_page=num, error_out=False)
#         return data
#
#     @staticmethod
#     def fetch_all_publicvariable():
#         obj = PublicVariableInfo.query.order_by(db.desc(PublicVariableInfo.create_time)).filter().all()
#         return obj
#
#     @staticmethod
#     def get_all_variables():
#         obj = PublicVariableInfo.query.filter().all()
#         return obj
#
#     @staticmethod
#     def query_variable_detail_byname(system_id, variable_name):
#         """根据变量名称获取变量详情"""
#         obj = PublicVariableInfo.query.filter_by(system_id=system_id, variable_name=variable_name).first()
#         return obj
#
#     @staticmethod
#     def query_variable_detail_byid(id_):
#         """根据变量id，返回变量详情"""
#         obj = PublicVariableInfo.query.filter_by(id=id_).first()
#         return obj
#
#     @staticmethod
#     def whether_variable_name_canbeupdated(variable_name, id_, system_id):
#         """判断更改变量名称时,是否被其它变量名称使用"""
#         obj = PublicVariableInfo.query.filter(PublicVariableInfo.id != id_,
#                                               PublicVariableInfo.variable_name == variable_name,
#                                               PublicVariableInfo.system_id == system_id).first()
#         if obj:
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def delete_variable(system_id, variable_name):
#         obj = PublicVariableInfo.query.filter_by(system_id=system_id, variable_name=variable_name).first()
#         if obj:
#             sh.session.delete(obj)
#             sh.session.commit()
#             return True
#         else:
#             return False
#
#     @staticmethod
#     def update_variable(id_, **kwargs):
#         obj = PublicVariableInfo.query.filter_by(id=id_).first()
#         for column in kwargs:
#             obj = obj_set_value(obj, column, kwargs[column])
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def get_variables(id_list):
#         objs = PublicVariableInfo.query.filter(PublicVariableInfo.id.in_(id_list)).all()
#         return objs
#
#     @staticmethod
#     def get_variable(**kwargs):
#         obj = PublicVariableInfo.query.filter_by(**kwargs).first()
#         return obj
#
#
# class TestPlanManager(object):
#     @staticmethod
#     def insert_test_plan(**kwargs):
#         obj = TestPlan(**kwargs)
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def update_test_plan(id_, **kwargs):
#         obj = TestPlan.query.filter_by(id=id_).first()
#         for column in kwargs:
#             obj = obj_set_value(obj, column, kwargs[column])
#         sh.session.add(obj)
#         sh.session.commit()
#
#     @staticmethod
#     def delete_test_plan(id_):
#         obj = TestPlan.query.filter_by(id=id_).first()
#         if obj:
#             sh.session.delete(obj)
#             sh.session.commit()
#
#     @staticmethod
#     def get_test_plan(id_):
#         obj = TestPlan.query.filter_by(id=id_).first()
#         return obj
#
#     @staticmethod
#     def get_test_plan_by_name(plan_name):
#         obj = TestPlan.query.filter_by(plan_name=plan_name).first()
#         return obj
#
#     @staticmethod
#     def paging_query_plans(page_no, page_size, search_keyword=None):
#         if search_keyword:
#             return sh.session.query(
#                 TestPlan.id, TestPlan.plan_name, TestPlan.crontab, TestPlan.simple_desc, TestPlan.creator,
#                 TestPlan.project_id, TestPlan.env_id,
#                 TestPlan.last_modifier, ProjectInfo.project_name, EnvInfo.env_name
#             ).outerjoin(
#                 EnvInfo, EnvInfo.id == TestPlan.env_id
#             ).outerjoin(
#                 ProjectInfo, ProjectInfo.id == TestPlan.project_id
#             ).filter(TestPlan.plan_name.ilike('%{0}%'.format(search_keyword))).order_by(
#                 db.desc(TestPlan.id)).paginate(page=page_no, per_page=page_size, error_out=False)
#         else:
#             return sh.session.query(
#                 TestPlan.id, TestPlan.plan_name, TestPlan.crontab, TestPlan.simple_desc, TestPlan.creator,
#                 TestPlan.project_id, TestPlan.env_id,
#                 TestPlan.last_modifier, ProjectInfo.project_name, EnvInfo.env_name
#             ).outerjoin(
#                 EnvInfo, EnvInfo.id == TestPlan.env_id
#             ).outerjoin(
#                 ProjectInfo, ProjectInfo.id == TestPlan.project_id
#             ).filter().order_by(
#                 db.desc(TestPlan.id)).paginate(page=page_no, per_page=page_size, error_out=False)


class UserManager(object):
    @staticmethod
    def insert_user(**kwargs):
        with SessionHandler() as sh:
            obj = User(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_user(id_, **kwargs):
        with SessionHandler() as sh:
            obj = User.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_user(id_):
        with SessionHandler() as sh:
            obj = User.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_user(id_):
        with SessionHandler() as sh:
            obj = User.query.filter_by(id=id_).first()
            return obj

    @staticmethod
    def get_user_by_username(username):
        with SessionHandler() as sh:
            obj = User.query.filter_by(username=username).first()
            return obj

    @staticmethod
    def get_user_by_nickname(nickname):
        with SessionHandler() as sh:
            obj = User.query.filter_by(nickname=nickname).first()
            return obj

    @staticmethod
    def paging_query_users(page_no, page_size):
        with SessionHandler() as sh:
            pagination_obj = User.query.filter().order_by(db.asc(User.id)).paginate(
                page=page_no, per_page=page_size, error_out=False)
            return pagination_obj

    @staticmethod
    def get_all_username_nickname():
        with SessionHandler() as sh:
            return sh.session.query(
                User.username, User.nickname
            ).filter().all()


class TestcaseTagManager(object):
    @staticmethod
    def get_testcase_tag(id_):
        with SessionHandler() as sh:
            return TestcaseTag.query.filter_by(id=id_).first()

    @staticmethod
    def query_testcase_tag():
        with SessionHandler() as sh:
            return TestcaseTag.query.filter_by().all()

    @staticmethod
    def query_testcase_tags(**kwargs):
        with SessionHandler() as sh:
            return TestcaseTag.query.filter_by(**kwargs).all()

    @staticmethod
    def get_tag_categories():
        with SessionHandler() as sh:
            return sh.session.query(TestcaseTag.tag_category).dinstinct().all()


def stat_api_testcase():
    with SessionHandler() as sh:
        return sh.session.query(
            ApiCompanyInfo.company_name, func.count(ApiTestcaseInfo.id)
        ).outerjoin(
            ApiSystemInfo, ApiCompanyInfo.id == ApiSystemInfo.api_company_id
        ).outerjoin(
            ApiIntfInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
        ).outerjoin(
            ApiTestcaseInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
        ).filter(
            # ApiTestcaseInfo.case_status == '0'
        ).group_by(
            ApiCompanyInfo.id
        ).all()


def get_reuse_group_by_testcase_id(start_date, end_date, intf_id):
    with SessionHandler() as sh:
        return sh.session.query(
            ApiTestcaseInfo.id, ApiTestcaseInfo.testcase_name, func.sum(ApiTestcaseReuseRecord.total_times),
            func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
        ).outerjoin(
            ApiTestcaseReuseRecord, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
        ).filter(
            ApiTestcaseInfo.api_intf_id == intf_id, ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
        ).group_by(
            ApiTestcaseInfo.id
        ).all()


def get_reuse_group_by_intf_id(start_date, end_date, system_id):
    with SessionHandler() as sh:
        return sh.session.query(
            ApiIntfInfo.id, ApiIntfInfo.intf_name, func.sum(ApiTestcaseReuseRecord.total_times),
            func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
        ).outerjoin(
            ApiTestcaseInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
        ).outerjoin(
            ApiTestcaseReuseRecord, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
        ).filter(
            ApiIntfInfo.api_system_id == system_id, ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
        ).group_by(
            ApiIntfInfo.id
        ).all()


def get_reuse_group_by_system_id(start_date, end_date, company_id):
    with SessionHandler() as sh:
        return sh.session.query(
            ApiSystemInfo.id, ApiSystemInfo.system_name, func.sum(ApiTestcaseReuseRecord.total_times),
            func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
        ).outerjoin(
            ApiIntfInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
        ).outerjoin(
            ApiTestcaseInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
        ).outerjoin(
            ApiTestcaseReuseRecord, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
        ).filter(
            ApiSystemInfo.api_company_id == company_id, ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
        ).group_by(
            ApiSystemInfo.id
        ).all()


def get_reuse_group_by_day(start_date, end_date, company_id=None, system_id=None, intf_id=None):
    with SessionHandler() as sh:
        if intf_id:
            return sh.session.query(
                ApiTestcaseReuseRecord.record_date, func.sum(ApiTestcaseReuseRecord.total_times),
                func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
            ).filter(
                ApiTestcaseInfo.api_intf_id == intf_id, ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
            ).group_by(
                ApiTestcaseReuseRecord.record_date
            ).all()
        elif system_id:
            return sh.session.query(
                ApiTestcaseReuseRecord.record_date, func.sum(ApiTestcaseReuseRecord.total_times),
                func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
            ).filter(
                ApiIntfInfo.api_system_id == system_id, ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
            ).group_by(
                ApiTestcaseReuseRecord.record_date
            ).all()
        elif company_id:
            return sh.session.query(
                ApiTestcaseReuseRecord.record_date, func.sum(ApiTestcaseReuseRecord.total_times),
                func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).filter(
                ApiSystemInfo.api_company_id == company_id,
                ApiTestcaseReuseRecord.record_date.between(start_date, end_date),
            ).group_by(
                ApiTestcaseReuseRecord.record_date
            ).all()


def get_reuse_group_by_week(start_date, end_date, company_id=None, system_id=None, intf_id=None):
    with SessionHandler() as sh:
        if intf_id:
            return sh.session.query(
                func.week(ApiTestcaseReuseRecord.record_date), func.sum(ApiTestcaseReuseRecord.total_times),
                func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
            ).filter(
                ApiTestcaseInfo.api_intf_id == intf_id, func.year(ApiTestcaseReuseRecord.record_date) == 2019,
                ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
            ).group_by(
                func.week(ApiTestcaseReuseRecord.record_date)
            ).all()
        elif system_id:
            return sh.session.query(
                func.week(ApiTestcaseReuseRecord.record_date), func.sum(ApiTestcaseReuseRecord.total_times),
                func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
            ).filter(
                ApiIntfInfo.api_system_id == system_id, func.year(ApiTestcaseReuseRecord.record_date) == 2019,
                ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
            ).group_by(
                func.week(ApiTestcaseReuseRecord.record_date)
            ).all()
        elif company_id:
            return sh.session.query(
                func.week(ApiTestcaseReuseRecord.record_date), func.sum(ApiTestcaseReuseRecord.total_times),
                func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).filter(
                ApiSystemInfo.api_company_id == company_id, func.year(ApiTestcaseReuseRecord.record_date) == 2019,
                ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
            ).group_by(
                func.week(ApiTestcaseReuseRecord.record_date)
            ).all()


def get_reuse_group_by_month(start_date, end_date, company_id=None, system_id=None, intf_id=None):
    with SessionHandler() as sh:
        if intf_id:
            return sh.session.query(
                func.month(ApiTestcaseReuseRecord.record_date), func.sum(ApiTestcaseReuseRecord.total_times),
                func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
            ).filter(
                ApiTestcaseInfo.api_intf_id == intf_id, func.year(ApiTestcaseReuseRecord.record_date) == 2019,
                ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
            ).group_by(
                func.month(ApiTestcaseReuseRecord.record_date)
            ).all()
        elif system_id:
            return sh.session.query(
                func.month(ApiTestcaseReuseRecord.record_date), func.sum(ApiTestcaseReuseRecord.total_times),
                func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
            ).filter(
                ApiIntfInfo.api_system_id == system_id, func.year(ApiTestcaseReuseRecord.record_date) == 2019,
                ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
            ).group_by(
                func.month(ApiTestcaseReuseRecord.record_date)
            ).all()
        elif company_id:
            return sh.session.query(
                func.month(ApiTestcaseReuseRecord.record_date), func.sum(ApiTestcaseReuseRecord.total_times),
                func.sum(ApiTestcaseReuseRecord.success_times), func.sum(ApiTestcaseReuseRecord.fail_times)
            ).outerjoin(
                ApiTestcaseInfo, ApiTestcaseInfo.id == ApiTestcaseReuseRecord.api_testcase_id
            ).outerjoin(
                ApiIntfInfo, ApiIntfInfo.id == ApiTestcaseInfo.api_intf_id
            ).outerjoin(
                ApiSystemInfo, ApiSystemInfo.id == ApiIntfInfo.api_system_id
            ).filter(
                ApiSystemInfo.api_company_id == company_id, func.year(ApiTestcaseReuseRecord.record_date) == 2019,
                ApiTestcaseReuseRecord.record_date.between(start_date, end_date)
            ).group_by(
                func.month(ApiTestcaseReuseRecord.record_date)
            ).all()


def obj_set_value(obj, attr, value):
    if value is not None and hasattr(obj, attr):
        setattr(obj, attr, value)
    return obj


class BaseProjectInfoManager(object):
    @staticmethod
    def insert_base_project(**kwargs):
        with SessionHandler() as sh:
            obj = BaseProjectInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_base_project(id_, **kwargs):
        with SessionHandler() as sh:
            obj = BaseProjectInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_base_project(**kwargs):
        with SessionHandler() as sh:
            obj = BaseProjectInfo.query.filter_by(**kwargs).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_project(**kwargs):
        with SessionHandler() as sh:
            obj = BaseProjectInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_all_projects():
        with SessionHandler() as sh:
            objs = BaseProjectInfo.query.filter_by().all()
            return objs

    @staticmethod
    def base_project_info(project_name):
        with SessionHandler() as sh:
            if project_name:
                project_name = '%' + project_name + '%'
                obj = BaseProjectInfo.query.filter(BaseProjectInfo.project_name.like(project_name)).all()
            else:
                obj = BaseProjectInfo.query.all()
            return obj


class BaseSystemInfoManager(object):
    @staticmethod
    def insert_base_system(**kwargs):
        with SessionHandler() as sh:
            obj = BaseSystemInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_base_system(**kwargs):
        with SessionHandler() as sh:
            obj = BaseSystemInfo.query.filter_by(**kwargs).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_system(system_name, project_id):
        with SessionHandler() as sh:
            obj = BaseSystemInfo.query.filter_by(system_name=system_name, project_id=project_id).first()
            return obj

    @staticmethod
    def get_systems(project_id):
        with SessionHandler() as sh:
            return BaseSystemInfo.query.filter_by(project_id=project_id).all()

    @staticmethod
    def get_total_systems():
        with SessionHandler() as sh:
            return BaseSystemInfo.query.filter_by().all()

    @staticmethod
    def get_all_system(project_id):
        with SessionHandler() as sh:
            obj = BaseSystemInfo.query.filter_by(project_id=project_id).all()
            return obj

    @staticmethod
    def query_system(**kwargs):
        with SessionHandler() as sh:
            obj = BaseSystemInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def update_system(**kwargs):
        with SessionHandler() as sh:
            systemId = kwargs.pop('systemId')
            obj = BaseSystemInfo.query.filter_by(id=systemId).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()


class BaseModuleInfoManager(object):
    @staticmethod
    def insert_base_module(**kwargs):
        with SessionHandler() as sh:
            obj = BaseModuleInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_base_module(**kwargs):
        with SessionHandler() as sh:
            obj = BaseModuleInfo.query.filter_by(**kwargs).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def batch_delete_by_module_ids(module_ids):
        with SessionHandler() as sh:
            objs = BaseModuleInfo.query.filter(BaseModuleInfo.id.in_(module_ids)).all()
            if objs:
                [sh.session.delete(obj) for obj in objs]
                sh.session.commit()

    @staticmethod
    def get_module(**kwargs):
        with SessionHandler() as sh:
            obj = BaseModuleInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_modules(**kwargs):
        with SessionHandler() as sh:
            objs = BaseModuleInfo.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_modules_by_module_ids(module_ids):
        with SessionHandler() as sh:
            objs = BaseModuleInfo.query.filter(BaseModuleInfo.id.in_(module_ids)).all()
            return objs


class BaseModuleInfoBakManager(object):
    @staticmethod
    def insert_base_module(**kwargs):
        with SessionHandler() as sh:
            obj = BaseModuleInfoBak(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_base_module(**kwargs):
        with SessionHandler() as sh:
            obj = BaseModuleInfoBak.query.filter_by(**kwargs).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def batch_delete_by_module_ids(module_ids):
        with SessionHandler() as sh:
            objs = BaseModuleInfoBak.query.filter(BaseModuleInfoBak.id.in_(module_ids)).all()
            if objs:
                [sh.session.delete(obj) for obj in objs]
                sh.session.commit()

    @staticmethod
    def get_module(**kwargs):
        with SessionHandler() as sh:
            return BaseModuleInfoBak.query.filter_by(**kwargs).first()

    @staticmethod
    def get_modules(**kwargs):
        with SessionHandler() as sh:
            return BaseModuleInfoBak.query.filter_by(**kwargs).all()


class BaseTestcaseInfoManager(object):
    @staticmethod
    def insert_base_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = BaseTestcaseInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_base_testcase(insert_list):
        with SessionHandler() as sh:
            objs = [BaseTestcaseInfo(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_base_testcase(id_, **kwargs):
        with SessionHandler() as sh:
            obj = BaseTestcaseInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_base_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = BaseTestcaseInfo.query.filter_by(**kwargs).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def batch_delete_by_module_ids(module_ids):
        with SessionHandler() as sh:
            objs = BaseTestcaseInfo.query.filter(BaseTestcaseInfo.module_id.in_(module_ids)).all()
            if objs:
                [sh.session.delete(obj) for obj in objs]
                sh.session.commit()

    @staticmethod
    def get_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = BaseTestcaseInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_all_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = BaseTestcaseInfo.query.filter_by(**kwargs).all()
            return obj

    @staticmethod
    def get_testcases_in_module_ids(module_ids):
        with SessionHandler() as sh:
            objs = BaseTestcaseInfo.query.filter(BaseTestcaseInfo.module_id.in_(module_ids)).all()
            return objs

    @staticmethod
    def query_all_basecase(module_id, page_no, page_size, testcase_name=None):
        """获取某一模块下的testcase"""
        with SessionHandler() as sh:
            if testcase_name:
                value = '%{0}%'.format(testcase_name)
                pagination_obj = BaseTestcaseInfo.query.order_by(db.asc(BaseTestcaseInfo.id)).filter(
                    BaseTestcaseInfo.module_id == module_id, BaseTestcaseInfo.testcase_name.ilike(value)).paginate(
                    page=page_no, per_page=page_size, error_out=False)
            else:
                pagination_obj = BaseTestcaseInfo.query.order_by(db.asc(BaseTestcaseInfo.id)).filter(
                    BaseTestcaseInfo.module_id == module_id).paginate(page=page_no, per_page=page_size, error_out=False)
            return pagination_obj

    @staticmethod
    def count_testcases(**kwargs):
        with SessionHandler() as sh:
            return sh.session.query(func.count(BaseTestcaseInfo.id)).filter_by(**kwargs).first()

    @staticmethod
    def group_testcases_by_module_id():
        with SessionHandler() as sh:
            return sh.session.query(BaseTestcaseInfo.module_id, func.count(BaseTestcaseInfo.id)).filter_by().group_by(
                BaseTestcaseInfo.module_id).all()


class BaseTestcaseInfoBakManager(object):
    @staticmethod
    def insert_base_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = BaseTestcaseInfoBak(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_base_testcase(insert_list):
        with SessionHandler() as sh:
            objs = [BaseTestcaseInfoBak(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def delete_base_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = BaseTestcaseInfoBak.query.filter_by(**kwargs).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def batch_delete_by_module_ids(module_ids):
        with SessionHandler() as sh:
            objs = BaseTestcaseInfoBak.query.filter(BaseTestcaseInfoBak.module_id.in_(module_ids)).all()
            if objs:
                [sh.session.delete(obj) for obj in objs]
                sh.session.commit()

    @staticmethod
    def get_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = BaseTestcaseInfoBak.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_all_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = BaseTestcaseInfoBak.query.filter_by(**kwargs).all()
            return obj

    @staticmethod
    def get_testcases_in_module_ids(module_ids):
        with SessionHandler() as sh:
            objs = BaseTestcaseInfo.query.filter(BaseTestcaseInfo.module_id.in_(module_ids)).all()
            return objs

    @staticmethod
    def query_all_basecase(module_id, page_no, page_size, testcase_name=None):
        """获取某一模块下的testcase"""
        with SessionHandler() as sh:
            if testcase_name:
                value = '%{0}%'.format(testcase_name)
                pagination_obj = BaseTestcaseInfoBak.query.order_by(db.asc(BaseTestcaseInfoBak.id)).filter(
                    BaseTestcaseInfoBak.module_id == module_id,
                    BaseTestcaseInfoBak.testcase_name.ilike(value)).paginate(
                    page=page_no, per_page=page_size, error_out=False)
            else:
                pagination_obj = BaseTestcaseInfoBak.query.order_by(db.asc(BaseTestcaseInfoBak.id)).filter(
                    BaseTestcaseInfoBak.module_id == module_id).paginate(page=page_no, per_page=page_size,
                                                                         error_out=False)
            return pagination_obj

    @staticmethod
    def count_testcases(**kwargs):
        with SessionHandler() as sh:
            return sh.session.query(func.count(BaseTestcaseInfoBak.id)).filter_by(**kwargs).first()

    @staticmethod
    def group_testcases_by_module_id():
        with SessionHandler() as sh:
            return sh.session.query(BaseTestcaseInfoBak.module_id, func.count(BaseTestcaseInfoBak.id)).filter_by(
            ).group_by(BaseTestcaseInfoBak.module_id).all()


class BaseJobHistoryManager(object):
    @staticmethod
    def insert_job_history(**kwargs):
        with SessionHandler() as sh:
            obj = BaseJobHistory(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def get_last_record():
        with SessionHandler() as sh:
            obj = sh.session.query(func.max(BaseJobHistory.create_time).label("last_time")).first()
            return obj


class UiProjectInfoManager(object):
    @staticmethod
    def insert_ui_project(**kwargs):
        with SessionHandler() as sh:
            obj = UiProjectInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def ui_project_info(project_name):
        with SessionHandler() as sh:
            if project_name:
                project_name = '%' + project_name + '%'
                obj = UiProjectInfo.query.filter(UiProjectInfo.project_name.like(project_name)).all()
            else:
                obj = UiProjectInfo.query.all()
            return obj


class UiSystemInfoManager(object):
    @staticmethod
    def insert_ui_system(**kwargs):
        with SessionHandler() as sh:
            obj = UiSystemInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_ui_system(**kwargs):
        with SessionHandler() as sh:
            obj = UiSystemInfo.query.filter_by(**kwargs).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_all_system(project_id):
        with SessionHandler() as sh:
            obj = UiSystemInfo.query.filter_by(project_id=project_id).all()
            return obj

    @staticmethod
    def query_system(**kwargs):
        with SessionHandler() as sh:
            obj = UiSystemInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def update_system(**kwargs):
        with SessionHandler() as sh:
            systemId = kwargs.pop('systemId')
            obj = UiSystemInfo.query.filter_by(id=systemId).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()


class UiModuleInfoManager(object):
    @staticmethod
    def insert_ui_module(**kwargs):
        with SessionHandler() as sh:
            obj = UiModuleInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_ui_module(**kwargs):
        with SessionHandler() as sh:
            obj = UiModuleInfo.query.filter_by(**kwargs).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_module(**kwargs):
        with SessionHandler() as sh:
            obj = UiModuleInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_modules(**kwargs):
        with SessionHandler() as sh:
            objs = UiModuleInfo.query.filter_by(**kwargs).all()
            return objs


class UICasePageInfoManager(object):
    @staticmethod
    def insert_ui_page(**kwargs):
        with SessionHandler() as sh:
            obj = UICasePageInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def query_ui_page(**kwargs):
        with SessionHandler() as sh:
            obj = UICasePageInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def query_ui_pages(**kwargs):
        with SessionHandler() as sh:
            obj = UICasePageInfo.query.filter_by(**kwargs).all()
            return obj


class UICasePageObjectInfoManage(object):
    @staticmethod
    def insert_ui_pageobject(**kwargs):
        with SessionHandler() as sh:
            obj = UICasePageObjectInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def query_paget_object(**kwargs):
        with SessionHandler() as sh:
            obj = UICasePageObjectInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def delete_paget_object(**kwargs):
        with SessionHandler() as sh:
            obj = UICasePageObjectInfo.query.filter_by(**kwargs).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def query_all_page_object(**kwargs):
        with SessionHandler() as sh:
            obj = UICasePageObjectInfo.query.filter_by(**kwargs).all()
            return obj

    @staticmethod
    def eidt_page_object(**kwargs):
        with SessionHandler() as sh:
            objectId = kwargs.pop('object_id')
            obj = UICasePageObjectInfo.query.filter_by(id=objectId).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()


class UITestCaseInfoManage(object):
    @staticmethod
    def insert_ui_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = UiTestcaseInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_ui_testcase(id_, **kwargs):
        with SessionHandler() as sh:
            obj = UiTestcaseInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def query_ui_testcase(**kwargs):
        with SessionHandler() as sh:
            obj = UiTestcaseInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def query_ui_testcases(**kwargs):
        with SessionHandler() as sh:
            obj = UiTestcaseInfo.query.filter_by(**kwargs).all()
            return obj

    @staticmethod
    def delete_ui_testcase(id_):
        with SessionHandler() as sh:
            obj = UiTestcaseInfo.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()


class ApiIntfDefaultRequestManager(object):
    @staticmethod
    def insert_request(**kwargs):
        with SessionHandler() as sh:
            obj = ApiIntfDefaultRequest(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_request(insert_list):
        with SessionHandler() as sh:
            objs = [ApiIntfDefaultRequest(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def delete_request(id_):
        with SessionHandler() as sh:
            obj = ApiIntfDefaultRequest.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def delete_request_by_intf_id(intf_id):
        with SessionHandler() as sh:
            obj = ApiIntfDefaultRequest.query.filter_by(api_intf_id=intf_id).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def update_request(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiIntfDefaultRequest.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def get_request(**kwargs):
        with SessionHandler() as sh:
            obj = ApiIntfDefaultRequest.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def update_request_by_intf_id(intf_id, **kwargs):
        with SessionHandler() as sh:
            obj = ApiIntfDefaultRequest.query.filter_by(api_intf_id=intf_id).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()


class ApiTestcaseReuseRecordManager(object):
    @staticmethod
    def insert_record(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseReuseRecord(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_record(insert_list):
        with SessionHandler() as sh:
            objs = [ApiTestcaseReuseRecord(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_record(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseReuseRecord.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_record(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseReuseRecord.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_record(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseReuseRecord.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_records(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTestcaseReuseRecord.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_recent_summary(testcase_id, start_date):
        with SessionHandler() as sh:
            return sh.session.query(
                func.sum(ApiTestcaseReuseRecord.total_times), func.sum(ApiTestcaseReuseRecord.success_times),
            ).filter(
                ApiTestcaseReuseRecord.api_testcase_id == testcase_id,
                ApiTestcaseReuseRecord.is_setup == 0, ApiTestcaseReuseRecord.record_date > start_date
            ).first()


class ApiTaskInfoManager(object):
    @staticmethod
    def insert_task(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTaskInfo(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_task(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiTaskInfo.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_task(id_):
        with SessionHandler() as sh:
            obj = ApiTaskInfo.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_task(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTaskInfo.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_tasks(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTaskInfo.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_tasks_paginate(page, num, company_id, keywords=None):
        with SessionHandler() as sh:
            task_type_list = [1, 2]
            if keywords:
                value = '%{0}%'.format(keywords)
                objs = ApiTaskInfo.query.order_by(db.desc(ApiTaskInfo.create_time)).filter(
                    ApiTaskInfo.api_company_id == company_id,
                    ApiTaskInfo.task_type.in_(task_type_list),
                    ApiTaskInfo.task_name.ilike(value)).paginate(page=page, per_page=num, error_out=False)
            else:
                objs = ApiTaskInfo.query.order_by(db.desc(ApiTaskInfo.create_time)).filter(
                    ApiTaskInfo.api_company_id == company_id,
                    ApiTaskInfo.task_type.in_(task_type_list)).paginate(
                    page=page, per_page=num, error_out=False)
            return objs

    @staticmethod
    def get_smoking_tasks_paginate(page, num, company_id, keywords=None):
        with SessionHandler() as sh:
            if keywords:
                value = '%{0}%'.format(keywords)
                objs = ApiTaskInfo.query.order_by(
                    db.desc(func.coalesce(ApiTaskInfo.update_time, ApiTaskInfo.create_time))).filter(
                    ApiTaskInfo.api_company_id == company_id,
                    ApiTaskInfo.task_type == 3,
                    ApiTaskInfo.task_name.ilike(value)).paginate(page=page, per_page=num, error_out=False)
            else:
                objs = ApiTaskInfo.query.order_by(db.desc(func.coalesce(ApiTaskInfo.update_time, ApiTaskInfo.create_time))).filter(
                    ApiTaskInfo.api_company_id == company_id, ApiTaskInfo.task_type == 3).paginate(
                    page=page, per_page=num, error_out=False)
            return objs

    @staticmethod
    def get_regression_tasks_paginate(page, num, company_id, keywords=None):
        with SessionHandler() as sh:
            if keywords:
                value = '%{0}%'.format(keywords)
                objs = ApiTaskInfo.query.order_by(db.desc(func.coalesce(ApiTaskInfo.update_time, ApiTaskInfo.create_time))).filter(
                    ApiTaskInfo.api_company_id == company_id,
                    ApiTaskInfo.task_type == 4,
                    ApiTaskInfo.task_name.ilike(value)).paginate(page=page, per_page=num, error_out=False)
            else:
                objs = ApiTaskInfo.query.order_by(db.desc(func.coalesce(ApiTaskInfo.update_time, ApiTaskInfo.create_time))).filter(
                    ApiTaskInfo.api_company_id == company_id, ApiTaskInfo.task_type == 4).paginate(
                    page=page, per_page=num, error_out=False)
            return objs

    @staticmethod
    def get_tasks_in_project_id_list(project_id_list):
        with SessionHandler() as sh:
            objs = ApiTaskInfo.query.filter(
                ApiTaskInfo.api_project_id.in_(project_id_list)
            ).order_by(db.desc(ApiTaskInfo.id)).all()
            return objs


class CeleryTaskRecordManager(object):
    @staticmethod
    def insert_celery(**kwargs):
        with SessionHandler() as sh:
            obj = CeleryTaskRecord(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def batch_insert_celery(insert_list):
        with SessionHandler() as sh:
            objs = [CeleryTaskRecord(**kw) for kw in insert_list]
            sh.session.bulk_save_objects(objs)
            sh.session.commit()

    @staticmethod
    def update_celery(id_, **kwargs):
        with SessionHandler() as sh:
            obj = CeleryTaskRecord.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_celery_by_task_no(celery_task_no, **kwargs):
        with SessionHandler() as sh:
            obj = CeleryTaskRecord.query.filter_by(celery_task_no=celery_task_no).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_celery(id_):
        with SessionHandler() as sh:
            obj = CeleryTaskRecord.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_celery(**kwargs):
        with SessionHandler() as sh:
            obj = CeleryTaskRecord.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_celeries(**kwargs):
        with SessionHandler() as sh:
            objs = CeleryTaskRecord.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_callback_celery(api_run_task_result_id):
        with SessionHandler() as sh:
            callback_keywords = ['WAITING', 'RUNNING', 'ERROR', 'SUCCESS']
            obj = CeleryTaskRecord.query.filter(
                CeleryTaskRecord.api_run_task_result_id == api_run_task_result_id,
                CeleryTaskRecord.celery_task_status.in_(callback_keywords)
            ).first()
            return obj


class ApiRunTaskResultManager(object):
    @staticmethod
    def insert_result(**kwargs):
        with SessionHandler() as sh:
            obj = ApiRunTaskResult(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_result(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiRunTaskResult.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_result(id_):
        with SessionHandler() as sh:
            obj = ApiRunTaskResult.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_result(**kwargs):
        with SessionHandler() as sh:
            obj = ApiRunTaskResult.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_results(**kwargs):
        with SessionHandler() as sh:
            objs = ApiRunTaskResult.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_results_order_by_id_desc(**kwargs):
        with SessionHandler() as sh:
            objs = ApiRunTaskResult.query.filter_by(**kwargs).order_by(
                db.desc(ApiRunTaskResult.id)).limit(10).all()
            return objs

    @staticmethod
    def get_next_result_id():
        with SessionHandler() as sh:
            """获取表下一个id"""
            obj = sh.session.query(func.max(ApiRunTaskResult.id)).first()
            if not obj[0]:
                return 1
            return obj[0] + 1

    @staticmethod
    def get_last_result_by_task_id(task_id):
        with SessionHandler() as sh:
            obj = ApiRunTaskResult.query.filter(ApiRunTaskResult.api_task_id == task_id).order_by(
                db.desc(ApiRunTaskResult.create_time)).first()
            return obj

    @staticmethod
    def get_results_group_by_run_date_in_company(company_id, recent_days):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiRunTaskResult.run_date, func.count(ApiRunTaskResult.id), func.sum(ApiRunTaskResult.total_cases),
                func.sum(ApiRunTaskResult.not_run_cases), func.sum(ApiRunTaskResult.run_cases),
                func.sum(ApiRunTaskResult.success_cases), func.sum(ApiRunTaskResult.fail_cases),
            ).outerjoin(
                ApiTaskInfo, ApiTaskInfo.id == ApiRunTaskResult.api_task_id
            ).outerjoin(
                ApiProjectInfo, ApiProjectInfo.id == ApiTaskInfo.api_project_id
            ).filter(
                ApiProjectInfo.api_company_id == company_id
            ).group_by(
                ApiRunTaskResult.run_date
            ).order_by(
                db.desc(ApiRunTaskResult.run_date)
            ).limit(int(recent_days))

    @staticmethod
    def get_results_group_by_run_date_in_company_ignore_project(company_id, recent_days):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiRunTaskResult.run_date, func.count(ApiRunTaskResult.id), func.sum(ApiRunTaskResult.total_cases),
                func.sum(ApiRunTaskResult.not_run_cases), func.sum(ApiRunTaskResult.run_cases),
                func.sum(ApiRunTaskResult.success_cases), func.sum(ApiRunTaskResult.fail_cases),
            ).outerjoin(
                ApiTaskInfo, ApiTaskInfo.id == ApiRunTaskResult.api_task_id
            ).filter(
                ApiTaskInfo.api_company_id == company_id
            ).group_by(
                ApiRunTaskResult.run_date
            ).order_by(
                db.desc(ApiRunTaskResult.run_date)
            ).limit(int(recent_days))

    @staticmethod
    def get_results_by_run_date_in_company(company_id, run_date):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiRunTaskResult.id, ApiTaskInfo.task_name, ApiTaskInfo.task_type,
                ApiProjectInfo.project_name, ApiRunTaskResult.total_cases, ApiRunTaskResult.not_run_cases,
                ApiRunTaskResult.run_cases, ApiRunTaskResult.success_cases, ApiRunTaskResult.fail_cases,
                ApiRunTaskResult.start_time, ApiRunTaskResult.end_time, ApiRunTaskResult.creator,
                EnvInfo.env_name
            ).outerjoin(
                ApiTaskInfo, ApiTaskInfo.id == ApiRunTaskResult.api_task_id
            ).outerjoin(
                ApiProjectInfo, ApiProjectInfo.id == ApiTaskInfo.api_project_id
            ).outerjoin(
                EnvInfo, EnvInfo.id == ApiRunTaskResult.run_env_id
            ).filter(
                ApiProjectInfo.api_company_id == company_id, ApiRunTaskResult.run_date == run_date
            ).order_by(
                db.desc(ApiRunTaskResult.start_time)
            ).all()

    @staticmethod
    def get_results_by_run_date_in_company_ignore_project(company_id, run_date):
        with SessionHandler() as sh:
            return sh.session.query(
                ApiRunTaskResult.id, ApiTaskInfo.task_name, ApiTaskInfo.task_type,
                ApiTaskInfo.api_project_id, ApiRunTaskResult.total_cases, ApiRunTaskResult.not_run_cases,
                ApiRunTaskResult.run_cases, ApiRunTaskResult.success_cases, ApiRunTaskResult.fail_cases,
                ApiRunTaskResult.start_time, ApiRunTaskResult.end_time, ApiRunTaskResult.creator,
                EnvInfo.env_name
            ).outerjoin(
                ApiTaskInfo, ApiTaskInfo.id == ApiRunTaskResult.api_task_id
            ).outerjoin(
                EnvInfo, EnvInfo.id == ApiRunTaskResult.run_env_id
            ).filter(
                ApiTaskInfo.api_company_id == company_id, ApiRunTaskResult.run_date == run_date,
                ApiTaskInfo.api_project_id == 0
            ).order_by(
                db.desc(ApiRunTaskResult.start_time)
            ).all()


class GitDiffVersionManager(object):
    @staticmethod
    def insert_git_diff_version(**kwargs):
        with SessionHandler() as sh:
            obj = GitDiffVersion(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_git_diff_version(id_, **kwargs):
        with SessionHandler() as sh:
            obj = GitDiffVersion.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_git_diff_version_by_seq_no(seq_no_, **kwargs):
        with SessionHandler() as sh:
            obj = GitDiffVersion.query.filter_by(seq_no=seq_no_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_git_diff_version(id_):
        with SessionHandler() as sh:
            obj = GitDiffVersion.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()
                sh.session.close()

    @staticmethod
    def delete_git_diff_version_by_obj(obj):
        with SessionHandler() as sh:
            if obj:
                sh.session.delete(obj)
                sh.session.commit()

    @staticmethod
    def get_git_diff_version(**kwargs):
        with SessionHandler() as sh:
            obj = GitDiffVersion.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_git_diff_versions(**kwargs):
        with SessionHandler() as sh:
            objs = GitDiffVersion.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_git_diff_versions_special(seq_no_, api_task_id_):
        with SessionHandler() as sh:
            objs = GitDiffVersion.query.filter(
                GitDiffVersion.seq_no != seq_no_ and GitDiffVersion.api_task_id == api_task_id_).all()
            return objs


class GenerateDataRecordManager(object):
    @staticmethod
    def insert_record(**kwargs):
        with SessionHandler() as sh:
            obj = GenerateDataRecord(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def get_record(**kwargs):
        with SessionHandler() as sh:
            obj = GenerateDataRecord.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_records(**kwargs):
        with SessionHandler() as sh:
            objs = GenerateDataRecord.query.filter_by(**kwargs).all()
            return objs

    @staticmethod
    def get_records_between(start, end):
        with SessionHandler() as sh:
            return sh.session.query(
                GenerateDataRecord.mobile_no
            ).filter(
                GenerateDataRecord.record_date.between(start, end)
            ).all()


class ApiTestcaseMainCustomFlowManager(object):
    @staticmethod
    def insert_flow(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseMainCustomFlow(**kwargs)
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def update_flow(id_, **kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseMainCustomFlow.query.filter_by(id=id_).first()
            for column in kwargs:
                obj = obj_set_value(obj, column, kwargs[column])
            sh.session.add(obj)
            sh.session.commit()

    @staticmethod
    def delete_flow(id_):
        with SessionHandler() as sh:
            obj = ApiTestcaseMainCustomFlow.query.filter_by(id=id_).first()
            if obj:
                sh.session.delete(obj)
                sh.session.commit()
                sh.session.close()

    @staticmethod
    def get_flow(**kwargs):
        with SessionHandler() as sh:
            obj = ApiTestcaseMainCustomFlow.query.filter_by(**kwargs).first()
            return obj

    @staticmethod
    def get_flows(**kwargs):
        with SessionHandler() as sh:
            objs = ApiTestcaseMainCustomFlow.query.filter_by(**kwargs).all()
            return objs


if __name__ == '__main__':
    pass
