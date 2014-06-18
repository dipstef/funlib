import functools
import inspect
from .util import instance_fun


def decorator(func):
    ''' Allow to use decorator either with arguments or not. '''

    @functools.wraps(func)
    def func_wrapper(*args, **kw):
        if _is_func_arg(*args, **kw):
            return func(args[0])
        else:
            def functor(user_fun):
                return func(user_fun, *args, **kw)

            return functor
    return func_wrapper


def _is_func_arg(*args, **kwargs):
    def _is_func(arg):
        return inspect.isfunction(arg) or inspect.ismethod(arg) or isinstance(arg, type)

    return len(args) == 1 and len(kwargs) == 0 and (_is_func(args[0]))


def property_decorator_(decoration):
    return property_decorator(decoration)


class DecoratorBase(object):

    def __init__(self, fun):
        self._fun = fun
        functools.update_wrapper(self, fun)
        self._instance = None

    def __get__(self, instance, owner):
        if not self._instance:
            self._fun = instance_fun(instance, self._fun)
            self._instance = instance
        return self

    def __call__(self, *args, **kwargs):
        return self._fun(*args, **kwargs)

    def __str__(self):
        return str(self._fun)


class Decorator(DecoratorBase):

    def __new__(cls, *args, **kwargs):
        if _is_func_arg(*args, **kwargs):
            return super(Decorator, cls).__new__(cls, args[0])
        else:
            def decorator_with_args(fun):
                klass = super(Decorator, cls).__new__(cls, fun)
                klass.__init__(fun, *args, **kwargs)
                return klass

            return decorator_with_args


class property_decorator(object):

    def __init__(self, decorator_fun):
        self._decorator = decorator_fun

    def __call__(self, *args, **kwargs):
        if _is_func_arg(*args, **kwargs):
            return PropertyDecorated(self._decorator(args[0]))
        else:
            return property_decorator(self._decorator(*args, **kwargs))


class PropertyDecorated(object):

    def __init__(self, decorated):
        self._decorated = decorated
        self._instance = None

    def __get__(self, instance, owner):
        decorated = self._decorated.__get__(instance, owner)
        return decorated()