# encoding: utf-8

from atp.httprunner.compat import JSONDecodeError, FileNotFoundError

""" failure type exceptions
    these exceptions will mark test as failure
"""

class MyBaseFailure(Exception):
    pass

class ValidationFailure(MyBaseFailure):
    pass

class ExtractFailure(MyBaseFailure):
    pass

class SetupHooksFailure(MyBaseFailure):
    pass

class TeardownHooksFailure(MyBaseFailure):
    pass

class RequestFailure(MyBaseFailure):
    pass


""" error type exceptions
    these exceptions will mark test as error
"""

class MyBaseError(Exception):
    pass

class FileFormatError(MyBaseError):
    pass

class ParamsError(MyBaseError):
    pass

class NotFoundError(MyBaseFailure):
    pass

class FileNotFound(FileNotFoundError, NotFoundError):
    pass

class FunctionNotFound(NotFoundError):
    pass

class VariableNotFound(NotFoundError):
    pass

class ApiNotFound(NotFoundError):
    pass

class TestcaseNotFound(NotFoundError):
    pass

class CustomFuncRunError(MyBaseFailure):
    pass
