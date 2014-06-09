import functools

from .. import FunctionCall
from .attempt import FunctionAttempt
from .error import try_times


class FunctionRetry(FunctionCall):

    def __init__(self, fun, result_check=None, err_callback=None):
        super(FunctionRetry, self).__init__(fun)
        self._fun = fun
        self._result_check = result_check

        self._error_callback = err_callback

    def _call_fun(self, *args, **kwargs):
        fun_attempt = FunctionAttempt(self._fun, *args, **kwargs)

        while True:
            outcome = fun_attempt()
            if not outcome.error and self._validate_result(outcome.result):
                return outcome.result
            else:
                self._err_callback(outcome)

    def _validate_result(self, result):
        return not self._result_check or self._result_check(result)

    def _err_callback(self, failed_attempt):
        if self._error_callback:
            self._error_callback(failed_attempt)


def retry_function(times, err_callback=None, sleep=None, result_check=None):

    def fun_retry(fun):
        @functools.wraps(fun)
        def retry_call(*args, **kwargs):
            err_fun = err_callback or kwargs.pop('err_callback', None)

            retry = FunctionRetry(fun, err_callback=try_times(times, err_fun, sleep=sleep), result_check=result_check)

            return retry(*args, **kwargs)

        return retry_call

    return fun_retry

