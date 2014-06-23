from collections import Hashable, namedtuple

from dated import utc

from .decorator import property_decorator, Decorator


class memoized(Decorator):

    def __init__(self, calls_cache=None):
        self._cache = {} if calls_cache is None else calls_cache

    def _decorate(self, fun, args, kwargs):
        if _hashable_arguments(*args, **kwargs):
            result = self._get_from_cache_or_execute(fun, *args, **kwargs)
        else:
            result = self._decorated(*args, **kwargs)

        return result

    def _get_from_cache_or_execute(self, fun, *args, **kwargs):
        call_key = _call_key(*args, **kwargs)

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
        return str(self._decorated)

    @property
    def _calls_cache(self):
        return self._get_class_method_cache() if self._instance else self._cache

    def _get_class_method_cache(self):
        try:
            calls_cache = self._instance._calls_cache
        except AttributeError:
            calls_cache = self._instance._calls_cache = {}

        fun_cache = calls_cache.get(self.__name__)
        if not fun_cache:
            fun_cache = calls_cache[self.__name__] = {}
        return fun_cache

    def memoized(self, *args, **kwargs):
        return self._calls_cache.get(_call_key(*args, **kwargs))


def _hashable_arguments(*args, **kwargs):
    return isinstance(args, Hashable) and isinstance(kwargs.iteritems(), Hashable)


def _call_key(*args, **kwargs):
    call_key = tuple(list(args) + kwargs.items())
    return call_key


class cached(memoized):

    def __init__(self, expiration=None):
        super(cached, self).__init__()
        self._expiration = expiration

    def _get_cache_result(self, call_key):
        computed = super(cached, self)._get_cache_result(call_key)
        if computed and not computed.is_expired():
            return computed.result

    def _set_result_to_cache(self, call_key, result):
        super(cached, self)._set_result_to_cache(call_key, ComputedResult(call_key, result, self._expiration))

    def result(self, *args, **kwargs):
        computed = self.memoized(*args, **kwargs)
        if computed and not computed.is_expired():
            return computed.result


class ComputedResult(namedtuple('ComputedResult', ('call_key', 'result', 'date'))):
    def __new__(cls, call_key, result, expiration=None):
        if expiration:
            return ExpiringResult(call_key, result, expiration)
        else:
            return super(ComputedResult, cls).__new__(cls, call_key, result, utc.now())

    @staticmethod
    def is_expired():
        return False


class ExpiringResult(namedtuple('ExpiringResult', ('call_key', 'result', 'date', 'expiration'))):
    def __new__(cls, call_key, result, expiration):
        return super(ExpiringResult, cls).__new__(cls, call_key, result, utc.now(), expiration)

    def is_expired(self):
        return utc.now() - self.date > self.expiration

#like django.utils.functional import cached_property but allows to define an expiration
cached_property = property_decorator(cached)