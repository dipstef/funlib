import sys
from collections import namedtuple
from dated.normalized import utc
from .. import LambdaFunction, Function

attempt = namedtuple('attempt', ['call_time', 'end_time', 'result', 'error'])


class CallAttempt(object):

    def __init__(self, number, start_time, call_time, end_time):
        self.number = number
        self.start_time = start_time
        self.call_time = call_time
        self.end_time = end_time

    @property
    def attempted(self):
        return self.end_time - self.start_time


class CompletedAttempt(CallAttempt):

    def __init__(self, fun_call, result, number, start_time, call_time, end_time):
        super(CompletedAttempt, self).__init__(number, start_time, call_time, end_time)
        self.result = result
        self.error = None
        self._fun_call = fun_call

    def outcome(self):
        return self.result

    def __str__(self):
        return '%s = %s' % (str(self._fun_call), self.result)


class FailedAttempt(CallAttempt):

    def __init__(self, fun_call, error, number, start_time, call_time, end_time):
        super(FailedAttempt, self).__init__(number, start_time, call_time, end_time)
        self.result = None
        self.error = error
        self._fun_call = fun_call

    def outcome(self):
        self.raise_cause()

    def raise_cause(self):
        raise self.error, None, sys.exc_info()[2]

    def __str__(self):
        return '%s Failed: %s: %s' % (str(self._fun_call), self.number, self.error.__class__.__name__)


class FunctionAttempt(Function):
    def __init__(self, fun, *args, **kwargs):
        super(FunctionAttempt, self).__init__(LambdaFunction(fun, *args, **kwargs))
        self.attempts = 0
        self.started = None
        self._calls = []

    def __call__(self):
        call_time = self._new_attempt()

        try:
            result = self._fun()

            result = CompletedAttempt(self._fun, result, self.attempts, self.started, call_time, utc.now())
        except BaseException, e:
            result = FailedAttempt(self._fun, e, self.attempts, self.started, call_time, utc.now())

        self._calls.append(result)

        return result

    def _new_attempt(self):
        call_time = utc.now()

        if not self.attempts:
            self.started = call_time

        self.attempts += 1
        return call_time

    @property
    def last_call(self):
        return self._calls[-1] if self._calls else None

    def __str__(self):
        if self._calls:
            return str(self.last_call)
        else:
            return str(self._fun)