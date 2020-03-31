# -*- coding:utf-8 -*-

from atp.extensions import db


class EnvInfo(db.Model):
    __tablename__ = 'api_env_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    env_name = db.Column(db.String(50), nullable=False, unique=True, comment='环境名称')
    base_host = db.Column(db.String(50), comment='基础host地址')
    dubbo_zookeeper = db.Column(db.String(50), comment='zookeeper地址')
    mq_key = db.Column(db.String(100), comment='mq相关配置')
    db_connect = db.Column(db.String(200), comment='数据库配置')
    remote_host = db.Column(db.String(50), comment='远程服务地址')
    disconf_host = db.Column(db.String(50), comment='disconf地址')
    redis_connect = db.Column(db.String(200), comment='redis地址')
    simple_desc = db.Column(db.String(50), comment='描述信息')
    creator = db.Column(db.String(100), comment='创建人')
    last_modifier = db.Column(db.String(100), comment='最后修改人')
    server_default_user = db.Column(db.String(200), comment='应用服务器默认用户信息')
    server_app_map = db.Column(db.String(1000), comment='应用服务器ip和应用名MAP')

    def __repr__(self):
        return '<EnvInfo %r, id %r>' % (self.env_name, self.id)



class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    username = db.Column(db.String(100), nullable=False, unique=True, comment='用户名')
    password = db.Column(db.String(50), nullable=False, comment='密码')
    nickname = db.Column(db.String(50), nullable=False, comment='昵称（中文名）')
    level = db.Column(db.Integer, comment='权限等级 # '
                                          '0:Admin '
                                          '10:Master '
                                          '20: Developer '
                                          '25: LimitDeveloper '
                                          '30: Reporter(unauthorized Developer) '
                                          '35: Reporter(unauthorized LimitDeveloper) '
                                          '99: Guest')
    user_status = db.Column(db.Integer, default=1, nullable=False, comment='用户认证状态 # 0:已认证  1:未认证')

    def __repr__(self):
        return '<User %r, id %r>' % (self.username, self.id)


class TestcaseTag(db.Model):
    __tablename__ = 'api_testcase_tag'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    tag_name = db.Column(db.String(100), nullable=False, comment='标签名称')
    tag_category = db.Column(db.String(50), nullable=False, comment='标签类别')
    is_for_task = db.Column(db.Integer, comment='测试任务查询时是否展示 0:否 1:是')

    def __repr__(self):
        return '<TestcaseTag %r, id %r>' % (self.tag_name, self.id)



class BaseProjectInfo(db.Model):
    __tablename__ = 'base_project_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    project_name = db.Column(db.String(50), nullable=False, comment='业务项目名')

    def __repr__(self):
        return '<BaseProjectInfo %r, id %r>' % (self.project_name, self.id)


class BaseSystemInfo(db.Model):
    __tablename__ = 'base_system_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    system_name = db.Column(db.String(50), nullable=False, comment='业务系统名')
    project_id = db.Column(db.Integer, comment='业务项目id')
    base_host = db.Column(db.String(50), comment='（已废弃）')
    remote_host = db.Column(db.String(50), comment='（已废弃）')

    def __repr__(self):
        return '<BaseSystemInfo %r, id %r>' % (self.system_name, self.id)


class BaseModuleInfoBak(db.Model):
    __tablename__ = 'base_module_info_bak'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=db.func.now())
    update_time = db.Column(db.DateTime, onupdate=db.func.now())
    module_name = db.Column(db.String(80), nullable=False)
    system_id = db.Column(db.Integer)
    parent_module_id = db.Column(db.Integer)

    def __repr__(self):
        return '<BaseModuleInfoBak %r, id %r>' % (self.module_name, self.id)


class BaseTestcaseInfoBak(db.Model):
    __tablename__ = 'base_testcase_info_bak'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=db.func.now())
    update_time = db.Column(db.DateTime, onupdate=db.func.now())
    module_id = db.Column(db.Integer)
    testcase_name = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.String(2000))
    test_type = db.Column(db.String(100))
    req_num = db.Column(db.String(100))

    def __repr__(self):
        return '<BaseTestcaseInfoBak %r, id %r>' % (self.testcase_name, self.id)


class BaseModuleInfo(db.Model):
    __tablename__ = 'base_module_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    module_name = db.Column(db.String(80), nullable=False, comment='业务模块名')
    system_id = db.Column(db.Integer, comment='业务系统id')
    parent_module_id = db.Column(db.Integer, comment='父节点id')

    def __repr__(self):
        return '<BaseModuleInfo %r, id %r>' % (self.module_name, self.id)


