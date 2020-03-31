# encoding: utf-8

import ast
import json
import os
import re
import traceback

from atp.httprunner import exceptions, utils, logger
from atp.httprunner.compat import basestring, builtin_str, numeric_types, str
from atp.httprunner.utils import query_json

variable_regexp = r"\$([\w_]+)"
new_variable_regexp = r"\$([\w]+[\w.]*)"

# function_regexp = r"\$\{([\w_]+\([\$\w\.\-\+/_ =,]*\))\}"
# function_regexp_compile = re.compile(r"^([\w_]+)\(([\$\w\.\-\+/_ =,]*)\)$")
# function_regexp = r"\$\{([\w_]+\([!！《》【】（）—~，。；：？\\￥\[\]#@&%\^\n\t`'\"<>;:\{\}\?\$\w\.\-\+/_ =,\|\(\)\*]*\))\}"
# function_regexp_compile = re.compile(r"^([\w_]+)\(([!！《》【】（）—~，。；：？\\￥\[\]#@&%\^\n\t`'\"<>;:\{\}\?\$\w\.\-\+/_ =,\|\(\)\*]*)\)$")
function_regexp = r"\$\{([\w_]+\(.*\))\}"
function_regexp_compile = re.compile(r"^([\w_]+)\((.*)\)$")


def parse_string_value(str_value):
    """ parse string to number if possible
    e.g. "123" => 123
         "12.2" => 12.3
         "abc" => "abc"
         "$var" => "$var"
    """
    try:
        return ast.literal_eval(str_value)
    except ValueError:
        return str_value
    except SyntaxError:
        # e.g. $var, ${func}
        return str_value


def extract_variables(content):
    """ extract all variable names from content, which is in format $variable

    Args:
        content (str): string content

    Returns:
        list: variables list extracted from string content

    Examples:
        >>> extract_variables("$variable")
        ["variable"]

        >>> extract_variables("/blog/$postid")
        ["postid"]

        >>> extract_variables("/$var1/$var2")
        ["var1", "var2"]

        >>> extract_variables("abc")
        []

    """
    # TODO: change variable notation from $var to {{var}}
    try:
        return re.findall(new_variable_regexp, content, re.A)
    except TypeError:
        return []


def extract_functions(content):
    """ extract all functions from string content, which are in format ${fun()}

    Args:
        content (str): string content

    Returns:
        list: functions list extracted from string content

    Examples:
        >>> extract_functions("${func(5)}")
        ["func(5)"]

        >>> extract_functions("${func(a=1, b=2)}")
        ["func(a=1, b=2)"]

        >>> extract_functions("/api/1000?_t=${get_timestamp()}")
        ["get_timestamp()"]

        >>> extract_functions("/api/${add(1, 2)}")
        ["add(1, 2)"]

        >>> extract_functions("/api/${add(1, 2)}?_t=${get_timestamp()}")
        ["add(1, 2)", "get_timestamp()"]

    """
    try:
        return re.findall(function_regexp, content)
    except TypeError:
        return []


def parse_function(content):
    """ parse function name and args from string content.

    Args:
        content (str): string content

    Returns:
        dict: function meta dict

            {
                "func_name": "xxx",
                "args": [],
                "kwargs": {}
            }

    Examples:
        >>> parse_function("func()")
        {'func_name': 'func', 'args': [], 'kwargs': {}}

        >>> parse_function("func(5)")
        {'func_name': 'func', 'args': [5], 'kwargs': {}}

        >>> parse_function("func(1, 2)")
        {'func_name': 'func', 'args': [1, 2], 'kwargs': {}}

        >>> parse_function("func(a=1, b=2)")
        {'func_name': 'func', 'args': [], 'kwargs': {'a': 1, 'b': 2}}

        >>> parse_function("func(1, 2, a=3, b=4)")
        {'func_name': 'func', 'args': [1, 2], 'kwargs': {'a':3, 'b':4}}

    """
    matched = function_regexp_compile.match(content)
    if not matched:
        raise exceptions.FunctionNotFound("{} not found!".format(content))

    function_meta = {
        "func_name": matched.group(1),
        "args": [],
        "kwargs": {}
    }

    args_str = matched.group(2).strip()
    if args_str == "":
        return function_meta

    # args_list = args_str.split(',')
    args_list = args_str.split('||')
    for arg in args_list:
        arg = arg.strip()
        # if '=' in arg:
        #     key, value = arg.split('=')
        #     function_meta["kwargs"][key.strip()] = parse_string_value(value.strip())
        # else:
        #     function_meta["args"].append(parse_string_value(arg))
        function_meta["args"].append(parse_string_value(arg))

    return function_meta


