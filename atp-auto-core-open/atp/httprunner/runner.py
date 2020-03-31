# encoding: utf-8
import traceback
from unittest.case import SkipTest

from atp.httprunner import exceptions, logger, response, utils
from atp.httprunner.client import HttpSession
from atp.httprunner.compat import OrderedDict
from atp.httprunner.context import Context


class Runner(object):

    def __init__(self, config_dict=None, http_client_session=None):
        """
        """
        self.http_client_session = http_client_session
        config_dict = config_dict or {}
        self.evaluated_validators = []

        # testcase variables
        config_variables = config_dict.get("variables", {})
        # testcase functions
        config_functions = config_dict.get("functions", {})
        # testcase setup hooks
        testcase_setup_hooks = config_dict.pop("setup_hooks", [])
        # testcase teardown hooks
        self.testcase_teardown_hooks = config_dict.pop("teardown_hooks", [])

        self.context = Context(config_variables, config_functions)
        self.init_config(config_dict, "testcase")

        self.teststep_dict = None
        self.step_teardown_executed = False
        self.running_hook = None
        self.step_teardown_pass = True
        self.step_setup_pass = True
        self.testcase_teardown_hooks_executed = False
        self.variable_not_found = False
        self.step_request_teardown_pass = True
        self.step_parse_variable_pass = True

        if testcase_setup_hooks:
            self.do_setup_hook_actions(testcase_setup_hooks)

    def __del__(self):
        # if not self.step_teardown_executed:
        #     logger.log_info("【提示】: 开始执行后置动作...")
        #     teardown_hooks = self.teststep_dict.get("teardown_hooks", [])
        #     self.step_teardown_executed = True
        #     if teardown_hooks:
        #         self.do_teardown_hook_actions(teardown_hooks)
        # if self.testcase_teardown_hooks:
        #     logger.log_info("【提示】: 开始执行全局后置动作...")
        #     self.do_teardown_hook_actions(self.testcase_teardown_hooks)
        pass

    def init_config(self, config_dict, level):
        """ create/update context variables binds

        Args:
            config_dict (dict):
            level (enum): "testcase" or "teststep"
                testcase:
                    {
                        "name": "testcase description",
                        "variables": [],   # optional
                        "request": {
                            "base_url": "http://127.0.0.1:5000",
                            "headers": {
                                "User-Agent": "iOS/2.8.3"
                            }
                        }
                    }
                teststep:
                    {
                        "name": "teststep description",
                        "variables": [],   # optional
                        "request": {
                            "url": "/api/get-token",
                            "method": "POST",
                            "headers": {
                                "Content-Type": "application/json"
                            }
                        },
                        "json": {
                            "sign": "f1219719911caae89ccc301679857ebfda115ca2"
                        }
                    }

        Returns:
            dict: parsed request dict

        """
        # convert keys in request headers to lowercase
        # config_dict = utils.lower_config_dict_key(config_dict)

        self.context.init_context_variables(level)
        variables = config_dict.get('variables') \
            or config_dict.get('variable_binds', OrderedDict())
        self.context.update_context_variables(variables, level, runner=self)

        request_config = config_dict.get('request', {})
        parsed_request = self.context.get_parsed_request(request_config, level, runner=self)

        base_url = parsed_request.pop("base_url", None)
        self.http_client_session = self.http_client_session or HttpSession(base_url)

        # if 'files' in parsed_request:
        #     files_list = parsed_request.pop('files')
        #     parsed_files_list = []
        #     for i in range(len(files_list)):
        #         for ii in range(len(files_list[i])):
        #             if isinstance(files_list[i][ii], list):
        #                 files_list[i][ii] = tuple(files_list[i][ii])
        #
        #     for f in files_list:
        #         if isinstance(f, list):
        #             f = tuple(f)
        #         parsed_files_list.append(f)
        #
        #     parsed_request['files'] = parsed_files_list
        #
        # print('parsed_request:{}'.format(parsed_request))

        return parsed_request

    def _handle_skip_feature(self, teststep_dict):
        """ handle skip feature for teststep
            - skip: skip current test unconditionally
            - skipIf: skip current test if condition is true
            - skipUnless: skip current test unless condition is true

        Args:
            teststep_dict (dict): teststep info

        Raises:
            SkipTest: skip teststep

        """
        # TODO: move skip to __initialize
        skip_reason = None

        if "skip" in teststep_dict:
            skip_reason = teststep_dict["skip"]

        elif "skipIf" in teststep_dict:
            skip_if_condition = teststep_dict["skipIf"]
            if self.context.eval_content(skip_if_condition):
                skip_reason = "{} evaluate to True".format(skip_if_condition)

        elif "skipUnless" in teststep_dict:
            skip_unless_condition = teststep_dict["skipUnless"]
            if not self.context.eval_content(skip_unless_condition):
                skip_reason = "{} evaluate to False".format(skip_unless_condition)

        if skip_reason:
            raise SkipTest(skip_reason)

    def do_setup_hook_actions(self, actions):
        for action in actions:
            # logger.log_debug("call hook: {}".format(action))
            logger.log_info("【执行前置动作】: {}".format(action))
            # TODO: check hook function if valid
            self.context.eval_content(action, runner=self)
            if not self.step_setup_pass:
                break

    def do_teardown_hook_actions(self, actions):
        for action in actions:
            # logger.log_debug("call hook: {}".format(action))
            logger.log_info("【执行后置动作】: {}".format(action))
            # TODO: check hook function if valid
            self.context.eval_content(action, runner=self)

    def do_request_teardown_hook_actions(self, actions):
        for action in actions:
            # logger.log_debug("call hook: {}".format(action))
            logger.log_info("【执行请求后置动作】: {}".format(action))
            # TODO: check hook function if valid
            self.context.eval_content(action, runner=self)

    def run_test(self, teststep_dict):
        """ run single teststep.

        Args:
            teststep_dict (dict): teststep info
                {
                    "name": "teststep description",
                    "skip": "skip this test unconditionally",
                    "times": 3,
                    "variables": [],        # optional, override
                    "request": {
                        "url": "http://127.0.0.1:5000/api/users/1000",
                        "method": "POST",
                        "headers": {
                            "Content-Type": "application/json",
                            "authorization": "$authorization",
                            "random": "$random"
                        },
                        "body": '{"name": "user", "password": "123456"}'
                    },
                    "extract": [],              # optional
                    "validate": [],             # optional
                    "setup_hooks": [],          # optional
                    "teardown_hooks": []        # optional
                }

        Raises:
            exceptions.ParamsError
            exceptions.ValidationFailure
            exceptions.ExtractFailure

        """
        self.teststep_dict = teststep_dict

        is_last = teststep_dict.get("is_last", None)
        case_name = teststep_dict.get("name", None)
        case_id = teststep_dict.get("case_id", None)
        logger.log_info("【开始执行用例】: ID_{0}, {1}".format(case_id, case_name))
        self.step_teardown_executed = False

        # check skip
        self._handle_skip_feature(teststep_dict)

        # prepare
        logger.log_info("-" * 12 + "【变量替换-开始】" + "-" * 12)
        extractors = teststep_dict.get("extract", []) or teststep_dict.get("extractors", [])
        validators = teststep_dict.get("validate", []) or teststep_dict.get("validators", [])
        self.step_parse_variable_pass = True
        self.running_hook = 'step_parse_variable'
        parsed_request = self.init_config(teststep_dict, level="teststep")
        self.context.update_teststep_variables_mapping("request", parsed_request)
        logger.log_info("-" * 12 + "【变量替换-结束】" + "-" * 12)
        if self.variable_not_found:
            self.handle_teardown(fail_type='变量替换')
            raise exceptions.VariableNotFound

        if not self.step_parse_variable_pass:
            self.handle_teardown(fail_type='变量替换')
            raise exceptions.CustomFuncRunError

        # setup hooks
        setup_hooks = teststep_dict.get("setup_hooks", [])
        setup_hooks.insert(0, "${setup_hook_prepare_kwargs($request)}")
        logger.log_info("-"*12 + "【请求前置-开始】" + "-"*12)
        self.step_setup_pass = True
        self.running_hook = 'step_setup'
        self.do_setup_hook_actions(setup_hooks)
        logger.log_info("-"*12 + "【请求前置-结束】" + "-"*12)
        if not self.step_setup_pass:
            self.handle_teardown(fail_type='前置动作')
            raise exceptions.SetupHooksFailure

        try:
            url = parsed_request.pop('url')
            method = parsed_request.pop('method')
            group_name = parsed_request.pop("group", None)
        except KeyError:
            raise exceptions.ParamsError("URL or METHOD missed!")

        # TODO: move method validation to json schema
        valid_methods = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        if method.upper() not in valid_methods:
            err_msg = u"Invalid HTTP method! => {}\n".format(method)
            err_msg += "Available HTTP methods: {}".format("/".join(valid_methods))
            logger.log_error(err_msg)
            self.handle_teardown(fail_type='校验发送方式')
            raise exceptions.ParamsError(err_msg)

        # logger.log_info("{method} {url}".format(method=method, url=url))
        # logger.log_debug("request kwargs(raw): {kwargs}".format(kwargs=parsed_request))

        # request
        try:
            resp = self.http_client_session.request(
                method,
                url,
                name=group_name,
                **parsed_request
            )
        except Exception as e:
            self.handle_teardown(fail_type='接口请求')
            raise exceptions.RequestFailure
        resp_obj = response.ResponseObject(resp)

        # # teardown hooks
        # teardown_hooks = teststep_dict.get("teardown_hooks", [])
        # if teardown_hooks:
        #     # logger.log_info("start to run teardown hooks")
        #     logger.log_info("【开始后置动作】...")
        #     self.context.update_teststep_variables_mapping("response", resp_obj)
        #     self.do_hook_actions(teardown_hooks)
        #     logger.log_info("【结束后置动作】")

        # request teardown hooks 新增请求后置
        request_teardown_hooks = teststep_dict.get("request_teardown_hooks", [])
        if request_teardown_hooks:
            # logger.log_info("start to run teardown hooks")
            logger.log_info("-"*12 + "【请求后置-开始】" + "-"*12)
            self.step_request_teardown_pass = True
            self.running_hook = 'step_request_teardown'
            self.context.update_teststep_variables_mapping("response", resp_obj)
            self.do_request_teardown_hook_actions(request_teardown_hooks)
            logger.log_info("-"*12 + "【请求后置-结束】" + "-"*12)
            if not self.step_request_teardown_pass:
                self.handle_teardown(fail_type='请求后置动作')
                raise exceptions.TeardownHooksFailure

        # extract
        logger.log_info("-" * 12 + "【提取变量-开始】" + "-" * 12)
        try:
            extracted_variables_mapping = resp_obj.extract_response(extractors, self.context)
            self.context.update_testcase_runtime_variables_mapping(extracted_variables_mapping)
        except Exception as err:
            logger.log_error('提取变量失败：{0}'.format(err.args[0]))
            self.handle_teardown(fail_type='提取变量')
            raise exceptions.ExtractFailure
        logger.log_info("-" * 12 + "【提取变量-结束】" + "-" * 12)

        # validate
        try:
            logger.log_info("-" * 12 + "【结果校验-开始】" + "-" * 12)
            self.evaluated_validators, validate_pass = self.context.validate(validators, resp_obj)
            logger.log_info("-" * 12 + "【结果校验-结束】" + "-" * 12)
            if not validate_pass:
                # self.handle_teardown(fail_type='结果校验')
                raise exceptions.ValidationFailure
        except (exceptions.ParamsError, exceptions.ValidationFailure, exceptions.ExtractFailure,
                exceptions.VariableNotFound) as err:
            # log request
            # err_req_msg = "request: \n"
            # err_req_msg += "headers: {}\n".format(parsed_request.pop("headers", {}))
            # for k, v in parsed_request.items():
            #     err_req_msg += "{}: {}\n".format(k, repr(v))
            # logger.log_error(err_req_msg)
            #
            # # log response
            # err_resp_msg = "response: \n"
            # err_resp_msg += "status_code: {}\n".format(resp_obj.status_code)
            # err_resp_msg += "headers: {}\n".format(resp_obj.headers)
            # err_resp_msg += "body: {}\n".format(repr(resp_obj.text))
            # logger.log_error(err_resp_msg)
            logger.log_error('结果校验失败')
            self.handle_teardown(fail_type='结果校验')
            raise exceptions.ValidationFailure

        # teardown hooks
        teardown_hooks = teststep_dict.get("teardown_hooks", [])
        self.step_teardown_executed = True
        if teardown_hooks:
            # logger.log_info("start to run teardown hooks")
            logger.log_info("-"*12 + "【用例后置-开始】" + "-"*12)
            self.step_teardown_pass = True
            self.running_hook = 'step_teardown'
            self.context.update_teststep_variables_mapping("response", resp_obj)
            self.do_teardown_hook_actions(teardown_hooks)
            logger.log_info("-"*12 + "【用例后置-结束】" + "-"*12)
            if not self.step_teardown_pass:
                self.handle_teardown(fail_type='后置动作')
                raise exceptions.TeardownHooksFailure

        # total teardown hooks
        if is_last:
            if self.testcase_teardown_hooks and not self.testcase_teardown_hooks_executed:
                logger.log_info("-"*12 + "【全局后置-开始】" + "-"*12)
                self.testcase_teardown_hooks_executed = True
                self.do_teardown_hook_actions(self.testcase_teardown_hooks)
                logger.log_info("-" * 12 + "【全局后置-结束】" + "-" * 12)

        logger.log_info("【结束执行用例】: ID_{0}, {1}".format(case_id, case_name))

    def handle_teardown(self, fail_type):
        logger.log_warning("因【{}】错误, 中断测试".format(fail_type))
        if not self.step_teardown_executed:
            teardown_hooks = self.teststep_dict.get("teardown_hooks", [])
            self.step_teardown_executed = True
            if teardown_hooks:
                logger.log_info("-"*12 + "【用例后置-开始】" + "-"*12)
                self.do_teardown_hook_actions(teardown_hooks)
                logger.log_info("-" * 12 + "【用例后置-结束】" + "-" * 12)

        if self.testcase_teardown_hooks and not self.testcase_teardown_hooks_executed:
            logger.log_info("-"*12 + "【全局后置-开始】" + "-"*12)
            self.testcase_teardown_hooks_executed = True
            self.do_teardown_hook_actions(self.testcase_teardown_hooks)
            logger.log_info("-" * 12 + "【全局后置-结束】" + "-" * 12)

    def extract_output(self, output_variables_list):
        """ extract output variables
        """
        variables_mapping = self.context.teststep_variables_mapping

        output = {}
        for variable in output_variables_list:
            if variable not in variables_mapping:
                logger.log_warning(
                    "variable '{}' can not be found in variables mapping, failed to output!"\
                        .format(variable)
                )
                continue

            output[variable] = variables_mapping[variable]

        return output
