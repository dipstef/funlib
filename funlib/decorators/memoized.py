import collections

from dated import utc

from ..decorator import decorator


@decorator
class memoized(object):

    def __init__(self, calls_cache=None):
        self._calls_cache = calls_cache if calls_cache is not None else {}

    def __call__(self, fun):
        def call_memoized(*args, **kwargs):
            if _hashable_arguments(*args, **kwargs):
                result = self._get_from_cache_or_execute(fun, *args, **kwargs)
            else:
                result = fun(*args, **kwargs)

            return result
        return call_memoized

    def _get_from_cache_or_execute(self, fun, *args, **kwargs):
        call_key = tuple(list(args) + kwargs.items())

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


def _hashable_arguments(*args, **kwargs):
    return isinstance(args, collections.Hashable) and isinstance(kwargs.iteritems(), collections.Hashable)


class cached(memoized):

    def __init__(self, expiration=None):
        super(cached, self).__init__()
        self._expiration = expiration

    def _get_cache_result(self, call_key):
        result_tuple = super(cached, self)._get_cache_result(call_key)
        if result_tuple:
            result, last_updated = result_tuple

            if not self._is_expired(last_updated):
                return result

    def _set_result_to_cache(self, call_key, result):
        super(cached, self)._set_result_to_cache(call_key, (result, utc.now()))

    def _is_expired(self, last_update):
        return bool(self._expiration) and utc.now() - last_update > self._expiration