def parse_validator(validator):
    """ parse validator, validator maybe in two format
    @param (dict) validator
        format1: this is kept for compatiblity with the previous versions.
            {"check": "status_code", "comparator": "eq", "expect": 201}
            {"check": "$resp_body_success", "comparator": "eq", "expect": True}
        format2: recommended new version
            {'eq': ['status_code', 201]}
            {'eq': ['$resp_body_success', True]}
    @return (dict) validator info
        {
            "check": "status_code",
            "expect": 201,
            "comparator": "eq"
        }
    """
    if not isinstance(validator, dict):
        raise exceptions.ParamsError("invalid validator: {}".format(validator))

    if "check" in validator and len(validator) > 1:
        # format1
        check_item = validator.get("check")

        if "expect" in validator:
            expect_value = validator.get("expect")
        elif "expected" in validator:
            expect_value = validator.get("expected")
        else:
            raise exceptions.ParamsError("invalid validator: {}".format(validator))

        comparator = validator.get("comparator", "eq")

    elif len(validator) == 1:
        # format2
        comparator = list(validator.keys())[0]
        compare_values = validator[comparator]

        # 有断言备注的情况下，舍弃备注信息
        if isinstance(compare_values, list) and len(compare_values) > 2:
            compare_values.pop()

        if not isinstance(compare_values, list) or len(compare_values) != 2:
            raise exceptions.ParamsError("invalid validator: {}".format(validator))

        check_item, expect_value = compare_values

    else:
        raise exceptions.ParamsError("invalid validator: {}".format(validator))

    return {
        "check": check_item,
        "expect": expect_value,
        "comparator": comparator
    }


def substitute_variables(content, variables_mapping):
    """ substitute variables in content with variables_mapping

    Args:
        content (str/dict/list/numeric/bool/type): content to be substituted.
        variables_mapping (dict): variables mapping.

    Returns:
        substituted content.

    Examples:
        >>> content = {
                'request': {
                    'url': '/api/users/$uid',
                    'headers': {'token': '$token'}
                }
            }
        >>> variables_mapping = {"$uid": 1000}
        >>> substitute_variables(content, variables_mapping)
            {
                'request': {
                    'url': '/api/users/1000',
                    'headers': {'token': '$token'}
                }
            }

    """
    if isinstance(content, (list, set, tuple)):
        return [
            substitute_variables(item, variables_mapping)
            for item in content
        ]

    if isinstance(content, dict):
        substituted_data = {}
        for key, value in content.items():
            eval_key = substitute_variables(key, variables_mapping)
            eval_value = substitute_variables(value, variables_mapping)
            substituted_data[eval_key] = eval_value

        return substituted_data

    if isinstance(content, basestring):
        # content is in string format here
        for var, value in variables_mapping.items():
            if content == var:
                # content is a variable
                content = value
            else:
                if not isinstance(value, str):
                    value = builtin_str(value)
                content = content.replace(var, value)

    return content


