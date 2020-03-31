# -*- coding:utf-8 -*-

import re
import traceback
import datetime
import decimal
import time
import sqlparse

from sqlalchemy import create_engine, DDL, MetaData
from sqlalchemy.pool import NullPool
from sqlalchemy import exc
from sqlalchemy import text

from atp.api.comm_log import logger
from atp.models.atp_auto import EnvInfo
from atp.httprunner import logger as hr_logger
from atp.utils.tools import transfer_json_string_to_dict, is_json_contains, convert_mysql_datatype_to_py


def sql_execute(sql, env_name=None, db_connect=None):
    """
    """
    # env = env.upper()
    if env_name:
        try:
            obj = EnvInfo.query.filter_by(env_name=env_name).first()
            if not obj:
                raise Exception("传入的环境不存在")
            db_info = obj.db_connect
            # db_info = db_connects[env][db_type]

        except Exception as err:
            raise Exception(err)
    elif db_connect:
        db_info = db_connect

    engine = create_engine(db_info, echo=False, poolclass=NullPool)
    return_info = None
    with engine.connect() as conn:
        try:
            sql = sql.replace('%', '%%')
            if re.match('select', sql.lower().strip()):
                return_info = conn.execute(sql).fetchall()
            elif re.match('exec', sql.lower().strip()):
                sql_new = DDL(sql)
                conn.execute(sql_new)
            else:
                for s in str(sql).strip().strip(';').split(';'):
                    if 'insert' not in s.lower() and 'where' not in s.lower():
                        raise Exception('更新和删除操作不符合安全规范，必须要带上where条件')
                    return_info = conn.execute(s).rowcount
                    # logger.info("受影响的行: {0}".format(return_info))
                    hr_logger.log_info("【执行SQL】: {0}  受影响的行: {1}".format(s.replace('\n', ''), return_info))
        except exc.SQLAlchemyError as err:
            hr_logger.log_error("数据库操作失败, {0}".format(err))
            raise err
            # hr_logger.log_error(err.args[0])

        finally:
            conn.close()

    return return_info


def sql_execute_with_params(sql_list, param_list, env_name=None, db_connect=None):
    """
    执行数据库操作，支持携带参数
    """
    if len(sql_list) != len(param_list):
        raise Exception("sql个数同参数个数不匹配")
    if env_name:
        try:
            obj = EnvInfo.query.filter_by(env_name=env_name).first()
            if not obj:
                raise Exception("传入的环境不存在")
            db_info = obj.db_connect
            # db_info = db_connects[env][db_type]

        except Exception as err:
            raise Exception(err)
    elif db_connect:
        db_info = db_connect

    engine = create_engine(db_info, echo=False, poolclass=NullPool)
    return_info = None
    with engine.connect() as conn:
        try:
            for s,p in zip(sql_list, param_list):
                if 'insert' not in s.lower() and 'where' not in s.lower():
                    raise Exception('更新和删除操作不符合安全规范，必须要带上where条件')
                if s.lower().strip().startswith('select'):
                    return_info = conn.execute(text(s), p).fetchall()
                    hr_logger.log_info("【执行SQL】: {0}  返回数据: {1}".format(s.replace('\n', ''), return_info))
                else:
                    return_info = conn.execute(text(s), p).rowcount
                    # logger.info("受影响的行: {0}".format(return_info))
                    hr_logger.log_info("【执行SQL】: {0}  受影响的行: {1}".format(s.replace('\n', ''), return_info))
        except exc.SQLAlchemyError as err:
            hr_logger.log_error("数据库操作失败, {0}".format(err))
            raise err

        finally:
            conn.close()

    return return_info


