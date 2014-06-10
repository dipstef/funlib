import signal
import functools


def timeout(seconds, error_message='Function call timed out'):

    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @functools.wraps(func)
        def timeout_execute(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return timeout_execute

    return decorated


class TimeoutError(Exception):
    pass