class BaseTestcaseInfo(db.Model):
    __tablename__ = 'base_testcase_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    module_id = db.Column(db.Integer, comment='业务模块id')
    testcase_name = db.Column(db.String(100), nullable=False, comment='业务用例标题')
    detail = db.Column(db.String(4000), comment='业务用例详细')
    test_type = db.Column(db.String(100), comment='测试类型 # 功能/')
    req_num = db.Column(db.String(100), comment='需求编号')

    def __repr__(self):
        return '<BaseTestcaseInfo %r, id %r>' % (self.testcase_name, self.id)


class BaseJobHistory(db.Model):
    __tablename__ = 'base_job_history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    summary = db.Column(db.String(5000), comment='job汇总信息')
    is_success = db.Column(db.Integer, comment='是否成功 # 0:失败 1:成功')
    is_update = db.Column(db.Integer, comment='是否更新 # 0:否 1:是')
    error_msg = db.Column(db.String(200), comment='错误信息')

    def __repr__(self):
        return '<BaseJobHistory, id %r>' % self.id


class UiProjectInfo(db.Model):
    __tablename__ = 'ui_project_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=db.func.now())
    update_time = db.Column(db.DateTime, onupdate=db.func.now())
    project_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<UiProjectInfo %r, id %r>' % (self.project_name, self.id)


class UiSystemInfo(db.Model):
    __tablename__ = 'ui_system_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=db.func.now())
    update_time = db.Column(db.DateTime, onupdate=db.func.now())
    system_name = db.Column(db.String(50), nullable=False)
    project_id = db.Column(db.Integer)
    base_host = db.Column(db.String(50))
    system_type= db.Column(db.String(50))
    remote_host = db.Column(db.String(50))

    def __repr__(self):
        return '<UiSystemInfo %r, id %r>' % (self.system_name, self.id)


class UiModuleInfo(db.Model):
    __tablename__ = 'ui_module_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=db.func.now())
    update_time = db.Column(db.DateTime, onupdate=db.func.now())
    module_name = db.Column(db.String(80), nullable=False)
    system_id = db.Column(db.Integer)
    parent_module_id = db.Column(db.Integer)

    def __repr__(self):
        return '<UiModuleInfo %r, id %r>' % (self.module_name, self.id)


class UiTestcaseInfo(db.Model):
    __tablename__ = 'ui_testcase_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=db.func.now())
    update_time = db.Column(db.DateTime, onupdate=db.func.now())
    module_id = db.Column(db.Integer)
    testcase_name = db.Column(db.String(100), nullable=False)
    simple_desc = db.Column(db.String(100))
    inlude = db.Column(db.String(100))
    request = db.Column(db.String(2000))
    req_num = db.Column(db.String(100))

    def __repr__(self):
        return '<UiTestcaseInfo %r, id %r>' % (self.testcase_name, self.id)


class UICasePageInfo(db.Model):
    __tablename__ = 'ui_case_page_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=db.func.now())
    update_time = db.Column(db.DateTime, onupdate=db.func.now())
    page_name = db.Column(db.String(100), nullable=False)
    simple_desc = db.Column(db.String(100))
    creator = db.Column(db.String(100))
    system_id = db.Column(db.Integer)

    def __repr__(self):
        return '<UICasePageInfo %r, id %r>' % (self.page_name, self.id)


class UICasePageObjectInfo(db.Model):
    __tablename__ = 'ui_case_page_object_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=db.func.now())
    update_time = db.Column(db.DateTime, onupdate=db.func.now())
    object_name = db.Column(db.String(100), nullable=False)
    object_value = db.Column(db.String(100), nullable=False)
    object_by = db.Column(db.String(50), nullable=False)
    simple_desc = db.Column(db.String(100))
    creator = db.Column(db.String(100))
    page_id = db.Column(db.Integer, db.ForeignKey('ui_case_page_info.id'))
    page = db.relationship('UICasePageInfo', backref=db.backref('pages'))

    def __repr__(self):
        return '<UICasePageObjectInfo %r, id %r>' % (self.object_name, self.id)


