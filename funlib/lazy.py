import time

from .decorator import ParamDecorator
from .util import instance_fun
from .decorators.memoized import memoized


class CachedCall(ParamDecorator):
    def __init__(self, expiration=0):
        assert isinstance(expiration, int)
        self.expiration = expiration

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

        return memoized(instance_fun(instance, self._fun))


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