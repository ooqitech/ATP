# encoding: utf-8

import json
import re
import traceback
import decimal

from atp.httprunner import exceptions, logger, utils, parser
from atp.httprunner.compat import OrderedDict, basestring, is_py2
from requests.models import PreparedRequest
from requests.structures import CaseInsensitiveDict

text_extractor_regexp_compile = re.compile(r".*\(.*\).*")


class ResponseObject(object):

    def __init__(self, resp_obj):
        """ initialize with a requests.Response object
        @param (requests.Response instance) resp_obj
        """
        self.resp_obj = resp_obj

    def __getattr__(self, key):
        try:
            if key == "json":
                value = self.resp_obj.json()
            else:
                value =  getattr(self.resp_obj, key)

            self.__dict__[key] = value
            return value
        except AttributeError:
            err_msg = "ResponseObject does not have attribute: {}".format(key)
            logger.log_error(err_msg)
            raise exceptions.ParamsError(err_msg)

    def _extract_field_with_regex(self, field):
        """ extract field from response content with regex.
            requests.Response body could be json or html text.
        @param (str) field should only be regex string that matched r".*\(.*\).*"
        e.g.
            self.text: "LB123abcRB789"
            field: "LB[\d]*(.*)RB[\d]*"
            return: abc
        """
        matched = re.search(field, self.text)
        if not matched:
            err_msg = u"Failed to extract data with regex! => {}\n".format(field)
            err_msg += u"response body: {}\n".format(self.text)
            logger.log_error(err_msg)
            raise exceptions.ExtractFailure(err_msg)

        return matched.group(1)

    def _extract_field_with_delimiter(self, field, context_obj=None):
        """ response content could be json or html text.
        @param (str) field should be string joined by delimiter.
        e.g.
            "status_code"
            "headers"
            "cookies"
            "content"
            "headers.content-type"
            "content.person.name.first_name"

            含用例内变量
            "123$phoneNo"

            查询SQL
            "SELECT NEXT_VALUE FROM user_db.sequence WHERE SEQ_NAME='$MEMBER_ID';"
        """
        # [:]
        sub_str_exp = None
        if field.endswith(']') and '[' in field and ':' in field.split('[')[-1]:
            sub_str_exp = '[' + field.split('[')[-1]
            field = field.strip(sub_str_exp)

        # 支持提取变量步骤中写查询sql，查询结果保存为变量
        if str(field).lower().startswith("select "):
            db_connect_content = '$DB_CONNECT'
            parsed_db_connect = context_obj.eval_content(db_connect_content)
            if parser.extract_variables(field):
                sql = context_obj.eval_content(field)
            else:
                sql = field
            from atp.api.mysql_sql_executor import sql_execute, db_operation_to_json
            from atp.utils.tools import convert_mysql_datatype_to_py
            try:
                res = sql_execute(sql, db_connect=parsed_db_connect)
            except Exception as err:
                raise
            if res:
                # 支持查询结果是多条数据的情况
                if len(res) == 1:
                    if len(res[0]) == 1:
                        res_value = convert_mysql_datatype_to_py(res[0][0])
                    else:
                        res_value = db_operation_to_json(sql, db_connect=parsed_db_connect, return_info=res)
                else:
                    res_value = []
                    for res_item in res:
                        if len(res_item) == 1:
                            res_value.append(convert_mysql_datatype_to_py(res_item[0]))
                        else:
                            res_value.append(
                                db_operation_to_json(sql, db_connect=parsed_db_connect, return_info=res_item, multi=True))
            else:
                res_value = 'variable sql return no result!'
            # res_value = res[0][0] if res else "DB query returns EMPTY result!"
            # if isinstance(res_value, decimal.Decimal):
            #     res_value = float(res_value)
            return res_value, sub_str_exp

        # string.split(sep=None, maxsplit=-1) -> list of strings
        # e.g. "content.person.name" => ["content", "person.name"]
        try:
            top_query, sub_query = field.split('.', 1)
        except ValueError:
            top_query = field
            sub_query = None

        # status_code
        if top_query in ["status_code", "encoding", "ok", "reason", "url"]:
            if sub_query:
                # status_code.XX
                err_msg = u"Failed to extract: {}\n".format(field)
                logger.log_error(err_msg)
                raise exceptions.ParamsError(err_msg)

            return getattr(self, top_query), sub_str_exp

        # cookies
        elif top_query == "cookies":
            cookies = self.cookies.get_dict()
            if not sub_query:
                # extract cookies
                return cookies, sub_str_exp

            try:
                return cookies[sub_query], sub_str_exp
            except KeyError:
                err_msg = u"Failed to extract cookie! => {}\n".format(field)
                err_msg += u"response cookies: {}\n".format(cookies)
                logger.log_error(err_msg)
                raise exceptions.ExtractFailure(err_msg)

        # elapsed
        elif top_query == "elapsed":
            available_attributes = u"available attributes: days, seconds, microseconds, total_seconds"
            if not sub_query:
                err_msg = u"elapsed is datetime.timedelta instance, attribute should also be specified!\n"
                err_msg += available_attributes
                logger.log_error(err_msg)
                raise exceptions.ParamsError(err_msg)
            elif sub_query in ["days", "seconds", "microseconds"]:
                return getattr(self.elapsed, sub_query), sub_str_exp
            elif sub_query == "total_seconds":
                return self.elapsed.total_seconds(), sub_str_exp
            else:
                err_msg = "{} is not valid datetime.timedelta attribute.\n".format(sub_query)
                err_msg += available_attributes
                logger.log_error(err_msg)
                raise exceptions.ParamsError(err_msg)

        # headers
        elif top_query == "headers":
            headers = self.headers
            if not sub_query:
                # extract headers
                return headers, sub_str_exp

            try:
                return headers[sub_query], sub_str_exp
            except KeyError:
                err_msg = u"Failed to extract header! => {}\n".format(field)
                err_msg += u"response headers: {}\n".format(headers)
                logger.log_error(err_msg)
                raise exceptions.ExtractFailure(err_msg)

        # response body
        elif top_query in ["content", "text", "json"]:
            try:
                body = self.json
            except exceptions.JSONDecodeError:
                body = self.text

            if not sub_query:
                # extract response body
                return body, sub_str_exp

            if isinstance(body, dict):
                # content = {"xxx": 123}, content.xxx
                '''如果body中content是字符串类型'content': "{'headImageUrl':'','isRegister':0,'nickName':''}"
                  转换成字典，然后'extract': [{'headImageUrl':"content.content.isRegister"}]可提取
                '''
                # if "content" in body.keys() and '{' in body["content"]:
                # 修复bug：如果body["content"]是NoneType，报错“TypeError:  argument  of  type  'NoneType'  is  not  iterable ”
                # if "content" in body.keys() and body["content"] and '{' in body["content"]:
                #     body_content_dict=json.loads(body["content"].replace("'", "\""))
                #     body["content"]=body_content_dict
                # 修复bug："[]"未被json.loads
                if "content" in body.keys() and body["content"] and isinstance(body["content"], str):
                    try:
                        body_content_dict = json.loads(body["content"].replace(' style="text-align: center;text-indent: 0;"', '').replace("'", "\""))
                        body["content"] = body_content_dict
                    except (TypeError, json.decoder.JSONDecodeError) as e:
                        # logger.log_error(body["content"].replace("'", "\""))
                        logger.log_error('\n'.join([e, traceback.format_exc()]))
                return utils.query_json(body, sub_query), sub_str_exp
            elif sub_query.isdigit():
                # content = "abcdefg", content.3 => d
                return utils.query_json(body, sub_query), sub_str_exp
            else:
                # content = "<html>abcdefg</html>", content.xxx
                err_msg = u"Failed to extract attribute from response body! => {}\n".format(field)
                err_msg += u"response body: {}\n".format(body)
                logger.log_error(err_msg)
                raise exceptions.ExtractFailure(err_msg)

        # new set response attributes in teardown_hooks
        elif top_query in self.__dict__:
            attributes = self.__dict__[top_query]

            if not sub_query:
                # extract response attributes
                return attributes, sub_str_exp

            if isinstance(attributes, (dict, list)):
                # attributes = {"xxx": 123}, content.xxx
                return utils.query_json(attributes, sub_query), sub_str_exp
            elif sub_query.isdigit():
                # attributes = "abcdefg", attributes.3 => d
                return utils.query_json(attributes, sub_query), sub_str_exp
            else:
                # content = "attributes.new_attribute_not_exist"
                err_msg = u"Failed to extract cumstom set attribute from teardown hooks! => {}\n".format(field)
                err_msg += u"response set attributes: {}\n".format(attributes)
                logger.log_error(err_msg)
                raise exceptions.TeardownHooksFailure(err_msg)

        elif context_obj and parser.extract_variables(top_query):
            # 表达式带已知变量，保存为新的变量
            # ha$phone => ha18551602992
            return context_obj.eval_content(top_query), sub_str_exp

        # others
        else:
            err_msg = u"Failed to extract attribute from response! => {}\n".format(field)
            err_msg += u"available response attributes: status_code, cookies, elapsed, headers, content, text, json, encoding, ok, reason, url.\n\n"
            err_msg += u"If you want to set attribute in teardown_hooks, take the following example as reference:\n"
            err_msg += u"response.new_attribute = 'new_attribute_value'\n"
            logger.log_error(err_msg)
            raise exceptions.ParamsError(err_msg)

    def extract_field(self, field, key=None, context_obj=None):
        """ extract value from requests.Response.
        """
        if not isinstance(field, basestring):
            err_msg = u"Invalid extractor! => {}\n".format(field)
            logger.log_error(err_msg)
            raise exceptions.ParamsError(err_msg)

        # msg = "extract: {}".format(field)
        if key:
            msg = "【提取变量】: {}".format(field)
        else:
            msg = "【提取】: {}".format(field)

        sub_str_exp = None
        original_value = None
        # if text_extractor_regexp_compile.match(field):
        #     value = self._extract_field_with_regex(field)
        # else:
        #     original_value, sub_str_exp = self._extract_field_with_delimiter(field, context_obj=context_obj)
        try:
            original_value, sub_str_exp = self._extract_field_with_delimiter(field, context_obj=context_obj)
        except Exception as err:
            raise exceptions.ExtractFailure(err)
        if sub_str_exp:
            value = eval('original_value' + sub_str_exp)
        else:
            value = original_value

        if is_py2 and isinstance(value, unicode):
            value = value.encode("utf-8")

        if key:
            if sub_str_exp:
                msg += "  ==>  {0}  ==>  {1}  保存为变量 {2}".format(original_value+sub_str_exp, value, key)
            else:
                msg += "  ==>  {0}  保存为变量 {1}".format(value, key)
        else:
            msg += "  ==>  {0}".format(value)
        logger.log_info(msg)

        return value

    def extract_response(self, extractors, context_obj):
        """ extract value from requests.Response and store in OrderedDict.
        @param (list) extractors
            [
                {"resp_status_code": "status_code"},
                {"resp_headers_content_type": "headers.content-type"},
                {"resp_content": "content"},
                {"resp_content_person_first_name": "content.person.name.first_name"}
            ]
        @return (OrderDict) variable binds ordered dict
        """
        if not extractors:
            return {}

        # logger.log_info("start to extract from response object.")
        extracted_variables_mapping = OrderedDict()
        extract_binds_order_dict = utils.convert_mappinglist_to_orderdict(extractors)

        try:
            for key, field in extract_binds_order_dict.items():
                extracted_variables_mapping[key] = self.extract_field(field, key=key, context_obj=context_obj)
                context_obj.update_testcase_runtime_variables_mapping({key: extracted_variables_mapping[key]})
        except Exception as err:
            raise

        return extracted_variables_mapping


if __name__ == '__main__':
    field = "content.person[0].name.first_name[5:]"
    field2 = "content.person[0].name.first_name[1]"
    field2 = "SELECT NEXT_VALUE FROM user_db.sequence[5:] WHERE SEQ_NAME='$MEMBER_ID';[5:]"
    sub_exp = None
    if field.endswith(']') and '[' in field and ':' in field.split('[')[-1]:
        sub_exp = '[' + field.split('[')[-1]
        print("")

    if sub_exp:
        print(field[5:])
        new = eval('field' + sub_exp)
        print(new)

