# encoding: utf-8

import copy
import json

# from atp.api.mysql_sql_executor import sql_execute, db_operation_to_json, sql_execute_cycle
from atp.api import mysql_sql_executor
from atp.api.redis_api import RedisUtils
from atp.utils.get_content_from_log import GetContenFromLog

from atp.httprunner import exceptions, logger, parser, utils
from atp.httprunner.compat import OrderedDict
from atp.utils.tools import transfer_json_string_to_dict


class Context(object):
    """ Manages context functions and variables.
        context has two levels, testcase and teststep.
    """
    def __init__(self, variables=None, functions=None):
        """ init Context with testcase variables and functions.
        """
        # testcase level context
        ## TESTCASE_SHARED_VARIABLES_MAPPING and TESTCASE_SHARED_FUNCTIONS_MAPPING will not change.
        self.TESTCASE_SHARED_VARIABLES_MAPPING = variables or OrderedDict()
        self.TESTCASE_SHARED_FUNCTIONS_MAPPING = functions or OrderedDict()

        # testcase level request, will not change
        self.TESTCASE_SHARED_REQUEST_MAPPING = {}

        self.evaluated_validators = []
        self.init_context_variables(level="testcase")

    def init_context_variables(self, level="testcase"):
        """ initialize testcase/teststep context

        Args:
            level (enum): "testcase" or "teststep"

        """
        if level == "testcase":
            # testcase level runtime context, will be updated with extracted variables in each teststep.
            self.testcase_runtime_variables_mapping = copy.deepcopy(self.TESTCASE_SHARED_VARIABLES_MAPPING)

        # teststep level context, will be altered in each teststep.
        # teststep config shall inherit from testcase configs,
        # but can not change testcase configs, that's why we use copy.deepcopy here.
        self.teststep_variables_mapping = copy.deepcopy(self.testcase_runtime_variables_mapping)

    def update_context_variables(self, variables, level, runner=None):
        """ update context variables, with level specified.

        Args:
            variables (list/OrderedDict): testcase config block or teststep block
                [
                    {"TOKEN": "debugtalk"},
                    {"random": "${gen_random_string(5)}"},
                    {"json": {'name': 'user', 'password': '123456'}},
                    {"md5": "${gen_md5($TOKEN, $json, $random)}"}
                ]
                OrderDict({
                    "TOKEN": "debugtalk",
                    "random": "${gen_random_string(5)}",
                    "json": {'name': 'user', 'password': '123456'},
                    "md5": "${gen_md5($TOKEN, $json, $random)}"
                })
            level (enum): "testcase" or "teststep"

        """
        if isinstance(variables, list):
            variables = utils.convert_mappinglist_to_orderdict(variables)

        for variable_name, variable_value in variables.items():
            variable_eval_value = self.eval_content(variable_value, runner=runner)

            if level == "testcase":
                self.testcase_runtime_variables_mapping[variable_name] = variable_eval_value

            self.update_teststep_variables_mapping(variable_name, variable_eval_value)

    def eval_content(self, content, runner=None):
        """ evaluate content recursively, take effect on each variable and function in content.
            content may be in any data structure, include dict, list, tuple, number, string, etc.
        """
        return parser.parse_data(
            content,
            self.teststep_variables_mapping,
            self.TESTCASE_SHARED_FUNCTIONS_MAPPING,
            runner=runner
        )

    def update_testcase_runtime_variables_mapping(self, variables):
        """ update testcase_runtime_variables_mapping with extracted vairables in teststep.

        Args:
            variables (OrderDict): extracted variables in teststep

        """
        for variable_name, variable_value in variables.items():
            self.testcase_runtime_variables_mapping[variable_name] = variable_value
            self.update_teststep_variables_mapping(variable_name, variable_value)

    def update_teststep_variables_mapping(self, variable_name, variable_value):
        """ bind and update testcase variables mapping
        """
        self.teststep_variables_mapping[variable_name] = variable_value

    def get_parsed_request(self, request_dict, level="teststep", runner=None):
        """ get parsed request with variables and functions.

        Args:
            runner:
            request_dict (dict): request config mapping
            level (enum): "testcase" or "teststep"

        Returns:
            dict: parsed request dict

        """
        if level == "testcase":
            # testcase config request dict has been parsed in parse_tests
            self.TESTCASE_SHARED_REQUEST_MAPPING = copy.deepcopy(request_dict)
            return self.TESTCASE_SHARED_REQUEST_MAPPING

        else:
            # teststep
            return self.eval_content(
                utils.deep_update_dict(
                    copy.deepcopy(self.TESTCASE_SHARED_REQUEST_MAPPING),
                    request_dict
                ),
                runner=runner
            )

    def __eval_check_item(self, validator, resp_obj):
        """ evaluate check item in validator.

        Args:
            validator (dict): validator
                {"check": "status_code", "comparator": "eq", "expect": 201}
                {"check": "$resp_body_success", "comparator": "eq", "expect": True}
            resp_obj (object): requests.Response() object

        Returns:
            dict: validator info
                {
                    "check": "status_code",
                    "check_value": 200,
                    "expect": 201,
                    "comparator": "eq"
                }

        """
        check_item = validator["check"]

        expect_value = self.eval_content(transfer_json_string_to_dict(validator["expect"]))

        if validator['comparator'] == 'db_validate':
            # format 6
            db_connect_content = '$DB_CONNECT'
            check_item = check_item.strip(db_connect_content)
            if parser.extract_variables(check_item):
                check_item = self.eval_content(check_item)
            res = mysql_sql_executor.sql_execute(check_item, db_connect=self.eval_content(db_connect_content))
            check_value = res[0][0] if res else "DB query returns EMPTY result!"
            validator["check"] = check_item
        elif validator['comparator'] == 'db_json_validate':
            # format 6
            db_connect_content = '$DB_CONNECT'
            check_item = check_item.strip(db_connect_content)
            if parser.extract_variables(check_item):
                check_item = self.eval_content(check_item)
            try:
                wait_time = int(check_item.split(';')[1])
                check_item = check_item.split(';')[0] + ';'
            except (IndexError, ValueError):
                wait_time = 30
            res = mysql_sql_executor.db_operation_to_json_cycle(check_item, db_connect=self.eval_content(db_connect_content), expect_value=expect_value, wait_time=wait_time)
            check_value = res if res is not None else "DB query returns EMPTY result!"
            validator["check"] = check_item
        elif validator['comparator'] == 'db_validate_cycle':
            # format 6
            db_connect_content = '$DB_CONNECT'
            check_item = check_item.strip(db_connect_content)
            if parser.extract_variables(check_item):
                check_item = self.eval_content(check_item)
            try:
                wait_time = int(check_item.split(';')[1])
                check_item = check_item.split(';')[0] + ';'
            except (IndexError, ValueError):
                wait_time = 30
            res = mysql_sql_executor.sql_execute_cycle(check_item, db_connect=self.eval_content(db_connect_content), expect_value=expect_value, wait_time=wait_time)
            check_value = res if res is not None else "DB query returns EMPTY result!"
            validator["check"] = check_item
        # 增加redis校验
        elif validator['comparator'] == 'redis_validate':
            db_num = self.eval_content(json.loads(validator['check'])['db_num'])
            redis_key = self.eval_content(json.loads(validator['check'])['redis_key'])
            redis_connect = self.eval_content('$REDIS_CONNECT')
            try:
                _redis_connect = json.loads(redis_connect)
            except Exception as err:
                raise Exception('环境信息中redis连接配置错误')
            redis_host = _redis_connect['host']
            redis_port = _redis_connect['port']
            redis_password = _redis_connect['password']

            with RedisUtils(redis_host, redis_port, redis_password, db_num) as r:
                check_value = r.get_str_value(redis_key)

        # 增加mq校验
        elif validator['comparator'] == 'mq_validate':
            topic = self.eval_content(json.loads(validator['check'])['topic']) + '_' + self.eval_content('$ENV_NAME')
            tag = self.eval_content(json.loads(validator['check'])['tag'])
            system_name = self.eval_content(json.loads(validator['check'])['system_name'])
            server_app_map = json.loads(self.eval_content('$SERVER_APP_MAP'))
            server_default_user = json.loads(self.eval_content('$SERVER_DEFAULT_USER'))
            server_host = None
            for k,v in server_app_map.items():
                if system_name in v:
                    server_host = k
                    break
            if not server_host:
                raise Exception('环境配置中找不到指定的系统名称 {0}'.format(system_name))
            server_info = [server_host, "22", server_default_user['user'], server_default_user['password']]
            gc = GetContenFromLog(system_name, server_info)
            check_value = list(gc.get_mq_log(topic, tag))

        elif isinstance(check_item, (dict, list)) \
            or parser.extract_variables(check_item) \
            or parser.extract_functions(check_item):
            # format 1/2/3
            check_value = self.eval_content(check_item)
        else:
            # format 4/5
            check_value = resp_obj.extract_field(check_item)

        from atp.utils.tools import convert_mysql_datatype_to_py
        validator["check_value"] = convert_mysql_datatype_to_py(check_value)
        validator["expect"] = expect_value
        validator["check_result"] = "unchecked"
        return validator

    def _do_validation(self, validator_dict):
        """ validate with functions

        Args:
            validator_dict (dict): validator dict
                {
                    "check": "status_code",
                    "check_value": 200,
                    "expect": 201,
                    "comparator": "eq"
                }

        """
        # TODO: move comparator uniform to init_test_suites
        comparator = utils.get_uniform_comparator(validator_dict["comparator"])
        validate_func = self.TESTCASE_SHARED_FUNCTIONS_MAPPING.get(comparator)

        if not validate_func:
            raise exceptions.FunctionNotFound("comparator not found: {}".format(comparator))

        check_item = validator_dict["check"]
        check_value = validator_dict["check_value"]
        expect_value = validator_dict["expect"]

        if (check_value is None or expect_value is None) \
            and comparator not in [
                    "is", "eq", "equals", "==", "json_contains", "json_same", "field_special_check", "db_validate",
                    "db_validate_cycle", "field_check_empty_list", "field_check_not_empty_list",
                    "field_check_not_in_list", "field_check_empty_json", "field_check_not_empty_json", "redis_validate", "mq_validate"]:
            raise exceptions.ParamsError("Null value can only be compared with comparator: eq/equals/==")

        # validate_msg = "validate: {} {} {}({})".format(
        validate_msg = "【验证点】: 校验方法：{}, 待校验内容：{}, 期望结果：{}({})".format(
            comparator,
            check_item,
            expect_value,
            type(expect_value).__name__
        )

        try:
            validator_dict["check_result"] = "pass"
            is_ok = validate_func(check_value, expect_value)
            if is_ok is True:
                validate_msg += "\t ....................PASS"
                logger.log_info(validate_msg)
            else:
                validate_msg += "\t ....................FAIL"
                if is_ok is not False:
                    validate_msg += "......原因: {}".format(is_ok[1])
                logger.log_error(validate_msg)
                validator_dict["check_result"] = "fail"
                raise exceptions.ValidationFailure(validate_msg)
        except (AssertionError, TypeError) as err:
            validate_msg += "\t ....................FAIL"
            validate_msg += "\t{}({}), {}, {}({})".format(
                check_value,
                type(check_value).__name__,
                comparator,
                expect_value,
                type(expect_value).__name__
            )
            validate_msg += "\t......原因: {}".format(err.args[0])
            logger.log_error(validate_msg)
            validator_dict["check_result"] = "fail"
            raise exceptions.ValidationFailure(validate_msg)

    def validate(self, validators, resp_obj):
        """ make validations
        """
        validate_pass = True
        evaluated_validators = []
        if not validators:
            return evaluated_validators, validate_pass

        for validator in validators:
            # evaluate validators with context variable mapping.
            try:
                evaluated_validator = self.__eval_check_item(
                    parser.parse_validator(validator),
                    resp_obj
                )
            except Exception as err:
                logger.log_error('【处理校验数据出错】{}'.format(repr(err)))
                validate_pass = False
                continue

            try:
                self._do_validation(evaluated_validator)
            except exceptions.ValidationFailure:
                validate_pass = False

            # check_vlue是生成器时做转换处理
            # from inspect import isgenerator
            # if isgenerator(evaluated_validator['check_value']):
            #     evaluated_validator['check_value'] = list(evaluated_validator['check_value'])
            evaluated_validators.append(evaluated_validator)

        # if not validate_pass:
        #     raise exceptions.ValidationFailure
        return evaluated_validators, validate_pass
