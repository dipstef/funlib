import signal

from .decorator import decorator


@decorator
def timeout(func, seconds):
    def _handle_timeout(signum, frame):
        raise TimeoutError('Function call timed out')

    def timeout_execute(*args, **kwargs):
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(seconds)
        try:
            result = func(*args, **kwargs)
        finally:
            signal.alarm(0)
        return result

    return timeout_execute


class TimeoutError(Exception):
    pass