import time


class Sleep(object):

    def __init__(self, seconds):
        self._seconds = seconds

    def __call__(self, failed_attempt):
        time.sleep(self._seconds)


class SleepIncrement(Sleep):

    def __init__(self, seconds, max_sleep=100):
        super(SleepIncrement, self).__init__(seconds)
        self._max_sleep = max_sleep

    def __call__(self, failed_attempt):
        super(SleepIncrement, self).__call__(failed_attempt)
        if self._seconds < self._max_sleep:
            seconds = self._increment_sleep(failed_attempt)
            seconds = seconds if seconds < self._max_sleep else self._max_sleep
            self._seconds = seconds

    def _increment_sleep(self, function_call_error):
        raise NotImplementedError


class SleepPenalty(SleepIncrement):

    def __init__(self, seconds, penalty, max_sleep=None):
        super(SleepPenalty, self).__init__(seconds, max_sleep)
        self._penalty = penalty

    def _increment_sleep(self, function_call_error):
        return self._seconds + self._penalty


class ExponentialSleep(SleepIncrement):
    def __init__(self, seconds, max_sleep=100):
        super(ExponentialSleep, self).__init__(seconds, max_sleep)
        self._max_sleep = max_sleep

    def _increment_sleep(self, function_call_error):
        return 2 ** function_call_error.attempts


def sleep(seconds):
    return Sleep(seconds)