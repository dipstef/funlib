from funlib import Lambda
from funlib.retry import retry, retry_on_errors, try_times, handle
from funlib.retry.sleep import sleep, random_sleep, incremental_sleep


def _print_attempt(attempt):
    print attempt


def _fail(times=10):
    attempts = []

    def fail(times):
        attempts.append(len(attempts))
        attempted = len(attempts)

        if attempted <= times:
            raise ValueError(attempted)

        return attempted

    return Lambda(fail, times=times)


def _test_no_specific_error():

    @retry(times=4, on_err=_print_attempt, sleep=sleep(1))
    def test(attempt):
        return attempt()

    assert test(_fail(times=3)) == 4


def _test_on_value_error():
    @retry_on_errors((ValueError, try_times(4, on_err=_print_attempt, sleep=sleep(1))))
    def test2(attempt):
        return attempt()

    assert test2(_fail(times=3)) == 4


def _test_on_error_catches():
    @retry_on_errors(handle(ValueError).doing(try_times(2, on_err=_print_attempt, sleep=sleep(1))),
                     handle(StandardError).doing(try_times(2, on_err=_print_attempt, sleep=incremental_sleep(1))),
                     handle(BaseException).doing(try_times(10, on_err=_print_attempt, sleep=random_sleep(1, to=2))))
    def test3(attempt):
        return attempt()

    try:
        test3(_fail(times=10))
        assert False
    except ValueError, e:
        pass


def main():
    _test_no_specific_error()

    _test_on_value_error()

    _test_on_error_catches()


if __name__ == '__main__':
    main()