def db_operation_to_json(sql, db_connect, return_info=None, multi=False):
    """
    执行查询sql，结果保存为一个json对象

    :multi 如果为True，说明查询结果包含多条记录，return_info为每条记录中元素
    """
    try:
        if not return_info:
            # 获取sql查询结果
            return_info = sql_execute(sql, db_connect=db_connect)
        if multi:
            value_list = list(return_info) if return_info else []
        else:
            value_list = list(return_info[0]) if return_info else []
        sql_lower = sql.lower()

        # 组成数据库结果值list
        for i in range(len(value_list)):
            # 处理查询结果字段类型是datetime/date/Decimal的情况
            value_list[i] = convert_mysql_datatype_to_py(value_list[i])

        between_select_from = sql[sql_lower.find('select') + len('select'):sql_lower.find('from')]
        # 组成字段名list
        if '*' in between_select_from:
            columns_list = get_table_columns(sql, db_connect)
            # database_name = sql[sql_lower.find('from') + len('from'):sql_lower.find('where')].strip()
            # table_name = database_name.split('.')[1]
            # library_name = database_name.split('.')[0]
            # columns_list = __get_table_columns(db_connect, library_name, table_name)
            # for i in range(len(columns_list)):
            #     columns_list[i] = columns_list[i].lower()
        else:
            columns_list = get_sql_columns(sql)
            # columns_list = sql_lower[sql_lower.find('select') + len('select'):sql_lower.find('from')].split(',')
            # for i in range(len(columns_list)):
            #     if '.' in columns_list[i]:
            #         columns_list[i] = columns_list[i].split('.', 1)[1]
            #     columns_list[i] = columns_list[i].strip()

        return dict(zip(columns_list, value_list))
    except Exception as err:
        # print("数据库操作失败, {0}".format(err))
        logger.error(traceback.format_exc())
        hr_logger.log_error("数据库操作失败, {0}".format(err))
        return None


def db_operation_to_json_cycle(sql, db_connect, expect_value, wait_time=30):
    """数据库json校验 轮询"""
    step_time = 5
    t = 0
    return_value = None

    dict_expect = transfer_json_string_to_dict(expect_value)
    # 如果期望值非json格式，直接报错
    if not isinstance(dict_expect, dict):
        raise Exception('结果校验中期望结果非json格式，期望结果内容为{0}({1})'.format(dict_expect, type(dict_expect).__name__))
    dict_expect_lower_key = {key.lower(): dict_expect[key] for key in dict_expect}

    while t <= wait_time:
        try:
            return_value = db_operation_to_json(sql, db_connect)
            dict_check = transfer_json_string_to_dict(return_value)
            dict_check_lower_key = {key.lower(): dict_check[key] for key in dict_check}

            if not dict_check_lower_key:
                hr_logger.log_info("【轮询SQL】: {0}  表中无数据，等待5秒后重试".format(sql.replace('\n', '')))
            else:
                res = is_json_contains(dict_check_lower_key, dict_expect_lower_key)
                if res is True:
                    hr_logger.log_info('【轮询SQL】: {0}  结果为 {1}'.format(sql.replace('\n', ''), dict_check))
                    return return_value
                else:
                    hr_logger.log_info(
                        '【轮询SQL】: {0}  结果为 {1}，等待5秒后重试'.format(sql.replace('\n', ''), dict_check))

            time.sleep(step_time)
            t += step_time

        except Exception as err:
            logger.error(traceback.format_exc())
            raise Exception("【轮询SQL】: 数据库操作失败, {0}".format(err))

    hr_logger.log_info('【轮询SQL】: 超过{0}秒表中仍无预期数据'.format(wait_time))

    return return_value


def __get_table_columns(db_connect, library_name, table_name):
    """
    根据表名table_name获取该表的所有列名，list格式
    """
    #替换db_connect的表名
    config_name = db_connect.split('?')[0].split('/')[-1]
    db_connect = db_connect.replace(config_name,library_name)

    engine = create_engine(db_connect, echo=False, poolclass=NullPool)
    columns_list = None
    with engine.connect() as conn:
        try:
            metadata = MetaData(engine, reflect=True)
            table_name = table_name.strip('`')
            table_name_upper = table_name.upper()
            table_name_lower = table_name.lower()
            if table_name_upper in metadata.tables:
                ex_table = metadata.tables[table_name_upper]
            elif table_name_lower in metadata.tables:
                ex_table = metadata.tables[table_name_lower]
            else:
                ex_table = metadata.tables[table_name]
            columns_list = ex_table.columns.keys()
        except Exception as err:
            hr_logger.log_error("数据库操作失败 \n {0}".format(err))
            logger.error(traceback.format_exc())
        finally:
            conn.close()
    return columns_list


