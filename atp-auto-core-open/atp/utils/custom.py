# -*- coding:utf-8 -*-

import calendar
import datetime
import json
import time
import random
import traceback
import inspect
import importlib

from dateutil.relativedelta import relativedelta

from atp.api.disconf_executor import disconf_execute, disconf_execute_new
from atp.api.http_client import HttpClient
from atp.api.mysql_sql_executor import sql_execute, db_operation_to_json, sql_execute_with_params
from atp.api.ssh_executor import server_upload_file
# from atp.httprunner.compat import basestring
from atp.utils.encryption import Encryption
from atp.utils.tools import (
    is_json_contains, generate_idcard, generate_random_num, json_loads, generate_phone, generate_bank_card_no,
    generate_random_str, get_sign_common, transfer_json_string_to_dict,
    get_repayment_plan_dic, generate_compute_expression, convert_mysql_datatype_to_py)
from atp.views.wrappers import custom_func_wrapper
from atp.api.ssh_client import SSHClient
from atp.api.get_log_content import GetLogContent
from atp.api.redis_api import RedisUtils
from atp.httprunner import logger as hr_logger
from atp.api.comm_log import logger

wait_max_time = 120
wait_time_sec = 2
basestring = (str, bytes)

""" custom functions
"""


@custom_func_wrapper
def get_json_dumps(json_):
    """ Json-序列化 : Json对象
    :desc: 说明: 将Json对象序列化，转为Json字符串
    :param json_:Json对象: 待序列化的Json对象
    """
    return json.dumps(json_).strip('"')


@custom_func_wrapper
def get_json_loads(json_):
    """ Json-反序列化 : Json字符串
    :desc: 说明: 将Json字符串反序列化，转为Json对象
    :param json_:Json字符串: 待反序列化的Json字符串
    """
    return json.loads(json_)


@custom_func_wrapper
def get_current_date(fmt="%Y-%m-%d"):
    """ 时间-获取当前日期
    get current date, default format is %Y-%m-%d
    :desc: 说明: 获取当前的日期，以%YYYY-%mm-%dd格式返回，例如 2019-09-10
    """
    return datetime.datetime.now().strftime(fmt)


@custom_func_wrapper
def get_current_time(fmt="%Y-%m-%d %H:%M:%S"):
    """ 时间-获取当前时间
    get current time, default format is %Y-%m-%d %H:%M:%S
    :desc: 说明: 获取当前的时间，以%YYYY-%mm-%dd %HH:%MM:%SS格式返回，例如 2019-09-10 11:12:13
    """
    return datetime.datetime.now().strftime(fmt)


@custom_func_wrapper
def get_deltatime(change=None):
    """ 时间-获取增量时间 : 增量
    get deltatime, default format is %Y-%m-%d %H:%M:%S
    :desc: 说明: 获取当前的时间，加上增量，以%YYYY-%mm-%dd %HH:%MM:%SS格式返回，例如 2019-09-10 11:12:13
    :param change:增量: 增减时间的量，+代表增加，-代表减去，d代表天，h代表小时，m代表分钟，s代表秒，例如 +3d 或 -10m 或 +50s
    """
    fmt = "%Y-%m-%d %H:%M:%S"
    now_time = datetime.datetime.now()
    if change:
        change = change.upper()
        unit_li = ['D', 'H', 'M', 'S']
        unit_dic = {'D': None, 'H': None, 'M': None, 'S': None}

        for k in unit_li:
            change_list = change.split(k)
            if len(change_list) == 2:
                unit_dic[k] = change_list[0]
                change = change_list[1]
            elif len(change_list) == 1:
                change = change_list[0]
            else:
                return 'Error'

        for k, v in unit_dic.items():
            if v:
                if k == 'D':
                    now_time += datetime.timedelta(days=int(v))
                elif k == 'H':
                    now_time += datetime.timedelta(hours=int(v))
                elif k == 'M':
                    now_time += datetime.timedelta(minutes=int(v))
                elif k == 'S':
                    now_time += datetime.timedelta(seconds=int(v))

    return now_time.strftime(fmt)


@custom_func_wrapper
def get_current_timestamp(length):
    """ 时间-获取当前时间戳 : 位数
    :desc: 说明: 获取当前的时间戳，返回10位或13位数字
    :param length:位数: 时间戳的位数，10或者13 二选一
    :return:
    """
    if str(length) == '10':
        return int(time.time())
    else:
        return int((time.time() * 1000))


@custom_func_wrapper
def get_deltatimestamp(length, change=None):
    """ 时间-获取增量时间戳 : 位数, 增量
    :desc: 说明: 获取当前的时间戳，加上增量，返回10位或13位数字
    :param length:位数: 时间戳的位数，10或者13 二选一
    :param change:增量: 增减时间的量，+代表增加，-代表减去，d代表天，h代表小时，m代表分钟，s代表秒，例如 +3d 或 -10m 或 +50s
    """
    now_time = datetime.datetime.now()
    if change:
        change = change.upper()
        unit_li = ['D', 'H', 'M', 'S']
        unit_dic = {'D': None, 'H': None, 'M': None, 'S': None}

        for k in unit_li:
            change_list = change.split(k)
            if len(change_list) == 2:
                unit_dic[k] = change_list[0]
                change = change_list[1]
            elif len(change_list) == 1:
                change = change_list[0]
            else:
                return 'Error'

        for k, v in unit_dic.items():
            if v:
                if k == 'D':
                    now_time += datetime.timedelta(days=int(v))
                elif k == 'H':
                    now_time += datetime.timedelta(hours=int(v))
                elif k == 'M':
                    now_time += datetime.timedelta(minutes=int(v))
                elif k == 'S':
                    now_time += datetime.timedelta(seconds=int(v))

    if str(length) == '10':
        return int(time.mktime(now_time.timetuple()))
    else:
        return int((time.mktime(now_time.timetuple()) * 1000))


@custom_func_wrapper
def get_month_range(change=None):
    """ 时间-获取当前月的总天数 : 增量
    :desc: 说明: 获取当前月的总天数，加上增量，返回月份的总天数
    :param change:增量: 增减月份的量，+代表增加，-代表减去，例如: +1代表下个月, -1代表上个月, 0代表当前月
    """
    change = int(change) if change else 0
    dt = datetime.datetime.now() + relativedelta(months=change)
    month_range = calendar.monthrange(dt.year, dt.month)
    # month_range: (3, 31)
    return month_range[1]


@custom_func_wrapper
def get_random_idcard(age=None):
    """ 生成-有效身份证号码 : 指定年龄
    :desc: 说明: 随机获取能通过身份证校验的的身份证号码
    :param age:指定年龄: 正整数，例如 20
    :return:
    """
    return generate_idcard(age=age)


@custom_func_wrapper
def get_random_phone_no(top, db_connect):
    """ 生成-随机手机号码 : 前三位
    :desc: 说明: 随机生成数据库中不存在的手机号码
    :param top:前三位: 例如 139
    :return:
    """
    while True:
        rand_phone = generate_phone(top)
        return_info = sql_execute("" % rand_phone,
                                  db_connect=db_connect)
        if return_info[0][0] == 1:
            continue
        else:
            break
    return rand_phone