def parse_parameters(parameters, variables_mapping, functions_mapping):
    """ parse parameters and generate cartesian product.

    Args:
        parameters (list) parameters: parameter name and value in list
            parameter value may be in three types:
                (1) data list, e.g. ["iOS/10.1", "iOS/10.2", "iOS/10.3"]
                (2) call built-in parameterize function, "${parameterize(account.csv)}"
                (3) call custom function in debugtalk.py, "${gen_app_version()}"

        variables_mapping (dict): variables mapping loaded from debugtalk.py
        functions_mapping (dict): functions mapping loaded from debugtalk.py

    Returns:
        list: cartesian product list

    Examples:
        >>> parameters = [
            {"user_agent": ["iOS/10.1", "iOS/10.2", "iOS/10.3"]},
            {"username-password": "${parameterize(account.csv)}"},
            {"app_version": "${gen_app_version()}"}
        ]
        >>> parse_parameters(parameters)

    """
    parsed_parameters_list = []
    for parameter in parameters:
        parameter_name, parameter_content = list(parameter.items())[0]
        parameter_name_list = parameter_name.split("-")

        if isinstance(parameter_content, list):
            # (1) data list
            # e.g. {"app_version": ["2.8.5", "2.8.6"]}
            #       => [{"app_version": "2.8.5", "app_version": "2.8.6"}]
            # e.g. {"username-password": [["user1", "111111"], ["test2", "222222"]}
            #       => [{"username": "user1", "password": "111111"}, {"username": "user2", "password": "222222"}]
            parameter_content_list = []
            for parameter_item in parameter_content:
                if not isinstance(parameter_item, (list, tuple)):
                    # "2.8.5" => ["2.8.5"]
                    parameter_item = [parameter_item]

                # ["app_version"], ["2.8.5"] => {"app_version": "2.8.5"}
                # ["username", "password"], ["user1", "111111"] => {"username": "user1", "password": "111111"}
                parameter_content_dict = dict(zip(parameter_name_list, parameter_item))

                parameter_content_list.append(parameter_content_dict)
        else:
            # (2) & (3)
            parsed_parameter_content = parse_data(parameter_content, variables_mapping, functions_mapping)
            # e.g. [{'app_version': '2.8.5'}, {'app_version': '2.8.6'}]
            # e.g. [{"username": "user1", "password": "111111"}, {"username": "user2", "password": "222222"}]
            if not isinstance(parsed_parameter_content, list):
                raise exceptions.ParamsError("parameters syntax error!")

            parameter_content_list = [
                # get subset by parameter name
                {key: parameter_item[key] for key in parameter_name_list}
                for parameter_item in parsed_parameter_content
            ]

        parsed_parameters_list.append(parameter_content_list)

    return utils.gen_cartesian_product(*parsed_parameters_list)


###############################################################################
##  parse content with variables and functions mapping
###############################################################################

def get_mapping_variable(variable_name, variables_mapping):
    """ get variable from variables_mapping.

    Args:
        variable_name (str): variable name
        variables_mapping (dict): variables mapping

    Returns:
        mapping variable value.

    Raises:
        exceptions.VariableNotFound: variable is not found.

    """
    try:
        if '.' in variable_name:
            top_query = variable_name.split('.', 1)[0]
            sub_query = variable_name.split('.', 1)[1]
            json_content = variables_mapping[top_query]
            json_content = transfer_json_string_to_dict(json_content)
            return query_json(json_content=json_content, query=sub_query, delimiter='.')
        return variables_mapping[variable_name]
    except (KeyError, exceptions.ExtractFailure) as err:
        # logger.log_debug("\n".join([str(err), traceback.format_exc()]))
        logger.log_error("【自定义变量未找到】变量名{}".format(variable_name))
        raise exceptions.VariableNotFound("{} is not found.".format(variable_name))


def get_mapping_function(function_name, functions_mapping):
    """ get function from functions_mapping,
        if not found, then try to check if builtin function.

    Args:
        function_name (str): variable name
        functions_mapping (dict): variables mapping

    Returns:
        mapping function object.

    Raises:
        exceptions.FunctionNotFound: function is neither defined in debugtalk.py nor builtin.

    """
    if function_name in functions_mapping:
        return functions_mapping[function_name]

    try:
        # check if builtin functions
        item_func = eval(function_name)
        if callable(item_func):
            # is builtin function
            return item_func
    except (NameError, TypeError):
        # is not builtin function
        logger.log_error("【自定义函数未找到】函数名{}".format(function_name))
        raise exceptions.FunctionNotFound("{} is not found.".format(function_name))


