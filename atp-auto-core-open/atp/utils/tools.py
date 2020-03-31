# -*- coding:utf-8 -*-

import datetime
import hashlib
import json
import random
import socket
import time
import os
# from io import BufferedReader

import decimal
from copy import deepcopy
from dateutil.relativedelta import relativedelta

from requests.cookies import RequestsCookieJar

Alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
            'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


def get_host():
    """
    获取运行主机host
    :return:
    """
    ip = socket.gethostbyname(socket.gethostname())
    return str(ip)


def get_host_port():
    """
    获取运行主机host+port
    :return:
    """
    ip = get_host()
    return "{}:7000".format(ip)

def get_current_time(time_format='%Y-%m-%d %H:%M:%S'):
    """
    获取当前时间，返回指定格式的时间字符串，默认格式YYYY-mm-dd HH:MM:SS
    """
    return str(time.strftime(time_format, time.localtime(time.time())))


def get_time_by_timestamp(timestamp, time_format='%Y-%m-%d %H:%M:%S'):
    """
    获取指定时间戳对应的时间字符串，返回指定格式的时间字符串，默认格式YYYY-mm-dd HH:MM:SS
    """
    return str(time.strftime(time_format, time.localtime(timestamp)))


def get_current_timestamp():
    """
    获取当前时间，返回10位时间戳
    """
    return int(time.time())


def str_time_to_timestamp(str_time):
    time_array = time.strptime(str_time, "%Y-%m-%d %H:%M:%S")
    return int(time.mktime(time_array))


def transfer_json_string_to_dict(json_str):
    """把可能是json的字符串转为json字典"""
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
        json_str = json_str.replace('False', 'false').replace('True', 'true')
        try:
            dict_ = json.loads(json_str)
        except json.decoder.JSONDecodeError:
            dict_ = json_str
        return dict_
    except TypeError:
        return json_str


def is_json_contains(actual, expect, err_msg=''):
    if not isinstance(actual, (list, dict)):
        err_msg += '实际结果不是Json格式'
        return False, err_msg
    if not isinstance(expect, (list, dict)):
        err_msg += '预期结果不是Json格式'
        return False, err_msg
    if not isinstance(actual, type(expect)):
        err_msg += '预期结果和实际结果的数据类型不同，预期结果的类型是"{0}"，实际结果的类型是"{1}"'.format(
            type(expect).__name__, type(actual).__name__)
        return False, err_msg
    if isinstance(actual, list) and isinstance(expect, list):
        if len(actual) != len(expect):
            err_msg += '预期结果中{0}的长度是{1}，实际结果中{2}的长度是{3}'.format(
                expect, len(expect), actual, len(actual))
            return False, err_msg
        actual_inner_dict_list = []
        actual_inner_list_list = []
        for key in actual:
            if isinstance(key, dict):
                actual_inner_dict_list.append(key)
            elif isinstance(key, list):
                actual_inner_list_list.append(key)
        for i, key in enumerate(expect):
            if isinstance(key, dict):
                _key = actual_inner_dict_list[i]
                res = is_json_contains(_key, key, err_msg)
                if res is not True:
                    return res
            elif isinstance(key, list):
                _key = actual_inner_list_list[i]
                res = is_json_contains(_key, key, err_msg)
                if res is not True:
                    return res
            else:
                _key = actual[i]
                if key != _key:
                    return False

    elif isinstance(actual, dict) and isinstance(expect, dict):
        for key in expect:
            if key not in actual:
                err_msg += '实际结果中未找到"{}"这个Key'.format(key)
                return False, err_msg
            elif not isinstance(actual[key], type(expect[key])):
                err_msg += '"{0}"这个Key的预期结果类型是"{1}",实际结果类型是"{2}"'.format(
                    key, type(expect[key]).__name__, type(actual[key]).__name__)
                return False, err_msg
            if isinstance(actual[key], dict) and isinstance(expect[key], dict):
                res = is_json_contains(actual[key], expect[key], err_msg)
                if res is not True:
                    return res
            elif isinstance(actual[key], list) and isinstance(expect[key], list):
                if len(actual[key]) != len(expect[key]):
                    err_msg += '预期结果中{0}的长度是{1}，实际结果中{0}的长度是{2}'.format(
                        key, len(expect[key]), len(actual[key]))
                    return False, err_msg
                res = is_json_contains(actual[key], expect[key], err_msg)
                if res is not True:
                    return res
            elif actual[key] != expect[key]:
                err_msg += '"{0}"这个Key的预期结果是"{1}"，实际结果是"{2}"'.format(key, expect[key], actual[key])
                return False, err_msg

    return True


