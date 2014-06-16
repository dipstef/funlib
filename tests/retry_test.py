from funlib.retry import retry, retry_on_errors, try_times, handle
from funlib.retry.sleep import sleep, random_sleep


_attempts = []


def _print_attempt(attempt):
    print attempt


def _print_value_error(attempt):
    print attempt.call, 'Value Error: ', attempt.error


def _test(i):
    _attempts.append(i)
    attempted = len(_attempts)

    if attempted < 10:
        raise ValueError(attempted)

    return i


def _test_no_specific_error():
    @retry(times=10, on_err=_print_attempt, sleep=sleep(1))
    def test(i):
        return _test(i)

    global _attempts
    _attempts = []

    assert test(1) == 1


def _test_on_value_error():
    @retry_on_errors((ValueError, try_times(10, on_err=_print_value_error, sleep=sleep(1))))
    def test2(i):
        return _test(i)

    global _attempts
    _attempts = []
    assert test2(1) == 1


def _test_on_error_catches():
    @retry_on_errors(handle(BaseException).doing(try_times(10, on_err=_print_attempt, sleep=random_sleep(1, to=2))),
                     handle(ValueError).doing(try_times(2, on_err=_print_value_error, sleep=sleep(1))))
    def test3(i):
        return _test(i)

    global _attempts
    _attempts = []
    try:
        test3(1)
    except ValueError, e:
        pass


def main():
    _test_no_specific_error()

    _test_on_value_error()

    _test_on_error_catches()


if __name__ == '__main__':
    main()