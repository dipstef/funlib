from .util import call_string


class Function(object):

    def __init__(self, fun):
        self._fun = fun

    @property
    def __name__(self):
        return self._fun.__name__

    def __call__(self, *args, **kwargs):
        return self._fun(*args, **kwargs)

    def __str__(self):
        return self.__name__

    def __unicode__(self):
        return unicode(str(self))


class FunctionCall(Function):

    def __init__(self, fun):
        super(FunctionCall, self).__init__(fun)
        self._last_call = None

    def __call__(self, *args, **kwargs):
        self._last_call = (args, kwargs)
        return self._call_fun(*args, **kwargs)

    def _call_fun(self, *args, **kwargs):
        return super(FunctionCall, self).__call__(*args, **kwargs)

    def __str__(self):
        if self._last_call is not None:
            args, kwargs = self._last_call
            return call_string(self._fun.__name__, *args, **kwargs)
        else:
            return super(FunctionCall, self).__str__()


class Lambda(Function):

    def __init__(self, fun, *args, **kwargs):
        super(Lambda, self).__init__(fun)
        self.args = args
        self.kwargs = kwargs or {}

    def __str__(self):
        return call_string(self._fun.__name__, *self.args, **self.kwargs)

    def __call__(self):
        return self._fun(*self.args, **self.kwargs)