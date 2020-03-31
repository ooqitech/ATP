# -*- coding:utf-8 -*-

import json

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


class LoadCaseError(BaseException):
    """
    组装用例时发生错误
    """
    pass


class RunCaseError(BaseException):
    """
    执行用例时发生错误
    """
    pass

class NoSuchElementError(BaseException):
    """
    元素路径错误：
    """