def parse_string_functions(content, variables_mapping, functions_mapping, runner=None):
    """ parse string content with functions mapping.

    Args:
        content (str): string content to be parsed.
        variables_mapping (dict): variables mapping.
        functions_mapping (dict): functions mapping.
        runner (object)

    Returns:
        str: parsed string content.

    Examples:
        >>> content = "abc${add_one(3)}def"
        >>> functions_mapping = {"add_one": lambda x: x + 1}
        >>> parse_string_functions(content, functions_mapping)
            "abc4def"

    """
    functions_list = extract_functions(content)
    for func_content in functions_list:
        # logger.log_debug("【执行函数】: {}".format(func_content))
        function_meta = parse_function(func_content)
        func_name = function_meta["func_name"]
        logger.log_info("【识别函数】: {}".format(func_name))

        args = function_meta.get("args", [])
        kwargs = function_meta.get("kwargs", {})
        args = parse_data(args, variables_mapping, functions_mapping)
        logger.log_info("【函数{0}参数列表】: {1}".format(func_name, args))
        kwargs = parse_data(kwargs, variables_mapping, functions_mapping)

        if func_name in ["parameterize", "P"]:
            from httprunner import loader
            eval_value = loader.load_csv_file(*args, **kwargs)
        else:
            func = get_mapping_function(func_name, functions_mapping)
            try:
                eval_value = func(*args, **kwargs)
                if eval_value is False:
                    logger.log_error("【函数{0}异常返回】: {1}".format(func_name, eval_value))
                else:
                    logger.log_info("【函数{0}返回】: {1}".format(func_name, eval_value))
            except Exception as err:
                logger.log_error("【函数{0}异常返回】: {1}".format(func_name, err.args[0]))
                eval_value = '自定义方法调用失败'

            if eval_value is False or eval_value == '自定义方法调用失败':
                if runner.running_hook == 'step_setup':
                    runner.step_setup_pass = False
                elif runner.running_hook == 'step_teardown':
                    runner.step_teardown_pass = False
                elif runner.running_hook == 'step_request_teardown':
                    runner.step_request_teardown_pass = False
                elif runner.running_hook == 'step_parse_variable':
                    runner.step_parse_variable_pass = False

        func_content = "${" + func_content + "}"
        if func_content == content:
            # content is a function, e.g. "${add_one(3)}"
            content = eval_value
        else:
            # content contains one or many functions, e.g. "abc${add_one(3)}def"
            content = content.replace(
                func_content,
                str(eval_value), 1
            )

    return content


def parse_string_variables(content, variables_mapping, runner=None):
    """ parse string content with variables mapping.

    Args:
        runner:
        content (str): string content to be parsed.
        variables_mapping (dict): variables mapping.

    Returns:
        str: parsed string content.

    Examples:
        >>> content = "/api/users/$uid"
        >>> variables_mapping = {"$uid": 1000}
        >>> parse_string_variables(content, variables_mapping)
            "/api/users/1000"

    """
    variables_list = extract_variables(content)
    for variable_name in variables_list:
        variable_not_found = False
        try:
            variable_value = get_mapping_variable(variable_name, variables_mapping)
        except (KeyError, exceptions.VariableNotFound) as err:
            # logger.log_debug("\n".join([str(err), traceback.format_exc()]))
            variable_not_found = True
            runner.variable_not_found = True

        if variable_not_found:
            break

        # TODO: replace variable label from $var to {{var}}
        if "${}".format(variable_name) == content:
            # content is a variable

            logger.log_info("【参数替换】: {content} 替换为==> {value}".format(content=content, value=variable_value))
            content = variable_value
        else:
            # content contains one or several variables
            if not isinstance(variable_value, str):
                variable_value = builtin_str(variable_value)

            logger.log_info("【参数替换】: ${name} 替换为==> {value}".format(name=variable_name, value=variable_value))
            content = content.replace(
                "${}".format(variable_name),
                variable_value, 1
            )

    return content


def parse_data(content, variables_mapping=None, functions_mapping=None, runner=None):
    """ parse content with variables mapping

    Args:
        content (str/dict/list/numeric/bool/type): content to be parsed
        variables_mapping (dict): variables mapping.
        functions_mapping (dict): functions mapping.
        runner (object)

    Returns:
        parsed content.

    Examples:
        >>> content = {
                'request': {
                    'url': '/api/users/$uid',
                    'headers': {'token': '$token'}
                }
            }
        >>> variables_mapping = {"uid": 1000, "token": "abcdef"}
        >>> parse_data(content, variables_mapping)
            {
                'request': {
                    'url': '/api/users/1000',
                    'headers': {'token': 'abcdef'}
                }
            }

    """
    # TODO: refactor type check
    if content is None or isinstance(content, (numeric_types, bool, type)):
        return content

    if isinstance(content, (list, set, tuple)):
        return [
            parse_data(item, variables_mapping, functions_mapping, runner=runner)
            for item in content
        ]

    if isinstance(content, dict):
        parsed_content = {}
        for key, value in content.items():
            parsed_key = parse_data(key, variables_mapping, functions_mapping, runner=runner)
            parsed_value = parse_data(value, variables_mapping, functions_mapping, runner=runner)
            parsed_content[parsed_key] = parsed_value

        return parsed_content

    if isinstance(content, basestring):
        # content is in string format here
        variables_mapping = variables_mapping or {}
        functions_mapping = functions_mapping or {}
        content = content.strip()

        # replace functions with evaluated value
        # Notice: _eval_content_functions must be called before _eval_content_variables
        content = parse_string_functions(content, variables_mapping, functions_mapping, runner=runner)

        # replace variables with binding value
        content = parse_string_variables(content, variables_mapping, runner=runner)

    return content


