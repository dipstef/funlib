import functools
import time

from .decorator import Memoized


class Wraps(object):
    __name__ = '__wrapper__'
    _fun = None

    def _wraps(self, fun, doc=None):
        self.__doc__ = doc or fun.__doc__
        self.__name__ = fun.__name__
        self.__module__ = fun.__module__
        self._fun = fun


class CachedCall(Wraps):
    def __init__(self, expiration=0):
        assert isinstance(expiration, int)
        self.expiration = expiration

    def __call__(self, property_fun, doc=None):
        self._wraps(property_fun, doc)
        return self

    def __get__(self, instance, owner):
        assert self._fun

        cache = _get_call_cache(instance)
        value, last_update = cache.get(self.__name__, (None, None))

        if not value or self._value_expired(last_update):
            value = self._execute(instance)
            cache[self.__name__] = (value, time.time())

        return value

    def _value_expired(self, last_update):
        return 0 < self.expiration < time.time() - last_update

    def _execute(self, inst):
        raise not NotImplementedError


def _get_call_cache(instance):
    try:
        cache = instance._cache
    except AttributeError:
        cache = instance._cache = {}
    return cache


class CachedFun(CachedCall):

    def _execute(self, instance):
        memoized = MemoizedClassFun(instance, self._fun)

        @functools.wraps(self._fun)
        def call_memoized(*args, **kwargs):
            return memoized(*args, **kwargs)

        return call_memoized


class MemoizedClassFun(Memoized):

    def __init__(self, instance, fun):
        super(MemoizedClassFun, self).__init__(fun, call_cache=_get_call_cache(instance))
        self._instance = instance

    def _execute_fun(self, *args, **kwargs):
        return super(MemoizedClassFun, self)._execute_fun(self._instance, *args, **kwargs)


class LazyFun(CachedFun):
    def __init__(self, function):
        super(LazyFun, self).__init__(expiration=0)
        self.__call__(function)


class CachedProperty(CachedCall):
    def _execute(self, instance):
        return self._fun(instance)


class LazyProperty(CachedProperty):
    def __init__(self, property_fun):
        super(LazyProperty, self).__init__(expiration=0)
        self.__call__(property_fun)

cached = CachedFun
lazy = LazyFun

cached_property = CachedProperty
lazy_property = LazyProperty