def sql_execute_cycle(sql, db_connect, expect_value, wait_time=30):
    """
    定时执行某条查询sql，用于特定场景，如检查贷款表中贷款数据是否生成，默认每5秒检查一次，1分钟超时退出  \n
    :param expect_value:
    :param db_connect:
    :param sql: 待执行的查询sql  \n
    :param wait_time: 超时时长，超过该时间自动退出 ，默认60秒 \n
    :return: 返回查询结果  \n
    """
    expect_is_json = False
    step_time = 5
    t = 0
    return_value = None
    dict_expect = transfer_json_string_to_dict(expect_value)
    if isinstance(dict_expect, dict):
        expect_is_json = True

    while t <= wait_time:
        try:
            return_info = sql_execute(sql, db_connect=db_connect)
            if expect_is_json:
                return_value = return_info[0][0] if return_info else None
                dict_check = transfer_json_string_to_dict(return_value)
                # dict_check_lower_key = {key.lower(): dict_check[key] for key in dict_check}
                if not dict_check:
                    hr_logger.log_info("【轮询SQL】: {0}  表中无数据，等待5秒后重试".format(sql.replace('\n', '')))
                else:
                    res = is_json_contains(dict_check, dict_expect)
                    if res is True:
                        hr_logger.log_info('【轮询SQL】: {0}  结果为 {1}'.format(sql.replace('\n', ''), dict_check))
                        return return_value
                    else:
                        hr_logger.log_info(
                            '【轮询SQL】: {0}  结果为 {1}，{2}，等待5秒后重试'.format(sql.replace('\n', ''), dict_check, res[1]))
            else:
                if not return_info:
                    hr_logger.log_info("【轮询SQL】: {0}  表中无数据，等待5秒后重试".format(sql.replace('\n', '')))
                else:
                    return_value = str(return_info[0][0])
                    if return_value == str(expect_value):
                        hr_logger.log_info('【轮询SQL】: {0}  结果为 {1}'.format(sql.replace('\n', ''), return_value))
                        return return_info[0][0]
                    else:
                        hr_logger.log_info('【轮询SQL】: {0}  结果为 {1}，等待5秒后重试'.format(sql.replace('\n', ''), return_value))

            time.sleep(step_time)
            t += step_time

        except Exception as err:
            logger.error(traceback.format_exc())
            raise Exception("【轮询SQL】: 数据库操作失败, {0}".format(err))

    hr_logger.log_info('【轮询SQL】: 超过{0}秒表中仍无预期数据'.format(wait_time))
    return return_value


def get_sql_columns(sql):
    """
    获取sql的查询字段名
    e.g.
    sql = "select ab,c.id,t.name as t_name,dd DD from atp_auto.aa;"
    column_list = ['ab', 'id', 't_name', 'DD']
    """
    column_list = []
    query_tokens = sqlparse.parse(sql)[0].tokens
    for token in query_tokens:
        # print('token[%s] ttype[%s] type[%s]' % (token, token.ttype, type(token)))
        if token.ttype is None:
            if isinstance(token, sqlparse.sql.IdentifierList):
                for id_ in token.get_identifiers():
                    # print(id_, type(id_), dir(id_))
                    try:
                        column = id_.get_name()
                    except AttributeError:
                        column = str(id_)
                    column_list.append(column)
            elif isinstance(token, sqlparse.sql.Identifier):
                column_list.append(token.get_name())
        elif str(token).lower() == 'from':
            break
    # print(column_list)
    return column_list


def get_table_columns(sql, db_connect):
    """
    获取sql中的表所有字段名
    e.g.
    sql = "select * from atp_auto.aa;"
    column_list = ['uu', 'id', 'name', 'age']
    """
    query_tokens = sqlparse.parse(sql)[0].tokens
    after_from_flag = False
    table_schema = ''
    table_name = ''
    for token in query_tokens:
        # print('token[%s] ttype[%s] type[%s]' % (token, token.ttype, type(token)))
        if after_from_flag and token.ttype is None:
            if isinstance(token, sqlparse.sql.Identifier):
                table_schema = token.get_parent_name()
                table_name = token.get_name().strip('`')
                break
        elif str(token).lower() == 'from':
            after_from_flag = True

    res = sql_execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE  table_schema='%s' AND table_name='%s';"
        % (table_schema, table_name), db_connect=db_connect)
    column_list = [row[0].lower() for row in res]
    return column_list

if __name__ == '__main__':

    import pymysql
    from atp.app import create_app
    app = create_app()
    with app.app_context():

        sql = [""]
        param = [{}]
        sql_execute_with_params(sql, param, db_connect='')
    pass