class JsonEncoder(json.JSONEncoder):
    """编码类，处理不能直接转为json的数据类型"""

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.__str__()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        elif isinstance(obj, type):
            return str(obj)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, RequestsCookieJar):
            # print(json_dumps(dict(obj)))
            return dict(obj)
            # elif isinstance(obj, BufferedReader):
            # return str(obj)
        return json.JSONEncoder.default(self, obj)


def json_dumps(dic):
    return json.dumps(dic, ensure_ascii=False, cls=JsonEncoder, separators=(',',':'))


def json_loads(str_):
    return json.loads(str_)


def generate_random_num(min_, max_):
    return random.randint(min_ + 1, max_)


def generate_random_str(sum_length, head):
    sum_length = int(sum_length)
    sum_length = 500 if sum_length > 500 else sum_length
    sum_length = 0 if sum_length < 0 else sum_length
    if len(head) >= sum_length:
        return head[:sum_length]
    else:
        remain_len = sum_length - len(head)
        return head + ''.join(random.choice(Alphabet) for _ in range(remain_len))


def generate_phone(top=None):
    if not top:
        phone_list = ['136', '188', '134', '135', '184', '187', '183']  # 定义号码段
        phone = random.choice(phone_list) + "".join(random.choice("0123456789") for _ in range(8))
    else:
        phone = str(top) + "".join(random.choice("0123456789") for _ in range(8))
    return phone


def generate_idcard(age=None):
    """
生成身份证号，生成规则同真实身份证，18位，最后一位可以是数字或者X
    :return:身份证号
    """
    ARR = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    LAST = ('1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2')

    u''' 随机生成新的18为身份证号码 '''
    t = time.localtime()[0]

    first_list = ['362402', '362421', '362422', '362423', '362424', '362425', '362426', '362427', '362428', '362429',
                  '362430', '362432', '110100', '110101', '110102', '110103', '110104', '110105', '110106', '110107',
                  '110108', '110109', '110111', '320101', '320102', '320103', '320104', '320105', '320106']

    try:
        age = int(age)
        if 0 > age or age > 200:
            target_year = random.randint(t - 50, t - 19)
        else:
            target_year = datetime.datetime.now().year - age
    except (ValueError, TypeError):
        target_year = random.randint(t - 50, t - 19)

    x = '%06d%04d%02d%02d%03d' % (int(random.choice(first_list)),
                                  target_year,
                                  random.randint(1, 12),
                                  random.randint(1, 28),
                                  random.randint(1, 999))

    y = 0
    for i in range(17):
        y += int(x[i]) * ARR[i]

    id_card = '%s%s' % (x, LAST[y % 11])
    return id_card


def get_repayment_plan_dic(start_timestamp, term_total, capital_no=None):
    """
    根据传入时间获取每月罚息时间
    """
    if isinstance(start_timestamp, int):
        start_timestamp = int(str(start_timestamp)[:10])
    elif isinstance(start_timestamp, str):
        start_timestamp = int(start_timestamp[:10])
    else:
        return {}
    term_total = int(term_total)

    big_month = [1, 3, 5, 7, 8, 10, 12]
    term_no = 0
    start_time = datetime.datetime.fromtimestamp(start_timestamp)
    plan_dic = {}
    plus_month = start_time + relativedelta(months=+1)
    term_start_time = start_time
    while term_no < term_total:
        term_no += 1
        # plan_dic[term_no] = [str(term_start_time)[0:10], str(plus_month)[0:10]]
        plan_dic[term_no] = [term_start_time, plus_month]
        term_start_time = plus_month
        plus_month += relativedelta(months=+1)
        if plus_month.day < start_time.day and plus_month.month in big_month:
            plus_month += relativedelta(days=+(start_time.day - plus_month.day))

    format_plan_dic = {}
    for term_no, time_list in plan_dic.items():
        if term_no == term_total:
            if capital_no == '045':
                time_list[1] = time_list[1] + relativedelta(days=-1)
        format_plan_dic[term_no] = [str(time_list[0])[0:10], str(time_list[1])[0:10]]

    return format_plan_dic


