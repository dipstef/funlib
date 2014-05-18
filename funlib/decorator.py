import signal
import functools
import collections
from .error import TimeoutError


def timeout(seconds, error_message='Function call timed out'):
    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return functools.wraps(func)(wrapper)

    return decorated


class Memoized(object):

    def __init__(self, fun, call_cache=None):
        self._fun = fun
        self._calls = call_cache or {}

    def __call__(self, *args, **kwargs):
        if _hashable_arguments(*args, **kwargs):
            result = self._execute_and_cache(*args, **kwargs)
        else:
            result = self._execute_fun(*args, **kwargs)

        return result

    def _execute_and_cache(self, *args, **kwargs):
        call_key = tuple(list(args) + kwargs.items())

        result = self._calls.get(call_key)
        if not result:
            result = self._execute_fun(*args, **kwargs)
            self._calls[call_key] = result

        return result

    def _execute_fun(self, *args, **kwargs):
        return self._fun(*args, **kwargs)


def _hashable_arguments(*args, **kwargs):
    return isinstance(args, collections.Hashable) and isinstance(kwargs.iteritems(), collections.Hashable)

memoized = Memoized