@custom_func_wrapper
def get_random_member_id(db_connect):
    """
    :desc:
    :return:
    """
    random_sec = random.randint(0, 10000)
    new_last_gen_time = datetime.datetime.strptime("2017-11-14 17:46:06", "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=random_sec)
    new_last_gen_time = new_last_gen_time.strftime("%Y-%m-%d %H:%M:%S")
    while True:
        return_info = sql_execute("", db_connect=db_connect)
        max_member_id = return_info[0][0] + 1
        last_gen_time = return_info[0][1].strftime("%Y-%m-%d %H:%M:%S")
        update_sequence = "" % (str(max_member_id), new_last_gen_time, last_gen_time)
        return_info = sql_execute(update_sequence, db_connect=db_connect)
        if return_info == 1:
            break
    return int(max_member_id)


@custom_func_wrapper
def get_random_apply_no(order_type):
    """
    :desc:
    :param
    :return:
    """
    if str(order_type) == '0':
        return str(int(round(time.time() * 1000))) + str(random.randint(100, 999))
    elif str(order_type) == '1':
        return str('09') + str(random.randint(1000, 9999)) + str(int(time.time()))
    else:
        return False, "订单类型输入有误"


@custom_func_wrapper
def get_random_bank_card_no(card_front, card_no_len):
    """ 生成-随机银行卡号 : 6位数BIN码, 长度
    :desc: 说明: 随机生成指定BIN码和长度的银行卡号
    :param card_front:6位数BIN码: 例如 325222
    :param card_no_len:长度: 银行卡卡号的总长度 例如 18
    :return:
    """
    res = generate_bank_card_no(str(card_front), card_no_len, 1)
    return res[0] if isinstance(res, list) else res


@custom_func_wrapper
def get_random_num(min_, max_):
    """ 生成-区间内随机数(左开右闭) : 最小值, 最大值
    :desc: 说明: 生成间内随机数(左开右闭)
    :param min_:最小值: 例如 1000
    :param max_:最大值: 例如 9999
    :return:
    """
    return generate_random_num(int(min_), int(max_))


@custom_func_wrapper
def get_random_str(length, head):
    """ 生成-随机字符串 : 总长度, 以开头
    :desc: 说明: 随机指定长度和开头的生成字符串
    :param length:总长度: 例如 10
    :param head:以开头: 例如 Test
    :return:
    """
    return generate_random_str(length, head)


@custom_func_wrapper
def get_repayment_plan_dict(start_timestamp, term_total, capital_no=None):
    """ 生成-还款计划对象 : 放款时间戳, 期数, 资方编号
    :desc: 说明: 指定放款时间和期数，生成还款计划对象，返回格式例如: {1: ['2019-01-31', '2019-02-28'], 2: ['2019-02-28', '2019-03-31'], 3: ['2019-03-31', '2019-04-30']}
    :param start_timestamp:放款时间戳: 10位或13位，例如 1548864000或1548864000000
    :param term_total:期数: 例如 6
    :param capital_no:资方编号: 例如 045 或 056
    :return:
    """
    return get_repayment_plan_dic(start_timestamp, term_total, capital_no)


@custom_func_wrapper
def compute_expression(expression, digits):
    """ 计算-四则运算 : 数学表达式, 小数点位数
    :desc: 说明: 随机指定长度和开头的生成字符串
    :param expression:数学表达式:支持+,-,*,/四则运算, 例如 (55+44)/100*2
    :param digits:小数点位数: 计算结果保留几位小数，其中0代表结果保存为整数，例如 0或2
    :return:
    """
    return generate_compute_expression(expression, int(digits))


@custom_func_wrapper
def encrypt_by_public_key(plain_text, public_key, remote_host):
    """ 加密-根据公钥加密 : 待加密文本, 公钥
    :desc: 说明: 根据公钥对待加密文本加密，返回加密后的文本
    :param plain_text:待加密文本:
    :param public_key:公钥:
    :return:
    """
    kwargs = {
        "remote_host": remote_host
    }
    e = Encryption(**kwargs)
    content = e.encrypt_public_key(plain_text, public_key)

    return content


@custom_func_wrapper
def encrypt_by_aes128(plain_text, public_key, remote_host):
    """ 加密-AES加密 : 代加密文本, 公钥
    :desc: 说明: 根据公钥对待加密文本AES加密，返回加密后的文本
    :param plain_text:待加密文本:
    :param public_key:公钥:
    :return:
    """

    kwargs = {
        "remote_host": remote_host
    }
    e = Encryption(**kwargs)
    content = e.aes(public_key, plain_text)

    return content


@custom_func_wrapper
def get_sso_login_ticket(username, password, service):
    """ 登录-单点登录 : 用户名, 密码, 服务
    :desc: 说明: 根据用户名+密码做单点登录，返回ticket
    :param username:用户名:
    :param password:密码:
    :param service:服务:
    :return:
    """

    data = {"username": username, "password": password, "service": service}
    url = ""
    header_info = {"header_info": "application/x-www-form-urlencoded"}
    hc = HttpClient()
    r = hc.http_post(url, header_info, data)
    redirect_url = r.headers["Location"]
    redirect_data = {"service": service}
    r = hc.http_post(redirect_url, header_info, redirect_data)

    return r.text


@custom_func_wrapper
def get_sso_login_cookie(username, password, url):
    """ 登录-单点登录(旧版) : 用户名, 密码, 请求url
    :desc: 说明: 根据用户名+密码做单点登录，返回cookie
    :param username:用户名: 例如
    :param password:密码: 例如 DwzlXxGYZGU=
    :param url:请求url:
    :return:
    """

    heard_info = {'Content-Type': 'application/x-www-form-urlencoded', }  # form表单提交
    body_for_cta = {"userName": username, "password": password}

    hc = HttpClient()
    post_url = url + '/getSt'
    response = hc.http_post(post_url, heard_info, body_for_cta)
    ticket = json.loads(response.text)['data']['ticket']  # 获取重定向的url
    session = json.loads(response.text)['data']['session']  # 获取cta-web-token

    redirect_url = url + '?ticket=' + ticket
    response = hc.http_get(redirect_url, heard_info)  # 请求重定向url
    jSessionId = response.headers['Set-Cookie'].split(';')[0]  # 获取JSESSIONID
    cta_web_token = 'cta-web-token=' + session
    return jSessionId + '; ' + cta_web_token


@custom_func_wrapper
def get_access_token(phone, base_host, redis_connect, db_connect):
    """ 登录-手机号动码登录获取accessToken : 手机号
    :desc: 说明: 指定手机号，依次调用获取验证码和动码登录接口，返回accessToken
    :param phone:手机号: 例如 18555555555
    :return:
    """
    # 根据手机号获取memberid
    # 根据memberid获取token
    try:
        _redis_connect = json.loads(redis_connect)
    except Exception as err:
        raise Exception('环境信息中redis连接配置错误')
    redis_host = _redis_connect['host']
    redis_port = _redis_connect['port']
    redis_password = _redis_connect['password']


    get_member_id_sql = "" % phone
    ret = sql_execute(get_member_id_sql, db_connect=db_connect)
    if ret and ret[0][0]:
        member_id = ret[0][0]
        with RedisUtils(redis_host, redis_port, redis_password, 2) as r:
            user_info = r.get_str_value('user_token_%s' % (str(member_id)))
        if isinstance(user_info, dict):
            return user_info['accessToken']

    hr_logger.log_info('【执行函数{0}】Redis中获取不到手机号【{1}】的accessToken数据，将调用动码登录接口获取'
                       .format(inspect.stack()[0][3], phone))
    current_timestamp = int((time.time() * 1000))
    heard_info = {'Content-Type': 'application/json;charset=utf-8'}
    send_code_url = base_host + '/user/v2/common/sendMobileCode'
    send_code_input = {
        "appld":  "6916984",
        "phone":  str(phone),
        "sourceFlag":  "1",
        "timestamp":  current_timestamp,
    }

    # 加签
    send_code_input = get_sign_common(send_code_input)

    # 获取验证码
    hc = HttpClient()
    try:
        response = hc.http_post(send_code_url, heard_info, send_code_input)
    except Exception as err:
        raise err
    res_dic = json.loads(response.text)
    hr_logger.log_info('【执行函数{0}】获取验证码接口返回内容{1}'.format(inspect.stack()[0][3], response.text))

    if 'content' not in res_dic:
        raise Exception('【执行函数{0}】调用获取验证码接口没有返回content字段，接口返回内容{1}'
                        .format(inspect.stack()[0][3], response.text))
    if 'serialNo' not in res_dic['content']:
        raise Exception('【执行函数{0}】调用获取验证码接口没有返回serialNo字段，接口返回内容{1}'
                        .format(inspect.stack()[0][3], response.text))
    serial_no = eval(res_dic['content'])['serialNo']

    login_url = base_host + '/user/login/v3/phoneLogin'
    login_input = {
        "phone":  str(phone),
        "smsSerialNo":  serial_no,
        "timestamp":  current_timestamp,
        "verifyCode":  "8888",
    }
    # 加签
    login_input = get_sign_common(login_input)

    # 动码登录
    try:
        response = hc.http_post(login_url, heard_info, login_input)
    except Exception as err:
        raise err

    res_dic = json.loads(response.text)
    hr_logger.log_info('【执行函数{0}】动码登录接口返回内容{1}'.format(inspect.stack()[0][3], response.text))

    if 'accessToken' not in res_dic:
        raise Exception('调用登录接口没有返回accessToken字段，接口返回内容{0}'.format(response.text))
    access_token = res_dic['accessToken']

    if not access_token:
        raise Exception('动码登录失败，具体原因请参考上面日志中动码登录接口返回内容')

    return access_token


@custom_func_wrapper
def disconf_query(env_name, disconf_id, disconf_name):
    """ disconf-查询disconf当前配置值 : Env_Name, Id, Name
    :desc: 说明: 查询disconf当前指定配置的值
    :param env_name:Env_Name: 环境名称，例如 ALIUAT
    :param disconf_id:Id: disconf配置id，例如 34
    :param disconf_name:Name: disconf配置内容中的key，例如 baseUrl
    :return:
    """
    disconf_obj = {
        "env_name": env_name,
        "disconf_method": "query",
        "disconf_id": disconf_id,
        "disconf_name": disconf_name,
        "disconf_value": "",
    }
    return disconf_execute(disconf_obj)


@custom_func_wrapper
def get_from_log_content(app_name, ssh_cmd, start_with, end_with, server_app_map, server_default_user):
    """ 日志-从日志中获取 : 应用名, grep命令, 起始字符, 结束字符
    :desc: 说明: 从日志中按相应条件获取内容并返回
    :param app_name: 应用名: 如loan-web，同环境配置中IP-应用映射表中应用名称保持一致
    :param ssh_cmd: 过滤命令:使用grep xxx 过滤出符合条件的日志，如grep "成功发送通知消息" "/usr/local/src/logs/ups-service-cell01-node01/sys.log"
    :param start_with: 起始字符: 从日志中筛选起始字符后的内容
    :param end_with: 结束字符: 从日志中筛选结束字符前的内容
    :return:
    """
    server_app_map = json.loads(server_app_map)
    server_default_user = json.loads(server_default_user)
    app_server_ip = ""
    for k, v in server_app_map.items():
        if app_name in v:
            app_server_ip = k
            break
    if not app_server_ip:
        raise Exception("根据应用名找不到匹配的服务器IP")

    if not ssh_cmd.startswith("grep"):
        raise Exception("为了安全考虑，目前暂只支持grep命令")

    ssh_server_info = [app_server_ip, "22", server_default_user['user'], server_default_user['password']]
    try:
        with SSHClient(ssh_server_info) as sc:
            logs = sc.exec_cmd(ssh_cmd)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise Exception('出现未知错误: {0}'.format(repr(e)))

    if not logs:
        raise Exception("日志中未找到匹配的内容")

    des_logs = logs.split("\n")[:-1]
    if len(des_logs) > 1:
        raise Exception("日志中找到超过一条匹配记录，请增加过滤条件！")

    glc = GetLogContent(des_logs[0], start_with, end_with)
    actual_value = glc.get_log_content()
    return actual_value


@custom_func_wrapper
def get_redis_value(db_num, key, redis_connect):
    """ Redis-获取指定key的值 : 库编号, 键名称
    :desc: 说明: 根据键名称查询键值
    :param db_num:库编号: 需要查询的键值对所在的库索引
    :param key:键名称: 查询使用的键名称
    :return:
    """
    try:
        _redis_connect = json.loads(redis_connect)
    except Exception as err:
        raise Exception('环境信息中redis连接配置错误')

    redis_host = _redis_connect['host']
    redis_port = _redis_connect['port']
    redis_password = _redis_connect['password']

    with RedisUtils(redis_host, redis_port, redis_password, db_num) as r:
        return r.get_str_value(key)


""" custom comparators
"""

@custom_func_wrapper
def db_validate(check_value, expect_value):
    """ 数据库-单字段校验(即时) : 校验sql, 预期结果
    :desc: 说明: 立即验证查询SQL的结果和期望值是否完全一致
    :param check_value:待校验内容: 查询单字段的SQL语句，例如 select merchant_no from accounting.fss_loans WHERE loan_id='$loan_id';
    :param expect_value:期望值: 例如 023 或 $my_var
    :return:
    """

    try:
        if check_value == expect_value:
            return True
        elif str(check_value) == str(expect_value):
            return True
        else:
            return False, '预期结果是"{0}", 实际结果是"{1}"'.format(expect_value, check_value)
    except:
        return False


@custom_func_wrapper
def db_validate_cycle(check_value, expect_value):
    """ 数据库-单字段校验(轮询) : 校验sql, 预期结果
    :desc: 说明: 30s内轮询验证查询SQL的单字段结果和期望值是否一致， 当查询SQL结果和期望值都是json时，自动转为json包含校验
    :param check_value: 待校验内容: 查询单字段的SQL语句，支持在SQL结束符';'后填一个正整数指定轮询超时时间，例如 select merchant_no from accounting.fss_loans WHERE loan_id='$loan_id';15
    :param expect_value: 期望值: 例如 023 或 {"a": "b", "c": "d"}
    :return:
    """
    dict_expect = transfer_json_string_to_dict(expect_value)
    if isinstance(dict_expect, (dict, list)):
        dict_check = transfer_json_string_to_dict(check_value)
        try:
            return is_json_contains(dict_check, dict_expect)
        except Exception as e:
            return False, format(e)
    else:
        try:
            if check_value == expect_value:
                return True
            elif str(check_value) == str(expect_value):
                return True
            else:
                return False, '预期结果是"{0}", 实际结果是"{1}"'.format(expect_value, check_value)
        except Exception as e:
            return False, format(e)


@custom_func_wrapper
def db_json_validate(dict_check, dict_expect):
    """ 数据库-多字段校验(轮询) : 校验sql, 预期结果
    :desc: 说明: 30s内轮询验证查询SQL的多字段结果和期望值是否一致
    :param dict_check: 待校验内容: 查询多字段的SQL语句，支持在SQL结束符';'后填一个正整数指定轮询超时时间，例如 select merchant_no,term_total from accounting.fss_loans WHERE loan_id='$loan_id';15
    :param dict_expect: 期望值: 必须json格式，其中key和查询SQL中的字段名对应，例如 {"merchant_no": $my_var, "term_total": 12}
    :return:
    """

    dict_check = transfer_json_string_to_dict(dict_check)
    dict_expect = transfer_json_string_to_dict(dict_expect)

    dict_check_lower_key = {key.lower(): dict_check[key] for key in dict_check}
    dict_expect_lower_key = {key.lower(): dict_expect[key] for key in dict_expect}
    # for key in dict_check:
    #     dict_check_lower_key[key.lower()] = dict_check[key]
    # for key in dict_expect:
    #     dict_expect_lower_key[key.lower()] = dict_expect[key]
    # 返回True和False或者(False, 'err_msg'),关联测试报告success和fail
    try:
        return is_json_contains(dict_check_lower_key, dict_expect_lower_key)
    except:
        return False


@custom_func_wrapper
def json_contains(check_value, expect_value):
    """ 接口响应-json包含校验 : 校验, 预期结果
    :desc: 说明: 验证待校验内容作为json是否包含期望值json
    :param check_value: 待校验内容: 指定待校验的内容，支持多层级，例如 content，content.demoList.0.code，headers
    :param expect_value: 期望值: 例如 {"code": "000","desc":"成功!", "msg": "$my_var"}
    :return:
    """
    try:
        if isinstance(check_value, bytes):
            # bytes转str
            str_content = check_value.decode('utf-8')
            # str转dict
            dict_check = json.loads(str_content)
        elif isinstance(check_value, str):
            dict_check = json.loads(check_value)
        else:  # dict
            dict_check = check_value
    except json.decoder.JSONDecodeError:
        dict_check = check_value

    # assert isinstance(expect_value, basestring)

    try:
        dict_expect = json.loads(expect_value)
    except json.decoder.JSONDecodeError:
        # json.loads异常时替换布尔类型后再次尝试，False => false , True => true
        expect_value = expect_value.replace('False', 'false').replace('True', 'true')
        try:
            dict_expect = json.loads(expect_value)
        except json.decoder.JSONDecodeError:
            dict_expect = expect_value
    except TypeError:
        dict_expect = expect_value

    # dict_check和dict_expect是字符串/数字/布尔的情况
    if isinstance(dict_expect, (str, int, bool)) and isinstance(dict_check, (str, int, bool)):
        if str(dict_expect) == str(dict_check):
            return True
        else:
            return False, '预期结果是"{0}", 实际结果是"{1}"'.format(str(dict_expect), str(dict_check))

    # 返回True和False或者(False, 'err_msg'),关联测试报告success和fail
    try:
        # assert is_json_contains(dict_check, dict_expect)
        res = is_json_contains(dict_check, dict_expect)
        return res
    except Exception as err:
        return False, err.args[0]


@custom_func_wrapper
def json_same(check_value, expect_value):
    """ 接口响应-json完全匹配校验 : 校验, 预期结果
    :desc: 说明: 验证待校验内容作为json是否和期望值json完全一致
    :param check_value: 待校验内容: 指定待校验的内容，支持多层级，例如 content，content.demoList.0.code，headers
    :param expect_value: 期望值: 例如 {"code": "000","desc":"成功!", "msg": "$my_var"}
    :return:
    """

    dict_check = transfer_json_string_to_dict(check_value)
    dict_expect = transfer_json_string_to_dict(expect_value)

    # dict_check和dict_expect是字符串/数字的情况
    if isinstance(dict_expect, (str, int)) and isinstance(dict_check, (str, int)):
        if str(dict_expect) == str(dict_check):
            return True
        else:
            return False, '预期结果是"{0}", 实际结果是"{1}"'.format(str(dict_expect), str(dict_check))

    # 返回True和False或者(False, 'err_msg'),关联测试报告success和fail
    try:
        # assert is_json_contains(dict_check, dict_expect)
        res = is_json_contains(dict_check, dict_expect)
        if res is not True:
            return res
        res = is_json_contains(dict_expect, dict_check)
        return res
    except Exception as err:
        return False, err.args[0]


@custom_func_wrapper
def field_special_check(check_value, expect_value):
    """ 接口响应-字段特殊校验 : 校验, 预期结果
    :desc: 说明: 验证返回报文中的某个字段的值为空或者非空, 空可以是null或''
    :param check_value:待校验内容: 指定返回报文中的某个字段，支持多层级，例如 content.code，content.demoList.0
    :param expect_value: 期望值: 非空/空 二选一
    :return:
    """
    _support_check_list = ['非空', '空']
    check_type = str(expect_value).strip()
    if check_type not in _support_check_list:
        return False, '不支持\'{0}\'预期，已支持的字段特殊校验预期是{1}，请选择其中一种填写'.format(check_type, _support_check_list)
    if check_type == '非空':
        if check_value == '' or check_value is None:
            return False, '校验的字段为空'
        else:
            return True
    elif check_type == '空':
        if check_value == '' or check_value is None:
            return True
        else:
            return False, '校验的字段不为空，值为 {}'.format(check_value)


@custom_func_wrapper
def field_check_empty_list(check_value, expect_value):
    """ 接口响应-字段为空list校验 : 校验, 预期结果
    :desc: 说明: 验证返回报文中的某个字段的值的类型是list，并且不包含任意元素
    :param check_value:待校验内容: 指定返回报文中的某个字段，支持多层级，例如 content.demoList
    :param expect_value: 期望值: 任意字符
    :return:
    """
    # 返回true和false,关联测试报告success和fail
    try:
        if isinstance(check_value, list):
            if len(check_value) == 0:
                return True
            else:
                return False, '预期结果是[], 实际结果是{0}'.format(check_value)
        else:
            return False, '预期结果是[], 实际结果是{0}, 实际结果类型为{1}'.format(check_value, type(check_value))
    except Exception as err:
        return False, err.args[0]


@custom_func_wrapper
def field_check_not_empty_list(check_value, expect_value):
    """ 接口响应-字段为非空list校验 : 校验, 预期结果
    :desc: 说明: 验证返回报文中的某个字段的值的类型是list,并且至少包含一个元素
    :param check_value:待校验内容: 指定返回报文中的某个字段，支持多层级，例如 content.demoList
    :param expect_value: 期望值: 任意字符
    :return:
    """
    # 返回true和false,关联测试报告success和fail
    try:
        if isinstance(check_value, list):
            if len(check_value) != 0:
                return True
            else:
                return False, '预期结果是非空list, 实际结果是{0}'.format(check_value)
        else:
            return False, '预期结果是非空list, 实际结果是{0}, 实际结果类型为{1}'.format(check_value, type(check_value))
    except Exception as err:
        return False, err.args[0]


@custom_func_wrapper
def field_check_not_in_json(check_value, expect_value):
    """ 接口响应-字段为json类型且不包含期望key : 校验, 预期结果
    :desc: 说明: 验证返回报文中的某个字段的值的类型是json，并且不包含期望key
    :param check_value:待校验内容: 指定返回报文中的某个字段，支持多层级，例如 content.demoList.0
    :param expect_value: 期望值: 期望不被包含的key
    :return:
    """
    # 返回true和false,关联测试报告success和fail
    try:
        if isinstance(check_value, dict):
            if expect_value not in check_value.keys():
                return True
            else:
                return False, '待校验的字段值是{0}, 包含了期望key{1}'.format(check_value, expect_value)
        else:
            return False, '待校验的字段值是{0}, 类型为{1}'.format(check_value, type(check_value))
    except Exception as err:
        return False, err.args[0]


def field_check_not_in_list(check_value, expect_value):
    """ 接口响应-字段为list类型且不包含期望值 : 校验, 预期结果
    :desc: 说明: 验证返回报文中的某个字段的值的类型是list，并且不包含期望值
    :param check_value:待校验内容: 指定返回报文中的某个字段，支持多层级，例如 content.demoList
    :param expect_value: 期望值: 期望不被包含的值
    :return:
    """
    # 返回true和false,关联测试报告success和fail
    try:
        if isinstance(check_value, list):
            if expect_value not in check_value:
                # json like
                if (expect_value.startswith('[') and expect_value.endswith(']')) or (expect_value.startswith('{') and expect_value.endswith('}')):
                    try:
                        expect_value = json_loads(expect_value)
                    except json.decoder.JSONDecodeError:
                        return True
                    if expect_value not in check_value:
                        return True
                    else:
                        return False, '待校验的字段值是{0}, 包含了期望值{1}'.format(check_value, expect_value)
                # num like
                elif expect_value.isdigit():
                    try:
                        expect_value = int(expect_value)
                    except ValueError:
                        return True
                    if expect_value not in check_value:
                        return True
                    else:
                        return False, '待校验的字段值是{0}, 包含了期望值{1}'.format(check_value, expect_value)
                # True/False like
                elif 'rue' in expect_value or 'alse' in expect_value:
                    if expect_value == 'true' or expect_value == 'True':
                        expect_value = True
                        if expect_value not in check_value:
                            return True
                        else:
                            return False, '待校验的字段值是{0}, 包含了期望值{1}'.format(check_value, expect_value)
                    elif expect_value == 'false' or expect_value == 'False':
                        expect_value = False
                        if expect_value not in check_value:
                            return True
                        else:
                            return False, '待校验的字段值是{0}, 包含了期望值{1}'.format(check_value, expect_value)
                    else:
                        return True
                else:
                    return True
            else:
                return False, '待校验的字段值是{0}, 包含了期望值{1}'.format(check_value, expect_value)
        else:
            return False, '待校验的字段值是{0}, 类型是{1}'.format(check_value, type(check_value))
    except Exception as err:
        return False, err.args[0]


def field_check_empty_json(check_value, expect_value):
    """ 接口响应-字段为空json校验 : 校验, 预期结果
    :desc: 说明: 验证返回报文中的某个字段的值的类型是json，并且不包含任何键值对
    :param check_value:待校验内容: 指定返回报文中的某个字段，支持多层级，例如 content.demoList.0
    :param expect_value: 期望值: 任意字符
    :return:
    """
    # 返回true和false,关联测试报告success和fail
    try:
        if isinstance(check_value, dict):
            if len(check_value) == 0:
                return True
            else:
                return False, '预期结果是{}, 实际结果是{0}'.format(check_value)
        else:
            return False, '预期结果是{}, 实际结果是{0}, 实际结果类型为{1}'.format(check_value, type(check_value))
    except Exception as err:
        return False, err.args[0]


def field_check_not_empty_json(check_value, expect_value):
    """ 接口响应-字段为非空json校验 : 校验, 预期结果
    :desc: 说明: 验证返回报文中的某个字段的值的类型是json，并且至少包含一组键值对
    :param check_value:待校验内容: 指定返回报文中的某个字段，支持多层级，例如 content.demoList.0
    :param expect_value: 期望值: 任意字符
    :return:
    """
    # 返回true和false,关联测试报告success和fail
    try:
        if isinstance(check_value, dict):
            if len(check_value) != 0:
                return True
            else:
                return False, '预期结果是非空json, 实际结果是{0}'.format(check_value)
        else:
            return False, '预期结果是非空json, 实际结果是{0}, 实际结果类型为{1}'.format(check_value, type(check_value))
    except Exception as err:
        return False, err.args[0]


def field_check_list_length(check_value, expect_value):
    """ 接口响应-字段为list类型校验长度 : 校验, 预期结果
    :desc: 说明: 验证返回报文中的某个字段的值的类型是list时，长度等于期望结果
    :param check_value:待校验内容: 指定返回报文中的某个字段，支持多层级，例如 content.demoList.0
    :param expect_value: 期望值: list长度
    :return:
    """
    # 返回true和false,关联测试报告success和fail
    try:
        if isinstance(check_value, list):
            if len(check_value) == expect_value:
                return True
            else:
                return False, '预期结果中长度是{0}，实际结果中长度是{1}'.format(expect_value, len(check_value))
        else:
            return False, '预期结果非list，不支持使用该断言'
    except Exception as err:
        return False, err.args[0]


@custom_func_wrapper
def redis_validate(check_value, expect_value):
    """ redis-key值包含校验 : 查询key, 预期结果
    :desc: 说明: 根据指定的key和db_num查询值，并同预期结果比对
    :param check_value:待校验内容: 需要查询的db_num和key，以json格式，如{"db_num": 2, "redis_key": "user_token_9998742"}，支持使用变量
    :param expect_value:期望值: 例如 "abc" 或 {"a": 123, "b": "xxx"}，支持使用变量
    :return:
    """
    # 返回ture和flase,关联测试报告success和fail
    if isinstance(check_value, dict) and isinstance(expect_value, dict):
        return is_json_contains(check_value, expect_value)

    if check_value == expect_value:
        return True
    elif str(check_value) == str(expect_value):
        return True
    else:
        return False, '预期结果和实际结果不一致。预期结果是"{0}", 实际结果是"{1}"'.format(expect_value, check_value)


@custom_func_wrapper
def mq_validate(check_value, expect_value):
    """ mq-消息内容包含校验 : topic+tag+system_name, 预期结果
    :desc: 说明: 根据topic+tag+system_name查询消息，同预期结果匹配
    :param check_value:待校验内容: 需要查询的消息topic和tag，以json格式，如{"topic": "TP_MIME_UNION_FINANCE", "tag": "TAG_capital-mgmt-core_createCashLoan", "system_name": "user-core"}，支持使用变量
    :param expect_value:期望值: 例如 "abc" 或 {"a": 123, "b": "xxx"}，支持使用变量
    :return:
    """
    # 返回ture和flase,关联测试报告success和fail
    if not check_value:
        return False, '根据topic和tag获取不到最近10分钟的MQ消息'

    # hr_logger.log_info(str(len(check_value)))
    for index, item in enumerate(check_value):
        hr_logger.log_info('消息({0})内容：{1}'.format(str(index+1), item))
        try:
            dict_check = json.loads(item)
            # hr_logger.log_info(type(dict_check).__name__)
            if not isinstance(expect_value, dict):
                return False, '预期结果和实际结果类型不一致，预期结果是"{0}"，期望结果是"{1}"'.format(type(dict_check).__name__, type(expect_value).__name__)

            is_ok = is_json_contains(dict_check, expect_value)
            # hr_logger.log_info(type(is_ok).__name__)
            if is_ok is True:
                return True
            else:
                continue

        except Exception as err:
            hr_logger.log_error(traceback.format_exc())
            dict_check = item

        if dict_check == expect_value:
            return True
        elif str(dict_check) == str(expect_value):
            return True
        else:
            continue

    return False, '找不到同预期结果匹配的MQ消息'


""" custom sign
"""


@custom_func_wrapper
def add_sign_common(request, remote_host):
    """ 加签(common) :
    :param remote_host:
    :param request:
    :return:
    """


""" custom setup-hooks
"""
@custom_func_wrapper
def setup_sleep_N_secs(n_secs):
    """ 时间-sleep : 秒
    :desc: 说明: 等待指定秒数
    :param n_secs:秒: 等待的秒数，例如 5
    """
    time.sleep(n_secs)


@custom_func_wrapper
def setup_db_operation(sql, db_connect):
    """ 数据库-执行SQL语句 : sql
    :desc: 说明: 执行SQL语句
    :param sql:sql: 需要执行的SQL语句，支持多条SQL按;分隔
    :return:
    """
    sql_execute(sql, db_connect=db_connect)


@custom_func_wrapper
def setup_wait_until_db_result_succeed(wait_time, sql, expect_value, db_connect):
    """ 数据库-轮询SQL等待结果为期望值 : wait_time, sql, expect_value
    :desc: 说明: 等待时间内，轮询查询SQL，直到SQL结果等于期望值
    :param wait_time: wait_time:等待时间秒数，例如 15
    :param sql: sql:需要执行的查询的SQL
    :param expect_value: expect_value:预期结果
    :return:
    """
    wait_time = int(wait_time)
    if wait_time > wait_max_time:
        wait_time = wait_max_time
    for time_no in range(wait_time):
        return_info = sql_execute(sql, db_connect=db_connect)
        if len(return_info) != 0:
            if str(return_info[0][0]) == str(expect_value):
                return True
        time.sleep(wait_time_sec)
    raise Exception('{0}秒内执行sql未返回期望结果{1}'.format(str(wait_time), str(expect_value)))


@custom_func_wrapper
def setup_fund_order_conf(args, db_connect):
    """ 数据库-配置资金方匹配规则 : 规则参数
    :desc: 说明: 写入capital.conf_order_fund表，设置资金方匹配规则
    :param args: 规则参数: 例如 {"idNo":"$ID_NO","applyAmount":"$applyAmount","termNo":"$termValue","repaymentWay":"554","fund":"$fund_id"}
    :return:
    """
    id_no = args['idNo']
    order_amount = args['applyAmount']
    term_no = args['termNo']
    repayment_way = args['repaymentWay']
    fund = args['fund']
    industry_type = args.pop('industry_type', None)
    is_accept_unclear = args.pop('is_accept_unclear', None)
    fund_level = args.pop('fund_level', None)
    product_type = args.pop('productType', 0)
    sql_user_age = "".format(
        id_no=id_no)
    user_age = sql_execute(sql_user_age, db_connect=db_connect)
    max_user_age = user_age[0][0]
    min_user_age = user_age[0][1]
    # sql_min_id = "SELECT MIN(id)-1 FROM capital.`conf_order_fund`;"
    # min_id = sql_execute(sql_min_id, db_connect=db_connect)[0][0]
    min_id = ""

    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    industry_type = industry_type if industry_type else '100013'
    is_accept_unclear = is_accept_unclear if is_accept_unclear else '10'
    fund_level = fund_level if fund_level else '0'

    # 检查规则是否唯一
    sql_check_unique = "".format(term_no=term_no, order_amount=order_amount, fund_level=fund_level, repayment_way=repayment_way, fund=fund)
    res = sql_execute(sql_check_unique, db_connect=db_connect)
    if res[0][0] > 0:
        return True, '已有相同资金方匹配规则, 未新写入规则'

    sql_fund_order_conf = "".format(min_id=min_id,order_amount=order_amount,min_user_age=min_user_age,max_user_age=max_user_age,term_no=term_no,repayment_way=repayment_way,fund=fund,create_time=now_time,industry_type=industry_type,is_accept_unclear=is_accept_unclear,fund_level=fund_level, product_type=product_type)
    sql_execute(sql_fund_order_conf, db_connect=db_connect)


@custom_func_wrapper
def setup_disconf_operation(env_name, disconf_id, disconf_method, disconf_name, disconf_value):
    """ disconf-前置操作disconf : Env_Name, Id, Method,  Name, Value
    :desc: 说明: 对disconf进行操作，支持新增/编辑/删除disconf的某一行配置
    :param env_name:Env_Name: 环境名称，例如 ALIUAT
    :param disconf_id:Id: disconf配置id，例如 34
    :param disconf_method:Method: 操作方法，add/edit/delete 三选一
    :param disconf_name:Name: disconf配置内容中某一行的key，例如 baseUrl
    :param disconf_value:Value: 更新后的值
    :return:
    """
    disconf_obj = {
        "env_name": env_name,
        "disconf_method": disconf_method,
        "disconf_id": disconf_id,
        "disconf_name": disconf_name,
        "disconf_value": str(disconf_value),
    }
    disconf_execute(disconf_obj)


@custom_func_wrapper
def setup_disconf_operation_merge(kwargs, disconf_host):
    """ disconf-前置操作disconf(合并参数) : 参数
    :desc: 说明: 对disconf进行操作，支持新增/编辑/删除disconf的某一行配置
    :param kwargs: 参数:包含disconf_method、disconf_id、disconf_name、disconf_value的参数字典。示例:{"disconf_method":"edit","disconf_id":"653","disconf_name":"huixin.url","disconf_value":"https://hx-uat.huixinfintech.com/gateway/mime/loan/"}
        :param disconf_host:
    :return:
    """
    if isinstance(kwargs, basestring):
        kwargs = json.loads(kwargs)
    if 'disconf_method' in kwargs.keys() and 'disconf_id' in kwargs.keys() and 'disconf_name' in kwargs.keys() and 'disconf_value' in kwargs.keys():
        kwargs['disconf_host'] = disconf_host
        disconf_execute_new(kwargs)
        return True
    else:
        raise Exception('操作disconf失败')


@custom_func_wrapper
def setup_zx_base_file_move(base_file_ori_path, base_file_des_path, server_app_map, server_default_user):
    """ 服务器-移动征信基础测试报文 : 报文源路径, 报文目标路径
    :param base_file_ori_path: 报文源路径:基础测试报文源路径，以/结尾
    :param base_file_des_path: 报文目标路径:基础测试报文目标路径，以/结尾
        :param server_app_map: 服务器ip映射表
        :param server_default_user: 服务器用户映射表
    :return:
        """
    if not base_file_ori_path or not base_file_des_path:
        raise Exception('报文源路径或报文目标路径不能为空')
    if base_file_ori_path[-1] != '/' or base_file_des_path[-1] != '/':
        raise Exception('报文源路径或报文目标路径格式错误')
    base_file_ori_path = base_file_ori_path[:-1]
    base_file_des_path = base_file_des_path[:-1]
    if isinstance(server_app_map, basestring):
        server_app_map = json.loads(server_app_map)
    if isinstance(server_default_user, basestring):
        server_default_user = json.loads(server_default_user)
    app_server_ip = ""
    for k, v in server_app_map.items():
        if 'bds-core' in v:
            app_server_ip = k
            break
    if not app_server_ip:
        raise Exception("根据应用名 bds-core 找不到匹配的服务器IP")
    ssh_server_info = [app_server_ip, "22", server_default_user['user'], server_default_user['password']]
    import os
    base_file_des_path_backup = os.path.join(os.path.dirname(base_file_des_path), os.path.basename(base_file_des_path) + '_bak')
    try:
        with SSHClient(ssh_server_info) as sc:
            backup_cmd = 'sudo rm -fr %s/*&&sudo mv %s %s&&sudo mkdir -p %s' % (
            base_file_des_path_backup, base_file_des_path, base_file_des_path_backup, base_file_des_path)
            sc.run_cmd(backup_cmd)
            move_cmd = 'sudo cp -rf %s/. %s' % (base_file_ori_path, base_file_des_path)
            sc.run_cmd(move_cmd)
            return True
    except Exception as e:
        logger.error(traceback.format_exc())
        raise Exception('出现未知错误: {0}'.format(repr(e)))


@custom_func_wrapper
def setup_zx_test_file_move(test_file_ori_path, test_file_des_path, server_app_map, server_default_user):
    """ 服务器-移动征信场景测试报文 : 报文源路径, 报文目标路径
    :param test_file_ori_path: 报文源路径:基础测试报文源路径，填写完整路径，以/结尾
    :param test_file_des_path: 报文目标路径:基础测试报文目标路径，填写完整路径，以/结尾
        :param server_app_map: 服务器ip映射表
        :param server_default_user: 服务器用户映射表
        :return:
        """
    if not test_file_ori_path or not test_file_des_path:
        raise Exception('报文源路径或测试报文目标路径不能为空')
    if test_file_des_path[-1] != '/':
        raise Exception('报文目标路径格式错误')
    test_file_des_path = test_file_des_path[:-1]
    if isinstance(server_app_map, basestring):
        server_app_map = json.loads(server_app_map)
    if isinstance(server_default_user, basestring):
        server_default_user = json.loads(server_default_user)
    app_server_ip = ""
    for k, v in server_app_map.items():
        if 'bds-core' in v:
            app_server_ip = k
            break
    if not app_server_ip:
        raise Exception("根据应用名找不到匹配的服务器IP")
    ssh_server_info = [app_server_ip, "22", server_default_user['user'], server_default_user['password']]

    try:
        with SSHClient(ssh_server_info) as sc:
            import os
            if test_file_ori_path[-1] != '/':
                move_cmd = 'sudo cp -rf %s %s' % (test_file_ori_path, test_file_des_path)
            else:
                move_cmd = 'sudo cp -rf %s/. %s' % (test_file_ori_path, test_file_des_path)
            sc.run_cmd(move_cmd)
            return True
    except Exception as e:
        logger.error(traceback.format_exc())
        raise Exception('出现未知错误: {0}'.format(repr(e)))


@custom_func_wrapper
def setup_qa_create_accounting_overdue(loan_id, overdue_days, env_name):
    """ 其他-根据偏移天数更新贷款数据 : 贷款编号, 偏移天数
    :param loan_id: 贷款编号:贷款编号loan_id
    :param overdue_days: 偏移天数:正整数-期望逾期的天数；负数-期望往前偏移的天数
    :param env_name: 环境名称
    :return:
    """
    if not isinstance(overdue_days, int):
        raise Exception('偏移天数输入有误，只支持数字')
    if overdue_days < 0:
        dt = datetime.datetime.now() + relativedelta(days=overdue_days)
    else:
        dt = datetime.datetime.now() + relativedelta(days=-overdue_days) + relativedelta(months=-1)
    loan_timestamp = int(time.mktime(dt.timetuple()))

    data = {"env": env_name, "loanDate": loan_timestamp, "loanId": loan_id}
    url = "http://****/atp/qa/createAccountingOverdue"
    header_info = {"Content-Type": "application/json"}
    hc = HttpClient()
    try:
        r = hc.http_post(url, header_info, data)
        r_dic = json_loads(r.text)
    except Exception as err:
        raise Exception('出现未知错误：{0}'.format(repr(err)))
    if r_dic['code'] == '000':
        return True
    else:
        raise Exception(r_dic['desc'])


""" custom teardown-hooks
"""


@custom_func_wrapper
def teardown_sleep_N_secs(n_secs):
    """ 时间-sleep : 秒
    :desc: 说明: 等待指定秒数
    :param n_secs:秒: 等待的秒数，例如 5
    """
    time.sleep(n_secs)


@custom_func_wrapper
def teardown_db_operation(sql, db_connect):
    """ 数据库-执行SQL语句 : sql
    :desc: 说明: 执行SQL语句
    :param sql:sql: 需要执行的SQL语句，支持多条SQL按;分隔
    :return:
    """

    sql_execute(sql, db_connect=db_connect)


@custom_func_wrapper
def teardown_wait_until_db_result_succeed(wait_time, sql, expect_value, db_connect):
    """ 数据库-轮询SQL等待结果为期望值 : wait_time, sql, expect_value
    :desc: 说明: 等待时间内，轮询查询SQL，直到SQL结果等于期望值
    :param wait_time: wait_time:等待时间秒数，例如 15
    :param sql: sql:需要执行的查询的SQL
    :param expect_value: expect_value:预期结果
    :return:
    """
    wait_time = int(wait_time)
    if wait_time > wait_max_time:
        wait_time = wait_max_time
    for time_no in range(wait_time):
        return_info = sql_execute(sql, db_connect=db_connect)
        if len(return_info) != 0:
            if str(return_info[0][0]) == str(expect_value):
                return True
        time.sleep(wait_time_sec)
    return False


@custom_func_wrapper
def teardown_update_capital_no_list(order_no, capital_no_list, db_connect):
    """ 数据库-资方匹配列表中去掉给定的资方 : order_no, capital_no_list

    """
    if isinstance(capital_no_list, basestring):
        capital_no_list = json.loads(capital_no_list)

    try:
        get_current_capital_no_list_sql = "SELECT  FROM w  WHERE " % (order_no)
        current_capital_no_list = json.loads(sql_execute(get_current_capital_no_list_sql, db_connect=db_connect)[0][0])
        update_capital_no_list = [o for o in current_capital_no_list if o not in capital_no_list]

        set_capital_no_list_sql = "" % (json.dumps(update_capital_no_list), order_no)
        sql_execute(set_capital_no_list_sql, db_connect=db_connect)
        return True
    except Exception as err:
        raise Exception("更新资方匹配列表失败: {0}".format(repr(err)))


@custom_func_wrapper
def teardown_disconf_operation(env_name, disconf_id, disconf_method, disconf_name, disconf_value):
    """ disconf-后置操作disconf : Env_Name, Id, Method,  Name, Value
    :desc: 说明: 对disconf进行操作，支持新增/编辑/删除disconf的某一行配置
    :param env_name:Env_Name: 环境名称，例如 ALIUAT
    :param disconf_id:Id: disconf配置id，例如 34
    :param disconf_method:Method: 操作方法，add/edit/delete 三选一
    :param disconf_name:Name: disconf配置内容中某一行的key，例如 baseUrl
    :param disconf_value:Value: 更新后的值
    :return:
    """
    disconf_obj = {
        "env_name": env_name,
        "disconf_method": disconf_method,
        "disconf_id": disconf_id,
        "disconf_name": disconf_name,
        "disconf_value": str(disconf_value),
    }
    disconf_execute(disconf_obj)


@custom_func_wrapper
def teardown_disconf_operation_merge(kwargs, disconf_host):
    """ disconf-后置操作disconf(合并参数) : 参数
    :desc: 说明: 对disconf进行操作，支持新增/编辑/删除disconf的某一行配置
    :param kwargs: 参数:包含disconf_method、disconf_id、disconf_name、disconf_value的参数字典。示例:{"disconf_method":"edit","disconf_id":"653","disconf_name":"huixin.url","disconf_value":"https://hx-uat.huixinfintech.com/gateway/mime/loan/"}
    :param disconf_host:
    :return:
    """
    if isinstance(kwargs, basestring):
        kwargs = json.loads(kwargs)
    if 'disconf_method' in kwargs and 'disconf_id' in kwargs and 'disconf_name' in kwargs and 'disconf_value' in kwargs:
        kwargs['disconf_host'] = disconf_host
        disconf_execute_new(kwargs)
        return True
    else:
        return False


@custom_func_wrapper
def teardown_compare_log_content(app_name, ssh_cmd, start_with, end_with, expect_kwargs, server_app_map, server_default_user):
    """ 日志-检查日志中是否包含期望内容 : 应用名, grep命令, 起始字符, 结束字符, 期望内容
    :desc: 说明: 根据条件检索日志内容，并与期望内容比较
    :param app_name: 应用名: 如loan-web，同环境配置中IP-应用映射表中应用名称保持一致
    :param ssh_cmd: 过滤命令:使用grep xxx 过滤出符合条件的日志，如grep "成功发送通知消息" "/usr/local/src/logs/ups-service-cell01-node01/sys.log"
    :param start_with: 起始字符: 从日志中筛选起始字符后的内容
    :param end_with: 结束字符: 从日志中筛选结束字符前的内容
    :param expect_kwargs: 期望内容:json格式，用于同日志中筛选出的内容做json包含比较，如果包含则返回true，否则返回false
    :return:
    """
    server_app_map = json.loads(server_app_map)
    server_default_user = json.loads(server_default_user)
    app_server_ip = ""
    for k, v in server_app_map.items():
        if app_name in v:
            app_server_ip = k
            break
    if not app_server_ip:
        raise Exception("根据应用名找不到匹配的服务器IP")

    if not ssh_cmd.startswith("grep"):
        raise Exception("为了安全考虑，目前暂只支持grep命令")

    ssh_server_info = [app_server_ip, "22", server_default_user['user'], server_default_user['password']]

    try:
        with SSHClient(ssh_server_info) as sc:
            logs = sc.exec_cmd(ssh_cmd)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise Exception('出现未知错误: {0}'.format(repr(e)))

    if not logs:
        raise Exception("日志中未找到匹配的内容")
    des_logs = logs.split("\n")[:-1]
    if len(des_logs) > 1:
        raise Exception("日志中找到超过一条匹配记录，请增加过滤条件！")

    glc = GetLogContent(des_logs[0], start_with, end_with)
    actual_value = glc.get_log_content()

    if not actual_value and not expect_kwargs:
        return True
    elif actual_value and expect_kwargs:
        try:
            if isinstance(actual_value, bytes):
                # bytes转str
                str_content = actual_value.decode('utf-8')
                # str转dict
                dict_check = json.loads(str_content)
            elif isinstance(actual_value, str):
                dict_check = json.loads(actual_value)
            else:  # dict
                dict_check = actual_value
        except json.decoder.JSONDecodeError:
            dict_check = actual_value

        try:
            dict_expect = json.loads(expect_kwargs)
        except json.decoder.JSONDecodeError:
            # json.loads异常时替换布尔类型后再次尝试，False => false , True => true
            expect_value = expect_kwargs.replace('False', 'false').replace('True', 'true')
            try:
                dict_expect = json.loads(expect_value)
            except json.decoder.JSONDecodeError:
                dict_expect = expect_value
        except TypeError:
            dict_expect = expect_kwargs

        # dict_check和dict_expect是字符串/数字的情况
        if isinstance(dict_expect, (str, int)) and isinstance(dict_check, (str, int)):
            if str(dict_expect) == str(dict_check):
                return True
            else:
                return False, "实际日志内容同期望不匹配，实际日志内容为 %s" % (str(actual_value))
        try:
            res = is_json_contains(dict_check, dict_expect)
            return res
        except Exception as e:
            return False, "json比对出现未知异常，%s" % traceback.format_exc()

    else:
        return False, "实际日志内容同期望不匹配，实际日志内容为 %s" % (str(actual_value))


@custom_func_wrapper
def teardown_zx_base_file_move(base_file_ori_path, base_file_des_path, server_app_map, server_default_user):
    """ 服务器-移动征信基础测试报文 : 报文源路径, 报文目标路径
    :param base_file_ori_path: 报文源路径:基础测试报文源路径，以/结尾
    :param base_file_des_path: 报文目标路径:基础测试报文目标路径，以/结尾
        :param server_app_map: 服务器ip映射表
        :param server_default_user: 服务器用户映射表
        :return:
        """
    return setup_zx_base_file_move(base_file_ori_path, base_file_des_path, server_app_map, server_default_user)


""" custom db
"""


@custom_func_wrapper
def variable_db_operation(sql, db_connect):
    res = sql_execute(sql, db_connect=db_connect)
    if res:
        # 支持查询结果是多条数据的情况
        if len(res) == 1:
            if len(res[0]) == 1:
                return convert_mysql_datatype_to_py(res[0][0])
            else:
                return db_operation_to_json(sql, db_connect=db_connect, return_info=res)
        else:
            sql_multi_result = []
            for res_item in res:
                if len(res_item) == 1:
                    sql_multi_result.append(convert_mysql_datatype_to_py(res_item[0]))
                else:
                    sql_multi_result.append(db_operation_to_json(sql, db_connect=db_connect, return_info=res_item, multi=True))
            return sql_multi_result
    else:
        return 'variable sql return no result!'


""" custom
"""


@custom_func_wrapper
def execution_testcase(testcase_id):
    """ 前置执行用例 :  用例编号
    :param testcase_id:
    """
    print("前置执行用例:{}".format(testcase_id))


# TODO 编辑此文件后校验格式


if __name__ == '__main__':

    from atp.app import create_app
    app = create_app()
    with app.app_context():
        get_redis_value(2, 'key_pair1', '', "", '')

    pass