def count_case_by_single_file(f_path):
    """统计某文件里RF用例数量"""
    sum = 0
    with open(f_path, mode='r', encoding='UTF-8') as f:
        exist_lines = f.readlines()
        is_case_file = False
        for line in exist_lines:
            if line.startswith('*** Test Cases ***'):
                is_case_file = True
                continue
            if is_case_file and not line.startswith('    ') and len(line) > 2:
                print('line:{}'.format(line))
                sum += 1
    return sum


def count_rf_cases(root_dir, case_num=None):
    """统计目录下RF用例总数"""
    if not case_num:
        case_num = 0
    f_d_list = os.listdir(root_dir)

    for f_d in f_d_list:
        if f_d.startswith('.'):
            continue
        f_d_path = os.path.join(root_dir, f_d)
        if os.path.isfile(f_d_path):
            if f_d_path.endswith('.txt') or f_d_path.endswith('.robot'):
                case_num += count_case_by_single_file(f_d_path)
        else:
            case_num = count_rf_cases(f_d_path, case_num)

    return case_num


def transfer_function_variable_to_expression(func_name, func_args_dict):
    from atp.utils.common import read_custom
    _custom = read_custom()
    func_args_str = ''
    for custom_func in _custom["functions"]:
        if custom_func["name"] == func_name:
            for x in custom_func["parameters"]:
                for input_arg in func_args_dict:
                    if input_arg == x:
                        if func_args_str == '':
                            func_args_str += func_args_dict[input_arg]
                        else:
                            func_args_str += '||{}'.format(func_args_dict[input_arg])
    expression = "${{{func}({args})}}".format(func=func_name, args=func_args_str)
    return expression


def generate_bank_card_no(card_front, card_no_len, number):
    """
    生成可以通过校验的银行卡号列表
    银行卡号校验算法参考 https://blog.csdn.net/dtm19931001/article/details/46582663
    :param card_front: 发卡机构标识码
    :param card_no_len: 银行卡长度
    :param number: 银行卡数量
    :return:
    """
    try:
        if len(card_front) != 6:
            return -1
        int(card_front)
    except ValueError:
        return -1

    try:
        sum_len = int(card_no_len)
        if not 10 <= sum_len <= 30:
            return -2
    except ValueError:
        return -2

    try:
        num = int(number)
        if not 1 <= num <= 100:
            return -3
    except ValueError:
        return -3

    gen_len = sum_len - len(str(card_front)) - 1
    bank_card_no_list = list()
    for _ in range(num):
        n = 0
        bank_card_no = 0
        while n < 10:
            str_x = generate_random_number(gen_len)
            bank_card_no = card_front + str_x + get_check_num(card_front + str_x)
            if bank_card_no not in bank_card_no_list:
                break
            else:
                n += 1
                # print('n:{}'.format(n))
        bank_card_no_list.append(bank_card_no)

    return bank_card_no_list


def generate_random_number(gen_len):
    """
    生成随机数字字符串
    :param gen_len:
    :return:
    """
    return "".join(random.choice("0123456789") for _ in range(gen_len))