def transfer_json_string_to_dict(json_str):
    try:
        if isinstance(json_str, bytes):
            # bytes转str
            json_str = json_str.decode('utf-8')
            # str转dict
            return json.loads(json_str)
        elif isinstance(json_str, str):
            return json.loads(json_str)
        else:  # dict
            return json_str
    except json.decoder.JSONDecodeError:
        # json.loads异常时替换布尔类型后再次尝试，False => false , True => true
        json_str = json_str.replace('False', 'false').replace('True', 'true')
        try:
            dict_ = json.loads(json_str)
        except json.decoder.JSONDecodeError:
            dict_ = json_str
        return dict_
    except TypeError:
        return json_str


if __name__ == '__main__':
    # f = "teardown_db_operation(SELECT env_name,as FROM atp_auto_sit.env_info WHERE id='a';||$DB_CONNECT)"
    # f2 = "teardown_db_operation($TEARDOWN_SQL_1,$DB_CONNECT)"
    # f3 = "teardown_db_operation(INSERT * INTO `atp_auto_sit`.`env_info` (`env_name`) VALUES ('NEW2',\"666');||$DB_CONNECT)"
    # f4 = "${teardown_db_operation(INSERT INTO credit_audit.ca_mem_contact_info (APPL_NO,ACTIVATE_NO, MEMBER_ID, NAME, PHONE_NO,IMAGE,CREATE_TIME) VALUES (NULL,'20190912$mn','9001$mn','朱大叔收纸箱',13166343408,0,now()),(NULL,'20190912$mn','9001$mn','e~老男孩',613206,0, now()),(NULL,'20190912$mn','9001$mn','老男孩',613206,0, now());||$DB_CONNECT)}"
    # f5 = "${teardown_compare_log_content(loan-web||grep -E '发送\\[恢复额度消息\\]内容为' /usr/local/src/logs/loan-web-cell01-node01/sys.log||发送[恢复额度消息]内容为：[||]||{\"categoryId\":1,\"financialProductsType\":\"2\",\"memberId\":\"$member_id\",\"restoreLimit\":\"$repayAmt\"})}"
    # f5 = "${aaa()}"
    # x = re.findall(function_regexp, f5)
    # print(x)
    # # x = re.findall(function_regexp, f2)
    # # print(x)
    # # res = parse_function(f3)
    # # print(res)
    # c = " ${setup_db_operation(delete  from  `fish_club_user_db`.`member_weixin`  whe——re < !！《》，。？#@%`union>_id`='olyeRjg8NEwjAdI-KatgNn5c2po8'; \nINSERT (),VALUES('','{\"city\":\"\"}')||$DB_CONNECT)} "
    # c = "${setup_db_operation(insert  into  merchant_audit.ma_unionpay_merchant_apply  (merchant_id,status,apply_user_id	,apply_department_id)  values  (\"121701\",\"5\",\"100016\",\"20\");||$DB_CONNECT)}"
    # c = "${setup_db_operation(INSERT INTO `cashloan`.`device_json_info` (`member_id`, `data_json`, `create_time`) VALUES ('$member_id', '{\\\"deviceId\":\"$DEVICE_ID\",\"imei\":\"$DEVICE_ID\",\"ip\":\"211.140.201.18\",\"ipCity\":\"南京\",\"ipNet\":\"\",\"latitude\":\"38.863351\",\"longitude\":\"121.516488\",\"mac\":\"020000000000\",\"phoneBrand\":\" EDI-AL10 \",\"phoneType\":\"Android\",\"phoneVersion\":\"Android 8.0.0\"}', '2019-06-04 10:02:59');||$DB_CONNECT)}"
    #
    # res = re.findall(function_regexp, c)
    # print(res)
    #
    # list_ = extract_functions(c)
    # print(list_)
    #
    # mm = parse_function(x[0])
    # print(mm)
    # # for i in res:
    # #     res = parse_function(i)
    # #     print(res)

    new_variable_regexp = r"\$([\w]+[\w.]*)"
    res = re.findall(new_variable_regexp, "$aB_a0$a.0-.asd中文", re.A)
    print(res)
    # # variables_mapping = {"bb": {"a_a": ['555', '666'], "chaos": "myb"}}
    # # res = get_mapping_variable('bb.chaos.7', variables_mapping)
    # print(res, type(res))
