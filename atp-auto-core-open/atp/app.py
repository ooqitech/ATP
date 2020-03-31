# -*- coding:utf-8 -*-

from flask import Flask
from flask_restful import Api
from atp.extensions import celery, db
from atp.config.load_config import load_config
from atp.env import RUNNING_ENV


def create_app():
    app = Flask('atp')
    current_config = load_config(RUNNING_ENV)
    app.config.from_object(current_config)
    # with app.app_context():
    db.init_app(app)
    celery.init_app(app)

    from .views import (
        env, Env,
        project, Project,
        file, File,
        support, Support,
        user, User,
        stat, Stat,
        tag, Tag,
        run_ui, RunUiTestCase,
        download, Download,
        page, Page,
        pageobject, PageObject,
        ui_testcase, UiTestCase,
        api_company, ApiCompany,
        api_system, ApiSystem,
        api_intf, ApiIntf,
        api_testcase, ApiTestcase,
        api_project, ApiProject,
        api_run, ApiRun,
        api_public_variable, ApiPublicVariable,
        api_report, ApiReport,
        api_product_line, ApiProductLine,
        api_testcase_main, ApiTestcaseMain,
        api_task, ApiTask,
        call_back, CallBack,
        api_push_log, ApiPushLog,
        testcase, Testcase,
    )
    app.register_blueprint(env)
    app.register_blueprint(project)
    app.register_blueprint(file)
    app.register_blueprint(support)
    app.register_blueprint(user)
    app.register_blueprint(stat)
    app.register_blueprint(tag)
    app.register_blueprint(run_ui)
    app.register_blueprint(download)
    app.register_blueprint(page)
    app.register_blueprint(pageobject)
    app.register_blueprint(ui_testcase)
    app.register_blueprint(api_company)
    app.register_blueprint(api_system)
    app.register_blueprint(api_intf)
    app.register_blueprint(api_testcase)
    app.register_blueprint(api_project)
    app.register_blueprint(api_run)
    app.register_blueprint(api_public_variable)
    app.register_blueprint(api_report)
    app.register_blueprint(api_product_line)
    app.register_blueprint(api_testcase_main)
    app.register_blueprint(api_task)
    app.register_blueprint(call_back)
    app.register_blueprint(api_push_log)
    app.register_blueprint(testcase)

    view = Api(app)
    view.add_resource(Env, '/atp/auto/env/<action>')
    view.add_resource(Project, '/atp/auto/project/<action>')
    view.add_resource(File, '/atp/auto/file/<action>')
    view.add_resource(Support, '/atp/auto/support/<action>')
    # view.add_resource(TestPlan, '/atp/auto/testPlan/<action>')
    # view.add_resource(Report, '/atp/auto/report/<action>')
    view.add_resource(User, '/atp/auto/user/<action>')
    view.add_resource(Stat, '/atp/auto/stat/<action>')
    view.add_resource(Tag, '/atp/auto/tag/<action>')
    view.add_resource(RunUiTestCase, '/atp/auto/run_ui')
    view.add_resource(Download, '/atp/auto/download/<action>')
    view.add_resource(Page, '/atp/auto/page/<action>')
    view.add_resource(PageObject, '/atp/auto/pageobject/<action>')
    view.add_resource(UiTestCase, '/atp/auto/uitestcase/<action>')
    view.add_resource(ApiCompany, '/atp/auto/apiCompany/<action>')
    view.add_resource(ApiSystem, '/atp/auto/apiSystem/<action>')
    view.add_resource(ApiIntf, '/atp/auto/apiIntf/<action>')
    view.add_resource(ApiTestcase, '/atp/auto/apiTestcase/<action>')
    view.add_resource(ApiProject, '/atp/auto/apiProject/<action>')
    view.add_resource(ApiRun, '/atp/auto/apiRun')
    view.add_resource(ApiPublicVariable, '/atp/auto/apiPublicVariable/<action>')
    view.add_resource(ApiReport, '/atp/auto/apiReport/<action>')
    view.add_resource(ApiProductLine, '/atp/auto/apiProductLine/<action>')
    view.add_resource(ApiTestcaseMain, '/atp/auto/apiTestcaseMain/<action>')
    view.add_resource(ApiTask, '/atp/auto/apiTask/<action>')
    view.add_resource(CallBack, '/atp/auto/callBack/<action>')
    view.add_resource(ApiPushLog, '/atp/auto/apiPushLog/<action>')
    view.add_resource(Testcase, '/atp/auto/testcase/<action>')

    # configure/initialize all your extensions

    # app.app_context().push()
    return app
