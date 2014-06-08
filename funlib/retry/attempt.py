import sys
from collections import namedtuple
from dated.normalized import utc
from .. import LambdaFunction

attempt = namedtuple('attempt', ['call_time', 'end_time', 'result', 'error'])


class FunctionAttempt(LambdaFunction):
    def __init__(self, fun, *args, **kwargs):
        super(FunctionAttempt, self).__init__(fun, *args, **kwargs)
        self.attempts = 0
        self._calls = []

    def __call__(self):
        call_time = utc.now()
        self.attempts += 1

        try:
            result = super(FunctionAttempt, self).__call__()

            result = attempt(call_time, utc.now(), result, None)
        except BaseException, e:
            result = attempt(call_time, utc.now(), None, e)

        self._calls.append(result)
        return result

    @property
    def result(self):
        last_call = self.last_call
        if last_call:
            if last_call.error:
                _raise_cause_trace(last_call.error)

            return self.last_call.result

    @property
    def error(self):
        last_call = self.last_call
        if last_call and last_call.error:
            return last_call.error

    @property
    def last_call(self):
        return self._calls[-1] if self._calls else None

    @property
    def started(self):
        return self._calls[0].call_time if self._calls else None

    @property
    def attempted(self):
        if self.started:
            return self._calls[-1].end_time - self.started

    def raise_cause(self):
        if self.error:
            raise _raise_cause_trace(self.error)

    def __str__(self):
        call_string = super(FunctionAttempt, self).__str__()

        last_call = self.last_call

        if not last_call:
            return call_string
        elif last_call.error:
            return '%s Failed: %s: %s' % (call_string, self.attempts, self.error.__class__.__name__)
        else:
            return '%s = %s' % (call_string, last_call.result)


def _raise_cause_trace(error):
    raise error, None, sys.exc_info()[2]