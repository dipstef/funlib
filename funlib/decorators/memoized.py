import collections

from ..decorator import Decorator


class memoized(Decorator):

    def __init__(self, fun):
        super(memoized, self).__init__(fun)
        self._calls_cache = {}

    def __call__(self, *args, **kwargs):
        if _hashable_arguments(*args, **kwargs):
            result = self._get_from_cache_or_execute(*args, **kwargs)
        else:
            result = self._fun(*args, **kwargs)

        return result

    def _get_from_cache_or_execute(self, *args, **kwargs):
        call_key = tuple(list(args) + kwargs.items())

        result = self._get_cache_result(call_key)
        if not result:
            result = self._fun(*args, **kwargs)
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