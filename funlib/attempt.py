import functools
import sys

from . import FunctionCall, LambdaFunction


class FunctionAttempt(object):

    def execute(self, fun, *args, **kwargs):
        function_call = LambdaFunction(fun, *args, **kwargs)

        while True:
            try:
                result = self._execute(function_call)
                return result
            except BaseException, e:
                self._handler_error(function_call, e)

    def _execute(self, function_call):
        result = function_call()
        return result

    def _handler_error(self, function_call, error):
        raise error


class ExecuteMaxTimes(FunctionAttempt):
    def __init__(self, max_times, call_back=None, err_callback=None):
        self._max_attempts = max_times
        self._attempted = 0
        self._call_back = call_back
        self._error_callback = err_callback

    def _execute(self, function_call):
        self._attempted += 1
        result = super(ExecuteMaxTimes, self)._execute(function_call)
        if self._call_back:
            function_result = AttemptedFunctionResult(function_call, self._attempted, result)
            self._call_back(function_result)

    def _handler_error(self, function_call, error):
        if self._attempted == self._max_attempts:
            _raise_cause_trace(error)
        elif self._error_callback:
            function_call_error = AttemptedFunctionCallError(function_call, self._attempted, error)
            self._error_callback(function_call_error)


def _raise_cause_trace(error):
    raise error, None, sys.exc_info()[2]


class AttemptedFunctionCall(object):

    def __init__(self, function_call, attempt):
        self._function_call = function_call
        self.attempt = attempt

    def __str__(self):
        return '%s' % self._function_call


class AttemptedFunctionCallError(AttemptedFunctionCall):
    def __init__(self, function_call, attempt, error):
        super(AttemptedFunctionCallError, self).__init__(function_call, attempt)
        self.error = error

    def raise_cause(self):
        raise _raise_cause_trace(self.error)

    def __str__(self):
        return '%s Failed: %s: %s' % (self._function_call, self.error.__class__.__name__, self.error.message)


class AttemptedFunctionResult(AttemptedFunctionCall):
    def __init__(self, function_call, attempt, result):
        super(AttemptedFunctionResult, self).__init__(function_call, attempt)
        self.result = result

    def __str__(self):
        return '%s = %s' % (self._function_call, self.result)


class FunctionRetry(FunctionCall):

    def __init__(self, fun, retry_attempt):
        super(FunctionRetry, self).__init__(fun)
        self._fun = fun
        self._attempts = retry_attempt

    def _call_fun(self, *args, **kwargs):
        return self._attempts.execute(self._fun, *args, **kwargs)


def retry_function(max_times, callback=None, err_callback=None):

    def fun_retry(fun):
        @functools.wraps(fun)
        def wrapping(*args, **kwargs):
            callback_fun = callback or kwargs.pop('callback')
            err_callback_fun = err_callback or kwargs.pop('err_callback')

            retry = FunctionRetry(fun, ExecuteMaxTimes(max_times, callback_fun, err_callback_fun))

            return retry(*args, **kwargs)

        return wrapping

    return fun_retry