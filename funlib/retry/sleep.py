import random
import time


class Sleep(object):

    def __init__(self, seconds):
        self._seconds = seconds

    def __call__(self, failed_attempt):
        self.zzz(self.sleepy_time(failed_attempt))

    def zzz(self, seconds):
        time.sleep(seconds)

    def sleepy_time(self, failed_attempt):
        return self._seconds


class RandomSleep(Sleep):

    def __init__(self, from_seconds, to_seconds):
        super(RandomSleep, self).__init__(from_seconds)
        self._to_seconds = to_seconds

    def sleepy_time(self, failed_attempt):
        return random.randint(self._seconds, self._to_seconds)


class IncrementalSleep(Sleep):

    def __init__(self, seconds, max_sleep=100):
        super(IncrementalSleep, self).__init__(seconds)
        self._max_sleep = max_sleep or seconds
        self._times = 0

    def sleepy_time(self, failed_attempt):
        if self._times and self._seconds < self._max_sleep:
            seconds = self._increment_sleep(failed_attempt)

            self._seconds = seconds if seconds < self._max_sleep else self._max_sleep

        self._times += 1
        return self._seconds

    def _increment_sleep(self, failed_attempt):
        raise NotImplementedError


class SleepPenalty(IncrementalSleep):

    def __init__(self, seconds, penalty, max_sleep=None):
        super(SleepPenalty, self).__init__(seconds, max_sleep)
        self._penalty = penalty

    def _increment_sleep(self, failed_attempt):
        return self._seconds + self._penalty


class ExponentialSleep(IncrementalSleep):
    def __init__(self, seconds, max_sleep=100):
        super(ExponentialSleep, self).__init__(seconds, max_sleep)
        self._max_sleep = max_sleep

    def _increment_sleep(self, failed_attempt):
        return 2 ** failed_attempt.attempts


def sleep(seconds):
    return Sleep(seconds)


def incremental_sleep(seconds, by=1, to=60):
    return SleepPenalty(seconds, penalty=by, max_sleep=to)


def random_sleep(from_seconds, to):
    return RandomSleep(from_seconds, to)