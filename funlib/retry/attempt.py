from datetime import datetime
import sys

from collections import Counter
from .. import Lambda, Function


class Attempt(object):

    def __init__(self, fun_call, number, start_time, call_time):
        self.call = fun_call
        self.number = number
        self.start_time = start_time
        self.call_time = call_time
        self.end_time = datetime.utcnow()

    @property
    def attempted(self):
        return self.end_time - self.start_time

    def __str__(self):
        return str(self.call)


class CompletedAttempt(Attempt):

    def __init__(self, fun_call, result, number, start_time, call_time):
        super(CompletedAttempt, self).__init__(fun_call, number, start_time, call_time)
        self.result = result
        self.error = None

    def outcome(self):
        return self.result

    def __str__(self):
        return '%s = %s' % (str(self.call), self.result)


class FailedAttempt(Attempt):

    def __init__(self, fun_call, error, error_count, catch, number, start_time, call_time):
        super(FailedAttempt, self).__init__(fun_call, number, start_time, call_time)
        self.result = None
        self.error = error
        self.error_count = error_count
        self.catch = catch

    def handle_error(self):
        if self.catch.handler:
            self.catch.handler(self)

    def outcome(self):
        self.raise_cause()

    def raise_cause(self):
        raise self.error, None, sys.exc_info()[2]

    def __str__(self):
        return '%s Failed attempt: %s, %s' % (str(self.call), self.number, self.error.__class__.__name__)


class Attempts(Function):

    def __init__(self, fun, *args, **kwargs):
        super(Attempts, self).__init__(Lambda(fun, *args, **kwargs))
        self.attempts = 0
        self.started = None
        self._calls = []
        self._error_counts = Counter()

    def __call__(self, catches, result_validator=None):
        call_time = self._new_attempt()

        try:
            attempt = CompletedAttempt(self._fun, self._fun(), self.attempts, self.started, call_time)

            if result_validator and not result_validator(attempt.result):
                raise ResultValidationError(attempt.result, result_validator)
        except catches.errors, e:
            catch = catches.get(e.__class__)

            self._error_counts.update(catch.errors)
            error_count = self._error_counts[e.__class__]

            attempt = FailedAttempt(self._fun, e, error_count, catch, self.attempts, self.started, call_time)
            attempt.handle_error()

        self._calls.append(attempt)

        return attempt

    def _new_attempt(self):
        call_time = datetime.utcnow()

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


class ResultValidationError(Exception):

    def __init__(self, result, validator):
        self.result = result
        self.validator = validator