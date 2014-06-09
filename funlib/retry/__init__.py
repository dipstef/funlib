import functools

from .. import FunctionCall
from .attempt import Attempt
from .retries import try_times
from .error import ErrorClasses


class FunctionRetryBase(FunctionCall):

    def __init__(self, fun, result_check=None):
        super(FunctionRetryBase, self).__init__(fun)

        self._result_check = result_check
        self._error_classes = (BaseException, )

    def _call_fun(self, *args, **kwargs):
        call_attempt = Attempt(self._fun, *args, **kwargs)

        while True:
            outcome = call_attempt(catch=self._error_classes)
            if not outcome.error and self._validate_result(outcome.result):
                return outcome.result
            else:
                self._err_callback(outcome)

    def _validate_result(self, result):
        return not self._result_check or self._result_check(result)

    def _err_callback(self, failed_attempt):
        error_callback = self._get_callback(failed_attempt.error)

        if error_callback:
            error_callback(failed_attempt)

    def _get_callback(self, error):
        return None


class GroupedRetry(FunctionRetryBase):

    def __init__(self, fun, result_check=None, *errors):
        super(GroupedRetry, self).__init__(fun, result_check)

        errors = errors or [(BaseException,)]
        self._error_handlers = ErrorClasses(*errors)
        self._error_classes = self._error_handlers.classes

    def _get_callback(self, error):
        return self._error_handlers.get(error.__class__)


class FunctionRetry(GroupedRetry):

    def __init__(self, fun, result_check=None, err_callback=None, on_errors=None):
        on_errors = on_errors or (BaseException, )
        super(FunctionRetry, self).__init__(fun, result_check, (on_errors, err_callback))


def retry_function(times, err_callback=None, sleep=None, result_check=None):

    def fun_retry(fun):
        @functools.wraps(fun)
        def retry_call(*args, **kwargs):
            err_fun = err_callback or kwargs.pop('err_callback', None)

            retry = FunctionRetry(fun, err_callback=try_times(times, err_fun, sleep=sleep), result_check=result_check)

            return retry(*args, **kwargs)

        return retry_call

    return fun_retry
