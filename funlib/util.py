from unicoder.text import byte_string


def call_string(fun_name, *args, **kwargs):
    args_str = ','.join('%s' % arg for arg in args)

    key_args = ','.join(('%s=%s' % (key, value) for (key, value) in kwargs.iteritems()))

    return byte_string('%s(%s%s)' % (fun_name, args_str, ',' + key_args if args_str and key_args else key_args))