class ApiCompanyInfo(db.Model):
    __tablename__ = 'api_company_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    company_name = db.Column(db.String(50), nullable=False, unique=True, comment='公司名称')
    simple_desc = db.Column(db.String(100), comment='描述信息')
    creator = db.Column(db.String(100), comment='创建人')
    last_modifier = db.Column(db.String(100), comment='最近修改人')

    def __repr__(self):
        return '<ApiCompanyInfo %r, id %r>' % (self.company_name, self.id)


class ApiProjectInfo(db.Model):
    __tablename__ = 'api_project_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    project_name = db.Column(db.String(50), nullable=False, comment='项目id')
    simple_desc = db.Column(db.String(100), comment='描述信息')
    api_company_id = db.Column(db.Integer, comment='公司id')
    creator = db.Column(db.String(100), comment='创建人')
    last_modifier = db.Column(db.String(100), comment='最近修改人')

    def __repr__(self):
        return '<ApiProjectInfo %r, id %r>' % (self.project_name, self.id)


class ApiSystemInfo(db.Model):
    __tablename__ = 'api_system_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    system_name = db.Column(db.String(50), nullable=False, comment='工程名称')
    simple_desc = db.Column(db.String(100), comment='描述信息')
    api_company_id = db.Column(db.Integer, comment='公司id')
    creator = db.Column(db.String(100), comment='创建人')
    last_modifier = db.Column(db.String(100), comment='最近修改人')
    git_url = db.Column(db.String(100), comment='git地址')

    def __repr__(self):
        return '<ApiSystemInfo %r, id %r>' % (self.system_name, self.id)


class ApiIntfInfo(db.Model):
    __tablename__ = 'api_intf_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    intf_name = db.Column(db.String(500), comment='接口名称')
    intf_desc = db.Column(db.String(100), comment='接口中文名')
    intf_type = db.Column(db.String(20), comment='接口类型 # HTTP/DUBBO/MQ')
    intf_info = db.Column(db.String(1200), comment='接口信息')
    api_system_id = db.Column(db.Integer, comment='工程id')
    creator = db.Column(db.String(100), comment='创建人')
    last_modifier = db.Column(db.String(100), comment='最近修改人')
    intf_relation = db.Column(db.String(200), comment='依赖接口列表')

    def __repr__(self):
        return '<ApiIntfInfo %r, id %r>' % (self.intf_name, self.id)


class ApiProjectSystemRelation(db.Model):
    __tablename__ = 'api_project_system_relation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    api_project_id = db.Column(db.Integer, nullable=False, comment='项目id')
    api_system_id = db.Column(db.Integer, nullable=False, comment='工程id')

    def __repr__(self):
        return '<ApiProjectSystemRelation %r-%r, id %r>' % (self.api_project_id, self.api_system_id, self.id)


class ApiProjectIntfRelation(db.Model):
    __tablename__ = 'api_project_intf_relation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    api_project_id = db.Column(db.Integer, nullable=False, comment='项目id')
    api_intf_id = db.Column(db.Integer, nullable=False, comment='接口id')

    def __repr__(self):
        return '<ApiProjectIntfRelation %r-%r, id %r>' % (self.api_project_id, self.api_intf_id, self.id)


class ApiTestcaseInfo(db.Model):
    __tablename__ = 'api_testcase_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    testcase_name = db.Column(db.String(200), nullable=False, comment='接口用例标题')
    type = db.Column(db.Integer, default=0, nullable=False, comment='用例类型 # 0:default 1:http 2:dubbo 3:mq')
    include = db.Column(db.String(400), comment='包含公共变量信息')
    simple_desc = db.Column(db.String(1000), comment='描述信息')
    case_status = db.Column(db.Integer, default=0, nullable=False, comment='用例启用状态 # 0:启用中 1:已停用')
    api_intf_id = db.Column(db.Integer, comment='接口id')
    api_request_id = db.Column(db.Integer, comment='请求详细信息id')
    creator = db.Column(db.String(100), comment='创建人')
    last_modifier = db.Column(db.String(100), comment='最近修改人')
    last_run = db.Column(db.Boolean, comment='最近一次运行结果 # 0:成功 1:失败')
    expect_result = db.Column(db.String(200), comment='预期结果')
    index = db.Column(db.Integer, comment='序号')
    setup_case_list = db.Column(db.String(1000), comment='前置用例列表')
    last_run_time = db.Column(db.DateTime, comment='最近一次运行时间')
    last_modify_time = db.Column(db.DateTime, comment='最近一次修改用例时间')

    def __repr__(self):
        return '<ApiTestcaseInfo %r, id %r>' % (self.testcase_name, self.id)