def get_check_num(str_x):
    """
    计算获得校验位
    """
    list_x_1 = list(str_x[-1::-2])  # 从最后一位每隔一位逆序截取
    list_x_2 = list(str_x[-2::-2])

    sum_x = 0
    for x in list_x_1:
        tmp = int(x) * 2
        if tmp >= 10:
            sum_x += (int(str(tmp)[0]) + int(str(tmp)[1]))
        else:
            sum_x += tmp
    for x in list_x_2:
        sum_x += int(x)

    last = int(str(sum_x)[-1])

    if last == 0:
        check_num = 0
    else:
        check_num = 10 - last

    return str(check_num)


def md5_for_sign(text):
    """MD5加密"""
    m = hashlib.md5()
    m.update(text.encode(encoding='UTF-8'))
    return m.hexdigest()


def get_sign_common(input_dic, secret_key=None):
    """common加签"""
    if not secret_key:
        secret_key = '2342342312324324324324324242342'

    upperParamKeys = []
    signData = {}

    for k, v in input_dic.items():
        if v is not None and v != '':
            upperParamKeys.append(k.upper())
            if isinstance(v, (bool, list)):
                signData[k.upper()] = json.dumps(v, ensure_ascii=False, separators=(',', ':'))
            else:
                signData[k.upper()] = deepcopy(v)

    upperParamKeys.sort()

    text_str = ''
    for upperParamKey in upperParamKeys:
        text_str += upperParamKey
        text_str += str(signData[upperParamKey])

    text_str += secret_key
    # print(text_str)
    sign = md5_for_sign(text_str)
    input_dic.update({'sign': sign})
    return input_dic


def generate_compute_expression(expression: str, digits: int):
    res = eval(expression)
    float_res = float('%.{}f'.format(digits) % res)
    if digits == 0:
        return int(float_res)
    return float_res


def convert_mysql_datatype_to_py(data):
    if isinstance(data, datetime.datetime):
        data = data.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(data, datetime.date):
        data = data.strftime("%Y-%m-%d")
    elif isinstance(data, decimal.Decimal):
        data = float(data)
    return data


