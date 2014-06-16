from .. import FunctionCall
from .attempt import Attempts
from ..decorator import decorator
from ..util import nothing
from .retries import try_times
from .errors import ErrorCatches, handle


class RetryOnErrors(FunctionCall):

    def __init__(self, fun, catches=None, result_check=None):
        super(RetryOnErrors, self).__init__(fun)

        self._result_check = result_check
        self._error_classes = ErrorCatches(*catches or handle(Exception).doing(nothing))

    def _call_fun(self, *args, **kwargs):
        call_attempt = Attempts(self._fun, *args, **kwargs)

        while True:
            outcome = call_attempt(catches=self._error_classes, result_validator=self._result_check)
            if not outcome.error:
                return outcome.result

    def _validate_result(self, result):
        return not self._result_check or self._result_check(result)


class FunctionRetry(RetryOnErrors):

    def __init__(self, fun, result_check=None, on_err=nothing, errors=(Exception,)):
        super(FunctionRetry, self).__init__(fun, (handle(*errors).doing(on_err), ), result_check)


@decorator
def retry(fun, times, on_err=nothing, sleep=None, result_check=None, on_errors=(Exception, )):
    def retry_call(*args, **kwargs):
        err_fun = kwargs.pop('on_err', on_err)

        handler = try_times(times, err_fun, sleep=sleep)
        retry_fun = FunctionRetry(fun, on_err=handler, result_check=result_check, errors=on_errors)

        return retry_fun(*args, **kwargs)

    return retry_call


@decorator
def retry_on_errors(fun, *error_handlers, **checks):
    def retry_call(*args, **kwargs):
        result_check = checks.pop('result', None)

        retry_fun = RetryOnErrors(fun, error_handlers, result_check)

        return retry_fun(*args, **kwargs)

    return retry_call