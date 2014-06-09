class FailedAttemptRetries(object):

    def __init__(self, sleep=None, err_callback=None):
        self._error_callback = err_callback
        self._sleep = sleep

    def __call__(self, failed_attempt):
        if self._should_stop(failed_attempt):
            failed_attempt.raise_cause()

        if self._error_callback:
            self._error_callback(failed_attempt)

        if self._sleep:
            self._sleep(failed_attempt)

    def _should_stop(self, function_call_error):
        return False


class StopAfterMaxTimes(FailedAttemptRetries):
    def __init__(self, max_times, err_callback=None, sleep=None):
        super(StopAfterMaxTimes, self).__init__(err_callback=err_callback, sleep=sleep)
        self._max_attempts = max_times

    def _should_stop(self, failed_attempt):
        return failed_attempt.number == self._max_attempts


def try_times(times, err_callback=None, sleep=None):
    return StopAfterMaxTimes(times, err_callback, sleep)