if __name__ == '__main__':
    actual = [{'feeDue':  0.0,  'insuranceDue':  6.0, 'lastRepayDate':  None,  'termTotal': 3, 'dueFlagEnum':  'PASS', 'accountStatus':  None, 'dateDiffDays': -9,  'insuranceInfos':  [{'insuranceDue':  6.0,  'insurancePaid':  0.0,  'insuranceType':  'GUARANTEE_YUANHENTAI',  'class':  'cn.me************.DubboInsuranceInfo',  'status':  50,  'insuranceDischarge':  0.0}],  'interestPaid':  0.0,  'lateChargePaid':  0.0,  'borrowerId':  10002445,  'principalDue':  533.33,  'lateChargeDue':  24.97,  'lateChargeTotal':  24.97,  'planStatusEnum':  'OVERDUE',  'dueTotal':  585.77,  'principalPaid':  0.0,  'planDueDate':  1567958400000,  'paidTotal':  0.0,  'interestDue':  21.47,  'feePaid':  0.0,  'insurancePaid':  0.0,  'termNo':  1,  'repayDetailList':  None,  'loanId':  '0967481568796458'},  {'feeDue':  0.0,  'insuranceDue':  0.0,  'dueDate':  1570550400000,  'lastRepayDate':  None,  'termTotal':  3,  'dueFlagEnum':  'CURRENT',  'accountStatus':  None,  'dateDiffDays':  21,  'id':  82625281,  'cycleDate':  1567958400000,  'class':  'cn.*********************epayPlan',  'insuranceInfos':  None,  'interestPaid':  0.0,  'lateChargePaid':  0.0,  'borrowerId':  10002445,  'principalDue':  533.33,  'lateChargeDue':  0.0,  'lateChargeTotal':  0.0,  'planStatusEnum':  'NORMAL',  'dueTotal':  554.8,  'principalPaid':  0.0,  'planDueDate':  1570550400000,  'paidTotal':  0.0,  'interestDue':  21.47,  'feePaid':  0.0,  'insurancePaid':  0.0,  'termNo':  2,  'repayDetailList':  None,  'loanId':  '0967481568796458'},  {'feeDue':  0.0,  'insuranceDue':  0.0,  'dueDate':  1573228800000,  'lastRepayDate':  None,  'termTotal':  3,  'dueFlagEnum':  'FUTURE',  'accountStatus':  None,  'dateDiffDays':  52,  'id':  82625282,  'cycleDate':  1570550400000,  'class':  'cn.*****************************LoanRepayPlan',  'insuranceInfos':  None,  'interestPaid':  0.0,  'lateChargePaid':  0.0,  'borrowerId':  10002445,  'principalDue':  533.34,  'lateChargeDue':  0.0,  'lateChargeTotal':  0.0,  'planStatusEnum':  'NORMAL',  'dueTotal':  554.81,  'principalPaid':  0.0,  'planDueDate':  1573228800000,  'paidTotal':  0.0,  'interestDue':  21.47,  'feePaid':  0.0,  'insurancePaid':  0.0,  'termNo':  3,  'repayDetailList':  None,  'loanId':  '0967481568796458'}]
    expect = [{'feeDue':  0.0,  'insuranceDue':  6.0, 'lastRepayDate':  None,  'termTotal': 3, 'dueFlagEnum':  'PASS', 'accountStatus':  None, 'dateDiffDays': -9,  'insuranceInfos':  [],  'interestPaid':  0.0,  'lateChargePaid':  0.0,  'borrowerId':  10002445,  'principalDue':  533.33,  'lateChargeDue':  24.97,  'lateChargeTotal':  24.97,  'planStatusEnum':  'OVERDUE',  'dueTotal':  585.77,  'principalPaid':  0.0,  'paidTotal':  0.0,  'interestDue':  21.47,  'feePaid':  0.0,  'insurancePaid':  0.0,  'termNo':  1,  'repayDetailList':  None,  'loanId':  '0967481568796458'},  {'feeDue':  0.0,  'insuranceDue':  0.0,  'lastRepayDate':  None,  'termTotal':  3,  'dueFlagEnum':  'CURRENT',  'accountStatus':  None,  'dateDiffDays':  21,  'insuranceInfos':  None,  'interestPaid':  0.0,  'lateChargePaid':  0.0,  'borrowerId':  10002445,  'principalDue':  533.33,  'lateChargeDue':  0.0,  'lateChargeTotal':  0.0,  'planStatusEnum':  'NORMAL',  'dueTotal':  554.8,  'principalPaid':  0.0,  'paidTotal':  0.0,  'interestDue':  21.47,  'feePaid':  0.0,  'insurancePaid':  0.0,  'termNo':  2,  'repayDetailList':  None,  'loanId':  '0967481568796458'},  {'feeDue':  0.0,  'insuranceDue':  0.0,  'lastRepayDate':  None,  'termTotal':  3,  'dueFlagEnum':  'FUTURE',  'accountStatus':  None,  'dateDiffDays':  52,  'insuranceInfos':  None,  'interestPaid':  0.0,  'lateChargePaid':  0.0,  'borrowerId':  10002445,  'principalDue':  533.34,  'lateChargeDue':  0.0,  'lateChargeTotal':  0.0,  'planStatusEnum':  'NORMAL',  'dueTotal':  554.81,  'principalPaid':  0.0,  'paidTotal':  0.0,  'interestDue':  21.47,  'feePaid':  0.0,  'insurancePaid':  0.0,  'termNo':  3,  'repayDetailList':  None,  'loanId':  '0967481568796458'}]

    actual = [{"feeDue":0.0,"insuranceDue":0.0,"dueDate":1573920000000,"lastRepayDate":None,"termTotal":3,"dueFlagEnum":"CURRENT","accountStatus":None,"dateDiffDays":31,"id":82635953,"cycleDate":1571241600000,"class":"cn.m*******************nRepayPlan","insuranceInfos":None,"interestPaid":0.0,"lateChargePaid":0.0,"borrowerId":10004051,"principalDue":533.33,"lateChargeDue":0.0,"lateChargeTotal":0.0,"planStatusEnum":"NORMAL","dueTotal":554.8,"principalPaid":0.0,"planDueDate":1573920000000,"paidTotal":0.0,"interestDue":21.47,"feePaid":0.0,"insurancePaid":0.0,"termNo":1,"repayDetailList":None,"loanId":"0997641571273573"},{"feeDue":0.0,"insuranceDue":0.0,"dueDate":1576512000000,"lastRepayDate":None,"termTotal":3,"dueFlagEnum":"FUTURE","accountStatus":None,"dateDiffDays":61,"id":82635954,"cycleDate":1573920000000,"class":"cn.**********************oanRepayPlan","insuranceInfos":None,"interestPaid":0.0,"lateChargePaid":0.0,"borrowerId":10004051,"principalDue":533.33,"lateChargeDue":0.0,"lateChargeTotal":0.0,"planStatusEnum":"NORMAL","dueTotal":554.8,"principalPaid":0.0,"planDueDate":1576512000000,"paidTotal":0.0,"interestDue":21.47,"feePaid":0.0,"insurancePaid":0.0,"termNo":2,"repayDetailList":None,"loanId":"0997641571273573"},{"feeDue":0.0,"insuranceDue":0.0,"dueDate":1579190400000,"lastRepayDate":None,"termTotal":3,"dueFlagEnum":"FUTURE","accountStatus":None,"dateDiffDays":92,"id":82635955,"cycleDate":1576512000000,"class":"cn.m*************lan","insuranceInfos":None,"interestPaid":0.0,"lateChargePaid":0.0,"borrowerId":10004051,"principalDue":533.34,"lateChargeDue":0.0,"lateChargeTotal":0.0,"planStatusEnum":"NORMAL","dueTotal":554.81,"principalPaid":0.0,"planDueDate":1579190400000,"paidTotal":0.0,"interestDue":21.47,"feePaid":0.0,"insurancePaid":0.0,"termNo":3,"repayDetailList":None,"loanId":"0997641571273573"}]
    expect = [{"feeDue":0.0,"insuranceDue":0.0,"lastRepayDate":None,"termTotal":3,"dueFlagEnum":"CURRENT","accountStatus":None,"dateDiffDays":30,"insuranceInfos":None,"interestPaid":0.0,"lateChargePaid":0.0,"borrowerId":10004051,"principalDue":533.33,"lateChargeDue":0.0,"lateChargeTotal":0.0,"planStatusEnum":"NORMAL","dueTotal":554.8,"principalPaid":0.0,"paidTotal":0.0,"interestDue":21.47,"feePaid":0.0,"insurancePaid":0.0,"termNo":1,"repayDetailList":None,"loanId":"0997641571273573"},{"feeDue":0.0,"insuranceDue":0.0,"lastRepayDate":None,"termTotal":3,"dueFlagEnum":"FUTURE","accountStatus":None,"dateDiffDays":61,"insuranceInfos":None,"interestPaid":0.0,"lateChargePaid":0.0,"borrowerId":10004051,"principalDue":533.33,"lateChargeDue":0.0,"lateChargeTotal":0.0,"planStatusEnum":"NORMAL","dueTotal":554.8,"principalPaid":0.0,"paidTotal":0.0,"interestDue":21.47,"feePaid":0.0,"insurancePaid":0.0,"termNo":2,"repayDetailList":None,"loanId":"0997641571273573"},{"feeDue":0.0,"insuranceDue":0.0,"lastRepayDate":None,"termTotal":3,"dueFlagEnum":"FUTURE","accountStatus":None,"dateDiffDays":91,"insuranceInfos":None,"interestPaid":0.0,"lateChargePaid":0.0,"borrowerId":10004051,"principalDue":533.34,"lateChargeDue":0.0,"lateChargeTotal":0.0,"planStatusEnum":"NORMAL","dueTotal":554.81,"principalPaid":0.0,"paidTotal":0.0,"interestDue":21.47,"feePaid":0.0,"insurancePaid":0.0,"termNo":3,"repayDetailList":None,"loanId":"0997641571273573"}]
    r = is_json_contains(actual, expect)
    print(r, type(r))
    pass
