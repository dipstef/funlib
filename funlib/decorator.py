import functools
import inspect
from .util import instance_fun


def decorator(func):
    ''' Allow to use decorator either with arguments or not. '''
    if isinstance(func, type):
        return _class_wrapper(func)
    else:
        return _func_wrapper(func)


def _is_func_arg(*args, **kw):
    return len(args) == 1 and len(kw) == 0 and (inspect.isfunction(args[0]) or isinstance(args[0], type))


def _class_wrapper(func):

    def class_wrapper(*args, **kw):
        if _is_func_arg(*args, **kw):
            # create class before usage
            return func()(*args, **kw)
        return func(*args, **kw)

    class_wrapper.__name__ = func.__name__
    class_wrapper.__module__ = func.__module__

    return class_wrapper


def _func_wrapper(func):
    @functools.wraps(func)
    def func_wrapper(*args, **kw):
        if _is_func_arg(*args, **kw):
            return func(*args, **kw)
        else:
            def functor(user_fun):
                return func(user_fun, *args, **kw)

            return functor
    return func_wrapper


def decorated_property(decoration):
    @decorator
    def decorate(fget, *args, **kwargs):
        if args or kwargs:
            return property(decoration(*args, **kwargs)(fget))
        else:
            return property(decoration(fget))
    return decorate


class Decorator(object):

    def __init__(self, fun):
        self._fun = fun
        functools.update_wrapper(self, fun)
        self._instance = None

    def __get__(self, instance, owner):
        assert self._fun

        if not self._instance:
            self._fun = instance_fun(instance, self._fun)
            self._instance = instance

        return self

    def __str__(self):
        return str(self._fun)


class ParamDecorator(object):
    _fun = None

    def __call__(self, fun, doc=None):
        self._fun = fun
        functools.update_wrapper(self, fun)
        return self

    def __str__(self):
        return str(self._fun)