class ApiTestcaseRequest(db.Model):
    __tablename__ = 'api_testcase_request'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    api_testcase_id = db.Column(db.Integer, nullable=False, unique=True, comment='接口用例id')
    request = db.Column(db.Text, comment='请求详细信息')

    def __repr__(self):
        return '<ApiTestcaseRequest %r, id %r>' % (self.api_testcase_id, self.id)


class ApiTestcaseRequestQll(db.Model):
    __tablename__ = 'api_testcase_request_qll'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    api_testcase_id = db.Column(db.Integer, nullable=False, unique=True, comment='主用例id')
    request = db.Column(db.Text, comment='请求详细信息')

    def __repr__(self):
        return '<ApiTestcaseRequest %r, id %r>' % (self.api_testcase_id, self.id)


class ApiPublicVariableInfo(db.Model):
    __tablename__ = 'api_public_variable_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    variable_name = db.Column(db.String(100), nullable=False, comment='公共变量名称')
    type = db.Column(db.String(50), nullable=False, comment='公共变量类型 # constant/db/function/files')
    value = db.Column(db.String(1000), nullable=False, comment='公共变量的值')
    simple_desc = db.Column(db.String(50), comment='描述信息')
    api_company_id = db.Column(db.Integer, comment='公司id')
    api_system_id = db.Column(db.Integer, comment='工程id')
    creator = db.Column(db.String(100), comment='创建人')
    last_modifier = db.Column(db.String(100), comment='最近修改人')
    save_as = db.Column(db.String(10), comment='保存变量的类型 # str/num/bool/list/dict')

    def __repr__(self):
        return '<ApiPublicVariableInfo %r, id %r>' % (self.variable_name, self.id)


class ApiTestcaseTagRelation(db.Model):
    __tablename__ = 'api_testcase_tag_relation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    api_testcase_id = db.Column(db.Integer, nullable=False, comment='接口用例id')
    tag_id = db.Column(db.Integer, nullable=False, comment='标签id')

    def __repr__(self):
        return '<ApiTestcaseTagRelation %r-%r, id %r>' % (self.api_testcase_id, self.tag_id, self.id)


class ApiTestcaseMainTagRelation(db.Model):
    __tablename__ = 'api_testcase_main_tag_relation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    api_testcase_id = db.Column(db.Integer, nullable=False, comment='主用例id')
    tag_id = db.Column(db.Integer, nullable=False, comment='标签id')

    def __repr__(self):
        return '<ApiTestcaseMainTagRelation %r-%r, id %r>' % (self.api_testcase_id, self.tag_id, self.id)


class ApiTestReport(db.Model):
    __tablename__ = 'api_test_report'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    start_at = db.Column(db.String(50), comment='起始时间')
    duration = db.Column(db.String(50), comment='耗时')
    status = db.Column(db.String(50), comment='状态')
    run_type = db.Column(db.Integer, comment='运行类型 # 0:调试执行 1:测试计划执行')
    api_project_id = db.Column(db.Integer, comment='项目id')
    url = db.Column(db.String(150), comment='报告地址')
    executor = db.Column(db.String(100), comment='执行人')

    def __repr__(self):
        return '<ApiTestReport, id %r>' % self.id


class ApiProductLine(db.Model):
    __tablename__ = 'api_product_line'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    product_line_name = db.Column(db.String(100), nullable=False, comment='产品线节点名称')
    simple_desc = db.Column(db.String(100), comment='描述信息')
    api_company_id = db.Column(db.Integer, comment='公司id')
    creator = db.Column(db.String(100), comment='创建人')
    last_modifier = db.Column(db.String(100), comment='最近修改人')
    index = db.Column(db.Integer, comment='序号')
    parent_id = db.Column(db.Integer, comment='父节点id')

    def __repr__(self):
        return '<ApiProductLine %r, id %r>' % (self.sub_name, self.id)


