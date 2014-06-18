from catches import catch, handle

from .. import FunctionCall
from .attempt import Attempts
from ..decorator import Decorator
from ..util import nothing
from .retries import try_times


class RetryOnErrors(FunctionCall):

    def __init__(self, fun, catches=None, result_check=None):
        super(RetryOnErrors, self).__init__(fun)

        self._result_check = result_check
        self._error_classes = catch(*catches or handle(Exception).doing(nothing))

    def _call_fun(self, *args, **kwargs):
        call_attempt = Attempts(self._fun, *args, **kwargs)

        while True:
            outcome = call_attempt(catches=self._error_classes, result_validator=self._result_check)
            if not outcome.error:
                return outcome.result


class FunctionRetry(RetryOnErrors):

    def __init__(self, fun, result_check=None, on_err=nothing, errors=(Exception,)):
        super(FunctionRetry, self).__init__(fun, (handle(*errors).doing(on_err), ), result_check)


class retry(Decorator):

    def __init__(self, times, on_err=nothing, sleep=None, result_check=None, on_errors=(Exception, )):
        self._handler = try_times(times, on_err, sleep=sleep)
        self._result_check = result_check
        self._on_errors = on_errors

    def _decorate(self, fun, args, kwargs):
        err_fun = kwargs.pop('on_err', self._handler)

        fun = FunctionRetry(fun, on_err=err_fun, result_check=self._result_check, errors=self._on_errors)
        return fun(*args, **kwargs)


class retry_on_errors(Decorator):

    def __init__(self, *error_handlers, **checks):
        self._error_handlers = error_handlers
        self._result_check = checks.pop('result', None)

    def _decorate(self, fun, args, kwargs):
        retry_fun = RetryOnErrors(fun, self._error_handlers, self._result_check)
        return retry_fun(*args, **kwargs)