import sys
from collections import namedtuple, Counter
from dated.normalized import utc
from .. import LambdaFunction, Function


class Attempt(object):

    def __init__(self, fun_call, number, start_time, call_time, end_time):
        self.call = fun_call
        self.number = number
        self.start_time = start_time
        self.call_time = call_time
        self.end_time = end_time

    @property
    def attempted(self):
        return self.end_time - self.start_time

    def __str__(self):
        return str(self.call)


class CompletedAttempt(Attempt):

    def __init__(self, fun_call, result, number, start_time, call_time, end_time):
        super(CompletedAttempt, self).__init__(fun_call, number, start_time, call_time, end_time)
        self.result = result
        self.error = None

    def outcome(self):
        return self.result

    def __str__(self):
        return '%s = %s' % (str(self.call), self.result)


class FailedAttempt(Attempt):

    def __init__(self, fun_call, error, error_count, catch_clause, number, start_time, call_time, end_time):
        super(FailedAttempt, self).__init__(fun_call, number, start_time, call_time, end_time)
        self.result = None
        self.error = error
        self.error_count = error_count
        self.catch_clause = catch_clause

    def outcome(self):
        self.raise_cause()

    def raise_cause(self):
        raise self.error, None, sys.exc_info()[2]

    def __str__(self):
        return '%s Failed: %s: %s' % (str(self.call), self.number, self.error.__class__.__name__)


class Attempts(Function):

    def __init__(self, fun, *args, **kwargs):
        super(Attempts, self).__init__(LambdaFunction(fun, *args, **kwargs))
        self.attempts = 0
        self.started = None
        self._calls = []
        self._error_counts = Counter()

    def __call__(self, catch=(BaseException, )):
        call_time = self._new_attempt()

        try:
            result = self._fun()

            result = CompletedAttempt(self._fun, result, self.attempts, self.started, call_time, utc.now())
        except catch, e:
            self._error_counts.update(catch)
            error_count = self._error_counts[catch]
            result = FailedAttempt(self._fun, e, error_count, catch, self.attempts, self.started, call_time, utc.now())

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