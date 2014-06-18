from collections import Hashable, namedtuple

from dated import utc

from .decorator import property_decorator, Decorator


class memoized(Decorator):

    def __init__(self, calls_cache=None):
        self._calls_cache = {} if calls_cache is None else calls_cache

    def _decorate(self, fun, args, kwargs):
        if _hashable_arguments(*args, **kwargs):
            result = self._get_from_cache_or_execute(fun, *args, **kwargs)
        else:
            result = self._fun(*args, **kwargs)

        return result

    def _get_from_cache_or_execute(self, fun, *args, **kwargs):
        call_key = self._call_key(*args, **kwargs)

        result = self._get_cache_result(call_key)
        if not result:
            result = fun(*args, **kwargs)
            self._set_result_to_cache(call_key, result)

        return result

    def _get_cache_result(self, call_key):
        result = self._calls_cache.get(call_key)
        return result

    def _set_result_to_cache(self, call_key, result):
        self._calls_cache[call_key] = result

    def __str__(self):
        return str(self._fun)

    def _call_key(self, *args, **kwargs):
        call_key = tuple(list(args) + kwargs.items())
        return call_key


def _hashable_arguments(*args, **kwargs):
    return isinstance(args, Hashable) and isinstance(kwargs.iteritems(), Hashable)


class cached(memoized):

    def __init__(self, expiration=None):
        super(cached, self).__init__()
        self._expiration = expiration

    def _get_cache_result(self, call_key):
        computed = super(cached, self)._get_cache_result(call_key)
        if computed and not (self._expiration and computed.older_than(self._expiration)):
            return computed.result

    def _set_result_to_cache(self, call_key, result):
        super(cached, self)._set_result_to_cache(call_key, ComputedResult(call_key, result))

    def get(self, *args, **kwargs):
        return super(cached, self)._get_cache_result(self._call_key(*args, **kwargs))


class ComputedResult(namedtuple('ComputedResult', ('call_key', 'result', 'date'))):
    def __new__(cls, call_key, result):
        return super(ComputedResult, cls).__new__(cls, call_key, result, utc.now())

    def older_than(self, time_delta):
        return utc.now() - self.date > time_delta


cached_property = property_decorator(cached)