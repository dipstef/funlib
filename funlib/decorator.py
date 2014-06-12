import functools
import inspect
from .util import instance_fun


def decorator(func):
    ''' Allow to use decorator either with arguments or not. '''
    if isinstance(func, type):
        return _class_wrapper(func)
    else:
        return _func_wrapper(func)


def _is_func(arg):
    return inspect.isfunction(arg) or inspect.ismethod(arg) or isinstance(arg, type)


def _is_func_arg(*args, **kwargs):
    return len(args) == 1 and len(kwargs) == 0 and (_is_func(args[0]))


def _class_wrapper(class_decorator):

    class class_wrapper(class_decorator):

        def __new__(cls, *args, **kwargs):
            if _is_func_arg(*args, **kwargs):
                klass = class_decorator.__new__(cls)
                klass.__init__()
                classed = klass(*args, **kwargs)
                functools.update_wrapper(classed, args[0])
            else:
                classed = class_decorator.__new__(cls, *args, **kwargs)
                classed.__init__(*args, **kwargs)

            return classed

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


def property_decorator(decoration):
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