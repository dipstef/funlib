from .. import FunctionCall
from .attempt import Attempt
from funlib.decorator import decorator
from .retries import try_times
from .errors import ErrorClasses


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
        error_callback = self._get_err_callback(failed_attempt.error)

        if error_callback:
            error_callback(failed_attempt)

    def _get_err_callback(self, error):
        raise NotImplementedError


class ErrorsRetries(FunctionRetryBase):

    def __init__(self, fun, *errors, **checks):
        result_check = checks.pop('result_check', None)
        super(ErrorsRetries, self).__init__(fun, result_check)

        errors = errors or [(Exception,)]
        self._error_handlers = ErrorClasses(*errors)
        self._error_classes = self._error_handlers.classes

    def _get_err_callback(self, error):
        return self._error_handlers.get(error.__class__)


class FunctionRetry(FunctionRetryBase):

    def __init__(self, fun, result_check=None, on_err=None, errors=None):
        super(FunctionRetry, self).__init__(fun, result_check)
        self._error_classes = errors or (Exception,)
        self._errors_callback = on_err

    def _get_err_callback(self, error):
        return self._errors_callback

@decorator
def retry(fun, times, on_err=None, sleep=None, result_check=None, on_errors=(Exception, )):
    def retry_call(*args, **kwargs):
        err_fun = kwargs.pop('on_err', on_err)

        handler = try_times(times, err_fun, sleep=sleep)
        retry_fun = FunctionRetry(fun, on_err=handler, result_check=result_check, errors=on_errors)

        return retry_fun(*args, **kwargs)

    return retry_call


@decorator
def retry_on_errors(fun, *error_handlers, **checks):
    def retry_call(*args, **kwargs):
        handlers = kwargs.pop('error_handlers', error_handlers)
        retry_fun = ErrorsRetries(fun, *handlers, **checks)

        return retry_fun(*args, **kwargs)

    return retry_call