class ApiTestcaseMain(db.Model):
    __tablename__ = 'api_testcase_main'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    testcase_name = db.Column(db.String(200), nullable=False, comment='主用例标题')
    simple_desc = db.Column(db.String(1000), comment='描述信息')
    case_type = db.Column(db.Integer, default=0, nullable=False, comment='用例类型 0:单接口基础用例 1:接口流程用例 2:全链路用例')
    case_status = db.Column(db.Integer, default=0, nullable=False, comment='用例启用状态 0:启用中 1:已停用')
    api_intf_id = db.Column(db.Integer, comment='接口id 当case_type=0/1')
    api_product_line_id = db.Column(db.Integer, comment='产品线id 当case_type=2')
    sub_list = db.Column(db.String(1000), comment='子用例id列表')
    creator = db.Column(db.String(100), comment='创建人')
    last_modifier = db.Column(db.String(100), comment='最近修改人')
    last_run = db.Column(db.Boolean, comment='最近一次运行是否成功 0:成功 1:失败')
    expect_result = db.Column(db.String(200), comment='预期结果')
    index = db.Column(db.Integer, comment='序号')
    setup_flow_list = db.Column(db.String(100), comment='前置列表（未使用）')
    main_teardown_hooks = db.Column(db.String(3000), comment='全链路用例独立后置步骤')
    last_run_time = db.Column(db.DateTime, comment='最近一次运行时间')
    # last_modify_time = db.Column(db.DateTime, comment='最近一次修改用例时间')

    def __repr__(self):
        return '<ApiTestcaseMain %r, id %r>' % (self.testcase_name, self.id)


class ApiTestcaseSub(db.Model):
    __tablename__ = 'api_testcase_sub'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    sub_name = db.Column(db.String(200), nullable=False, comment='子用例标题')
    request_type = db.Column(db.Integer, default=0, nullable=False, comment='接口请求类型 0:default 1:http 2:dubbo 3:mq')
    include = db.Column(db.String(400), comment='包含的公共变量')
    simple_desc = db.Column(db.String(200), comment='描述信息')
    case_type = db.Column(db.Integer, default=0, nullable=False, comment='用例类型 0:单接口基础用例 1:接口流程用例 2:全链路用例')
    api_intf_id = db.Column(db.Integer, comment='接口id')
    api_request_id = db.Column(db.Integer, comment='用例请求信息id')
    creator = db.Column(db.String(100), comment='创建人')
    last_modifier = db.Column(db.String(100), comment='最近修改人')
    expect_result = db.Column(db.String(200), comment='预期结果')
    main_list = db.Column(db.String(1000), comment='关联的主用例id列表')

    def __repr__(self):
        return '<ApiTestcaseSub %r, id %r>' % (self.sub_name, self.id)


class ApiIntfDefaultRequest(db.Model):
    __tablename__ = 'api_intf_default_request'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    api_intf_id = db.Column(db.Integer, nullable=False, unique=True, comment='接口id')
    request = db.Column(db.Text, comment='接口默认请求报文')
    request_detail = db.Column(db.Text, comment='接口默认请求报文详细信息')

    def __repr__(self):
        return '<ApiIntfDefaultRequest %r, id %r>' % (self.api_intf_id, self.id)


class ApiTaskInfo(db.Model):
    __tablename__ = 'api_task_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    task_name = db.Column(db.String(100), nullable=False, comment='任务名称')
    api_project_id = db.Column(db.Integer, comment='项目id')
    task_type = db.Column(db.Integer, comment='任务类型 1:人工指定 2:基于代码变更 3:CI构建触发-冒烟测试 4:CI构建触发-回归测试')
    case_tree = db.Column(db.String(5000), comment='任务勾选的用例')
    env_id = db.Column(db.Integer, comment='环境id（已废弃）')
    creator = db.Column(db.String(50), comment='创建人')
    last_modifier = db.Column(db.String(50), comment='最近修改人')
    receiver_list = db.Column(db.String(500), comment='任务结果接收人列表')
    effect_intf_id_list = db.Column(db.String(5000), comment='覆盖的接口id列表')
    uncovered_info = db.Column(db.String(2000), comment='未覆盖的信息')
    task_status = db.Column(db.Integer, comment='任务可执行状态 0:不可执行 1:可执行')
    api_company_id = db.Column(db.Integer, comment='公司id')
    related_tag_id_list = db.Column(db.String(100), comment='关联的用例标签id列表')

    def __repr__(self):
        return '<ApiTaskInfo %r, id %r>' % (self.task_name, self.id)


class GitDiffVersion(db.Model):
    __tablename__ = 'api_git_diff_version'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    seq_no = db.Column(db.Integer, comment='序列号')
    api_task_id = db.Column(db.Integer, comment='任务id')
    api_system_id = db.Column(db.Integer, comment='工程id')
    git_branch_name = db.Column(db.String(100), comment='git分支名称')
    old_commit_id = db.Column(db.String(50), comment='旧commitId')
    new_commit_id = db.Column(db.String(50), comment='新commitId')
    detail = db.Column(db.Text, comment='对比详情')
    creator = db.Column(db.String(50), comment='创建人')
    last_modifier = db.Column(db.String(50), comment='最近修改人')

    def __repr__(self):
        return '<GitDiffVersion %r, id %r>' % (self.git_branch_name, self.id)


