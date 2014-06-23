from abc import abstractmethod
import functools
import inspect


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


class DecoratorBase(object):
    _instance = None
    _fun = None

    @property
    def fun(self):
        return self._fun

    @fun.setter
    def fun(self, fun):
        self._fun = fun
        functools.update_wrapper(self, fun)

    def __get__(self, instance, owner):
        return self._class_method_decorator(instance)

    def __call__(self, *args, **kwargs):
        assert self._fun
        return self._decorate(self._fun, args, kwargs)

    @abstractmethod
    def _decorate(self, fun, args, kwargs):
        raise NotImplementedError

    def __str__(self):
        return str(self._fun)

    def __getattr__(self, item):
        if hasattr(self._fun, item):
            return getattr(self._fun, item)
        else:
            raise AttributeError(item)

    @property
    def _class_method_decorator(self):
        decorator_class, decorated_fun = self.__class__, self._fun

        class ClassMethodDecorator(decorator_class):
            __metaclass__ = lambda name, bases, class_dict: type(decorator_class.__name__, bases, class_dict)

            def __init__(self, instance):
                self._instance = instance
                self._fun = functools.partial(decorated_fun, instance)

            def __new__(cls, *args, **kwargs):
                method_decorator = object.__new__(cls)
                method_decorator.__dict__ = dict(self.__dict__)
                return method_decorator

        return ClassMethodDecorator


class Decorator(DecoratorBase):

    def __new__(cls, *args, **kwargs):
        if _is_func_arg(*args, **kwargs):
            decorator = super(Decorator, cls).__new__(cls)
            decorator.__init__()
            decorator.fun = args[0]
            return NoArgsDecorator(decorator)
        else:
            def args_decorator(fun):
                decorator = super(Decorator, cls).__new__(cls)
                decorator.__init__(*args, **kwargs)
                decorator.fun = fun
                return decorator

        return args_decorator


class NoArgsDecorator(DecoratorBase):

    def __init__(self, fun_decorator):
        self.fun = fun_decorator
        self._decorator = fun_decorator

    def __get__(self, instance, owner):
        return self._decorator.__get__(instance, owner)

    def __call__(self, *args, **kwargs):
        return self._decorator(*args, **kwargs)

    def __getattr__(self, item):
        return getattr(self._decorator, item)


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

    def __get__(self, instance, owner):
        decorated = self._decorated.__get__(instance, owner)
        return decorated()