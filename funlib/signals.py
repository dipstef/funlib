import signal

from .decorator import decorator


class Signal(Exception):
    def __init__(self, signal_number, traceback):
        super(Signal, self).__init__(signal_number, traceback)
        self.signal = signal_number
        self.message = 'Signal received: %d' % signal_number


def raise_signal(sig):
    def raise_sig(action, traceback):
        raise Signal(action, traceback)
    signal.signal(sig, raise_sig)


@decorator
def sig_raise(func, sig):
    def timeout_execute(*args, **kwargs):
        raise_signal(sig)
        return func(*args, **kwargs)

    return timeout_execute


class Termination(Signal):
    def __init__(self, traceback):
        super(Termination, self).__init__(signal.SIGKILL, traceback)
        self.message = 'SIGKILL %d' % self.signal


def raise_termination():
    def raise_sig(action, traceback):
        raise Termination(traceback)
    signal.signal(signal.SIGTERM, raise_sig)


@decorator
def termination_raise(func):
    def timeout_execute(*args, **kwargs):
        raise_termination()
        return func(*args, **kwargs)

    return timeout_execute


@decorator
def timeout(func, seconds):
    def _handle_timeout(signum, frame):
        raise CallTimeout('Function call timed out')

    def timeout_execute(*args, **kwargs):
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(seconds)
        try:
            result = func(*args, **kwargs)
        finally:
            signal.alarm(0)
        return result

    return timeout_execute


class CallTimeout(Exception):
    pass