class ApiRunTaskResult(db.Model):
    __tablename__ = 'api_run_task_result'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    run_date = db.Column(db.Date, default=db.func.now(), comment='运行日期')
    start_time = db.Column(db.DateTime, comment='任务开始时间')
    end_time = db.Column(db.DateTime, comment='任务结束时间')
    api_task_id = db.Column(db.Integer, comment='任务id')
    covered_intf_id_list = db.Column(db.String(5000), comment='覆盖的接口id列表')
    uncovered_intf_id_list = db.Column(db.String(5000), comment='未覆盖的接口id列表')
    total_cases = db.Column(db.Integer, comment='总用例数')
    not_run_cases = db.Column(db.Integer, comment='未运行用例数')
    run_cases = db.Column(db.Integer, comment='运行用例数')
    success_cases = db.Column(db.Integer, comment='成功用例数')
    fail_cases = db.Column(db.Integer, comment='失败用例数')
    creator = db.Column(db.String(50), comment='任务触发人')
    report_url = db.Column(db.String(100), comment='报告地址（已废弃）')
    run_env_id = db.Column(db.Integer, comment='运行环境id')
    run_main_case_in_parallel = db.Column(db.Integer, comment='全链路是否并发运行 0:否 1:是')
    worker_num = db.Column(db.Integer, comment='分配worker数量')

    def __repr__(self):
        return '<ApiRunTaskResult %r, id %r>' % (self.api_task_id, self.id)


class ApiTestcaseReuseRecord(db.Model):
    __tablename__ = 'api_testcase_reuse_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    record_date = db.Column(db.Date, default=db.func.now(), comment='记录日期')
    api_testcase_id = db.Column(db.Integer, comment='接口用例id')
    api_testcase_main_id = db.Column(db.Integer, comment='全链路用例id')
    is_setup = db.Column(db.Integer, comment='是否被前置 0: 否， 1: 是')
    been_setup_testcase_id = db.Column(db.Integer, comment='被前置的用例id')
    total_times = db.Column(db.Integer, comment='总计数')
    success_times = db.Column(db.Integer, comment='成功计数')
    fail_times = db.Column(db.Integer, comment='失败计数')

    def __repr__(self):
        return '<ApiTestcaseReuseRecord %r, id %r>' % (self.record_date, self.id)


class CeleryTaskRecord(db.Model):
    __tablename__ = 'api_celery_task_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    celery_task_no = db.Column(db.String(36), comment='celery任务编号')
    celery_task_status = db.Column(db.String(10), comment='celery任务状态')
    api_run_task_result_id = db.Column(db.Integer, comment='关联api_run_task_result.id')

    def __repr__(self):
        return '<CeleryTaskRecord %r, id %r>' % (self.celery_task_id, self.id)


class GenerateDataRecord(db.Model):
    __tablename__ = 'api_generate_data_record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    create_time = db.Column(db.DateTime, default=db.func.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, onupdate=db.func.now(), comment='修改时间')
    record_date = db.Column(db.Date, default=db.func.now(), comment='记录日期')
    case_id = db.Column(db.String(10), comment='用例id')
    mobile_no = db.Column(db.String(11), comment='手机号')
    id_no = db.Column(db.String(20), comment='身份证号')
    bank_card_no_credit = db.Column(db.String(20), comment='信用卡号')
    bank_card_no_debit = db.Column(db.String(20), comment='借记卡号')

    def __repr__(self):
        return '<GenerateDataRecord %r, id %r>' % (self.case_id, self.id)


class ApiTestcaseMainCustomFlow(db.Model):
    __tablename__ = 'api_testcase_main_custom_flow'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='自增id')
    flow_name = db.Column(db.String(11), comment='自定义流名称')
    testcase_id = db.Column(db.Integer, comment='主用例id')
    start_sub_index = db.Column(db.Integer, comment='起始子用例序号（已废弃）')
    end_sub_index = db.Column(db.Integer, comment='结束子用例序号（已废弃）')
    flow_index_list = db.Column(db.String(255), comment='序号列表')

    def __repr__(self):
        return '<ApiTestcaseMainCustomFlow %r, id %r>' % (self.flow_name, self.id)
