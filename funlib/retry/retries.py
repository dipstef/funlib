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


class AttemptTimes(FailedAttemptRetries):

    def __init__(self, times=None, err_callback=None, sleep=None):
        super(AttemptTimes, self).__init__(err_callback=err_callback, sleep=sleep)
        self.times = times

    def _should_stop(self, failed_attempt):
        return self.times and failed_attempt.error_count == self.times


def try_times(times, on_err=None, sleep=None):
    return AttemptTimes(times, on_err, sleep)