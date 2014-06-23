import functools


def call_string(fun_name, *args, **kwargs):
    args_str = ','.join('%s' % arg for arg in args)

    key_args = ','.join(('%s=%s' % (key, value) for (key, value) in kwargs.iteritems()))

    return '%s(%s%s)' % (fun_name, args_str, ',' + key_args if args_str and key_args else key_args)


def nothing(*args, **kwargs):
    pass


class method_call(functools.partial):

    def __init__(self, fun, instance):
        super(method_call, self).__init__(fun, instance)
        self._fun = fun
        functools.update_wrapper(self, fun)

    def __str__(self):
        return str(self._fun)