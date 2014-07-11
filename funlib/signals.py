from functools import wraps
import signal

from .decorator import decorator


class Signal(Exception):
    def __init__(self, signal_number, traceback):
        super(Signal, self).__init__(signal_number, traceback)
        self.signal = signal_number
        self.message = 'Signal received: %d' % signal_number


class Termination(Signal):
    def __init__(self, traceback):
        super(Termination, self).__init__(signal.SIGKILL, traceback)
        self.message = 'SIGKILL %d' % self.signal


class SigRaise(Signal):
    def __new__(cls, signal_number, traceback):
        if signal_number == signal.SIGTERM:
            return Termination(traceback)
        return Signal(signal_number, traceback)


def raise_signal(sig):
    def raise_sig(action, traceback):
        raise SigRaise(action, traceback)
    signal.signal(sig, raise_sig)


@decorator
def sig_raise(fun, sig):
    @wraps(fun)
    def timeout_execute(*args, **kwargs):
        raise_signal(sig)
        return fun(*args, **kwargs)

    return timeout_execute


def raise_termination():
    return raise_signal(signal.SIGTERM)

@sig_raise(signal.SIGTERM)
def termination_raise(fun):
    @wraps(fun)
    def timeout_execute(*args, **kwargs):
        return fun(*args, **kwargs)

    return timeout_execute


@decorator
def timeout(fun, seconds):
    def _handle_timeout(signum, frame):
        raise CallTimeout('Function call timed out')

    def timeout_execute(*args, **kwargs):
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(seconds)
        try:
            result = fun(*args, **kwargs)
        finally:
            signal.alarm(0)
        return result

    return timeout_execute


class CallTimeout(Exception):
    pass